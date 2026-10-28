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
            part["nodes"] = validate_nodes(part.get("nodes"), phase)
            part["edges"] = validate_edges(part.get("edges"), part["nodes"], phase)
        out["modified"] = out.get("modified", [])
        if not isinstance(out["modified"], list) or not all(isinstance(x, str) for x in out["modified"]):
            raise GraphError("modified must be a list of node ids")
        base_ids = {n["id"] for n in out["base"]["nodes"]}
        head_ids = {n["id"] for n in out["head"]["nodes"]}
        if not set(out["modified"]) <= base_ids & head_ids:
            raise GraphError("modified node ids must exist in both base and head")
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
    seen: set[tuple[str, str, str, str]] = set()
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
        key = (edge["from"], edge["to"], edge["relationship"], edge["presence"])
        if key in seen:
            raise GraphError(f"duplicate edge {key}")
        seen.add(key)
        result.append(edge)
    return result


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def line_wrap(text: str, limit: int = 20) -> list[str]:
    lines: list[str] = []
    current = ""
    width = 0
    parts = text.split(" ") if " " in text else list(text)
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


def phase_nodes(data: dict[str, Any], phase: str) -> list[dict[str, Any]]:
    part = data[phase]
    ids = {n["id"] for n in part["nodes"]}
    base_ids = {n["id"] for n in data["base"]["nodes"]}
    head_ids = {n["id"] for n in data["head"]["nodes"]}
    changed = set(data["modified"]) | (head_ids - base_ids) | (base_ids - head_ids)
    distances = affected_distance(part["nodes"], part["edges"], changed, phase)
    out = []
    for node in part["nodes"]:
        item = dict(node)
        if item["id"] not in ids:
            continue
        if item["id"] not in head_ids:
            item["status"] = "deleted"
        elif item["id"] not in base_ids:
            item["status"] = "added"
        elif item["id"] in data["modified"]:
            item["status"] = "modified"
        elif item["id"] in distances or item.get("status") == "affected":
            item["status"] = "affected"
            item["impact_distance"] = distances.get(item["id"], item.get("impact_distance", 1))
        else:
            item["status"] = "unchanged"
        out.append(item)
    return out


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


def required_width(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], minimum: int = 560) -> int:
    rank, _ = ranks(nodes, edges)
    counts: dict[int, int] = defaultdict(int)
    for node in nodes:
        counts[rank[node["id"]]] += 1
    widest = max(counts.values(), default=1) * 180 + max(0, max(counts.values(), default=1) - 1) * 20 + 36
    return max(minimum, widest)


def draw_graph(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], x0: int, y0: int, width: int, edge_changes: dict[tuple[str, str, str], str] | None = None) -> tuple[list[str], int]:
    if not nodes:
        return [f'<text x="{x0 + 24}" y="{y0 + 35}" class="muted">无模块节点</text>'], 90
    rank, acyclic = ranks(nodes, edges)
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
        if rank[source] < rank[target]:
            start_y, end_y = sy + box_h // 2, ty - box_h // 2
            mid_y = (start_y + end_y) / 2
            d = f"M {sx} {start_y} C {sx} {mid_y}, {tx} {mid_y}, {tx} {end_y}"
        else:
            start_x, end_x = sx + box_w // 2, tx - box_w // 2
            bend = max(start_x, end_x) + 28
            d = f"M {start_x} {sy} C {bend} {sy}, {bend} {ty}, {end_x} {ty}"
        confidence = edge.get("confidence", "unknown")
        change = (edge_changes or {}).get((source, target, edge.get("relationship", "")), "unchanged")
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
        impact_label = "间接受影响" if node.get("impact_distance", 1) > 1 and node.get("status") == "affected" else status_label
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
        base_nodes = phase_nodes(data, "base")
        head_nodes = phase_nodes(data, "head")
        base_ids = {n["id"] for n in data["base"]["nodes"]}
        head_ids = {n["id"] for n in data["head"]["nodes"]}
        base_edge_keys = {(e["from"], e["to"], e.get("relationship", "")) for e in data["base"]["edges"]}
        head_edge_keys = {(e["from"], e["to"], e.get("relationship", "")) for e in data["head"]["edges"]}
        changed_ids = set(data["modified"]) | (head_ids - base_ids) | (base_ids - head_ids)
        base_impacted = affected_distance(data["base"]["nodes"], data["base"]["edges"], changed_ids, "base")
        head_impacted = affected_distance(data["head"]["nodes"], data["head"]["edges"], changed_ids, "head")
        impacted = dict(base_impacted)
        for node_id, distance in head_impacted.items():
            impacted[node_id] = min(distance, impacted.get(node_id, distance))
        base_changes = {key: "removed" for key in base_edge_keys - head_edge_keys}
        head_changes = {key: "added" for key in head_edge_keys - base_edge_keys}
        all_nodes = {n["id"]: {k: v for k, v in n.items() if k != "presence"} for n in data["base"]["nodes"]}
        all_nodes.update({n["id"]: {k: v for k, v in n.items() if k != "presence"} for n in data["head"]["nodes"]})
        metadata_nodes = []
        for node_id, node in all_nodes.items():
            status = "deleted" if node_id not in head_ids else "added" if node_id not in base_ids else "modified" if node_id in data["modified"] else "affected" if node_id in impacted else "unchanged"
            metadata_nodes.append({**node, "status": status, "impact_distance": impacted.get(node_id), "impact_by_phase": {"base": base_impacted.get(node_id), "head": head_impacted.get(node_id)}, "phases": [p for p, ids in (("base", base_ids), ("head", head_ids)) if node_id in ids]})
        metadata_edges = []
        for phase, edges in (("base", data["base"]["edges"]), ("head", data["head"]["edges"])):
            for edge in edges:
                key = (edge["from"], edge["to"], edge.get("relationship", ""))
                change = "removed" if phase == "base" and key not in head_edge_keys else "added" if phase == "head" and key not in base_edge_keys else "unchanged"
                metadata_edges.append({k: v for k, v in edge.items() if k != "presence"} | {"phase": phase, "change": change})
        metadata = {"schema": SCHEMA, "kind": "pr", "title": data["title"], "scope": data["scope"], "base": {k: data["base"][k] for k in ("ref", "sha")}, "head": {k: data["head"][k] for k in ("ref", "sha")}, "nodes": metadata_nodes, "edges": metadata_edges, "unknowns": unknowns}
        panel_w = max(700, required_width(base_nodes, data["base"]["edges"]), required_width(head_nodes, data["head"]["edges"]))
        width = panel_w
        base_top = 56
        graph_y = base_top + 50
        base_parts, base_h = draw_graph(base_nodes, data["base"]["edges"], 18, graph_y, panel_w - 36, base_changes)
        head_top = base_top + base_h + 68 + 14
        head_graph_y = head_top + 50
        head_parts, head_h = draw_graph(head_nodes, data["head"]["edges"], 18, head_graph_y, panel_w - 36, head_changes)
        panel_h = max(base_h, head_h) + 68
        legend_y = head_top + panel_h + 30
        footer_y = legend_y + 68
        footer_svg, footer_h = draw_footer(data["scope"], unknowns, footer_y, width)
        height = footer_y + footer_h + 14
        body = [f'<rect x="0" y="0" width="{width}" height="{height}" rx="12" fill="#f6f8fa"/>']
        body.append(f'<text x="24" y="34" class="chart-title">{title}</text>')
        body.append(f'<rect x="12" y="{base_top}" width="{panel_w - 24}" height="{base_h + 68}" rx="10" fill="#ffffff" stroke="#d0d7de"/>')
        body.append(f'<rect x="12" y="{head_top}" width="{panel_w - 24}" height="{panel_h}" rx="10" fill="#ffffff" stroke="#d0d7de"/>')
        body.append(f'<text x="28" y="{base_top + 27}" class="panel-title">Base · {escape(data["base"].get("ref", "Base"))} · {escape(data["base"]["sha"])}</text>')
        body.append(f'<text x="28" y="{head_top + 27}" class="panel-title">Head · {escape(data["head"].get("ref", "Head"))} · {escape(data["head"]["sha"])}</text>')
        body.extend(base_parts)
        body.extend(head_parts)
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
<style>text{{font-family:Arial,"Noto Sans CJK SC",sans-serif;fill:#24292f}}.chart-title{{font-size:18px;font-weight:700}}.panel-title{{font-size:15px;font-weight:700}}.node-title{{font-size:14px;font-weight:600}}.node-status{{font-size:11px;font-weight:700}}.edge-label{{font-size:11px;paint-order:stroke;stroke:#fff;stroke-width:5px;stroke-linejoin:round}}.muted,.scope{{font-size:12px;fill:#57606a}}.warning{{font-size:11px;fill:#9a6700}}.legend-label{{font-size:11px;fill:#57606a}}</style>
{''.join(body)}
</svg>\n'''


def legend_pr(width: int, y: int) -> str:
    items = [("#1a7f37", "新增节点 / 依赖边"), ("#9a6700", "修改节点"), ("#cf222e", "删除节点 / 依赖边"), ("#0969da", "受影响消费者"), ("#57606a", "未改"), ("#6e7781", "虚线：报告/推测/待确认或已删除")]
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
