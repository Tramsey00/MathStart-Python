"""Read-only historical V02 intake audit, requiring its separate original workspace."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.historical_sources import retired_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    workspace = parser.parse_args().workspace.resolve()
    if workspace == ROOT:
        raise ValueError('Historical audit cannot establish current target readiness')
    load = lambda name: retired_json('docs/acceptance/MS7-MIG-V02/' + name)
    manifest = load('workspace-manifest.json')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=workspace).decode().strip()
    if head != manifest['input_sha']:
        raise ValueError('Historical intake workspace must use its exact original input SHA')
    for path, record in manifest['files'].items():
        if sha256((workspace / path).read_bytes()).hexdigest() != record['checkout_byte_sha256']:
            raise AssertionError('Workspace drift: ' + path)
    ownership = load('frozen-ownership.json')
    for record in ownership['checked_frozen_files']:
        blob = subprocess.check_output(['git', 'show', 'HEAD:' + record['path']], cwd=workspace)
        if sha256(blob).hexdigest() != record['head_blob_sha256']:
            raise AssertionError('Frozen Git blob drift: ' + record['path'])
    tracked = subprocess.check_output(['git', 'diff', '--name-only'], cwd=workspace).decode().splitlines()
    if tracked:
        raise AssertionError('Existing tracked files changed')
    files = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=workspace).decode().splitlines()
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
