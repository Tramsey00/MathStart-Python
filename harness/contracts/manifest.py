from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

import jsonschema

from harness.contracts.checks import KNOWN_CHECKS

from harness.runner.repository import (
    commit_exists,
    current_branch,
    head_sha,
    is_ancestor,
)


class ManifestValidationError(RuntimeError):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


KNOWN_PROFILES = {
    "bootstrap",
}

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return f"sha256:{digest.hexdigest()}"


def _validate_repository_path(value: str) -> bool:
    if not value:
        return False

    if "\\" in value:
        return False

    path = PurePosixPath(value)

    if path.is_absolute():
        return False

    if ".." in path.parts:
        return False

    if len(value) >= 2 and value[1] == ":":
        return False

    return True


def _static_prefix(pattern: str) -> str:
    parts: list[str] = []

    for part in PurePosixPath(pattern).parts:
        if any(character in part for character in "*?["):
            break
        parts.append(part)

    return "/".join(parts)


def _paths_obviously_overlap(first: str, second: str) -> bool:
    first_prefix = _static_prefix(first).rstrip("/")
    second_prefix = _static_prefix(second).rstrip("/")

    if not first_prefix or not second_prefix:
        return True

    return (
        first_prefix == second_prefix
        or first_prefix.startswith(second_prefix + "/")
        or second_prefix.startswith(first_prefix + "/")
    )


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise ManifestValidationError(
            [f"manifest file does not exist: {path}"]
        ) from exc
    except json.JSONDecodeError as exc:
        raise ManifestValidationError(
            [f"manifest is not valid JSON: {exc}"]
        ) from exc

    if not isinstance(data, dict):
        raise ManifestValidationError(
            ["manifest root must be a JSON object"]
        )

    return data


def load_and_validate_manifest(
    repo_root: Path,
    task_id: str,
) -> dict[str, Any]:
    manifest_path = repo_root / "harness" / "tasks" / f"{task_id}.json"
    schema_path = (
        repo_root
        / "specs"
        / "harness"
        / "task-manifest-v1.schema.json"
    )

    manifest = _load_json(manifest_path)

    try:
        with schema_path.open("r", encoding="utf-8") as file:
            schema = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestValidationError(
            [f"cannot load TaskManifest schema: {exc}"]
        ) from exc

    validator = jsonschema.Draft202012Validator(schema)
    schema_errors = sorted(
        validator.iter_errors(manifest),
        key=lambda error: list(error.absolute_path),
    )

    if schema_errors:
        errors = []

        for error in schema_errors:
            location = ".".join(
                str(part) for part in error.absolute_path
            )
            prefix = f"{location}: " if location else ""
            errors.append(prefix + error.message)

        raise ManifestValidationError(errors)

    errors: list[str] = []

    if manifest["task_id"] != task_id:
        errors.append(
            f"task_id mismatch: requested {task_id}, "
            f"manifest contains {manifest['task_id']}"
        )

    branch = current_branch(repo_root)

    if branch != manifest["branch"]:
        errors.append(
            f"branch mismatch: expected {manifest['branch']}, "
            f"current {branch or '<detached>'}"
        )

    current_head = head_sha(repo_root)
    base_sha = manifest["base_sha"]

    if not commit_exists(repo_root, base_sha):
        errors.append(f"base_sha does not exist: {base_sha}")
    elif not is_ancestor(repo_root, base_sha, current_head):
        errors.append(
            f"base_sha {base_sha} is not an ancestor "
            f"of current HEAD {current_head}"
        )

    if manifest["profile"] not in KNOWN_PROFILES:
        errors.append(
            f"unsupported profile: {manifest['profile']}"
        )

    for check_id in manifest["required_checks"]:
        if check_id not in KNOWN_CHECKS:
            errors.append(
                f"unknown required check: {check_id}"
            )

    refs = [
        *manifest["accepted_spec_refs"],
        manifest["plan_ref"],
    ]

    for ref in refs:
        relative_path = ref["path"]

        if not _validate_repository_path(relative_path):
            errors.append(
                f"invalid repository path: {relative_path}"
            )
            continue

        file_path = repo_root / relative_path

        if not file_path.is_file():
            errors.append(
                f"required referenced file is missing: {relative_path}"
            )
            continue

        actual_digest = _sha256(file_path)

        if actual_digest != ref["digest"]:
            errors.append(
                f"digest mismatch for {relative_path}: "
                f"expected {ref['digest']}, actual {actual_digest}"
            )

    for category in ("writable_paths", "protected_paths"):
        for path_pattern in manifest[category]:
            if not _validate_repository_path(path_pattern):
                errors.append(
                    f"invalid {category} entry: {path_pattern}"
                )

    for writable in manifest["writable_paths"]:
        for protected in manifest["protected_paths"]:
            if _paths_obviously_overlap(writable, protected):
                errors.append(
                    "writable/protected path overlap: "
                    f"{writable} <-> {protected}"
                )

    if errors:
        raise ManifestValidationError(errors)

    return manifest