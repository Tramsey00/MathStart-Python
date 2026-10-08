"""Preserve accepted input outside exact R03 adapters; historical pins stay strict."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
INPUT = "8d958aeeb17da46839722441425ccbb5889e2ab7"
ADAPTED = frozenset({
    "scripts/verify_repo.py", "scripts/check_database.py", "scripts/version_report.py",
    "scripts/fresh_install_smoke.py", "harness/runner/verification.py",
    "tests/harness/test_verification.py", "tests/harness/test_canonical_verification.py",
    ".github/workflows/migration-ci.yml", "specs/harness/README.md",
    "skills/verification/SKILL.md",
})


def verify(root=ROOT):
    # Git object hashes are independent of the working tree, no historical rewrite.
    paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", INPUT], cwd=root).decode().splitlines()
    names = [name for name in paths if name not in ADAPTED]
    requests = "".join(INPUT + ":" + name + "\n" for name in names).encode()
    data = subprocess.run(["git", "cat-file", "--batch"], cwd=root, input=requests,
                          capture_output=True, check=True, timeout=60).stdout
    offset = 0
    for name in names:
        end = data.index(b"\n", offset)
        fields = data[offset:end].split()
        if len(fields) != 3 or fields[1] != b"blob":
            raise ValueError("accepted blob missing: " + name)
        size = int(fields[2]); expected = data[end + 1:end + 1 + size]
        if (root / name).read_bytes() != expected:
            raise ValueError("unowned/frozen accepted input changed: " + name)
        offset = end + size + 2
    for manifest, key in [("specs/api/candidate-manifest-v1.json", "artifacts"),
                          ("docs/acceptance/MS7-MIG-R02/contract-digests.json", "files")]:
        pins = json.loads((root / manifest).read_text(encoding="utf-8"))[key]
        for name, digest in pins.items():
            if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
                raise ValueError("historical pin differs: " + name)
    return {"accepted_input": INPUT, "preserved_files": len(names), "adapted_files": sorted(ADAPTED)}


if __name__ == "__main__":
    try:
        print(json.dumps(verify(), indent=2))
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print("FAIL: " + str(exc))
        raise SystemExit(1)
