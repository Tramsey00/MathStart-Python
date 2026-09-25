from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from harness.cli.main import main
from harness.contracts.manifest import (
    ManifestValidationError,
)


VALID_MANIFEST = {
    "schema_version": "harness-task-v1",
    "task_id": "MS6-R04",
    "issue_ref": None,
    "owner": "test-owner",
    "base_sha": "a" * 40,
    "branch": "test-branch",
    "workflow": "implementation",
    "profile": "bootstrap",
    "accepted_spec_refs": [
        {
            "path": "SPEC.md",
            "digest": (
                "sha256:"
                + ("0" * 64)
            ),
        }
    ],
    "plan_ref": {
        "path": "PLAN.md",
        "digest": (
            "sha256:"
            + ("1" * 64)
        ),
    },
    "writable_paths": [
        "tests/harness/**",
    ],
    "protected_paths": [
        ".env",
    ],
    "required_checks": [
        "repo-baseline",
        "harness-unit",
        "harness-cli-smoke",
    ],
    "expected_outputs": [
        "runner",
    ],
    "limits": {
        "max_turns": 30,
        "wall_time_seconds": 1800,
    },
    "human_gates": [
        "review",
    ],
}


class CliTests(unittest.TestCase):
    def test_dry_run_does_not_execute_engine(self) -> None:
        output = io.StringIO()

        with (
            patch(
                "harness.cli.main.repository_root",
                return_value=Path(
                    "C:/fake/repo"
                ),
            ),
            patch(
                "harness.cli.main.load_and_validate_manifest",
                return_value=VALID_MANIFEST,
            ),
            patch(
                "harness.cli.main.head_sha",
                return_value="b" * 40,
            ),
            patch(
                "harness.cli.main.working_tree_status",
                return_value="",
            ),
            patch(
                "harness.cli.main.working_tree_diff",
                return_value="",
            ),
            patch(
                "harness.cli.main.staged_diff",
                return_value="",
            ),
            patch(
                "harness.cli.main.execute_bootstrap_run",
            ) as execute,
            redirect_stdout(output),
        ):
            exit_code = main(
                [
                    "run",
                    "MS6-R04",
                    "--mode",
                    "dry-run",
                ]
            )

        self.assertEqual(
            exit_code,
            0,
        )

        execute.assert_not_called()

        text = output.getvalue()

        self.assertIn(
            "Status: DRY_RUN_OK",
            text,
        )
        self.assertIn(
            "Model invocation:  DISABLED",
            text,
        )
        self.assertIn(
            "Network:           DISABLED",
            text,
        )
        self.assertIn(
            "File mutation:     DISABLED",
            text,
        )

    def test_profile_mismatch_is_blocked(self) -> None:
        output = io.StringIO()

        with (
            patch(
                "harness.cli.main.repository_root",
                return_value=Path(
                    "C:/fake/repo"
                ),
            ),
            patch(
                "harness.cli.main.load_and_validate_manifest",
                return_value=VALID_MANIFEST,
            ),
            redirect_stdout(output),
        ):
            exit_code = main(
                [
                    "run",
                    "MS6-R04",
                    "--mode",
                    "dry-run",
                    "--profile",
                    "reviewer",
                ]
            )

        self.assertEqual(
            exit_code,
            2,
        )

        self.assertIn(
            "BLOCKED_CONFIGURATION",
            output.getvalue(),
        )

    def test_invalid_manifest_is_blocked(self) -> None:
        output = io.StringIO()

        with (
            patch(
                "harness.cli.main.repository_root",
                return_value=Path(
                    "C:/fake/repo"
                ),
            ),
            patch(
                "harness.cli.main.load_and_validate_manifest",
                side_effect=ManifestValidationError(
                    [
                        "digest mismatch for SPEC.md",
                    ]
                ),
            ),
            redirect_stdout(output),
        ):
            exit_code = main(
                [
                    "run",
                    "MS6-R04",
                    "--mode",
                    "dry-run",
                ]
            )

        self.assertEqual(
            exit_code,
            2,
        )

        text = output.getvalue()

        self.assertIn(
            "BLOCKED_CONFIGURATION",
            text,
        )
        self.assertIn(
            "digest mismatch",
            text,
        )

    def test_execute_uses_persisted_result(self) -> None:
        output = io.StringIO()

        result = {
            "run_id": "run-test",
            "task_id": "MS6-R04",
            "adapter": {
                "name": "fake",
                "version": "1",
            },
            "execution": {
                "turns_used": 3,
            },
            "verification": {
                "status": "NOT_RUN",
            },
            "status": (
                "BLOCKED_CONFIGURATION"
            ),
            "blockers": [
                {
                    "code": (
                        "VERIFICATION_NOT_IMPLEMENTED"
                    ),
                    "message": (
                        "verification missing"
                    ),
                }
            ],
        }

        with (
            patch(
                "harness.cli.main.repository_root",
                return_value=Path(
                    "C:/fake/repo"
                ),
            ),
            patch(
                "harness.cli.main.load_and_validate_manifest",
                return_value=VALID_MANIFEST,
            ),
            patch(
                "harness.cli.main.execute_bootstrap_run",
                return_value=(
                    result,
                    2,
                ),
            ),
            redirect_stdout(output),
        ):
            exit_code = main(
                [
                    "run",
                    "MS6-R04",
                    "--mode",
                    "execute",
                ]
            )

        self.assertEqual(
            exit_code,
            2,
        )

        text = output.getvalue()

        self.assertIn(
            "Adapter:           fake@1",
            text,
        )
        self.assertIn(
            "Turns:             3",
            text,
        )


if __name__ == "__main__":
    unittest.main()