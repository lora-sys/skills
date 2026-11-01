import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "e38-pr-modes"
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

    def test_cli_reports_merged_while_rest_reports_closed(self):
        merged = self.run_gh("pr", "merge", "5", "--squash")
        self.assertEqual(merged.returncode, 0, merged.stderr)

        cli = self.run_gh("pr", "view", "5", "--json", "state")
        rest = self.run_gh("api", "repos/lora-sys/skills/pulls/5")

        self.assertEqual(json.loads(cli.stdout)["state"], "MERGED")
        rest_data = json.loads(rest.stdout)
        self.assertEqual(rest_data["state"], "closed")
        self.assertTrue(rest_data["merged"])

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

    def test_stale_approval_is_rejected_when_repo_dismisses_stale_reviews(self):
        state = self.read_state()
        state["repository_rules"]["branch_protection"] = True
        state["repository_rules"]["required_review_count"] = 1
        state["repository_rules"]["dismiss_stale_reviews"] = True
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

    def test_stale_approval_is_rejected_even_when_repo_does_not_dismiss_it(self):
        state = self.read_state()
        state["repository_rules"]["branch_protection"] = True
        state["repository_rules"]["required_review_count"] = 1
        state["repository_rules"]["dismiss_stale_reviews"] = False
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

    def test_missing_required_status_context_is_pending_and_blocks_merge(self):
        state = self.read_state()
        state["repository_rules"]["branch_protection"] = True
        state["repository_rules"]["required_status_checks"] = ["CI"]
        state["required_check_runs"] = []
        self.write_state(state)

        checks = self.run_gh("pr", "checks", "5", "--json", "bucket,name,state")
        merge = self.run_gh("pr", "merge", "5", "--squash")

        self.assertEqual(checks.returncode, 8)
        self.assertEqual(json.loads(checks.stdout)[0]["name"], "CI")
        self.assertEqual(json.loads(checks.stdout)[0]["bucket"], "pending")
        self.assertNotEqual(merge.returncode, 0)
        self.assertFalse(self.read_state()["merged"])

    def test_required_skipped_or_neutral_status_check_allows_merge(self):
        for conclusion in ("skipped", "neutral"):
            with self.subTest(conclusion=conclusion):
                state = json.loads(json.dumps(BASE_STATE))
                state["repository_rules"]["branch_protection"] = True
                state["repository_rules"]["required_status_checks"] = ["CI"]
                state["required_check_runs"] = [{
                    "name": "CI",
                    "status": "completed",
                    "conclusion": conclusion,
                }]
                self.write_state(state)

                checks = self.run_gh("pr", "checks", "5", "--json", "bucket,name,state")
                merge = self.run_gh("pr", "merge", "5", "--squash")

                self.assertEqual(checks.returncode, 0, checks.stderr)
                self.assertEqual(merge.returncode, 0, merge.stderr)
                self.assertTrue(self.read_state()["merged"])

    def test_status_check_rollup_uses_gh_pr_view_fields(self):
        result = self.run_gh("pr", "view", "5", "--json", "statusCheckRollup")

        self.assertEqual(result.returncode, 0, result.stderr)
        check = json.loads(result.stdout)["statusCheckRollup"][0]
        self.assertEqual(check["__typename"], "CheckRun")
        self.assertEqual(check["status"], "COMPLETED")
        self.assertEqual(check["conclusion"], "SUCCESS")
        self.assertNotIn("bucket", check)

    def test_branch_protection_endpoint_uses_pull_request_base(self):
        state = self.read_state()
        state["base"]["ref"] = "release"
        state["repository_rules"]["branch_protection"] = True
        state["repository_rules"]["required_status_checks"] = ["CI"]
        self.write_state(state)

        result = self.run_gh("api", "repos/lora-sys/skills/branches/release/protection")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNotNone(json.loads(result.stdout)["required_status_checks"])

    def test_comment_review_does_not_revoke_an_approval(self):
        state = self.read_state()
        state["repository_rules"]["branch_protection"] = True
        state["repository_rules"]["required_review_count"] = 1
        state["reviewDecision"] = "APPROVED"
        state["reviews"] = [
            {"state": "APPROVED", "commit_id": state["head"]["sha"], "user": {"login": "reviewer-1"}},
            {"state": "COMMENTED", "commit_id": state["head"]["sha"], "user": {"login": "reviewer-1"}},
        ]
        self.write_state(state)

        result = self.run_gh("pr", "merge", "5", "--squash")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.read_state()["merged"])

    def test_null_review_user_does_not_crash_cli_or_gate(self):
        state = self.read_state()
        state["repository_rules"]["branch_protection"] = True
        state["repository_rules"]["required_review_count"] = 1
        state["reviewDecision"] = "APPROVED"
        state["reviews"] = [{"state": "COMMENTED", "user": None}]
        self.write_state(state)

        view = self.run_gh("pr", "view", "5", "--json", "reviews")
        merge = self.run_gh("pr", "merge", "5", "--squash")

        self.assertEqual(view.returncode, 0, view.stderr)
        self.assertIsNone(json.loads(view.stdout)["reviews"][0]["author"])
        self.assertNotEqual(merge.returncode, 0)
        self.assertNotIn("AttributeError", merge.stderr)
        self.assertFalse(self.read_state()["merged"])

    def test_full_send_can_merge_with_current_head_required_approval(self):
        state = self.read_state()
        state["repository_rules"]["branch_protection"] = True
        state["repository_rules"]["required_review_count"] = 1
        state["reviewDecision"] = "APPROVED"
        state["reviews"] = [{
            "state": "APPROVED",
            "commit_id": state["head"]["sha"],
            "user": {"login": "reviewer-1"},
        }]
        self.write_state(state)

        result = self.run_gh("pr", "merge", "5", "--squash")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.read_state()["merged"])

    def test_auto_merge_disables_when_current_head_approval_is_missing(self):
        state = self.read_state()
        state["repository_rules"]["branch_protection"] = True
        state["repository_rules"]["required_review_count"] = 1
        state["mergeable_state"] = "blocked"
        state["reviewDecision"] = "APPROVED"
        state["reviews"] = [{
            "state": "APPROVED",
            "commit_id": "older-head",
            "user": {"login": "reviewer-1"},
        }]
        state["auto_merge_enabled"] = True
        state["auto_merge_method"] = "squash"
        self.write_state(state)

        before = self.run_gh("pr", "view", "5", "--json", "headRefOid,reviews,autoMergeRequest")
        disabled = self.run_gh("pr", "merge", "5", "--disable-auto")
        after = self.run_gh("pr", "view", "5", "--json", "state,autoMergeRequest")

        self.assertEqual(before.returncode, 0, before.stderr)
        self.assertEqual(disabled.returncode, 0, disabled.stderr)
        self.assertEqual(json.loads(before.stdout)["reviews"][0]["commit"]["oid"], "older-head")
        self.assertIsNotNone(json.loads(before.stdout)["autoMergeRequest"])
        self.assertEqual(json.loads(after.stdout)["state"], "OPEN")
        self.assertIsNone(json.loads(after.stdout)["autoMergeRequest"])
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

    def test_merge_queue_state_is_visible_by_node_query_and_direct_merge_is_rejected(self):
        state = self.read_state()
        state["in_merge_queue"] = True
        state["auto_merge_enabled"] = True
        state["auto_merge_method"] = "squash"
        self.write_state(state)

        queued_view = self.run_gh(
            "api", "graphql",
            "--raw-field", 'query=query($id: ID!) { node(id: $id) { ... on PullRequest { isInMergeQueue } } }',
            "--field", f'id={state["node_id"]}',
            "-q", ".data.node.isInMergeQueue",
        )
        direct_merge = self.run_gh("pr", "merge", "5", "--squash")

        self.assertEqual(queued_view.returncode, 0, queued_view.stderr)
        self.assertEqual(queued_view.stdout.strip(), "true")
        self.assertEqual(direct_merge.returncode, 2)
        self.assertTrue(self.read_state()["in_merge_queue"])
        self.assertTrue(self.read_state()["auto_merge_enabled"])
        self.assertFalse(self.read_state()["merged"])

    def test_branch_protection_endpoint_reports_required_review_and_checks(self):
        state = self.read_state()
        state["repository_rules"]["branch_protection"] = True
        state["repository_rules"]["required_review_count"] = 1
        state["repository_rules"]["dismiss_stale_reviews"] = True
        state["repository_rules"]["required_status_checks"] = ["CI"]
        self.write_state(state)

        result = self.run_gh("api", "repos/lora-sys/skills/branches/main/protection")

        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["required_status_checks"]["contexts"], ["CI"])
        self.assertEqual(data["required_pull_request_reviews"]["required_approving_review_count"], 1)
        self.assertTrue(data["required_pull_request_reviews"]["dismiss_stale_reviews"])

    def test_cli_json_shapes_and_unknown_fields(self):
        checks = self.run_gh("pr", "checks", "5", "--json", "bucket,name,state")
        self.assertEqual(checks.returncode, 0, checks.stderr)
        self.assertIsInstance(json.loads(checks.stdout), list)
        self.assertEqual(json.loads(checks.stdout)[0]["bucket"], "pass")

        invalid = self.run_gh("pr", "view", "5", "--json", "risk_review")
        self.assertNotEqual(invalid.returncode, 0)

        names = self.run_gh("pr", "checks", "5", "--json", "name,state", "--jq", ".[] | .name")
        self.assertEqual(names.returncode, 0, names.stderr)
        self.assertEqual(names.stdout.strip(), "CI")

        state = self.read_state()
        state["reviews"] = [{
            "state": "APPROVED",
            "commit_id": state["head"]["sha"],
            "user": {"login": "reviewer-1"},
        }]
        self.write_state(state)
        reviews = self.run_gh("pr", "view", "5", "--json", "reviews", "--jq", ".reviews[]")
        self.assertEqual(reviews.returncode, 0, reviews.stderr)
        review_rows = [json.loads(line) for line in reviews.stdout.splitlines() if line]
        self.assertEqual(len(review_rows), 1)
        self.assertEqual(review_rows[0]["commit"]["oid"], state["head"]["sha"])

        commits = self.run_gh("pr", "view", "5", "--json", "reviews", "-q", ".reviews[] | .commit.oid")
        self.assertEqual(commits.returncode, 0, commits.stderr)
        self.assertEqual(commits.stdout.strip(), state["head"]["sha"])

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
