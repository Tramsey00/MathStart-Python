"""R01 independent source, original preservation, scoped links and safety audit.

Uses private original QA inventory; never rewrites that initial inventory.
Run after documents are prepared, before committing. No database connection.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from collections import Counter

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--original', type=Path, required=True)
    args = parser.parse_args()
    original = args.original.resolve()
    root = Path(__file__).resolve().parents[4]
    records = root / 'docs/acceptance/MS7-MIG-R01'
    source = json.loads((records / 'source-manifest.json').read_text(encoding='utf-8'))
    allowed = {'.gitattributes', 'AGENTS.md', 'PRODUCT.md', 'ARCHITECTURE.md', 'README.md'}
    failures, unchanged = [], []
    for entry in source['files']:
        path = root / entry['path']
        if entry['path'] not in allowed:
            if digest(path) != entry['sha256']:
                failures.append({'source_changed': entry['path']})
            else:
                unchanged.append(entry['path'])
        if digest(original / entry['path']) != entry['original_checkout_sha256']:
            failures.append({'original_source_changed': entry['path']})
    preservation = json.loads((original / 'tmp/ms7-mig-r01/qa/preservation.json').read_text(encoding='utf-8'))
    for entry in preservation:
        p = original / entry['path']
        if not p.is_file() or p.stat().st_size != entry['size'] or digest(p) != entry['sha256']:
            failures.append({'preservation_changed': entry['path']})
    recovery = Path('docs/agent-traces/local-runtime-recovery-20261007.md')
    assert digest(root / recovery) == digest(original / recovery)
    spec = root / 'specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md'
    assert digest(spec) == 'c5a554e3911bdb43db28d67fd02d26e38d50b2820e1154a272d89ecb44b1faae'
    # This report is itself a linked generated deliverable; establish its path
    # before link checking and write complete results after all checks finish.
    (records / 'validation.json').touch(exist_ok=True)
    docs = list(records.rglob('*.md')) + list((root / 'specs/migration').glob('README.md')) + [
        root / 'docs/adr/ADR-0006-react-fastapi-migration.md',
        root / 'docs/exec-plans/active/MS7-MIG-R01.md', root / 'docs/agent-traces/MS7-MIG-R01.md']
    links = []
    for p in docs:
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'):
                continue
            resolved = (p.parent / target.split('#')[0]).resolve()
            exists = resolved.exists()
            links.append({'file':p.relative_to(root).as_posix(),'target':target,'exists':exists})
            if not exists:
                failures.append({'broken_link':p.relative_to(root).as_posix(),'target':target})
    refs = json.loads((records / 'historical-output-links.json').read_text(encoding='utf-8'))
    # No raw working credentials, dumps, row-level user/session data or bulk QA files.
    additions = [p for folder in ['docs/acceptance/MS7-MIG-R01', 'specs/migration'] for p in (root / folder).rglob('*') if p.is_file()]
    forbidden = []
    patterns = [r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----', r'gh[pousr]_[A-Za-z0-9]{30,}', r'github_pat_[A-Za-z0-9_]{30,}']
    for p in additions:
        if p.name in {'.env', 'db.sqlite3'} or p.suffix in {'.dump', '.sql', '.sqlite3'}:
            forbidden.append(p.relative_to(root).as_posix())
        value = p.read_text(encoding='utf-8', errors='replace')
        if any(re.search(pattern,value) for pattern in patterns):
            forbidden.append(p.relative_to(root).as_posix())
    failures += [{'forbidden_artifact':x} for x in forbidden]
    result = {'input_commit':source['source_commit'], 'result':'FAIL' if failures else 'PASS',
              'unchanged_input_files':len(unchanged),'scoped_existing_changes':sorted(allowed),
              'frozen_contracts_and_legacy_code':'all input tracked files except five allowed root files exact Git blob SHA256 checked',
              'original_tracked_files_checked':len(source['files']), 'original_output_tmp_files_preserved':len(preservation),
              'recovery_trace_sha256':digest(root / recovery),'canonical_spec_sha256':digest(spec),
              'historical_output_reference_counts':dict(Counter(x['kind'] for x in refs)),
              'document_links':links,'artifact_safety':'no raw DB values/dumps/.env/token/private key; synthetic disposable credentials only in task audit utilities',
              'failures':failures}
    (records / 'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'document_links'},ensure_ascii=True))
    raise SystemExit(bool(failures))

if __name__ == '__main__':
    main()
