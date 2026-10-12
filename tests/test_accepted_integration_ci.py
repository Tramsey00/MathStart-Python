"""Reject approval transfer and stale/altered combined-input CI provenance."""
import copy
import json
import unittest
from unittest.mock import patch

from scripts import accepted_integration_ci as ci
from scripts.frontend_ci import validate_report
from tests.test_frontend_ci import report

PINS = json.loads(ci.CONFIG.read_text())
HISTORICAL = json.loads((ci.ROOT / "specs/migration/r03-v1/frontend-ci-pr50.json").read_text())


def receipt(number):
    pin = PINS["receipts"][str(number)]
    pr = {"number": number, "state": "closed", "merged": True,
          "merged_at": "2026-10-11T16:50:00Z", "merged_by": {"login": pin["approver"]},
          "merge_commit_sha": pin["merge_sha"],
          "head": {"sha": pin["approved_head"], "repo": {"full_name": PINS["repository"]}},
          "base": {"ref": "ms7-mig-react-fastapi", "repo": {"full_name": PINS["repository"]}}}
    approval = {"id": pin["approval_id"], "state": "APPROVED", "commit_id": pin["approved_head"],
                "user": {"login": pin["approver"]}, "submitted_at": "2026-10-11T16:45:00Z",
                "html_url": f"https://github.com/{PINS['repository']}/pull/{number}#pullrequestreview-{pin['approval_id']}"}
    return pr, approval


def fake_git(root, *args):
    if args == ("rev-parse", "HEAD"): return PINS["integration_sha"].encode()
    if args == ("rev-parse", "HEAD^{tree}"): return PINS["integration_tree"].encode()
    if args[:3] == ("show", "-s", "--format=%P"):
        pin = next(p for p in PINS["receipts"].values() if p["merge_sha"] == args[3])
        return pin["merge_parent"].encode()
    return b""


class AcceptedIntegrationTests(unittest.TestCase):
    def test_both_receipts_require_actual_approval_and_merge(self):
        for number in (50, 51):
            pr, approval = receipt(number)
            ci.validate_receipt(PINS["repository"], number, PINS["receipts"][str(number)], pr, approval)

    def test_wrong_review_state_head_id_actor_link_or_time_rejected(self):
        pr, approval = receipt(50)
        for key, value in (("state", "DISMISSED"), ("commit_id", "other-head"), ("id", 1),
                           ("user", {"login": "other-reviewer"}), ("html_url", "other-PR"),
                           ("submitted_at", "2026-10-12T00:00:00Z")):
            changed = copy.deepcopy(approval); changed[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                ci.validate_receipt(PINS["repository"], 50, PINS["receipts"]["50"], pr, changed)

    def test_closed_unmerged_or_wrong_merge_head_repo_base_rejected(self):
        pr, approval = receipt(51)
        for key, value in (("merged", False), ("state", "open"), ("merge_commit_sha", "other-merge"),
                           ("head", {"sha": "other-head", "repo": {"full_name": PINS["repository"]}}),
                           ("base", {"ref": "main", "repo": {"full_name": "foreign/repo"}})):
            changed = copy.deepcopy(pr); changed[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                ci.validate_receipt(PINS["repository"], 51, PINS["receipts"]["51"], changed, approval)

    def test_immutable_base_and_historical_head_cannot_be_reassigned(self):
        for key in ("pr_head_sha", "pr_base_sha", "repository"):
            changed = copy.deepcopy(HISTORICAL); changed[key] = "other"
            with self.subTest(key=key), self.assertRaises(ValueError): ci.accepted_config(changed)
        changed = copy.deepcopy(PINS); changed["mig_base_sha"] = "other"
        with patch.object(ci.json, "loads", return_value=changed), self.assertRaises(ValueError):
            ci.accepted_config(HISTORICAL)

    def test_approved_pr_head_cannot_substitute_for_actual_integration_result(self):
        config = ci.accepted_config(HISTORICAL)
        with self.assertRaises(ValueError): validate_report(report(), config)
        actual = report(); actual["tested_implementation_sha"] = PINS["integration_sha"]
        for key in ("git_before", "git_after"): actual[key]["head"] = PINS["integration_sha"]
        self.assertEqual(validate_report(actual, config)["frontend_tests_passed"], 112)

    def test_wrong_checkout_tree_dirty_source_or_squash_parent_rejected(self):
        mutations = {"head": ("rev-parse", "HEAD"), "tree": ("rev-parse", "HEAD^{tree}"),
                     "dirty": ("status",), "source": ("diff",), "parents": ("show",)}
        for name, prefix in mutations.items():
            def changed_git(root, *args):
                return b"altered" if args[:len(prefix)] == prefix else fake_git(root, *args)
            with self.subTest(name=name), patch.object(ci, "git", side_effect=changed_git), self.assertRaises(ValueError):
                ci.validate_tree(ci.ROOT, ci.ROOT, PINS)

    def test_full_accepted_inventory_is_checked_after_domain_and_chain_checks(self):
        with patch.object(ci, "git", side_effect=fake_git), patch("scripts.check_migration_preservation.verify") as verify:
            ci.validate_tree(ci.ROOT, ci.ROOT, PINS)
            verify.assert_called_once_with(ci.ROOT, input_sha=PINS["integration_sha"])

    def test_advanced_live_integration_ref_rejected_before_receipt_intake(self):
        with patch.object(ci, "validate_tree", return_value={}), patch.object(ci, "fetch", return_value={"object": {"sha": "new-input"}}), self.assertRaises(ValueError):
            ci.intake(ci.ROOT, ci.accepted_config(HISTORICAL))


if __name__ == "__main__": unittest.main()
