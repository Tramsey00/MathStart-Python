"""Bind CI event, actual checkout, tree and merge parents without environment dumps."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, timeout=30).strip()


def collect(event, environment):
    head = git("rev-parse", "HEAD")
    expected = environment.get("GITHUB_SHA", head)
    if head != expected:
        raise ValueError("checkout does not match event SHA")
    parents = git("show", "-s", "--format=%P", "HEAD").split()
    record = {"checkout_sha": head, "tree_sha": git("rev-parse", "HEAD^{tree}"),
              "parents": parents, "event": environment.get("GITHUB_EVENT_NAME", "local"),
              "ref": environment.get("GITHUB_REF", "local"),
              "run_id": environment.get("GITHUB_RUN_ID"),
              "run_attempt": environment.get("GITHUB_RUN_ATTEMPT")}
    pr = event.get("pull_request")
    if pr:
        base, proposed = pr["base"]["sha"], pr["head"]["sha"]
        if parents != [base, proposed]:
            raise ValueError("tested merge parents do not match PR base/head")
        record.update({"pr_head_sha": proposed, "pr_base_sha": base,
                       "tested_merge_ref": environment.get("GITHUB_REF"),
                       "pr_head_tree": git("rev-parse", proposed + "^{tree}")})
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        event_path = os.environ.get("GITHUB_EVENT_PATH")
        event = json.loads(Path(event_path).read_text(encoding="utf-8")) if event_path else {}
        record = collect(event, os.environ)
        output = (ROOT / args.output).resolve()
        if not output.is_relative_to(ROOT / "var"):
            raise ValueError("evidence output must be under var")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(record, indent=2))
        return 0
    except (ValueError, KeyError, OSError, subprocess.SubprocessError):
        print("FAIL: CI checkout/event linkage could not be established.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
