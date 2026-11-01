import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


FIXTURE = Path(__file__).parent
BASE_STATE = json.loads((FIXTURE / "state.json").read_text())


class MockGhTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        shutil.copytree(FIXTURE / "bin", self.root / "bin")
        self.state_path = self.root / "state.json"
        self.write_state(BASE_STATE)
        self.env = os.environ.copy()
        self.env["PATH"] = f"{self.root / 'bin'}{os.pathsep}{self.env.get('PATH', '')}"

    def tearDown(self):
        self.temp.cleanup()

    def read_state(self):
        return json.loads(self.state_path.read_text())

    def write_state(self, state):
        self.state_path.write_text(json.dumps(state, indent=2) + "\n")

    def run_gh(self, *args):
        return subprocess.run(
            [str(self.root / "bin" / "gh"), *args],
            cwd=self.root,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_pr_view_is_read_only_even_when_auto_merge_is_eligible(self):
        state = self.read_state()
        state["auto_merge_enabled"] = True
        state["auto_merge_method"] = "squash"
        self.write_state(state)

        result = self.run_gh("pr", "view", "5", "--json", "state,autoMergeRequest,headRefOid")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read_state()["merged"], False)
        self.assertTrue(self.read_state()["auto_merge_enabled"])

    def test_rejected_admin_merge_never_mutates_pr_state(self):
        state = self.read_state()
        state["auto_merge_enabled"] = True
        state["auto_merge_method"] = "squash"
        self.write_state(state)

        result = self.run_gh("pr", "merge", "5", "--squash", "--admin")

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.read_state()["merged"])
        self.assertTrue(self.read_state()["auto_merge_enabled"])

    def test_stale_approval_does_not_satisfy_required_review(self):
        state = self.read_state()
        state["repository_rules"]["branch_protection"] = True
        state["repository_rules"]["required_review_count"] = 1
        state["reviewDecision"] = "APPROVED"
        state["reviews"] = [{
            "state": "APPROVED",
            "commit_id": "older-head",
            "user": {"login": "reviewer-1"},
        }]
        self.write_state(state)

        result = self.run_gh("pr", "merge", "5", "--squash")

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.read_state()["merged"])

    def test_changes_requested_blocks_merge_despite_an_approval(self):
        state = self.read_state()
        state["repository_rules"]["branch_protection"] = True
        state["repository_rules"]["required_review_count"] = 1
        state["reviewDecision"] = "CHANGES_REQUESTED"
        state["reviews"] = [
            {"state": "APPROVED", "commit_id": state["head"]["sha"], "user": {"login": "reviewer-1"}},
            {"state": "CHANGES_REQUESTED", "commit_id": state["head"]["sha"], "user": {"login": "reviewer-2"}},
        ]
        self.write_state(state)

        result = self.run_gh("pr", "merge", "5", "--squash")

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.read_state()["merged"])

    def test_high_risk_review_must_be_completed_and_clear(self):
        for risk_review, findings in [
            ({"status": "pending", "blocking_findings": []}, []),
            ({"status": "completed", "blocking_findings": ["unresolved issue"]}, []),
            ({"status": "completed", "blocking_findings": []}, ["blocking issue"]),
        ]:
            with self.subTest(risk_review=risk_review, findings=findings):
                state = self.read_state()
                state["risk_review"] = risk_review
                state["blocking_findings"] = findings
                self.write_state(state)

                result = self.run_gh("pr", "merge", "5", "--squash")

                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.read_state()["merged"])

    def test_draft_pr_cannot_merge(self):
        state = self.read_state()
        state["draft"] = True
        self.write_state(state)

        result = self.run_gh("pr", "merge", "5", "--squash")

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.read_state()["merged"])

    def test_full_stop_can_disable_auto_merge_and_dequeue(self):
        state = self.read_state()
        state["auto_merge_enabled"] = True
        state["auto_merge_method"] = "squash"
        state["in_merge_queue"] = True
        self.write_state(state)

        disabled_while_queued = self.run_gh("pr", "merge", "5", "--disable-auto")
        self.assertEqual(disabled_while_queued.returncode, 0, disabled_while_queued.stderr)
        self.assertTrue(self.read_state()["auto_merge_enabled"])
        self.assertTrue(self.read_state()["in_merge_queue"])

        dequeued = self.run_gh(
            "api", "graphql", "-f", "query=mutation { dequeuePullRequest(input: {id: $id}) { clientMutationId } }",
            "-F", "id=PR_fixture_5",
        )
        self.assertEqual(dequeued.returncode, 0, dequeued.stderr)
        self.assertFalse(self.read_state()["in_merge_queue"])

        disabled = self.run_gh("pr", "merge", "5", "--disable-auto")
        self.assertEqual(disabled.returncode, 0, disabled.stderr)
        self.assertFalse(self.read_state()["auto_merge_enabled"])
        self.assertFalse(self.read_state()["merged"])

    def test_dequeue_accepts_inline_graphql_node_id(self):
        state = self.read_state()
        state["in_merge_queue"] = True
        self.write_state(state)

        result = self.run_gh(
            "api", "graphql", "-f",
            'query=mutation { dequeuePullRequest(input: {id: "PR_fixture_5"}) { clientMutationId } }',
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.read_state()["in_merge_queue"])
        self.assertFalse(self.read_state()["merged"])

    def test_merge_queue_requires_ready_gate_then_only_queues(self):
        state = self.read_state()
        state["repository_rules"]["merge_queue"] = True
        state["repository_rules"]["branch_protection"] = True
        state["repository_rules"]["required_review_count"] = 1
        self.write_state(state)

        blocked = self.run_gh("pr", "merge", "5", "--squash")
        self.assertNotEqual(blocked.returncode, 0)
        self.assertFalse(self.read_state()["in_merge_queue"])

        state = self.read_state()
        state["reviewDecision"] = "APPROVED"
        state["reviews"] = [{
            "state": "APPROVED",
            "commit_id": state["head"]["sha"],
            "user": {"login": "reviewer-1"},
        }]
        self.write_state(state)
        queued = self.run_gh("pr", "merge", "5", "--squash")

        self.assertEqual(queued.returncode, 0, queued.stderr)
        self.assertTrue(self.read_state()["in_merge_queue"])
        self.assertFalse(self.read_state()["merged"])

    def test_cli_json_shapes_and_unknown_fields(self):
        checks = self.run_gh("pr", "checks", "5", "--json", "bucket,name,state")
        self.assertEqual(checks.returncode, 0, checks.stderr)
        self.assertIsInstance(json.loads(checks.stdout), list)
        self.assertEqual(json.loads(checks.stdout)[0]["bucket"], "pass")

        invalid = self.run_gh("pr", "view", "5", "--json", "risk_review")
        self.assertNotEqual(invalid.returncode, 0)

        unsupported_jq = self.run_gh("pr", "checks", "5", "--json", "name,state", "--jq", ".[] | .name")
        self.assertNotEqual(unsupported_jq.returncode, 0)

    def test_failed_and_pending_checks_return_nonzero(self):
        state = self.read_state()
        state["required_check_runs"] = [{
            "name": "CI",
            "status": "completed",
            "conclusion": "failure",
        }]
        self.write_state(state)
        failed = self.run_gh("pr", "checks", "5", "--json", "bucket,name,state")
        self.assertNotEqual(failed.returncode, 0)

        state["required_check_runs"] = [{"name": "CI", "status": "queued", "conclusion": None}]
        self.write_state(state)
        pending = self.run_gh("pr", "checks", "5", "--json", "bucket,name,state")
        self.assertEqual(pending.returncode, 8)


if __name__ == "__main__":
    unittest.main()
