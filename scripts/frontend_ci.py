"""R03 checks a separately pinned I01 candidate; never rewrites its captures."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.accepted_integration_ci import accepted_config, intake as accepted_intake, tested_sha
OUTPUT = ROOT / "var/frontend-ci"
CONFIG = ROOT / "specs/migration/r03-v1/frontend-ci-pr50.json"
COMMAND_NAMES = ["node-version", "npm-version", "generate-api", "typecheck",
                 "native-validator-esm", "unit-component-security",
                 "historical-dispatcher", "production-build", "dependency-tree", "audit"]


def now():
    return datetime.now(timezone.utc).isoformat()


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, timeout=30)


def save(name, data):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    # Every CI checkout is disposable. Refuse refresh of already published evidence.
    with (OUTPUT / name).open("x", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def check_identity(config, pr, checkout):
    if (pr["number"] != config["pr_number"] or pr["state"] != "open"
            or pr["head"]["repo"]["full_name"] != config["repository"]
            or pr["base"]["repo"]["full_name"] != config["repository"]
            or pr["head"]["sha"] != config["pr_head_sha"]
            or pr["base"]["sha"] != config["pr_base_sha"]
            or checkout != config["pr_head_sha"]):
        raise ValueError("live PR or actual checkout differs from pinned candidate")


def snapshot(candidate, config):
    if Path(git(candidate, "rev-parse", "--show-toplevel").decode().strip()).resolve() != candidate:
        raise ValueError("candidate must be its own Git checkout")
    head = git(candidate, "rev-parse", "HEAD").decode().strip()
    status = git(candidate, "status", "--porcelain=v1", "--untracked-files=all").decode()
    if head != tested_sha(config) or status:
        raise ValueError("candidate is stale or dirty")
    workflows = {}
    for name in (".github/workflows/ci.yml", ".github/workflows/migration-ci.yml"):
        original = git(candidate, "show", config["pr_base_sha"] + ":" + name)
        current = git(candidate, "show", "HEAD:" + name)
        if original != current:
            raise ValueError("frozen baseline workflow changed")
        workflows[name] = hashlib.sha256(current).hexdigest()
    paths = git(candidate, "ls-files", "-z", "docs/acceptance/MS7-MIG-I01").decode().split("\0")
    captures = [p for p in paths if re.match(r"docs/acceptance/MS7-MIG-I01/(checkpoint1|checkpoint2|final)/", p)]
    if len(captures) != config["historical_capture_count"]:
        raise ValueError("historical capture inventory changed")
    historical = {p: hashlib.sha256((candidate / p).read_bytes()).hexdigest() for p in sorted(captures)}
    return {"checkout_sha": head, "checkout_tree": git(candidate, "rev-parse", "HEAD^{tree}").decode().strip(),
            "dirty": False, "frozen_workflows": workflows, "historical_captures": historical}


def intake(candidate, config):
    request = urllib.request.Request(
        "https://api.github.com/repos/" + config["repository"] + "/pulls/" + str(config["pr_number"]),
        headers={"Accept": "application/vnd.github+json", "User-Agent": "MathStart-R03-CI"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(request, timeout=30) as response:
        pr = json.load(response)
    before = snapshot(candidate, config)
    acceptance = None
    if "accepted_input" in config:
        pr, acceptance = accepted_intake(candidate, config)
    else:
        check_identity(config, pr, before["checkout_sha"])
    record = {"format": "r03-frontend-ci-v1", "captured_at": now(),
              "evidence_class": config["evidence_class"],
              "i01_acceptance": "ACCEPTED_INTEGRATION" if acceptance else "NOT_DECLARED",
              "acceptance_provenance": acceptance,
              "pr_number": config["pr_number"], "pr_head_sha": pr["head"]["sha"],
              "pr_base_sha": pr["base"]["sha"], "pr_merge_ref_sha_observed": pr["merge_commit_sha"],
              "candidate_checkout": before, "workflow_checkout_sha": git(ROOT, "rev-parse", "HEAD").decode().strip(),
              "event_sha": os.environ.get("GITHUB_SHA"), "event": os.environ.get("GITHUB_EVENT_NAME", "local"),
              "ref": os.environ.get("GITHUB_REF"), "run_id": os.environ.get("GITHUB_RUN_ID"),
              "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
              "run_url": "https://github.com/" + config["repository"] + "/actions/runs/" + os.environ.get("GITHUB_RUN_ID", "local")}
    save("candidate-provenance.json", record)
    print(json.dumps({k: v for k, v in record.items()
                      if k not in ("candidate_checkout", "acceptance_provenance")}, indent=2))
    print("ACTUAL_CANDIDATE_CHECKOUT=" + before["checkout_sha"])


def validate_report(report, config):
    if (report["exit_code"] != 0 or report["tested_implementation_sha"] != tested_sha(config)
            or report["dirty_or_uncommitted"] is not False or report["source_changed_during_run"] is not False
            or any(report[key]["head"] != tested_sha(config) or report[key]["dirty"] is not False
                   for key in ("git_before", "git_after"))):
        raise ValueError("foundation report is failed, dirty, or bound to another SHA")
    history = report["history_integrity"]
    if (history["file_count"] != config["historical_capture_count"] or history["changed_paths"]
            or history["before_sha256"] != history["after_sha256"]):
        raise ValueError("historical capture integrity failed")
    results = report["results"]
    if [r["name"] for r in results] != COMMAND_NAMES or any(
            r["exit_code"] != 0 or r.get("error") or r.get("signal") for r in results):
        raise ValueError("required command absent or failed")
    ansi = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
    unit = ansi.sub("", results[5]["stdout"] + results[5]["stderr"])
    historical = results[6]["stdout"] + results[6]["stderr"]
    unit_count = re.search(r"Tests\s+(\d+) passed\s+\(\1\)", unit)
    # Node 24 may select either TAP or the native spec reporter for captured output.
    passed = re.search(r"(?:#|ℹ) pass (\d+)", historical)
    if (not unit_count or int(unit_count[1]) < config["minimum_frontend_tests"]
            or not passed or int(passed[1]) < config["minimum_historical_tests"]
            or not re.search(r"(?:#|ℹ) fail 0(?:\n|\r|$)", historical)
            or not re.search(r"(?:#|ℹ) skipped 0(?:\n|\r|$)", historical)
            or not re.search(r"(?:#|ℹ) cancelled 0(?:\n|\r|$)", historical)):
        raise ValueError("nonempty complete frontend/dispatcher test evidence required")
    return {"frontend_tests_passed": int(unit_count[1]), "historical_tests_passed": int(passed[1]),
            "required_commands_passed": len(results)}


def run(candidate, config):
    record = json.loads((OUTPUT / "candidate-provenance.json").read_text(encoding="utf-8"))
    before = snapshot(candidate, config)
    if before != record["candidate_checkout"]:
        raise ValueError("candidate changed since CI intake")
    commands = []
    result = {"started_at": now(), "finished_at": None, "exit_code": 1, "commands": commands}
    try:
        npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
        node = shutil.which("node")
        if not npm or not node:
            raise ValueError("Node/npm tooling missing")
        # Intake alone receives the API token. Candidate scripts never receive it.
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GH_TOKEN")}
        versions = [subprocess.check_output([exe, "--version"], env=env, timeout=30).decode().strip()
                    for exe in (node, npm)]
        result["versions"] = dict(zip(("node", "npm"), versions))
        for observed, expected in zip(versions, (config["node_version"], config["npm_version"])):
            if observed != expected:
                raise ValueError("exact Node/npm toolchain required")
        owner_output = candidate / "frontend/.cache/r03-ci-command-results.json"
        for name, argv, deadline in (
                ("locked-install", [npm, "ci", "--no-fund"], 600),
                ("foundation", [npm, "run", "verify:foundation", "--", "--output", ".cache/r03-ci-command-results.json"], 900)):
            entry = {"name": name, "command": argv, "started_at": now(), "exit_code": None}
            commands.append(entry)
            try:
                with (OUTPUT / (name + ".log")).open("x", encoding="utf-8") as log:
                    process = subprocess.run(argv, cwd=candidate / "frontend", env=env, stdout=log,
                                             stderr=subprocess.STDOUT, timeout=deadline)
                entry["exit_code"] = process.returncode
            except subprocess.TimeoutExpired:
                entry["exit_code"] = 124
                raise
            except OSError:
                entry["exit_code"] = 127
                raise
            finally:
                entry["finished_at"] = now()
            print(name + ": " + str(process.returncode), flush=True)
            if process.returncode:
                raise ValueError("frontend command failed: " + name)
        report = json.loads(owner_output.read_text(encoding="utf-8"))
        save("foundation-command-results.json", report)
        result.update(validate_report(report, config))
        after = snapshot(candidate, config)
        if before != after:
            raise ValueError("candidate or historical evidence changed during checks")
        result.update({"candidate_after": after, "exit_code": 0})
    finally:
        # Keep raw owner failure evidence as well as outer nonzero status.
        owner_output = candidate / "frontend/.cache/r03-ci-command-results.json"
        if owner_output.is_file() and not (OUTPUT / "foundation-command-results.json").exists():
            save("foundation-command-results.json", json.loads(owner_output.read_text(encoding="utf-8")))
        result["finished_at"] = now()
        save("execution.json", result)
    print(json.dumps({k: v for k, v in result.items() if k != "candidate_after"}, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("intake", "run"))
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args(argv)
    try:
        config = accepted_config(json.loads(CONFIG.read_text(encoding="utf-8")))
        candidate = Path(args.candidate).resolve()
        (intake if args.action == "intake" else run)(candidate, config)
        return 0
    except ValueError as error:
        print("FAIL: " + str(error))
        return 1
    except (KeyError, OSError, subprocess.SubprocessError):
        print("FAIL: frontend CI prerequisites, execution or evidence validation failed; no acceptance claim")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
