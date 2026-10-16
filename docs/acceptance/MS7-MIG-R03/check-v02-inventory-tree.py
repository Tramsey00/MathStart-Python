"""Check declared inventory tree against the pre-existing R03 pin, without writes to Git.

This is an inventory-only check, not blob verification or publication approval.
No candidate executable is loaded and no expected pin is regenerated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
BASE = "0c03197e23f69a233c0fcf8bdffa336feca20b92"
EXPECTED_TREE = "dbad1e853dff354c5d3255755afb5cc32e0ad279"
ATTRIBUTES = {
    "binary", "crlf", "diff", "encoding", "eol", "export-ignore",
    "export-subst", "filter", "ident", "merge", "text", "whitespace",
    "working-tree-encoding",
}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=30)


def tree_oid(entries: dict[str, tuple[str, str]]) -> str:
    """Encode Git SHA1 tree objects in Git's directory-aware byte ordering."""
    directory: dict = {}
    for path, value in entries.items():
        parts = path.split("/")
        current = directory
        for part in parts[:-1]:
            current = current.setdefault(part, {})
            if not isinstance(current, dict):
                raise ValueError("file/directory collision")
        if parts[-1] in current:
            raise ValueError("duplicate path or directory/file collision")
        current[parts[-1]] = value

    def encode(node: dict) -> str:
        ordered = sorted(node.items(), key=lambda item:
                         item[0].encode("utf-8") + (b"/" if isinstance(item[1], dict) else b""))
        payload = bytearray()
        for name, item in ordered:
            mode, oid = ("40000", encode(item)) if isinstance(item, dict) else item
            payload.extend(mode.encode("ascii") + b" " + name.encode("utf-8") + b"\0")
            payload.extend(bytes.fromhex(oid))
        return hashlib.sha1(b"tree " + str(len(payload)).encode("ascii") + b"\0" + payload).hexdigest()

    return encode(directory)


def check(raw: bytes) -> dict:
    inventory = json.loads(raw)
    if inventory["base_sha"] != BASE or inventory["file_count"] != 151:
        raise ValueError("wrong BASE/count")
    files = inventory["files"]
    if len(files) != 151 or len({f["path"] for f in files}) != 151:
        raise ValueError("wrong entries/duplicate paths")
    base_entries = {}
    for row in git("ls-tree", "-r", "-z", BASE).split(b"\0"):
        if not row:
            continue
        header, path = row.split(b"\t", 1)
        mode, kind, oid = header.decode("ascii").split()
        if kind != "blob":
            raise ValueError("unsupported BASE object type")
        base_entries[path.decode("utf-8")] = (mode, oid)
    measured_base_tree = tree_oid(base_entries)
    actual_base_tree = git("rev-parse", BASE + "^{tree}").decode("ascii").strip()
    if measured_base_tree != actual_base_tree:
        raise ValueError("tree encoder disagrees with Git on actual BASE")
    entries = base_entries.copy()
    raw_paths = []
    differing_working = []
    for entry in files:
        path = entry["path"]
        if (path in entries or path.startswith("/") or "\\" in path or
                any(p in {"", ".", ".."} for p in path.split("/")) or
                "\0" in path or path.split("/")[0].casefold() == ".git"):
            raise ValueError("not a safe new path")
        if entry["mode"] != "100644" or re.fullmatch(r"[0-9a-f]{40}", entry["blob_oid"]) is None:
            raise ValueError("unexpected declared mode/OID")
        for key in ["sha256", "working_sha256"]:
            if re.fullmatch(r"[0-9a-f]{64}", entry[key]) is None:
                raise ValueError("invalid declared SHA256")
        for key in ["size", "working_size"]:
            if type(entry[key]) is not int or entry[key] < 0:
                raise ValueError("invalid declared size")
        attrs = entry["attributes"]
        if set(attrs) != ATTRIBUTES or attrs["text"] not in {"auto", "unset"}:
            raise ValueError("unexpected declared attribute schema")
        if (attrs["eol"] != "lf" or
                any(v != "unspecified" for k, v in attrs.items() if k not in {"text", "eol"}) or
                entry["attributes_all"] != {"eol": "lf", "text": attrs["text"]}):
            raise ValueError("unexpected declared effective attributes")
        if attrs["text"] == "unset":
            raw_paths.append(path)
            if entry["sha256"] != entry["working_sha256"] or entry["size"] != entry["working_size"]:
                raise ValueError("declared raw working/blob drift")
        if entry["sha256"] != entry["working_sha256"]:
            differing_working.append(path)
            if attrs["text"] != "auto" or entry["working_vs_blob_reason"] != "CRLF_TO_LF_GIT_TEXT_AUTO_EOL_LF":
                raise ValueError("unexplained declared working/blob difference")
        entries[path] = (entry["mode"], entry["blob_oid"])
    if len(raw_paths) != 73 or len(differing_working) != 20:
        raise ValueError("wrong declared raw/working drift counts")
    observed = tree_oid(entries)
    if observed != EXPECTED_TREE:
        raise ValueError("declared inventory tree differs from existing approved R03 tree pin")
    return {
        "format": "r03-v02-inventory-tree-check-v1",
        "date": "2026-10-14", "verification_class": "INVENTORY_ONLY_NOT_BLOB_APPROVAL",
        "result": "PASS_DECLARED_TREE", "base_sha": BASE, "base_tree_oid": actual_base_tree,
        "base_path_count": len(base_entries), "addition_count": 151, "full_path_count": len(entries),
        "inventory_sha256": hashlib.sha256(raw).hexdigest(),
        "inventory_original_expected_tree_oid": inventory["expected_tree_oid"],
        "inventory_expected_typo_preserved": inventory["expected_tree_oid"] != EXPECTED_TREE,
        "approved_expected_tree_oid": EXPECTED_TREE, "recomputed_tree_oid": observed,
        "pin_authority": "Existing f73f2d5 intake and original auditor report, user correction 2026-10-14",
        "encoder_base_git_crosscheck": "PASS",
        "declared_raw_paths": sorted(raw_paths), "declared_working_blob_difference_paths": sorted(differing_working),
        "actual_blob_bytes_verified": False, "actual_effective_attributes_verified": False,
        "actual_archive_received": False, "publication_gate_status": "NOT_READY",
        "git_object_index_ref_writes": False, "candidate_pin_regeneration": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = check(args.inventory.read_bytes())
        payload = json.dumps(result, indent=2) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8", newline="\n") as out:
                out.write(payload)
        print(payload, end="")
        return 0
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as exc:
        print("FAIL inventory-only check: " + str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
