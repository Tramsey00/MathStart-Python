"""Verify SHA256 of exact published Git blob bytes, using only stdlib and Git.

Run from Windows or Linux: python docs/acceptance/MS7-MIG-V01/verify-publication-v1.py
--create is an explicit record creation operation; normal verification never writes.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AREA = Path(__file__).resolve().parent
IMPLEMENTATION = "1f97d762c4089efb2e4ef6d8c7ebe0bdcbe161f4"
INPUT = "8d958aeeb17da46839722441425ccbb5889e2ab7"
BASE = "60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7"
MANIFEST = AREA / "publication-manifest-v1.json"
COMPARISON = AREA / "publication-comparison-v1.json"
SCOPE = ["backend", "docs/acceptance/MS7-MIG-V01",
         "docs/exec-plans/active/MS7-MIG-V01.md", "docs/agent-traces/MS7-MIG-V01.md"]


def git(*args):
    # No text mode, shell, decoding, or newline transformation of blob content.
    return subprocess.check_output(["git", *args], cwd=ROOT)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def published_entries():
    result = []
    for row in git("ls-tree", "-r", "-z", IMPLEMENTATION, "--", *SCOPE).split(b"\0"):
        if not row:
            continue
        header, path = row.split(b"\t", 1)
        mode, kind, oid = header.decode("ascii").split()
        if kind != "blob":
            raise ValueError(f"Unexpected non-blob: {path!r}")
        data = git("cat-file", "blob", oid)
        result.append({"path": path.decode("utf-8"), "mode": mode,
                       "git_blob_oid": oid, "content_sha256": digest(data),
                       "size_bytes": len(data), "verification_status": "PASS"})
    return sorted(result, key=lambda f: f["path"])


def historical_comparison(entries):
    old_path = "docs/acceptance/MS7-MIG-V01/file-manifest-v4.json"
    old = json.loads(git("cat-file", "blob", IMPLEMENTATION + ":" + old_path))
    by_path = {e["path"]: e for e in entries}
    records = []
    for entry in old["files"]:
        current = by_path[entry["path"]]
        data = git("cat-file", "blob", current["git_blob_oid"])
        matches = entry["sha256"] == current["content_sha256"]
        crlf_only = not matches and digest(data.replace(b"\n", b"\r\n")) == entry["sha256"]
        records.append({"path": entry["path"], "historical_checkout_sha256": entry["sha256"],
                        "published_blob_sha256": current["content_sha256"],
                        "comparison_status": "PASS" if matches else "FAIL",
                        "explanation": "IDENTICAL_BYTES" if matches else
                        "LF_TO_CRLF_EXACT_MATCH" if crlf_only else "OTHER_DIFFERENCE"})
    return {"version": "publication-comparison-v1", "implementation_sha": IMPLEMENTATION,
            "historical_manifest": old_path, "historical_source_sha": old["source_sha"],
            "semantics": "Old digests retained; newline conversion diagnoses FAIL, never waives it.",
            "file_count": len(records), "pass_count": sum(r["comparison_status"] == "PASS" for r in records),
            "fail_count": sum(r["comparison_status"] == "FAIL" for r in records), "records": records}


def expected_manifest(entries):
    return {"version": "publication-manifest-v1", "implementation_sha": IMPLEMENTATION,
            "source_tree_sha": git("rev-parse", IMPLEMENTATION + "^{tree}").decode("ascii").strip(),
            "accepted_integration_input_sha": INPUT, "immutable_mig_base_sha": BASE,
            "content_digest_algorithm": "SHA256", "git_object_id_algorithm": "SHA1",
            "source": "git ls-tree -r -z then git cat-file blob <git_blob_oid>; binary subprocess output",
            "publication_scope": SCOPE, "file_count": len(entries),
            "line_ending_policy": "Hash exact Git object bytes without normalization. Published text uses LF under root .gitattributes; Windows checkout may use CRLF. Binary bytes remain exact.",
            "evidence_publication": {"status": "PENDING", "new_evidence_commit_sha": None,
                                     "post_evidence_pr_head_sha": None,
                                     "scope": "Only already published blobs at implementation_sha. This manifest and all new v5 evidence are local/uncommitted and excluded."},
            "files": entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--negative-controls", action="store_true")
    args = parser.parse_args()
    entries = published_entries()
    expected = expected_manifest(entries)
    comparison = historical_comparison(entries)
    if args.create:
        for path in [MANIFEST, COMPARISON]:
            if path.exists():
                raise FileExistsError(f"Refusing to overwrite versioned record: {path}")
        for path, value in [(MANIFEST, expected), (COMPARISON, comparison)]:
            path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    actual = json.loads(MANIFEST.read_bytes())
    actual_comparison = json.loads(COMPARISON.read_bytes())
    verify_records(actual, actual_comparison, expected, comparison)
    if args.negative_controls:
        import copy
        corruptions = []
        wrong_digest = copy.deepcopy(actual)
        wrong_digest["files"][0]["content_sha256"] = "0" * 64
        corruptions.append(("wrong digest", wrong_digest, actual_comparison))
        omitted = copy.deepcopy(actual)
        omitted["files"].pop()
        corruptions.append(("missing file", omitted, actual_comparison))
        wrong_oid = copy.deepcopy(actual)
        wrong_oid["files"][0]["git_blob_oid"] = "0" * 40
        corruptions.append(("wrong Git object ID", wrong_oid, actual_comparison))
        hidden_fail = copy.deepcopy(actual_comparison)
        next(r for r in hidden_fail["records"] if r["comparison_status"] == "FAIL")["comparison_status"] = "PASS"
        corruptions.append(("hidden historical FAIL", actual, hidden_fail))
        for name, manifest, old in corruptions:
            try:
                verify_records(manifest, old, expected, comparison)
            except ValueError:
                print(f"PASS negative control: rejected {name}")
            else:
                raise AssertionError(f"Verifier accepted corruption: {name}")
    print(f"PASS: {len(entries)} exact published Git blobs; historical comparison "
          f"{comparison['pass_count']} PASS / {comparison['fail_count']} FAIL")


def verify_records(actual, actual_comparison, expected, comparison):
    if actual != expected:
        raise ValueError("FAIL: manifest differs from exact Git tree/blob content or metadata")
    if actual_comparison != comparison:
        raise ValueError("FAIL: historical comparison differs; mismatches must remain visible")


if __name__ == "__main__":
    main()
