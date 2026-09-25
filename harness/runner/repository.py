from __future__ import annotations

import subprocess
from pathlib import Path


class RepositoryError(RuntimeError):
    pass


def run_git(repo_root: Path, *args: str) -> str:
    process = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        shell=False,
        check=False,
    )

    if process.returncode != 0:
        message = process.stderr.strip() or process.stdout.strip()
        raise RepositoryError(message or "git command failed")

    return process.stdout.strip()


def repository_root(start: Path) -> Path:
    output = run_git(start, "rev-parse", "--show-toplevel")
    return Path(output).resolve()


def current_branch(repo_root: Path) -> str:
    return run_git(repo_root, "branch", "--show-current")


def head_sha(repo_root: Path) -> str:
    return run_git(repo_root, "rev-parse", "HEAD")

def commit_exists(repo_root: Path, sha: str) -> bool:
    process = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        shell=False,
        check=False,
    )
    return process.returncode == 0


def is_ancestor(repo_root: Path, ancestor_sha: str, descendant_sha: str) -> bool:
    process = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor_sha, descendant_sha],
        cwd=repo_root,
        capture_output=True,
        text=True,
        shell=False,
        check=False,
    )
    return process.returncode == 0


def working_tree_status(repo_root: Path) -> str:
    return run_git(
        repo_root,
        "status",
        "--short",
        "--untracked-files=all",
    )


def working_tree_diff(repo_root: Path) -> str:
    return run_git(
        repo_root,
        "diff",
        "--no-ext-diff",
        "--binary",
        "--",
    )


def staged_diff(repo_root: Path) -> str:
    return run_git(
        repo_root,
        "diff",
        "--cached",
        "--no-ext-diff",
        "--binary",
        "--",
    )
