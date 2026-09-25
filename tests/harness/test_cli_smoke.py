"""Real CLI subprocess smoke with a separate dry-run engine assertion."""

from __future__ import annotations

import io
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from harness.cli.main import main


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
        result = self._run("run", "MS6-R04", "--mode", "dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Status: DRY_RUN_OK", result.stdout)
        with patch("harness.cli.main.execute_bootstrap_run") as execute:
            with redirect_stdout(io.StringIO()):
                exit_code = main(["run", "MS6-R04", "--mode", "dry-run"])
            self.assertEqual(exit_code, 0)
            execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
