"""Read-only index/worktree verification; reports full whitespace FAIL honestly."""
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
MANIFEST = 'docs/acceptance/MS7-MIG-V02/publication-byte-audit/publication-manifest.json'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def digest(raw):
    return sha256(raw).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def whitespace_check(args):
    result = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    groups = defaultdict(list)
    raw = result.stdout + result.stderr
    for path, number, reason in re.findall(rb'^([^\n]+):(\d+): ([^\n]+)\.\r?$', raw, re.MULTILINE):
        groups[path.decode()].append({'line': int(number), 'reason': reason.decode()})
    return {'argv': ['git', *args], 'exit_code': result.returncode,
            'diagnostic_sha256': digest(raw), 'findings_by_path': dict(groups),
            'findings_count': sum(len(items) for items in groups.values())}


def secret_scan(paths):
    patterns = {
        'private_key_block': rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
        'github_token': rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b',
        'aws_access_key': rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
        'slack_token': rb'\bxox[baprs]-[A-Za-z0-9-]{20,}\b',
        'openai_key': rb'\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b',
    }
    findings = []
    synthetic_urls = 0
    for path in paths:
        raw = git('show', ':' + path)
        for label, pattern in patterns.items():
            if re.search(pattern, raw):
                findings.append({'path': path, 'type': label})
        if Path(path).name == '.env' or Path(path).suffix.lower() in ('.pem', '.key', '.p12', '.pfx'):
            findings.append({'path': path, 'type': 'credential_file'})
        for password in re.findall(rb'[A-Za-z][A-Za-z0-9+.-]*://[^\s/:@]+:([^\s/@]+)@', raw):
            if password.startswith(b'synthetic-'):
                synthetic_urls += 1
            else:
                findings.append({'path': path, 'type': 'nonfixture_credential_url'})
    return {'scanned_staged_files': len(paths), 'method': 'staged-byte signatures, credential filenames and URL passwords',
            'findings': findings, 'synthetic_url_occurrences': synthetic_urls,
            'limit': 'Signature inspection is not a guarantee of detecting every secret; fixture credentials manually reviewed.'}


def verify_indexed_patch():
    prefix = 'docs/acceptance/MS7-MIG-V02/remediation-f01-f02/'
    target = 'backend/infrastructure/http/app.py'
    previous = git('show', ':' + prefix + 'history/initial/' + target)
    patch = git('show', ':' + prefix + 'F02-runtime.patch')
    expected = git('show', ':' + target)
    with tempfile.TemporaryDirectory(prefix='v02-publication-apply-', dir=ROOT / 'var') as directory:
        scratch = Path(directory).resolve()
        assert scratch.is_relative_to((ROOT / 'var').resolve())
        source = scratch / target
        source.parent.mkdir(parents=True)
        source.write_bytes(previous)
        patch_file = scratch / 'F02-runtime.patch'
        patch_file.write_bytes(patch)
        for options in (['--check'], []):
            result = subprocess.run(['git', 'apply', '-p1', *options, str(patch_file)],
                                    cwd=scratch, capture_output=True)
            assert result.returncode == 0, result.stderr.decode(errors='replace')
        assert source.read_bytes() == expected, 'Strict indexed patch output mismatch'
    return 'PASS: strict git apply --check/apply; exact indexed backend bytes; owned temporary scratch only'


def main():
    manifest = load(HERE / 'publication-manifest.json')
    evidence = load(HERE / 'publication-evidence.json')
    base = manifest['input_sha']
    assert git('rev-parse', 'HEAD').decode().strip() == base
    assert git('branch', '--show-current').decode().strip() == 'ms7-mig-v02-content'
    assert git('merge-base', 'HEAD', 'origin/ms7-mig-react-fastapi').decode().strip() == base
    assert not git('diff', '--name-only'), 'Unstaged drift'
    assert not git('diff', '--cached', '--diff-filter=MDRTCU', '--name-only'), 'Existing baseline changed'
    paths = git('diff', '--cached', '--name-only', '-z').decode().split('\0')[:-1]
    assert set(paths) == set(manifest['files']) | {MANIFEST}
    assert len(paths) == manifest['staged_file_count']
    assert (ROOT / MANIFEST).read_bytes() == git('show', ':' + MANIFEST), 'Manifest self working/index mismatch'
    for path, record in manifest['files'].items():
        work = (ROOT / path).read_bytes()
        blob = git('show', ':' + path)
        assert digest(work) == record['working_byte_sha256'], path
        assert digest(blob) == record['index_blob_byte_sha256'], path
        if record['byte_policy'] == 'EXACT_RAW':
            assert work == blob, path
        else:
            assert work.replace(b'\r\n', b'\n') == blob, path
    old = load(ROOT / 'docs/acceptance/MS7-MIG-V02/workspace-manifest.json')
    assert digest((ROOT / 'docs/acceptance/MS7-MIG-V02/workspace-manifest.json').read_bytes()) == evidence['input_workspace_manifest_sha256']
    changed = {path for path, record in old['files'].items()
               if digest((ROOT / path).read_bytes()) != record['checkout_byte_sha256']}
    assert changed == {'docs/acceptance/MS7-MIG-V02/remediation-f01-f02/F02-runtime.patch'}, changed
    for path, record in evidence['index_before'].items():
        if path.startswith('backend/'):
            assert digest((ROOT / path).read_bytes()) == record['work_sha256'], path
            assert digest(git('show', ':' + path)) == record['index_blob_sha256'], path
    archive = ROOT / 'docs/acceptance/MS7-MIG-V02/remediation-f01-f02'
    snapshot = load(archive / 'original-audit/independent-source-snapshot.json')
    for path, record in snapshot['files'].items():
        absolute = archive / 'history/initial' / path
        relative = absolute.relative_to(ROOT).as_posix()
        assert digest(absolute.read_bytes()) == record['sha256'], path
        assert digest(git('show', ':' + relative)) == record['sha256'], path
    for name, record in load(archive / 'intake.json')['auditor_report_and_snapshot'].items():
        relative = (archive / 'original-audit' / name).relative_to(ROOT).as_posix()
        assert digest((ROOT / relative).read_bytes()) == record['sha256']
        assert digest(git('show', ':' + relative)) == record['sha256']
    frozen = load(ROOT / 'docs/acceptance/MS7-MIG-V02/frozen-ownership.json')['checked_frozen_files']
    for record in frozen:
        path = record['path']
        assert digest(git('show', base + ':' + path)) == record['input_blob_sha256']
        assert digest(git('show', 'HEAD:' + path)) == record['head_blob_sha256']
        assert digest(git('show', ':' + path)) == record['head_blob_sha256']
        assert digest((ROOT / path).read_bytes()) == record['checkout_sha256']
    exemptions = evidence['exact_evidence_allowlist']
    for record in exemptions:
        path = record['path']
        assert digest(git('show', ':' + path)) == record['required_blob_and_work_sha256']
    excludes = [':(exclude,literal)' + record['path'] for record in exemptions]
    checks = {
        'ordinary': whitespace_check(['diff', '--cached', '--check']),
        'cr-at-eol': whitespace_check(['-c', 'core.whitespace=cr-at-eol', 'diff', '--cached', '--check']),
        'scoped-ordinary': whitespace_check(['diff', '--cached', '--check', '--', '.', *excludes]),
        'scoped-cr-at-eol': whitespace_check(['-c', 'core.whitespace=cr-at-eol', 'diff', '--cached', '--check', '--', '.', *excludes]),
    }
    for name, check in checks.items():
        expected = evidence['final_checks'][name]
        assert check['exit_code'] == expected['exit_code'], name
        assert check['findings_by_path'] == expected['findings_by_path'], name
        assert check['diagnostic_sha256'] == expected['diagnostic_sha256'], name
    secrets = secret_scan(paths)
    assert not secrets['findings'], secrets['findings']
    patch_result = verify_indexed_patch()
    print(json.dumps({'staged_files': len(paths), 'bound_files_excluding_manifest': len(manifest['files']),
        'full_whitespace_checks': {name:checks[name]['exit_code'] for name in ('ordinary','cr-at-eol')},
        'scoped_whitespace_checks': {name:checks[name]['exit_code'] for name in ('scoped-ordinary','scoped-cr-at-eol')},
        'backend_unchanged': True, 'frozen_unchanged':len(frozen), 'initial_archive_exact_blobs':len(snapshot['files']),
        'audit_copies_exact_blobs': True, 'secrets':secrets, 'indexed_patch_application':patch_result,
        'status':'LOCAL_PUBLICATION_POLICY_CONFORMANCE; FULL_WHITESPACE_FAIL; SCOPED_EVIDENCE_REAUDIT_PENDING',
        'tested_implementation_sha':None,'publication':'PENDING_PUBLICATION'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
