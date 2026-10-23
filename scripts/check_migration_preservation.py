"""Check actual current inputs, explicit platform dispositions and historical pins."""
from __future__ import annotations

import hashlib
from functools import lru_cache
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
INPUT = "8d958aeeb17da46839722441425ccbb5889e2ab7"
SOURCE = "1a87b044e8c5a7519b0ab57e22d2a35d57b4a986"
MAINTENANCE_SOURCE = "3a290a46d991e22269a17dde41e39f0637576071"
DISPOSITIONS = "specs/migration/post-django-preservation.json"
WORKFLOW_SOURCE = "1a015f7513933901e8bb252e94c660e4383b6b0e"
WORKFLOW_DISPOSITIONS = "specs/maintenance/docs-workflow-dispositions.json"
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
        if row.get('source_sha', SOURCE) not in {SOURCE, MAINTENANCE_SOURCE}:
            raise ValueError('Unreviewed historical source')
    return {row['path']: row for row in rows}


@lru_cache(maxsize=4096)
def _historical_blob(root, sha, name):
    return subprocess.check_output(['git', 'show', sha + ':' + name], cwd=root)


@lru_cache(maxsize=8)
def _historical_batch(root, requests):
    data = subprocess.run(['git', 'cat-file', '--batch'], cwd=root,
                          input=''.join(sha + ':' + name + '\n' for sha, name in requests).encode(),
                          capture_output=True, check=True, timeout=60).stdout
    offset = 0
    result = {}
    for key in requests:
        end = data.index(b'\n', offset)
        fields = data[offset:end].split()
        if len(fields) != 3 or fields[1] != b'blob':
            raise ValueError('Historical blob missing: ' + key[1])
        size = int(fields[2])
        result[key] = data[end + 1:end + 1 + size]
        offset = end + size + 2
    return result


def historical_artifact(name, root=ROOT):
    """Original manifest digests stay original; changed current files are pinned too.

    Only explicit dispositions use historical bytes. All retained contracts and
    content are always read from the actual current tree.
    """
    from scripts.repository_history import repository_changes, retired_document, task_changes, TASK_SOURCE
    if name in task_changes(root):
        return _historical_blob(str(root), TASK_SOURCE, name)
    current_retirement = repository_changes(root).get(name)
    if current_retirement and current_retirement['action'] == 'removed':
        return retired_document(name, root)
    row = dispositions(root).get(name)
    if row is None:
        if current_retirement and current_retirement['action'] == 'updated' and name.endswith('.md'):
            # Historical digest consumers retain original documentation bytes.
            # The translated working document is independently pinned/checked above.
            from scripts.repository_history import SOURCE as documentation_source
            return _historical_blob(str(root), documentation_source, name)
        return (root / name).read_bytes()
    raw = _historical_blob(str(root), row.get('source_sha', SOURCE), name)
    if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
        raise ValueError('Historical provenance differs: ' + name)
    return raw


def workflow_changes(root=ROOT):
    """Explicit per-file current-task changes; original baseline pins stay intact.

    Only the fixed audited source SHA is allowed. Before bytes are checked from
    Git and every current file must match its reviewed after hash. No prefix or
    wildcard exemption can permit an unknown deletion/change.
    """
    from scripts.repository_history import repository_changes
    followup = repository_changes(root)
    from scripts.repository_history import task_changes
    followup = {**task_changes(root), **followup}
    data = json.loads((root / WORKFLOW_DISPOSITIONS).read_text(encoding='utf-8'))
    if data['base_sha'] != WORKFLOW_SOURCE or not data.get('authority'):
        raise ValueError('Unexpected workflow preservation authority')
    rows = data['files']
    if len({r['path'] for r in rows}) != len(rows):
        raise ValueError('Duplicate workflow disposition')
    original = _historical_batch(str(root), tuple((WORKFLOW_SOURCE, row['path']) for row in rows))
    for row in rows:
        name = row['path']
        target = root / name
        if Path(name).is_absolute() or '..' in Path(name).parts or not target.resolve().is_relative_to(root.resolve()):
            raise ValueError('Workflow disposition path escaped')
        before = original[(WORKFLOW_SOURCE, name)]
        if len(before) != row['before_bytes'] or hashlib.sha256(before).hexdigest() != row['before_sha256']:
            raise ValueError('Workflow original bytes changed: ' + name)
        if not row.get('reason'):
            raise ValueError('Workflow disposition has no reason')
        if name in followup:
            # Both historical before bytes and the explicit new candidate are checked.
            if row['action'] == 'updated' and followup[name]['before_sha256'] != row['after_sha256']:
                raise ValueError('Repository cleanup chain differs: ' + name)
            continue
        if row['action'] == 'removed':
            if not name.startswith(('harness/', 'specs/harness/', 'tests/harness/')):
                raise ValueError('Removal outside explicitly retired subsystem: ' + name)
            if target.exists() or target.is_symlink():
                raise ValueError('Retired workflow source reintroduced: ' + name)
        elif row['action'] == 'updated':
            if target.is_symlink() or not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != row['after_sha256']:
                raise ValueError('Unreviewed workflow change: ' + name)
        else:
            raise ValueError('Unknown workflow disposition action')
    result = {r['path']: r for r in rows}
    for name, row in followup.items():
        if name in result and result[name]['action'] == 'updated':
            # Retain the first before pin for moved-source provenance checks.
            result[name] = dict(result[name], action=row['action'], after_sha256=row.get('after_sha256'))
        else:
            result[name] = row
    return result


def verify(root=ROOT, input_sha=INPUT):
    # Git object hashes are independent of the working tree, no historical rewrite.
    paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", input_sha], cwd=root).decode().splitlines()
    changes = dispositions(root)
    workflow = workflow_changes(root)
    original = _historical_batch(str(root), tuple((row.get('source_sha', SOURCE), name)
                                                  for name, row in changes.items()))
    for name, row in changes.items():
        raw = original[(row.get('source_sha', SOURCE), name)]
        if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('Historical provenance differs: ' + name)
        current = root / name
        if name in workflow:
            # Original source/pins above still verified; current bytes are bound
            # separately to this user's explicit docs/Harness retirement scope.
            continue
        action = row['action']
        if action in {'removed', 'moved', 'moved_updated'}:
            if current.exists() or current.is_symlink():
                raise ValueError('Retired source reintroduced: ' + name)
            if action in {'moved', 'moved_updated'}:
                destination = root / row['destination']
                if not destination.resolve().is_relative_to(root.resolve()):
                    raise ValueError('Move escaped repository')
                expected = row['sha256'] if action == 'moved' else row['current_sha256']
                followup = workflow.get(row['destination'])
                if followup is not None and followup['action'] in {'updated', 'removed'}:
                    # The move itself remains immutable. A later explicit task
                    # may change its destination only from the exact moved bytes.
                    if followup['before_sha256'] != expected:
                        raise ValueError('Moved workflow input differs: ' + name)
                elif hashlib.sha256(destination.read_bytes()).hexdigest() != expected:
                    raise ValueError('Moved shared behavior source changed: ' + name)
        elif action == 'updated':
            if hashlib.sha256(current.read_bytes()).hexdigest() != row['current_sha256']:
                raise ValueError('Unreviewed platform adapter change: ' + name)
        else:
            raise ValueError('Unknown preservation disposition')
    names = [name for name in paths if name not in ADAPTED and name not in changes and name not in workflow]
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
        pins = json.loads(historical_artifact(manifest, root))[key]
        for name, digest in pins.items():
            if hashlib.sha256(historical_artifact(name, root)).hexdigest() != digest:
                raise ValueError("historical pin differs: " + name)
    return {"accepted_input": input_sha, "preserved_files": len(names),
            "explicit_dispositions": len(changes), "source_sha": SOURCE,
            "adapted_files": sorted(ADAPTED),
            "baseline_dispositions": len(set(paths).intersection(set(changes) | set(workflow)) - ADAPTED),
            "workflow_source": WORKFLOW_SOURCE, "workflow_dispositions": len(workflow)}


if __name__ == "__main__":
    try:
        print(json.dumps(verify(), indent=2))
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print("FAIL: " + str(exc))
        raise SystemExit(1)
