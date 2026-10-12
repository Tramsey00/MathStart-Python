"""R03 verifies human receipts and an exact combined input, independently of CI PASS."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "specs/migration/r03-v1/accepted-integration-20261012.json"
MIG_BASE_SHA = "60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7"
HISTORICAL_INPUT = "8d958aeeb17da46839722441425ccbb5889e2ab7"


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, timeout=60)


def tested_sha(config):
    return config.get("integration_sha", config["pr_head_sha"])


def accepted_config(historical):
    accepted = json.loads(CONFIG.read_text(encoding="utf-8"))
    receipt = accepted["receipts"][str(historical["pr_number"])]
    if (accepted["mig_base_sha"] != MIG_BASE_SHA
            or accepted["historical_input_sha"] != HISTORICAL_INPUT
            or historical["pr_base_sha"] != HISTORICAL_INPUT
            or historical["repository"] != accepted["repository"]
            or historical["pr_head_sha"] != receipt["approved_head"]):
        raise ValueError("Accepted input contradicts immutable/historical provenance")
    return {**historical, "integration_sha": accepted["integration_sha"], "accepted_input": accepted}


def fetch(repository, resource):
    request = urllib.request.Request("https://api.github.com/repos/" + repository + "/" + resource,
                                     headers={"Accept": "application/vnd.github+json",
                                              "User-Agent": "MathStart-R03-CI"})
    if os.environ.get("GITHUB_TOKEN"):
        request.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def validate_receipt(repository, number, pin, pr, approval):
    expected_url = f"https://github.com/{repository}/pull/{number}#pullrequestreview-{pin['approval_id']}"
    if (pr["number"] != number or pr["state"] != "closed" or pr["merged"] is not True
            or not pr["merged_at"] or pr["merged_by"]["login"] != pin["approver"]
            or pr["head"]["repo"]["full_name"] != repository
            or pr["base"]["repo"]["full_name"] != repository
            or pr["base"]["ref"] != "ms7-mig-react-fastapi"
            or pr["head"]["sha"] != pin["approved_head"]
            or pr["merge_commit_sha"] != pin["merge_sha"]
            or approval["id"] != pin["approval_id"] or approval["state"] != "APPROVED"
            or approval["commit_id"] != pin["approved_head"]
            or approval["user"]["login"] != pin["approver"]
            or approval["html_url"] != expected_url or not approval["submitted_at"]
            or approval["submitted_at"] > pr["merged_at"]):
        raise ValueError("Human approval/merged PR differs from pinned acceptance receipt")


def validate_tree(candidate, workflow, accepted):
    head = git(candidate, "rev-parse", "HEAD").decode().strip()
    tree = git(candidate, "rev-parse", "HEAD^{tree}").decode().strip()
    if (head != accepted["integration_sha"] or tree != accepted["integration_tree"]
            or git(candidate, "status", "--porcelain=v1", "--untracked-files=all")):
        raise ValueError("Actual integration checkout is stale, dirty or has a wrong tree")
    for ancestor in (MIG_BASE_SHA, HISTORICAL_INPUT, accepted["integration_sha"]):
        git(workflow, "merge-base", "--is-ancestor", ancestor, "HEAD")
    for pin in accepted["receipts"].values():
        parents = git(candidate, "show", "-s", "--format=%P", pin["merge_sha"]).decode().strip().split()
        if parents != [pin["merge_parent"]]:
            raise ValueError("Accepted squash merge parent differs from pinned integration chain")
        git(candidate, "merge-base", "--is-ancestor", pin["merge_sha"], head)
        for checkout in (candidate, workflow):
            for path in pin["preserved_paths"]:
                # R03 adds dated receipt records; existing owner evidence stays immutable.
                filters = ("--diff-filter=DMRTUXB",) if path.startswith("docs/acceptance/") else ()
                if git(checkout, "diff", *filters, pin["approved_head"], "HEAD", "--", path):
                    raise ValueError("Accepted implementation or historical owner evidence changed")
    # Every accepted file is immutable except the pre-reviewed R03 adapter boundary.
    from scripts.check_migration_preservation import verify
    return verify(workflow, input_sha=accepted["integration_sha"])


def intake(candidate, config):
    accepted = config["accepted_input"]
    preserved = validate_tree(candidate, ROOT, accepted)
    live_ref = fetch(accepted["repository"], "git/ref/heads/" + accepted["integration_branch"])
    if live_ref["object"]["sha"] != accepted["integration_sha"]:
        raise ValueError("Live integration advanced; explicit new input/receipts required")
    receipts = {}
    selected = None
    for number, pin in accepted["receipts"].items():
        pr = fetch(accepted["repository"], "pulls/" + number)
        approval = fetch(accepted["repository"], f"pulls/{number}/reviews/{pin['approval_id']}")
        validate_receipt(accepted["repository"], int(number), pin, pr, approval)
        receipts[number] = {"pin": pin, "pr": pr, "approval": approval,
                            "status": "ACCEPTED_INTEGRATION"}
        if int(number) == config["pr_number"]:
            selected = pr
    return selected, {"accepted_input": accepted, "live_integration_ref": live_ref,
                      "human_receipts": receipts, "preservation": preserved,
                      "actual_test_checkout_sha": tested_sha(config)}
