"""Check actual current inputs, explicit platform dispositions and historical pins."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
INPUT = "8d958aeeb17da46839722441425ccbb5889e2ab7"
SOURCE = "1a87b044e8c5a7519b0ab57e22d2a35d57b4a986"
DISPOSITIONS = "specs/migration/post-django-preservation.json"
ADAPTED = frozenset({
    "scripts/verify_repo.py", "scripts/check_database.py", "scripts/version_report.py",
    "scripts/fresh_install_smoke.py", "harness/runner/verification.py",
    "tests/harness/test_verification.py", "tests/harness/test_canonical_verification.py",
    ".github/workflows/migration-ci.yml", "specs/harness/README.md",
    "skills/verification/SKILL.md",
})


def dispositions(root=ROOT):
    data = json.loads((root / DISPOSITIONS).read_text(encoding="utf-8"))
    if data['source_sha'] != SOURCE or data['accepted_input'] != INPUT:
        raise ValueError('Unexpected preservation provenance')
    rows = data['files']
    if len({row['path'] for row in rows}) != len(rows):
        raise ValueError('Duplicate preservation disposition')
    for row in rows:
        path = row['path']
        if not path or Path(path).is_absolute() or '..' in Path(path).parts:
            raise ValueError('Invalid preservation path')
    return {row['path']: row for row in rows}


def historical_artifact(name, root=ROOT):
    """Original manifest digests stay original; changed current files are pinned too.

    Only explicit dispositions use historical bytes. All retained contracts and
    content are always read from the actual current tree.
    """
    row = dispositions(root).get(name)
    if row is None:
        return (root / name).read_bytes()
    raw = subprocess.check_output(['git', 'show', SOURCE + ':' + name], cwd=root)
    if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
        raise ValueError('Historical provenance differs: ' + name)
    return raw


def verify(root=ROOT, input_sha=INPUT):
    # Git object hashes are independent of the working tree, no historical rewrite.
    paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", input_sha], cwd=root).decode().splitlines()
    changes = dispositions(root)
    for name, row in changes.items():
        historical_artifact(name, root)
        current = root / name
        action = row['action']
        if action in {'removed', 'moved'}:
            if current.exists() or current.is_symlink():
                raise ValueError('Retired source reintroduced: ' + name)
            if action == 'moved':
                destination = root / row['destination']
                if not destination.resolve().is_relative_to(root.resolve()):
                    raise ValueError('Move escaped repository')
                if hashlib.sha256(destination.read_bytes()).hexdigest() != row['sha256']:
                    raise ValueError('Moved shared behavior source changed: ' + name)
        elif action == 'updated':
            if hashlib.sha256(current.read_bytes()).hexdigest() != row['current_sha256']:
                raise ValueError('Unreviewed platform adapter change: ' + name)
        else:
            raise ValueError('Unknown preservation disposition')
    names = [name for name in paths if name not in ADAPTED and name not in changes]
    requests = "".join(input_sha + ":" + name + "\n" for name in names).encode()
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
            if hashlib.sha256(historical_artifact(name, root)).hexdigest() != digest:
                raise ValueError("historical pin differs: " + name)
    return {"accepted_input": input_sha, "preserved_files": len(names),
            "explicit_dispositions": len(changes), "source_sha": SOURCE,
            "adapted_files": sorted(ADAPTED),
            "baseline_dispositions": len(set(paths).intersection(changes) - ADAPTED)}


if __name__ == "__main__":
    try:
        print(json.dumps(verify(), indent=2))
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print("FAIL: " + str(exc))
        raise SystemExit(1)
