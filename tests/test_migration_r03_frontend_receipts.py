"""Frontend process success cannot replace the required nonempty check result."""
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import target_check


class FrontendReceiptTests(unittest.TestCase):
    def run_child(self, check, child, root):
        with patch.object(target_check, "ROOT", root), patch.object(
            target_check, "command_for", return_value=([sys.executable, "-c", child], root)
        ), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return target_check.main([check])

    def test_real_empty_success_child_is_rejected_for_each_frontend_interface(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for check in target_check.FRONTEND_SCRIPTS:
                with self.subTest(check=check):
                    self.assertEqual(self.run_child(check, "raise SystemExit(0)", root), 1)

    def test_real_child_receives_its_check_id_and_unique_result_destination(self):
        child = (
            "import json,os; from pathlib import Path; "
            "p=Path(os.environ['MATHSTART_CHECK_RESULT']); "
            "assert not p.exists(); "
            "p.write_text(json.dumps(dict(check_id=os.environ['MATHSTART_CHECK_ID'],"
            "status='PASS',evidence_class='TARGET_RUNTIME',assertions=2,skipped=0)),encoding='utf-8')"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for check in target_check.FRONTEND_SCRIPTS:
                with self.subTest(check=check):
                    self.assertEqual(self.run_child(check, child, root), 0)
                    self.assertEqual(self.run_child(check, child, root), 0)
            paths = list((root / "var/target-checks").glob("*/result.json"))
            self.assertEqual(len(paths), 8)
            self.assertEqual(len({p.parent.name for p in paths}), 8)

    def test_real_success_child_with_empty_malformed_or_nonobject_result_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for body in ("", "{", "[]", "null", '"PASS"', "{}"):
                child = (
                    "import os; from pathlib import Path; "
                    "Path(os.environ['MATHSTART_CHECK_RESULT']).write_text("
                    + repr(body) + ",encoding='utf-8')"
                )
                with self.subTest(body=body):
                    self.assertEqual(self.run_child("frontend-e2e", child, root), 1)

    def test_frontend_result_rejects_zero_skipped_wrong_check_and_invalid_counts(self):
        good = dict(check_id="frontend-e2e", status="PASS", evidence_class="TARGET_RUNTIME",
                    assertions=3, skipped=0)
        with tempfile.TemporaryDirectory() as directory:
            result = Path(directory) / "result.json"
            for delta in ({"assertions": 0}, {"assertions": True}, {"assertions": 2.5},
                          {"skipped": True}, {"skipped": 1}, {"check_id": "frontend-tests"},
                          {"status": "NOT_RUN"}, {"evidence_class": "MODEL_SYNTHETIC"}):
                with self.subTest(delta=delta):
                    result.write_text(json.dumps({**good, **delta}), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        target_check.validate_result(result, "frontend-e2e")

    def test_failed_frontend_child_stays_failure_even_if_it_writes_pass_receipt(self):
        child = (
            "import json,os; from pathlib import Path; "
            "Path(os.environ['MATHSTART_CHECK_RESULT']).write_text(json.dumps(dict("
            "check_id=os.environ['MATHSTART_CHECK_ID'],status='PASS',"
            "evidence_class='TARGET_RUNTIME',assertions=1,skipped=0)),encoding='utf-8'); "
            "raise SystemExit(7)"
        )
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(self.run_child("frontend-e2e", child, Path(directory)), 7)


if __name__ == "__main__":
    unittest.main()
