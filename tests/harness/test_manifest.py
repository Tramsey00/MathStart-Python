from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from harness.contracts.manifest import (
    ManifestValidationError,
    load_and_validate_manifest,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return f"sha256:{digest}"


class ManifestValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)

        schema_source = Path(
            "specs/harness/task-manifest-v1.schema.json"
        )

        schema_target = (
            self.repo_root
            / "specs"
            / "harness"
            / "task-manifest-v1.schema.json"
        )

        schema_target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copyfile(
            schema_source,
            schema_target,
        )

        self.task_dir = (
            self.repo_root
            / "harness"
            / "tasks"
        )

        self.task_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.spec_path = (
            self.repo_root
            / "SPEC.md"
        )

        self.spec_path.write_text(
            "contract\n",
            encoding="utf-8",
        )

        self.plan_path = (
            self.repo_root
            / "PLAN.md"
        )

        self.plan_path.write_text(
            "plan\n",
            encoding="utf-8",
        )

        self.manifest = {
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
                    "digest": _sha256(
                        self.spec_path
                    ),
                }
            ],
            "plan_ref": {
                "path": "PLAN.md",
                "digest": _sha256(
                    self.plan_path
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
            ],
            "expected_outputs": [
                "tests",
            ],
            "limits": {
                "max_turns": 30,
                "wall_time_seconds": 1800,
            },
            "human_gates": [
                "review",
            ],
        }

        self.manifest_path = (
            self.task_dir
            / "MS6-R04.json"
        )

        self._write_manifest()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_manifest(self) -> None:
        self.manifest_path.write_text(
            json.dumps(
                self.manifest,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def _load(self) -> dict:
        with (
            patch(
                "harness.contracts.manifest.current_branch",
                return_value="test-branch",
            ),
            patch(
                "harness.contracts.manifest.head_sha",
                return_value="b" * 40,
            ),
            patch(
                "harness.contracts.manifest.commit_exists",
                return_value=True,
            ),
            patch(
                "harness.contracts.manifest.is_ancestor",
                return_value=True,
            ),
        ):
            return load_and_validate_manifest(
                self.repo_root,
                "MS6-R04",
            )

    def test_valid_manifest_is_accepted(self) -> None:
        result = self._load()

        self.assertEqual(
            result["task_id"],
            "MS6-R04",
        )

    def test_digest_mismatch_is_blocked(self) -> None:
        self.manifest[
            "accepted_spec_refs"
        ][0]["digest"] = (
            "sha256:" + ("0" * 64)
        )

        self._write_manifest()

        with self.assertRaises(
            ManifestValidationError
        ) as context:
            self._load()

        self.assertTrue(
            any(
                "digest mismatch"
                in error
                for error
                in context.exception.errors
            )
        )

    def test_missing_spec_is_blocked(self) -> None:
        self.spec_path.unlink()

        with self.assertRaises(
            ManifestValidationError
        ) as context:
            self._load()

        self.assertTrue(
            any(
                "required referenced file is missing"
                in error
                for error
                in context.exception.errors
            )
        )

    def test_path_traversal_is_blocked(self) -> None:
        self.manifest[
            "writable_paths"
        ] = [
            "../outside/**",
        ]

        self._write_manifest()

        with self.assertRaises(
            ManifestValidationError
        ):
            self._load()

    def test_unknown_required_check_is_blocked(self) -> None:
        self.manifest["required_checks"] = ["unknown-command"]
        self._write_manifest()

        with self.assertRaises(ManifestValidationError) as context:
            self._load()

        self.assertTrue(any(
            "unknown required check" in error for error in context.exception.errors
        ))

    def test_unsupported_profile_is_blocked(self) -> None:
        self.manifest["profile"] = (
            "unknown-profile"
        )

        self._write_manifest()

        with self.assertRaises(
            ManifestValidationError
        ) as context:
            self._load()

        self.assertTrue(
            any(
                "unsupported profile"
                in error
                for error
                in context.exception.errors
            )
        )

    def test_branch_mismatch_is_blocked(self) -> None:
        with (
            patch(
                "harness.contracts.manifest.current_branch",
                return_value="wrong-branch",
            ),
            patch(
                "harness.contracts.manifest.head_sha",
                return_value="b" * 40,
            ),
            patch(
                "harness.contracts.manifest.commit_exists",
                return_value=True,
            ),
            patch(
                "harness.contracts.manifest.is_ancestor",
                return_value=True,
            ),
        ):
            with self.assertRaises(
                ManifestValidationError
            ) as context:
                load_and_validate_manifest(
                    self.repo_root,
                    "MS6-R04",
                )

        self.assertTrue(
            any(
                "branch mismatch"
                in error
                for error
                in context.exception.errors
            )
        )


if __name__ == "__main__":
    unittest.main()