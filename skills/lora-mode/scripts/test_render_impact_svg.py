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
            data = self.render_fixture(FIXTURES / "e14-pr" / "map.json", Path(directory) / "map.svg")
        self.assertEqual((data["base"]["sha"], data["head"]["sha"]), ("1111111", "2222222"))
        statuses = {node["id"]: node["status"] for node in data["nodes"]}
        self.assertEqual(statuses["api-auth"], "added")
        self.assertEqual(statuses["credential-store"], "added")
        self.assertEqual(statuses["session"], "modified")
        self.assertEqual(statuses["token-helper"], "deleted")
        self.assertEqual(statuses["web"], "affected")
        changes = {(edge["phase"], edge["from"], edge["to"]): edge["change"] for edge in data["edges"]}
        self.assertEqual(changes[("base", "session", "token-helper")], "removed")
        self.assertEqual(changes[("head", "session", "credential-store")], "added")

    def test_issue_svg_keeps_reported_and_unknown_relationships_separate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            data = self.render_fixture(FIXTURES / "e16-issue" / "map.json", Path(directory) / "map.svg")
        statuses = {node["id"]: node["status"] for node in data["nodes"]}
        self.assertEqual(statuses["unauthorized"], "observed")
        self.assertEqual(statuses["expected"], "expected")
        self.assertEqual(statuses["auth"], "unknown")
        self.assertTrue(all(edge["confidence"] == "unknown" for edge in data["edges"][-2:]))
        self.assertEqual(len(data["unknowns"]), 4)

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


if __name__ == "__main__":
    unittest.main()
