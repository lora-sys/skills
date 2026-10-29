import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPT = Path(__file__).with_name("render-impact-svg.py")
FIXTURES = Path(__file__).parents[1] / "evals" / "fixtures"
SVG_NS = {"svg": "http://www.w3.org/2000/svg"}


class RenderImpactSvgTests(unittest.TestCase):
    def render_fixture(self, fixture: Path, output: Path) -> dict:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(fixture), "--output", str(output)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        root = ET.parse(output).getroot()
        self.assertLessEqual(float(root.attrib["width"]), 728)
        self.assertIsNotNone(root.find("svg:title", SVG_NS))
        self.assertIsNotNone(root.find("svg:desc", SVG_NS))
        self.assertEqual(root.findall(".//svg:script", SVG_NS), [])
        self.assertTrue(
            all(
                not value.startswith(("http:", "https:", "file:"))
                for element in root.iter()
                for key, value in element.attrib.items()
                if key.endswith("href")
            )
        )
        metadata = root.find("svg:metadata", SVG_NS)
        self.assertIsNotNone(metadata)
        if "e16-issue" in fixture.parts:
            visible_text = " ".join(element.text or "" for element in root.findall(".//svg:text", SVG_NS))
            for fact in ("several times a day", "Token type", "401 response source", "stable reproduction"):
                self.assertIn(fact, visible_text)
        return json.loads(metadata.text)

    def test_pr_svg_records_module_and_edge_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "map.svg"
            data = self.render_fixture(FIXTURES / "e14-pr" / "map.json", output)
            root = ET.parse(output).getroot()
        self.assertEqual((data["base"]["sha"], data["head"]["sha"]), ("1111111", "2222222"))
        headings = " ".join(element.text or "" for element in root.findall(".//svg:text", SVG_NS))
        self.assertIn("Base · 1111111 → Head · 2222222", headings)
        self.assertIn("模块是主体；节点与依赖边标出前后变化", headings)
        self.assertEqual(headings.count("Base · 1111111 → Head · 2222222"), 1)
        self.assertNotIn("Base panel", headings)
        for label in ("新增", "修改", "删除", "受影响·1", "packages/", "token-helper"):
            self.assertIn(label, headings)
        self.assertEqual(len(data["nodes"]), 5)
        self.assertIn("reported in the prompt", root.find("svg:desc", SVG_NS).text)
        statuses = {node["id"]: node["status"] for node in data["nodes"]}
        self.assertEqual(statuses["api-auth"], "added")
        self.assertEqual(statuses["credential-store"], "added")
        self.assertEqual(statuses["session"], "modified")
        self.assertEqual(statuses["token-helper"], "deleted")
        self.assertEqual(statuses["web"], "affected")
        nodes = {node["id"]: node for node in data["nodes"]}
        self.assertEqual(nodes["session"]["phases"], ["base", "head"])
        self.assertNotIn("presence", nodes["session"])
        self.assertTrue(all("presence" not in edge for edge in data["edges"]))
        self.assertTrue(all(edge["confidence"] == "reported" for edge in data["edges"]))
        changes = {(edge["from"], edge["to"]): (edge["phases"], edge["change"]) for edge in data["edges"]}
        self.assertEqual(changes[("session", "token-helper")], (["base"], "removed"))
        self.assertEqual(changes[("session", "credential-store")], (["head"], "added"))

    def test_pr_layout_uses_head_topology_without_false_cross_version_cycle(self) -> None:
        data = json.loads((FIXTURES / "e14-pr" / "map.json").read_text(encoding="utf-8"))
        data["edges"][0] = {
            "from": "session",
            "to": "web",
            "relationship": "depends on",
            "presence": "base",
            "confidence": "reported",
            "evidence": "reversed in base summary",
        }
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "map.json"
            output_path = Path(directory) / "map.svg"
            input_path.write_text(json.dumps(data), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), "--output", str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            root = ET.parse(output_path).getroot()
        warnings = root.findall('.//svg:text[@class="warning"]', SVG_NS)
        self.assertEqual(warnings, [])

    def test_pr_rejects_edges_and_modified_nodes_missing_from_a_phase(self) -> None:
        cases = (
            (
                "head edge references a node absent from that phase",
                lambda data: data["edges"].append({
                    "from": "api-auth",
                    "to": "token-helper",
                    "relationship": "depends on",
                    "presence": "head",
                }),
            ),
            ("modified node ids must exist in both base and head", lambda data: data.update(modified=["token-helper"])),
        )
        original = json.loads((FIXTURES / "e14-pr" / "map.json").read_text(encoding="utf-8"))
        for expected_error, mutate in cases:
            with self.subTest(expected_error=expected_error), tempfile.TemporaryDirectory() as directory:
                data = json.loads(json.dumps(original))
                mutate(data)
                input_path = Path(directory) / "bad.json"
                output_path = Path(directory) / "bad.svg"
                input_path.write_text(json.dumps(data), encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), str(input_path), "--output", str(output_path)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn(expected_error, result.stderr)
                self.assertFalse(output_path.exists())

    def test_pr_evidence_caption_includes_only_explicit_branch_refs(self) -> None:
        data = json.loads((FIXTURES / "e14-pr" / "map.json").read_text(encoding="utf-8"))
        data["base"]["ref"] = "main"
        data["head"]["ref"] = "feature/auth-refresh"
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "map.json"
            output_path = Path(directory) / "map.svg"
            input_path.write_text(json.dumps(data), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), "--output", str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            root = ET.parse(output_path).getroot()
        headings = " ".join(element.text or "" for element in root.findall(".//svg:text", SVG_NS))
        self.assertIn("Base · main · 1111111 → Head · feature/auth-refresh · 2222222", headings)

    def test_issue_svg_keeps_reported_and_unknown_relationships_separate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            data = self.render_fixture(FIXTURES / "e16-issue" / "map.json", Path(directory) / "map.svg")
        statuses = {node["id"]: node["status"] for node in data["nodes"]}
        self.assertEqual(statuses["unauthorized"], "observed")
        self.assertEqual(statuses["expected"], "expected")
        self.assertEqual(statuses["auth"], "unknown")
        self.assertTrue(all(edge["confidence"] == "unknown" for edge in data["edges"][-2:]))
        self.assertTrue(all("presence" not in edge for edge in data["edges"]))
        self.assertEqual(len(data["unknowns"]), 4)

    def test_legends_explain_dashes_and_arrow_direction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            pr_path = Path(directory) / "pr.svg"
            issue_path = Path(directory) / "issue.svg"
            self.render_fixture(FIXTURES / "e14-pr" / "map.json", pr_path)
            self.render_fixture(FIXTURES / "e16-issue" / "map.json", issue_path)
            pr_root = ET.parse(pr_path).getroot()
            issue_root = ET.parse(issue_path).getroot()
        pr_text = " ".join(element.text or "" for element in pr_root.findall(".//svg:text", SVG_NS))
        issue_text = " ".join(element.text or "" for element in issue_root.findall(".//svg:text", SVG_NS))
        self.assertIn("虚线：报告/推测/待确认或已删除", pr_text)
        self.assertIn("箭头由 A 指向 B；关系看边标签", pr_text)
        self.assertIn("箭头由起点指向终点，关系看边标签", issue_text)

    def test_long_edge_label_keeps_confidence_and_unknown_node_badge(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "map.json"
            output_path = Path(directory) / "map.svg"
            input_path.write_text(
                json.dumps(
                    {
                        "kind": "issue",
                        "title": "long relationship",
                        "scope": "edge confidence remains visible",
                        "nodes": [
                            {"id": "a", "label": "A", "status": "observed", "confidence": "reported", "evidence": "issue report"},
                            {"id": "b", "label": "B", "status": "unknown", "confidence": "reported", "evidence": "issue report"},
                        ],
                        "edges": [
                            {
                                "from": "a",
                                "to": "b",
                                "relationship": "happens during concurrent refresh",
                                "confidence": "reported",
                                "evidence": "issue report",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), "--output", str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            root = ET.parse(output_path).getroot()
        visible_text = " ".join(element.text or "" for element in root.findall(".//svg:text", SVG_NS))
        self.assertIn("… · 报告", visible_text)
        self.assertIn("报告·待确认", visible_text)

    def test_issue_status_rejects_pr_only_labels(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "bad.json"
            output_path = Path(directory) / "bad.svg"
            input_path.write_text(
                json.dumps(
                    {
                        "kind": "issue",
                        "title": "bad issue status",
                        "scope": "test",
                        "nodes": [{"id": "a", "label": "A", "status": "modified"}],
                        "edges": [],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), "--output", str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("status is not supported", result.stderr)
        self.assertFalse(output_path.exists())

    def test_invalid_edge_reference_fails_before_writing_svg(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "bad.json"
            output_path = Path(directory) / "bad.svg"
            input_path.write_text(
                json.dumps(
                    {
                        "kind": "issue",
                        "title": "bad map",
                        "scope": "test",
                        "nodes": [{"id": "known", "label": "Known"}],
                        "edges": [{"from": "known", "to": "missing"}],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), "--output", str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("references missing node", result.stderr)
        self.assertFalse(output_path.exists())

    def test_missing_edge_confidence_defaults_to_unknown_and_draws_dashed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "map.json"
            output_path = Path(directory) / "map.svg"
            input_path.write_text(
                json.dumps(
                    {
                        "kind": "issue",
                        "title": "unverified relation",
                        "scope": "source not inspected",
                        "nodes": [
                            {"id": "a", "label": "A"},
                            {"id": "b", "label": "B"},
                            {"id": "c", "label": "C"},
                        ],
                        "edges": [
                            {"from": "a", "to": "b", "relationship": "depends on"},
                            {
                                "from": "b",
                                "to": "c",
                                "relationship": "calls",
                                "confidence": "reported",
                                "evidence": "issue report",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), "--output", str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            root = ET.parse(output_path).getroot()
        data = json.loads(root.find("svg:metadata", SVG_NS).text)
        self.assertEqual([edge["confidence"] for edge in data["edges"]], ["unknown", "reported"])
        visible_text = " ".join(element.text or "" for element in root.findall(".//svg:text", SVG_NS))
        self.assertIn("待确认", visible_text)
        self.assertIn("报告", visible_text)
        self.assertTrue(
            all(
                path.get("stroke-dasharray") == "6 5"
                for path in root.findall(".//svg:path[@marker-end]", SVG_NS)
            )
        )

    def test_non_unknown_edge_requires_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "bad.json"
            output_path = Path(directory) / "bad.svg"
            input_path.write_text(
                json.dumps(
                    {
                        "kind": "issue",
                        "title": "unsupported claim",
                        "scope": "test",
                        "nodes": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
                        "edges": [
                            {"from": "a", "to": "b", "relationship": "depends on", "confidence": "confirmed"}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), "--output", str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("evidence is required", result.stderr)
        self.assertFalse(output_path.exists())

    def test_edge_requires_relationship_label(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "bad.json"
            output_path = Path(directory) / "bad.svg"
            input_path.write_text(
                json.dumps(
                    {
                        "kind": "issue",
                        "title": "unlabeled edge",
                        "scope": "test",
                        "nodes": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
                        "edges": [{"from": "a", "to": "b"}],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), "--output", str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("relationship must be a non-empty string", result.stderr)
        self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()
