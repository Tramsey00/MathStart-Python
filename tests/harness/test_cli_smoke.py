"""Real help/doctor smoke and a deterministic dry-run fixture, independent of Git branch."""

from __future__ import annotations

import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from harness.cli.main import main
from tests.harness.test_cli import VALID_MANIFEST


ROOT = Path(__file__).resolve().parents[2]


class CliSmokeTests(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "harness", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            shell=False,
            check=False,
            timeout=60,
        )

    def test_help(self) -> None:
        result = self._run("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MathStart Harness", result.stdout)

    def test_doctor(self) -> None:
        result = self._run("doctor")
        self.assertIn(result.returncode, (0, 2), result.stderr)
        self.assertIn("Status:", result.stdout)

    def test_valid_dry_run_and_no_execute_engine(self) -> None:
        # Semantic manifest tests own real branch enforcement. This CLI fixture
        # neither loads MS6-R04 from the checkout nor depends on its Git branch.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = io.StringIO()
            with (
                patch("harness.cli.main.repository_root", return_value=root),
                patch("harness.cli.main.load_and_validate_manifest",
                      return_value=VALID_MANIFEST) as load,
                patch("harness.cli.main.head_sha", return_value="b" * 40),
                patch("harness.cli.main.working_tree_status", return_value=""),
                patch("harness.cli.main.working_tree_diff", return_value=""),
                patch("harness.cli.main.staged_diff", return_value=""),
                patch("harness.cli.main.execute_bootstrap_run") as execute,
                redirect_stdout(output),
            ):
                exit_code = main(["run", "MS6-R04", "--mode", "dry-run"])
            self.assertEqual(exit_code, 0)
            self.assertIn("Status: DRY_RUN_OK", output.getvalue())
            load.assert_called_once_with(root, "MS6-R04")
            execute.assert_not_called()
            self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
