from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from harness.cli.status import status_command
from harness.contracts.manifest import (
    ManifestValidationError,
    load_and_validate_manifest,
)
from harness.contracts.validation import validate_schema_file
from harness.runner.engine import execute_bootstrap_run
from harness.runner.repository import (
    RepositoryError,
    current_branch,
    head_sha,
    repository_root,
    staged_diff,
    working_tree_diff,
    working_tree_status,
)


REQUIRED_SCHEMA_FILES = (
    "specs/harness/task-manifest-v1.schema.json",
    "specs/harness/run-result-v1.schema.json",
    "specs/harness/profile-v1.draft.schema.json",
    "specs/harness/hook-v1.draft.schema.json",
)

REQUIRED_CONTRACT_FILES = (
    "specs/harness/adapter-protocol-v1.md",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m harness",
        description="MathStart Harness",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "doctor",
        help="Check whether the local Harness environment is usable.",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Validate and execute a Harness task.",
    )

    run_parser.add_argument(
        "task_id",
        help="Task identifier, for example MS6-R04.",
    )

    run_parser.add_argument(
        "--mode",
        choices=("dry-run", "execute"),
        required=True,
    )

    run_parser.add_argument(
        "--profile",
        default=None,
        help="Optional profile assertion.",
    )

    status_parser = subparsers.add_parser(
        "status",
        help="Show the persisted result of a Harness run.",
    )

    status_parser.add_argument(
        "run_id",
        help="Harness run identifier.",
    )

    return parser


def _print_check(
    name: str,
    status: str,
    detail: str | None = None,
) -> None:
    line = f"{name:<24} {status}"

    if detail:
        line += f"  {detail}"

    print(line)


def doctor() -> int:
    print("MathStart Harness Doctor")
    print()

    blocking_failure = False
    warning = False

    python_version = (
        f"{sys.version_info.major}."
        f"{sys.version_info.minor}."
        f"{sys.version_info.micro}"
    )

    if sys.version_info >= (3, 12):
        _print_check(
            "Python",
            "OK",
            python_version,
        )
    else:
        _print_check(
            "Python",
            "WARN",
            f"{python_version}; project target is Python 3.12+",
        )
        warning = True

    if shutil.which("git") is None:
        _print_check(
            "Git executable",
            "FAIL",
            "git not found on PATH",
        )
        blocking_failure = True
        repo_root = None
    else:
        _print_check(
            "Git executable",
            "OK",
        )

        try:
            repo_root = repository_root(Path.cwd())
            _print_check(
                "Repository",
                "OK",
                str(repo_root),
            )
        except RepositoryError as exc:
            _print_check(
                "Repository",
                "FAIL",
                str(exc),
            )
            blocking_failure = True
            repo_root = None

    if repo_root is not None:
        try:
            branch = current_branch(repo_root)
            sha = head_sha(repo_root)

            if branch:
                _print_check(
                    "Branch",
                    "OK",
                    branch,
                )
            else:
                _print_check(
                    "Branch",
                    "WARN",
                    "detached HEAD",
                )
                warning = True

            _print_check(
                "HEAD SHA",
                "OK",
                sha,
            )
        except RepositoryError as exc:
            _print_check(
                "Git state",
                "FAIL",
                str(exc),
            )
            blocking_failure = True

    if repo_root is not None:
        for relative_path in REQUIRED_SCHEMA_FILES:
            path = repo_root / relative_path

            if not path.is_file():
                _print_check(
                    relative_path,
                    "FAIL",
                    "missing",
                )
                blocking_failure = True
                continue

            try:
                validate_schema_file(path)
            except Exception as exc:
                _print_check(
                    relative_path,
                    "FAIL",
                    str(exc),
                )
                blocking_failure = True
            else:
                _print_check(
                    relative_path,
                    "OK",
                )

        for relative_path in REQUIRED_CONTRACT_FILES:
            path = repo_root / relative_path

            if path.is_file():
                _print_check(
                    relative_path,
                    "OK",
                )
            else:
                _print_check(
                    relative_path,
                    "FAIL",
                    "missing",
                )
                blocking_failure = True

    if repo_root is not None:
        task_dir = repo_root / "harness" / "tasks"

        if task_dir.is_dir():
            _print_check(
                "Task directory",
                "OK",
                str(task_dir),
            )
        else:
            _print_check(
                "Task directory",
                "FAIL",
                "missing",
            )
            blocking_failure = True

    if repo_root is not None:
        run_dir = repo_root / "var" / "harness" / "runs"

        try:
            run_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            probe = run_dir / ".doctor-write-test"
            probe.write_text(
                "ok",
                encoding="utf-8",
            )
            probe.unlink()

            _print_check(
                "Run storage",
                "OK",
                str(run_dir),
            )
        except OSError as exc:
            _print_check(
                "Run storage",
                "FAIL",
                str(exc),
            )
            blocking_failure = True

    print()

    if blocking_failure:
        print("Status: BLOCKED_CONFIGURATION")
        return 2

    if warning:
        print("Status: READY_WITH_WARNINGS")
        return 0

    print("Status: READY")
    return 0


def run_task(
    task_id: str,
    mode: str,
    requested_profile: str | None,
) -> int:
    try:
        repo_root = repository_root(Path.cwd())
        manifest = load_and_validate_manifest(
            repo_root,
            task_id,
        )
    except (RepositoryError, ManifestValidationError) as exc:
        print("Status: BLOCKED_CONFIGURATION")

        if isinstance(exc, ManifestValidationError):
            for error in exc.errors:
                print(f"- {error}")
        else:
            print(f"- {exc}")

        return 2

    if requested_profile is not None:
        if requested_profile != manifest["profile"]:
            print("Status: BLOCKED_CONFIGURATION")
            print(
                "- profile mismatch: "
                f"manifest={manifest['profile']}, "
                f"requested={requested_profile}"
            )
            return 2

    if mode == "dry-run":
        print("MathStart Harness Dry Run")
        print()

        print(
            f"Task:              "
            f"{manifest['task_id']}"
        )
        print(
            f"Base SHA:          "
            f"{manifest['base_sha']}"
        )
        print(
            f"Current HEAD:      "
            f"{head_sha(repo_root)}"
        )
        print(
            f"Branch:            "
            f"{manifest['branch']}"
        )
        print(
            f"Workflow:          "
            f"{manifest['workflow']}"
        )
        print(
            f"Profile:           "
            f"{manifest['profile']}"
        )
        print(
            "Accepted specs:    "
            f"{len(manifest['accepted_spec_refs'])}"
        )
        print(
            "Writable paths:    "
            f"{len(manifest['writable_paths'])}"
        )
        print(
            "Protected paths:   "
            f"{len(manifest['protected_paths'])}"
        )
        print(
            "Required checks:   "
            + ", ".join(
                manifest["required_checks"]
            )
        )
        print(
            "Limits:            "
            f"{manifest['limits']['max_turns']} turns, "
            f"{manifest['limits']['wall_time_seconds']} seconds"
        )

        initial_status = working_tree_status(repo_root)
        initial_diff = working_tree_diff(repo_root)
        initial_staged_diff = staged_diff(repo_root)

        print(
            "Working tree:      "
            + ("DIRTY" if initial_status else "CLEAN")
        )
        print(
            "Unstaged diff:     "
            + ("PRESENT" if initial_diff else "NONE")
        )
        print(
            "Staged diff:       "
            + ("PRESENT" if initial_staged_diff else "NONE")
        )

        print("Model invocation:  DISABLED")
        print("Network:           DISABLED")
        print("File mutation:     DISABLED")

        print()
        print("Status: DRY_RUN_OK")
        return 0

    if mode == "execute":
        try:
            result, exit_code = execute_bootstrap_run(
                repo_root,
                manifest,
            )
        except Exception as exc:
            print("Status: BLOCKED_CONFIGURATION")
            print(f"- execute lifecycle failed: {exc}")
            return 2

        print("MathStart Harness Run")
        print()

        print(
            f"Run ID:            "
            f"{result['run_id']}"
        )
        print(
            f"Task:              "
            f"{result['task_id']}"
        )

        adapter = result["adapter"]

        adapter_text = (
            "-"
            if adapter is None
            else (
                f"{adapter['name']}@"
                f"{adapter['version']}"
            )
        )

        print(
            f"Adapter:           "
            f"{adapter_text}"
        )
        print(
            f"Turns:             "
            f"{result['execution']['turns_used']}"
        )
        print(
            f"Verification:      "
            f"{result['verification']['status']}"
        )

        print()
        print(
            f"Status:            "
            f"{result['status']}"
        )

        for blocker in result["blockers"]:
            print(
                f"- {blocker['code']}: "
                f"{blocker['message']}"
            )

        return exit_code

    print("Status: BLOCKED_CONFIGURATION")
    print(f"- unsupported mode: {mode}")
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        return doctor()

    if args.command == "run":
        return run_task(
            task_id=args.task_id,
            mode=args.mode,
            requested_profile=args.profile,
        )

    if args.command == "status":
        return status_command(
            args.run_id,
        )

    parser.error(
        f"Unsupported command: {args.command}"
    )
    return 2
