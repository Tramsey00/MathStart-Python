"""Read-only current workspace evidence check; never refreshes historical pins."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / 'docs/acceptance/MS7-MIG-V02'


def main():
    load = lambda name: json.loads((EVIDENCE / name).read_text(encoding='utf-8'))
    manifest = load('workspace-manifest.json')
    for path, record in manifest['files'].items():
        if sha256((ROOT / path).read_bytes()).hexdigest() != record['checkout_byte_sha256']:
            raise AssertionError('Workspace drift: ' + path)
    ownership = load('frozen-ownership.json')
    for record in ownership['checked_frozen_files']:
        blob = subprocess.check_output(['git', 'show', 'HEAD:' + record['path']], cwd=ROOT)
        if sha256(blob).hexdigest() != record['head_blob_sha256']:
            raise AssertionError('Frozen Git blob drift: ' + record['path'])
    tracked = subprocess.check_output(['git', 'diff', '--name-only'], cwd=ROOT).decode().splitlines()
    if tracked:
        raise AssertionError('Existing tracked files changed')
    files = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=ROOT).decode().splitlines()
    allowed = ('backend/content/', 'backend/staff/', 'backend/infrastructure/http/',
               'backend/tests/v02/', 'docs/acceptance/MS7-MIG-V02/')
    records = {'docs/agent-traces/MS7-MIG-V02.md', 'docs/exec-plans/active/MS7-MIG-V02.md'}
    if any(not path.startswith(allowed) and path not in records for path in files):
        raise AssertionError('New file outside V02 ownership')
    if set(files) != set(manifest['files']) | {'docs/acceptance/MS7-MIG-V02/workspace-manifest.json'}:
        raise AssertionError('New publication file set differs from workspace manifest')
    print(json.dumps({'workspace_hashes': len(manifest['files']), 'frozen_blobs': len(ownership['checked_frozen_files']),
        'ownership': 'PASS', 'publication': manifest['publication'], 'implementation_sha': manifest['tested_implementation_sha']}))


if __name__ == '__main__':
    main()
