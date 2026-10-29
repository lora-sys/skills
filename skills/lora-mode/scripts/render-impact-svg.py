#!/usr/bin/env python3
"""Render a compact lora-mode PR/Issue graph SVG from a small JSON file."""

from __future__ import annotations

import argparse
import html
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


SCHEMA = "lora-change-map/v1"
NODE_STATUS = {
    "added": ("#1a7f37", "新增"),
    "modified": ("#9a6700", "修改"),
    "deleted": ("#cf222e", "删除"),
    "affected": ("#0969da", "受影响"),
    "unchanged": ("#57606a", "未改"),
    "observed": ("#0969da", "观察到"),
    "expected": ("#8250df", "期望"),
    "unknown": ("#6e7781", "待确认"),
    "inferred": ("#9a6700", "推测"),
}
VALID_CONFIDENCE = {"confirmed", "reported", "inferred", "unknown"}
ISSUE_NODE_STATUSES = {"observed", "expected", "unknown", "inferred"}


class GraphError(ValueError):
    pass


def need_text(obj: dict[str, Any], key: str, where: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise GraphError(f"{where}.{key} must be a non-empty string")
    return value.strip()


def validate(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise GraphError("root must be a JSON object")
    kind = data.get("kind")
    if kind not in {"pr", "issue", "state"}:
        raise GraphError("kind must be pr, issue, or state")
    out = dict(data)
    out["schema"] = SCHEMA
    out["title"] = need_text(out, "title", "root")
    out["scope"] = need_text(out, "scope", "root")
    out["unknowns"] = out.get("unknowns", [])
    if not isinstance(out["unknowns"], list) or not all(isinstance(x, str) for x in out["unknowns"]):
        raise GraphError("unknowns must be a list of strings")

    if kind == "pr":
        for phase in ("base", "head"):
            part = out.get(phase)
            if not isinstance(part, dict):
                raise GraphError(f"{phase} must be an object")
            need_text(part, "sha", phase)
            part.setdefault("ref", phase.title())
        out["nodes"] = validate_nodes(out.get("nodes"), "pr")
        out["edges"] = validate_edges(out.get("edges"), out["nodes"], "pr")
        out["modified"] = out.get("modified", [])
        if not isinstance(out["modified"], list) or not all(isinstance(x, str) for x in out["modified"]):
            raise GraphError("modified must be a list of node ids")
        base_ids = {n["id"] for n in out["nodes"] if n["presence"] in {"base", "both"}}
        head_ids = {n["id"] for n in out["nodes"] if n["presence"] in {"head", "both"}}
        if not set(out["modified"]) <= base_ids & head_ids:
            raise GraphError("modified node ids must exist in both base and head")
        for edge in out["edges"]:
            for phase in ("base", "head"):
                if edge["presence"] in {phase, "both"}:
                    phase_ids = base_ids if phase == "base" else head_ids
                    if edge["from"] not in phase_ids or edge["to"] not in phase_ids:
                        raise GraphError(f"{phase} edge references a node absent from that phase")
    else:
        out["nodes"] = validate_nodes(out.get("nodes"), "root", ISSUE_NODE_STATUSES)
        out["edges"] = validate_edges(out.get("edges"), out["nodes"], "root")
    return out


def validate_nodes(value: Any, where: str, allowed_statuses: set[str] | None = None) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise GraphError(f"{where}.nodes must be a non-empty list")
    result: list[dict[str, Any]] = []
    ids: set[str] = set()
    for i, item in enumerate(value):
        at = f"{where}.nodes[{i}]"
        if not isinstance(item, dict):
            raise GraphError(f"{at} must be an object")
        node = dict(item)
        node["id"] = need_text(node, "id", at)
        node["label"] = need_text(node, "label", at)
        if node["id"] in ids:
            raise GraphError(f"duplicate node id: {node['id']}")
        ids.add(node["id"])
        if where != "root":
            presence = node.get("presence", "both")
            if presence not in {"base", "head", "both"}:
                raise GraphError(f"{at}.presence must be base, head, or both")
            node["presence"] = presence
        elif allowed_statuses is not None:
            status = node.get("status", "unknown")
            if status not in allowed_statuses:
                raise GraphError(f"{at}.status is not supported")
            node["status"] = status
        node["evidence"] = str(node.get("evidence", ""))
        node["confidence"] = node.get("confidence", "unknown")
        if node["confidence"] not in VALID_CONFIDENCE:
            raise GraphError(f"{at}.confidence is not supported")
        if node["confidence"] != "unknown" and not node["evidence"].strip():
            raise GraphError(f"{at}.evidence is required when confidence is not unknown")
        result.append(node)
    return result


def validate_edges(value: Any, nodes: list[dict[str, Any]], where: str) -> list[dict[str, Any]]:
    if value is None:
        value = []
    if not isinstance(value, list):
        raise GraphError(f"{where}.edges must be a list")
    ids = {n["id"] for n in nodes}
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for i, item in enumerate(value):
        at = f"{where}.edges[{i}]"
        if not isinstance(item, dict):
            raise GraphError(f"{at} must be an object")
        edge = dict(item)
        for key in ("from", "to"):
            edge[key] = need_text(edge, key, at)
            if edge[key] not in ids:
                raise GraphError(f"{at}.{key} references missing node {edge[key]}")
        edge["relationship"] = need_text(edge, "relationship", at)
        edge["confidence"] = edge.get("confidence", "unknown")
        if edge["confidence"] not in VALID_CONFIDENCE:
            raise GraphError(f"{at}.confidence is not supported")
        edge["evidence"] = str(edge.get("evidence", ""))
        if edge["confidence"] != "unknown" and not edge["evidence"].strip():
            raise GraphError(f"{at}.evidence is required when confidence is not unknown")
        edge["presence"] = edge.get("presence", "both")
        if edge["presence"] not in {"base", "head", "both"}:
            raise GraphError(f"{at}.presence must be base, head, or both")
        key = (edge["from"], edge["to"], edge["relationship"])
        if key in seen:
            raise GraphError(f"duplicate edge {key}; use presence=both for an unchanged relationship")
        seen.add(key)
        result.append(edge)
    return result


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def line_wrap(text: str, limit: int = 20) -> list[str]:
    lines: list[str] = []
    current = ""
    width = 0
    if " " in text:
        parts = text.split(" ")
    elif "/" in text:
        segments = text.split("/")
        parts = [f"{segment}/" for segment in segments[:-1]] + [segments[-1]]
    else:
        parts = list(text)
    for part in parts:
        unit_width = sum(2 if ord(char) > 255 else 1 for char in part)
        spacer = " " if current and " " in text else ""
        if current and width + (1 if spacer else 0) + unit_width > limit:
            lines.append(current)
            current, width = "", 0
            spacer = ""
        if unit_width > limit:
            for char in part:
                char_width = 2 if ord(char) > 255 else 1
                if width + char_width > limit and current:
                    lines.append(current)
                    current, width = "", 0
                current += char
                width += char_width
            continue
        current += spacer + part
        width += (1 if spacer else 0) + unit_width
    if current:
        lines.append(current)
    if len(lines) > 3:
        lines = lines[:3]
        lines[-1] = lines[-1] + "…"
    return lines


def affected_distance(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], changed: set[str], phase: str | None = None) -> dict[str, int]:
    dependents: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        if phase and edge.get("presence", "both") not in {phase, "both"}:
            continue
        # A -> B means A depends on B, so changes to B affect A.
        dependents[edge["to"]].append(edge["from"])
    distances: dict[str, int] = {}
    queue = deque((node, 0) for node in changed)
    while queue:
        changed_id, distance = queue.popleft()
        for consumer in dependents.get(changed_id, []):
            if consumer in changed or consumer in distances:
                continue
            distances[consumer] = distance + 1
            queue.append((consumer, distance + 1))
    return distances


def ranks(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> tuple[dict[str, int], bool]:
    ids = {n["id"] for n in nodes}
    outgoing: dict[str, list[str]] = defaultdict(list)
    indegree = {node_id: 0 for node_id in ids}
    for edge in edges:
        if edge["from"] in ids and edge["to"] in ids:
            outgoing[edge["from"]].append(edge["to"])
            indegree[edge["to"]] += 1
    queue = deque(sorted(node_id for node_id, degree in indegree.items() if degree == 0))
    rank = {node_id: 0 for node_id in queue}
    visited = 0
    while queue:
        node_id = queue.popleft()
        visited += 1
        for target in outgoing[node_id]:
            rank[target] = max(rank.get(target, 0), rank[node_id] + 1)
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    acyclic = visited == len(ids)
    if not acyclic:
        return {node_id: 0 for node_id in ids}, False
    return rank, True


def layout_ranks(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> tuple[dict[str, int], bool]:
    rank, acyclic = ranks(nodes, edges)
    if acyclic:
        current = [rank[node["id"]] for node in nodes if node.get("status") != "deleted"]
        deleted_rank = max(current, default=0) + 1
        for node in nodes:
            if node.get("status") == "deleted":
                rank[node["id"]] = deleted_rank
    return rank, acyclic


def required_width(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], minimum: int = 560) -> int:
    rank, _ = layout_ranks(nodes, edges)
    counts: dict[int, int] = defaultdict(int)
    for node in nodes:
        counts[rank[node["id"]]] += 1
    widest = max(counts.values(), default=1) * 180 + max(0, max(counts.values(), default=1) - 1) * 20 + 36
    return max(minimum, widest)


def draw_graph(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], x0: int, y0: int, width: int, edge_changes: dict[tuple[str, str, str], str] | None = None, layout_edges: list[dict[str, Any]] | None = None) -> tuple[list[str], int]:
    if not nodes:
        return [f'<text x="{x0 + 24}" y="{y0 + 35}" class="muted">无模块节点</text>'], 90
    rank, acyclic = layout_ranks(nodes, edges if layout_edges is None else layout_edges)
    groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        groups[rank[node["id"]]].append(node)
    max_per_row = max(len(items) for items in groups.values())
    box_w, box_h, gap_x, gap_y = 180, 68, 20, 68
    graph_w = max(width, max_per_row * box_w + (max_per_row - 1) * gap_x + 36)
    centers: dict[str, tuple[int, int]] = {}
    parts: list[str] = []
    for layer, group in sorted(groups.items()):
        row_w = len(group) * box_w + max(0, len(group) - 1) * gap_x
        start_x = x0 + max(0, (graph_w - row_w) // 2)
        y = y0 + layer * (box_h + gap_y)
        for index, node in enumerate(group):
            x = start_x + index * (box_w + gap_x)
            centers[node["id"]] = (x + box_w // 2, y + box_h // 2)

    outgoing_edge_counts: dict[str, int] = defaultdict(int)
    for edge in edges:
        if edge["from"] in centers and edge["to"] in centers:
            outgoing_edge_counts[edge["from"]] += 1
    outgoing_edge_indexes: dict[str, int] = defaultdict(int)
    for edge in edges:
        source, target = edge["from"], edge["to"]
        if source not in centers or target not in centers:
            continue
        sx, sy = centers[source]
        tx, ty = centers[target]
        confidence = edge.get("confidence", "unknown")
        presence = edge.get("presence", "both")
        change = "removed" if presence == "base" else "added" if presence == "head" else (edge_changes or {}).get((source, target, edge.get("relationship", "")), "unchanged")
        forward = rank[source] < rank[target]
        rank_gap = abs(rank[target] - rank[source])
        side_route = change == "removed" or not forward or rank_gap > 1
        side = -1 if change == "removed" or not forward else 1
        if side_route:
            offset = box_w // 2 + 70
            if forward:
                start_y, end_y = sy + box_h // 2, ty - box_h // 2
                d = f"M {sx} {start_y} C {sx + side * offset} {start_y}, {tx + side * offset} {end_y}, {tx} {end_y}"
            else:
                start_x, end_x = sx + side * box_w // 2, tx + side * box_w // 2
                d = f"M {start_x} {sy} C {sx + side * offset} {sy}, {tx + side * offset} {ty}, {end_x} {ty}"
        elif forward:
            start_y, end_y = sy + box_h // 2, ty - box_h // 2
            mid_y = (start_y + end_y) / 2
            d = f"M {sx} {start_y} C {sx} {mid_y}, {tx} {mid_y}, {tx} {end_y}"
        else:
            start_x, end_x = sx + box_w // 2, tx - box_w // 2
            bend = max(start_x, end_x) + 28
            d = f"M {start_x} {sy} C {bend} {sy}, {bend} {ty}, {end_x} {ty}"
        stroke = "#1a7f37" if change == "added" else "#cf222e" if change == "removed" else "#57606a"
        dash = ' stroke-dasharray="6 5"' if confidence in {"reported", "inferred", "unknown"} or change == "removed" else ""
        marker = "arrow-green" if change == "added" else "arrow-red" if change == "removed" else "arrow"
        parts.append(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="2"{dash} marker-end="url(#{marker})"/>')
        confidence_label = {"reported": "报告", "inferred": "推测", "unknown": "待确认"}.get(confidence, "")
        relationship = edge.get("relationship", "")
        details = [label for label in (confidence_label,) if label]
        if change != "unchanged":
            details.append("新增" if change == "added" else "删除")
        suffix = " · ".join(details)
        max_relationship = max(6, 20 - len(suffix) - (3 if suffix else 0))
        if len(relationship) > max_relationship:
            relationship = relationship[: max_relationship - 1] + "…"
        label = f"{relationship} · {suffix}" if suffix else relationship
        if label:
            lx, ly = (sx + tx) // 2, (sy + ty) // 2
            if side_route:
                lx += side * (box_w // 2 + 85)
            index = outgoing_edge_indexes[source]
            outgoing_edge_indexes[source] += 1
            count = outgoing_edge_counts[source]
            ly += (index - (count - 1) / 2) * 15
            parts.append(f'<text x="{lx}" y="{ly - 5}" text-anchor="middle" class="edge-label">{escape(label)}</text>')

    for node in nodes:
        x, cy = centers[node["id"]]
        y = cy - box_h // 2
        color, status_label = NODE_STATUS[node.get("status", "unknown")]
        confidence = node.get("confidence", "unknown")
        border_dash = ' stroke-dasharray="5 4"' if confidence in {"reported", "inferred", "unknown"} else ""
        parts.append(f'<rect x="{x - box_w // 2}" y="{y}" width="{box_w}" height="{box_h}" rx="9" fill="#ffffff" stroke="{color}" stroke-width="2"{border_dash}/>')
        parts.append(f'<rect x="{x - box_w // 2}" y="{y}" width="5" height="{box_h}" rx="2" fill="{color}"/>')
        label_lines = line_wrap(node["label"])
        label_y = y + (box_h - len(label_lines) * 18) // 2 + 13
        for i, line in enumerate(label_lines):
            parts.append(f'<text x="{x - box_w // 2 + 15}" y="{label_y + i * 18}" class="node-title">{escape(line)}</text>')
        confidence_label = {"reported": "报告", "inferred": "推测", "unknown": "待确认"}.get(confidence, "")
        impact_distance = node.get("impact_distance")
        impact_label = f"受影响·{impact_distance}" if impact_distance and node.get("status") == "affected" else status_label
        badge = f"{confidence_label}·{impact_label}" if confidence_label and confidence_label != impact_label else impact_label
        parts.append(f'<text x="{x + box_w // 2 - 10}" y="{y + box_h - 10}" text-anchor="end" class="node-status" fill="{color}">{escape(badge)}</text>')
    if not acyclic:
        parts.append(f'<text x="{x0 + 8}" y="{y0 + box_h + 28}" class="warning">依赖包含环；节点按名称排列，检查边方向</text>')
    row_count = max(groups, default=0) + 1
    graph_h = row_count * (box_h + gap_y) - gap_y + 20
    return parts, graph_h


def render(data: dict[str, Any]) -> str:
    title = escape(data["title"])
    scope = escape(data["scope"])
    unknowns = data["unknowns"]
    if data["kind"] == "pr":
        base_ids = {n["id"] for n in data["nodes"] if n["presence"] in {"base", "both"}}
        head_ids = {n["id"] for n in data["nodes"] if n["presence"] in {"head", "both"}}
        changed_ids = set(data["modified"]) | (head_ids - base_ids) | (base_ids - head_ids)
        base_impacted = affected_distance(data["nodes"], data["edges"], changed_ids, "base")
        head_impacted = affected_distance(data["nodes"], data["edges"], changed_ids, "head")
        impacted = dict(base_impacted)
        for node_id, distance in head_impacted.items():
            impacted[node_id] = min(distance, impacted.get(node_id, distance))
        metadata_nodes = []
        for node in data["nodes"]:
            node_id = node["id"]
            status = "deleted" if node_id not in head_ids else "added" if node_id not in base_ids else "modified" if node_id in data["modified"] else "affected" if node_id in impacted else "unchanged"
            phases = [phase for phase, ids in (("base", base_ids), ("head", head_ids)) if node_id in ids]
            metadata_nodes.append({k: v for k, v in node.items() if k != "presence"} | {"status": status, "impact_distance": impacted.get(node_id), "impact_by_phase": {"base": base_impacted.get(node_id), "head": head_impacted.get(node_id)}, "phases": phases})
        metadata_edges = []
        for edge in data["edges"]:
            phases = [phase for phase in ("base", "head") if edge["presence"] in {phase, "both"}]
            change = "removed" if phases == ["base"] else "added" if phases == ["head"] else "unchanged"
            metadata_edges.append({k: v for k, v in edge.items() if k != "presence"} | {"phases": phases, "change": change})
        metadata = {"schema": SCHEMA, "kind": "pr", "title": data["title"], "scope": data["scope"], "base": {k: data["base"][k] for k in ("ref", "sha")}, "head": {k: data["head"][k] for k in ("ref", "sha")}, "nodes": metadata_nodes, "edges": metadata_edges, "unknowns": unknowns}
        head_edges = [edge for edge in data["edges"] if edge["presence"] in {"head", "both"}]
        width = max(700, required_width(metadata_nodes, head_edges))
        graph_y = 88
        graph_parts, graph_h = draw_graph(metadata_nodes, data["edges"], 18, graph_y, width - 36, layout_edges=head_edges)
        legend_y = graph_y + graph_h + 20
        footer_y = legend_y + 68
        footer_svg, footer_h = draw_footer(data["scope"], unknowns, footer_y, width)
        height = footer_y + footer_h + 14
        body = [f'<rect x="0" y="0" width="{width}" height="{height}" rx="12" fill="#f6f8fa"/>']
        body.append(f'<text x="24" y="34" class="chart-title">{title}</text>')
        base_ref = data["base"]["ref"]
        head_ref = data["head"]["ref"]
        base_name = f' · {escape(base_ref)}' if base_ref.casefold() != "base" else ""
        head_name = f' · {escape(head_ref)}' if head_ref.casefold() != "head" else ""
        body.append(f'<text x="24" y="58" class="evidence">Base{base_name} · {escape(data["base"]["sha"])} → Head{head_name} · {escape(data["head"]["sha"])}</text>')
        body.append(f'<text x="24" y="76" class="evidence">模块是主体；节点与依赖边标出前后变化</text>')
        body.extend(graph_parts)
        body.append(legend_pr(width, legend_y))
        body.append(footer_svg)
    else:
        metadata = {"schema": SCHEMA, "kind": data["kind"], "title": data["title"], "scope": data["scope"], "nodes": data["nodes"], "edges": [{k: v for k, v in edge.items() if k != "presence"} for edge in data["edges"]], "unknowns": unknowns}
        width = max(700, required_width(data["nodes"], data["edges"]))
        graph_parts, graph_h = draw_graph(data["nodes"], data["edges"], 18, 76, width - 36)
        legend_y = 76 + graph_h + 20
        footer_y = legend_y + 68
        footer_svg, footer_h = draw_footer(data["scope"], unknowns, footer_y, width)
        height = footer_y + footer_h + 14
        body = [f'<rect x="0" y="0" width="{width}" height="{height}" rx="12" fill="#f6f8fa"/>']
        body.append(f'<text x="24" y="34" class="chart-title">{title}</text>')
        body.extend(graph_parts)
        body.append(legend_issue(width, legend_y))
        body.append(footer_svg)

    description = data.get("description") or f"{data['kind']} 影响图。分析范围：{data['scope']}。箭头方向和线型含义见图例。"
    meta = escape(json.dumps(metadata, ensure_ascii=False, separators=(",", ":")))
    desc = escape(description)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#57606a"/></marker><marker id="arrow-green" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#1a7f37"/></marker><marker id="arrow-red" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#cf222e"/></marker></defs>
<title id="title">{title}</title>
<desc id="desc">{desc}</desc>
<metadata id="lora-change-map-v1">{meta}</metadata>
<style>text{{font-family:Arial,"Noto Sans CJK SC",sans-serif;fill:#24292f}}.chart-title{{font-size:18px;font-weight:700}}.evidence{{font-size:11px;fill:#57606a}}.node-title{{font-size:14px;font-weight:600}}.node-status{{font-size:11px;font-weight:700}}.edge-label{{font-size:11px;paint-order:stroke;stroke:#fff;stroke-width:5px;stroke-linejoin:round}}.muted,.scope{{font-size:12px;fill:#57606a}}.warning{{font-size:11px;fill:#9a6700}}.legend-label{{font-size:11px;fill:#57606a}}</style>
{''.join(body)}
</svg>\n'''


def legend_pr(width: int, y: int) -> str:
    items = [("#1a7f37", "新增模块 / 依赖边"), ("#9a6700", "修改模块"), ("#cf222e", "删除模块 / 依赖边"), ("#0969da", "受影响模块"), ("#57606a", "未改模块 / 前后未变边"), ("#6e7781", "虚线：报告/推测/待确认或已删除")]
    return legend_items(items, width, y, "箭头由 A 指向 B；关系看边标签。实线仅表示已核实关系")


def legend_issue(width: int, y: int) -> str:
    items = [("#0969da", "观察到"), ("#8250df", "期望"), ("#6e7781", "待确认"), ("#9a6700", "推测")]
    return legend_items(items, width, y, "箭头由起点指向终点，关系看边标签；实线已核实，虚线为报告/推测/待确认")


def wrap_footer(text: str, limit: int) -> list[str]:
    words = text.split(" ") if " " in text else list(text)
    lines: list[str] = []
    current = ""
    current_width = 0
    for word in words:
        word_width = sum(2 if ord(char) > 255 else 1 for char in word)
        space = 1 if current and " " in text else 0
        if current and current_width + space + word_width > limit:
            lines.append(current)
            current, current_width, space = "", 0, 0
        if word_width > limit:
            for char in word:
                char_width = 2 if ord(char) > 255 else 1
                if current_width + char_width > limit and current:
                    lines.append(current)
                    current, current_width = "", 0
                current += char
                current_width += char_width
        else:
            current += (" " if space else "") + word
            current_width += space + word_width
    if current:
        lines.append(current)
    return lines or [""]


def draw_footer(scope: str, unknowns: list[str], y: int, width: int) -> tuple[str, int]:
    limit = max(40, (width - 48) // 6)
    parts: list[str] = []
    line_y = y
    entries = [("范围", scope)] + [("待核实", item) for item in unknowns]
    if not unknowns:
        entries.append(("待核实", "无额外未知项"))
    for heading, value in entries:
        prefix = f"{heading}："
        lines = wrap_footer(value, max(12, limit - len(prefix)))
        for index, line in enumerate(lines):
            label = prefix if index == 0 else "　"
            parts.append(f'<text x="24" y="{line_y}" class="scope">{escape(label + line)}</text>')
            line_y += 18
    return "".join(parts), line_y - y


def legend_items(items: list[tuple[str, str]], width: int, y: int, note: str) -> str:
    parts = [f'<line x1="24" y1="{y - 16}" x2="{width - 24}" y2="{y - 16}" stroke="#d0d7de"/>']
    columns = 3
    slot = (width - 48) // columns
    for index, (color, label) in enumerate(items):
        row, column = divmod(index, columns)
        x, item_y = 26 + column * slot, y + row * 20
        parts.append(f'<rect x="{x}" y="{item_y - 7}" width="9" height="9" rx="2" fill="{color}"/>')
        parts.append(f'<text x="{x + 14}" y="{item_y + 1}" class="legend-label">{escape(label)}</text>')
    rows = (len(items) + columns - 1) // columns
    parts.append(f'<text x="24" y="{y + rows * 20 + 4}" class="scope">{escape(note)}</text>')
    return "".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON graph input")
    parser.add_argument("--output", "-o", type=Path, help="SVG output path (default: input name with .svg)")
    args = parser.parse_args()
    try:
        data = validate(json.loads(args.input.read_text(encoding="utf-8")))
        output = args.output or args.input.with_suffix(".svg")
        output.write_text(render(data), encoding="utf-8")
    except (OSError, json.JSONDecodeError, GraphError) as exc:
        print(f"impact svg: {exc}", file=sys.stderr)
        return 2
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
