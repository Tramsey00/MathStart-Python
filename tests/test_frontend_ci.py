"""Reject stale/partial/dirty frontend CI evidence without altering I01 tests."""
import copy
import json
from pathlib import Path
import unittest

from scripts.frontend_ci import check_identity, COMMAND_NAMES, validate_report

CONFIG = json.loads((Path(__file__).resolve().parents[1] /
                     "specs/migration/r03-v1/frontend-ci-pr50.json").read_text())


def report(reporter="#"):
    result = {"exit_code": 0, "tested_implementation_sha": CONFIG["pr_head_sha"],
              "dirty_or_uncommitted": False, "source_changed_during_run": False,
              "git_before": {"head": CONFIG["pr_head_sha"], "dirty": False},
              "git_after": {"head": CONFIG["pr_head_sha"], "dirty": False},
              "history_integrity": {"file_count": 84, "changed_paths": [],
                                    "before_sha256": "same", "after_sha256": "same"},
              "results": [{"name": name, "exit_code": 0, "stdout": "", "stderr": ""}
                          for name in COMMAND_NAMES]}
    result["results"][5]["stdout"] = "Tests 112 passed (112)\n"
    result["results"][6]["stdout"] = "".join(
        f"{reporter} {key} {value}\n" for key, value in
        (("pass", 5), ("fail", 0), ("skipped", 0), ("cancelled", 0)))
    return result


class FrontendEvidenceTests(unittest.TestCase):
    def test_both_native_node_reporters_are_supported(self):
        for reporter in ("#", "ℹ"):
            counts = validate_report(report(reporter), CONFIG)
            self.assertEqual(counts["frontend_tests_passed"], 112)
            self.assertEqual(counts["historical_tests_passed"], 5)

    def test_stale_or_dirty_owner_result_rejected(self):
        for key, value in (("exit_code", 1), ("tested_implementation_sha", "stale"),
                           ("dirty_or_uncommitted", True), ("source_changed_during_run", True)):
            item = report(); item[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_report(item, CONFIG)
        item = report(); item["git_after"]["dirty"] = True
        with self.assertRaises(ValueError):
            validate_report(item, CONFIG)

    def test_missing_command_and_nonzero_or_timeout_rejected(self):
        item = report(); item["results"].pop()
        with self.assertRaises(ValueError):
            validate_report(item, CONFIG)
        for code in (1, 124, 127, None):
            item = report(); item["results"][0]["exit_code"] = code
            with self.subTest(code=code), self.assertRaises(ValueError):
                validate_report(item, CONFIG)

    def test_empty_or_partial_frontend_suite_rejected(self):
        for stdout in ("", "Tests 0 passed (0)", "Tests 111 passed (111)",
                       "Tests 112 passed | 1 skipped (113)"):
            item = report(); item["results"][5]["stdout"] = stdout
            with self.subTest(stdout=stdout), self.assertRaises(ValueError):
                validate_report(item, CONFIG)

    def test_skipped_failed_cancelled_or_empty_historical_suite_rejected(self):
        for old, new in (("# skipped 0", "# skipped 1"), ("# fail 0", "# fail 1"),
                         ("# cancelled 0", "# cancelled 1"), ("# pass 5", "# pass 0")):
            item = report(); item["results"][6]["stdout"] = item["results"][6]["stdout"].replace(old, new)
            with self.subTest(new=new), self.assertRaises(ValueError):
                validate_report(item, CONFIG)

    def test_history_changes_or_missing_inventory_rejected(self):
        for key, value in (("changed_paths", ["historical.json"]), ("file_count", 83),
                           ("after_sha256", "changed")):
            item = report(); item["history_integrity"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_report(item, CONFIG)

    def test_actual_checkout_and_live_pr_head_are_separate_assertions(self):
        pr = {"number": 50, "state": "open",
              "head": {"sha": CONFIG["pr_head_sha"], "repo": {"full_name": CONFIG["repository"]}},
              "base": {"sha": CONFIG["pr_base_sha"], "repo": {"full_name": CONFIG["repository"]}}}
        check_identity(CONFIG, pr, CONFIG["pr_head_sha"])
        with self.assertRaises(ValueError):
            check_identity(CONFIG, pr, "different-actual-checkout")
        for field, value in (("head", "new-head"), ("base", "new-base")):
            stale = copy.deepcopy(pr); stale[field]["sha"] = value
            with self.assertRaises(ValueError):
                check_identity(CONFIG, stale, CONFIG["pr_head_sha"])

    def test_closed_or_foreign_pr_rejected(self):
        pr = {"number": 50, "state": "closed",
              "head": {"sha": CONFIG["pr_head_sha"], "repo": {"full_name": CONFIG["repository"]}},
              "base": {"sha": CONFIG["pr_base_sha"], "repo": {"full_name": CONFIG["repository"]}}}
        with self.assertRaises(ValueError):
            check_identity(CONFIG, pr, CONFIG["pr_head_sha"])
        pr["state"] = "open"; pr["head"]["repo"]["full_name"] = "foreign/repo"
        with self.assertRaises(ValueError):
            check_identity(CONFIG, pr, CONFIG["pr_head_sha"])


if __name__ == "__main__":
    unittest.main()
