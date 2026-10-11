"""Read-only consistency checks for V01 evidence remediation. stdlib + Git only."""
import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AREA = Path(__file__).resolve().parent
H = "1f97d762c4089efb2e4ef6d8c7ebe0bdcbe161f4"
I = "8d958aeeb17da46839722441425ccbb5889e2ab7"
B = "60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7"


def require(condition, message):
    if not condition:
        raise ValueError("FAIL: " + message)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def read(name):
    return json.loads((AREA / name).read_bytes())


def check_references(value):
    if isinstance(value, str) and value.startswith(("docs/", "backend/", "specs/")):
        require((ROOT / value).is_file(), "missing evidence reference " + value)
    elif isinstance(value, dict):
        for item in value.values():
            check_references(item)
    elif isinstance(value, list):
        for item in value:
            check_references(item)


def main():
    require(git("rev-parse", H).decode().strip() == H, "implementation commit unavailable")
    index = read("old-to-new-evidence-v4.json")
    historical = json.loads(git("cat-file", "blob", H + ":docs/acceptance/MS7-MIG-V01/old-to-new-evidence-v3.json"))
    require(index["implementation_sha"] == H and index["accepted_integration_input_sha"] == I
            and index["immutable_mig_base_sha"] == B, "implementation/input/base identity")
    require(index["source_tree_sha"] == git("rev-parse", H + "^{tree}").decode().strip(), "tree identity")
    require(index["current_status"] == "INCOMPLETE", "task must remain INCOMPLETE")
    require([r["original_result"] for r in index["records"]] == [r["original_result"] for r in historical["records"]], "historical results/approvals changed")
    for row in index["records"]:
        require(all(k in row for k in ["original_result", "platform_disposition", "migration_follow_up", "target_evidence", "current_status"]), "section 17 fields")
        require(row["current_status"] in ["INCOMPLETE", "NOT_VERIFIED"], "unapproved task status")
        require(row["migration_follow_up"]["implementation_sha"] == H, "record implementation identity")
        require(row["target_evidence"]["target_postgres_ci_status"] == "PENDING" and row["target_evidence"]["human_task_approval"] == "PENDING", "pending gates changed")
    check_references(index)
    ci = read("github-ci-observation-v5.json")
    require(ci["run"]["head_sha"] == H == ci["job"]["head_sha"] == ci["pr_head_sha"], "CI exact PR head")
    require(ci["run"]["conclusion"] == "success" and ci["job"]["conclusion"] == "success", "legacy CI observation")
    require(ci["target_ci"]["status"] == "PENDING" and not ci["scope"]["target_sqlalchemy_alembic_suite"], "legacy CI misrepresented as target")
    frozen = json.loads(git("cat-file", "blob", I + ":docs/acceptance/MS7-MIG-R02/contract-digests.json"))
    for path, expected in frozen["files"].items():
        data = git("cat-file", "blob", H + ":" + path)
        require(hashlib.sha256(data).hexdigest() == expected, "frozen R02 digest " + path)
        require(data == git("cat-file", "blob", I + ":" + path), "frozen input changed " + path)
    require(not git("diff", I, H, "--", "docs/acceptance/MS7-MIG-R02", "specs/migration/r02-v1", "content/migrations", "users/migrations"), "frozen/history publication changed")
    provenance = read("independent-review-provenance-v5.json")
    audit = provenance["positive_f1_f2_f3_reaudit"]
    for artifact in audit["artifacts"]:
        data = (ROOT / artifact["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == artifact["sha256"] and len(data) == artifact["size_bytes"], "immutable audit copy " + artifact["path"])
    require((AREA / "independent-reviews-v5/final-f1-f2-f3/.gitattributes").read_bytes() == b"* -text whitespace=cr-at-eol\n", "archived bytes need explicit preservation policy")
    require(audit["checked_head"] == I and audit["untracked_files"] == 71, "reaudit checked scope")
    check_references(provenance)
    expected_cases = read("target-ci-cases-v5.json")
    ids = []
    for module in ["test_unit", "test_postgres", "test_remediation"]:
        tree = ast.parse(git("cat-file", "blob", H + ":backend/tests/" + module + ".py"))
        for cls in tree.body:
            if isinstance(cls, ast.ClassDef):
                ids.extend(f"backend.tests.{module}.{cls.name}.{m.name}" for m in cls.body if isinstance(m, ast.FunctionDef) and m.name.startswith("test_"))
    require(ids == [c["id"] for c in expected_cases["cases"]] and len(ids) == 34, "target explicit case list")
    require(sum(c["environment"] == "PostgreSQL" for c in expected_cases["cases"]) == 23, "PG case count")
    # Resolve relative links in newly authored proposals; historical immutable reports retain their original local links.
    for name in ["r03-ci-handoff-v5.md", "pr-description-proposed-v5.md", "owner-review-evidence-remediation-report-v5.md"]:
        path = AREA / name
        if not path.exists():
            raise ValueError("FAIL: missing new report " + name)
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            repository_link = re.match(r"https://github.com/Tramsey00/MathStart-Python/blob/([^/]+)/(.+)", target)
            if repository_link:
                ref, linked_path = repository_link.groups()
                require((ROOT / linked_path).is_file(), "missing PR evidence link " + linked_path)
                if ref == H:
                    git("cat-file", "-e", H + ":" + linked_path)
                else:
                    require(ref == "ms7-mig-v01-schema", "unexpected future PR evidence reference")
            elif not target.startswith(("https://", "http://")):
                require((path.parent / target.split("#")[0]).is_file(), "broken proposal link " + target)
    print(f"PASS: section 17 (4 histories), links, CI scope, {len(frozen['files'])} frozen digests, 6 immutable audit artifacts, target 34/23 case list")


if __name__ == "__main__":
    main()
