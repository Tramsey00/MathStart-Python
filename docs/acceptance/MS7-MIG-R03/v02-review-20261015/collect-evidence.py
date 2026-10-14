"""Reconcile original GitHub artifacts and retain every raw byte, with source dedup."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT/'docs/acceptance/MS7-MIG-R03/v02-source-snapshot-20261014.zip'
SOURCE_SHA = '57cad8b19e75bda674ce1ac9ddcf9c92a6b57daa2a3b4bd1f39e528c1a77cd0a'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.write_bytes((json.dumps(value, indent=2, ensure_ascii=False)+'\n').encode('utf-8'))


def collect(original, digest, run, artifact, allow_missing=False):
    assert sha(original.read_bytes()) == digest, 'Original GitHub ZIP digest'
    source_bytes = SOURCE.read_bytes()
    assert sha(source_bytes) == SOURCE_SHA
    target = HERE/f'linux-{run}-raw.zip'
    duplicates, member_inventory, manifest_checks, missing = [], [], [], []
    commands = 0
    with zipfile.ZipFile(original) as z, zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as out:
        names = z.namelist()
        assert len(names) == len(set(names))
        for name in names:
            assert not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts
            if name.endswith('evidence-manifest.json'):
                rows = json.loads(z.read(name))
                base = name.rsplit('/', 1)[0]+'/' if '/' in name else ''
                for row in rows:
                    if base+row['path'] not in names:
                        assert allow_missing, 'Missing artifact member: '+base+row['path']
                        missing.append(dict(manifest=name, expected=row, actual='ABSENT_FROM_GITHUB_ARTIFACT'))
                        continue
                    raw = z.read(base+row['path'])
                    assert sha(raw) == row['sha256'] and len(raw) == row.get('size', row.get('bytes')), row['path']
                manifest_checks.append({'path': name, 'rows': len(rows), 'result': 'INCOMPLETE' if missing else 'PASS'})
            if name.endswith('/commands.json'):
                for row in json.loads(z.read(name)):
                    for stream in ('stdout', 'stderr'):
                        raw = z.read(name.rsplit('/', 1)[0]+'/'+row[stream+'_path'])
                        assert sha(raw) == row[stream+'_sha256']
                    commands += 1
        for name in names:
            raw = z.read(name)
            member_inventory.append({'path': name, 'size': len(raw), 'sha256': sha(raw)})
            if len(raw) == len(source_bytes) and sha(raw) == SOURCE_SHA:
                assert raw == source_bytes
                duplicates.append(dict(artifact_path=name, size=len(raw), sha256=SOURCE_SHA,
                                       exact_bytes_at_repository_path=SOURCE.relative_to(ROOT).as_posix()))
            else:
                out.writestr(name, raw)
            if name in ('published-result.json', 'task-result.json', 'phases.json', 'source-provenance.json',
                        'checkout-provenance.json', 'section17-current-overlay.json', 'runtime-no-django.json',
                        'content-parity.json', 'runtime-service.json'):
                (HERE/f'{run}-{name}').write_bytes(raw)
        out.writestr('duplicate-byte-map.json', json.dumps(duplicates, indent=2)+'\n')
    save(HERE/f'{run}-member-inventory.json', member_inventory)
    receipt = dict(run_id=run, artifact_id=artifact, original_zip_sha256=digest,
                   original_zip_bytes=original.stat().st_size, original_members=len(names),
                   original_url=f'https://github.com/Tramsey00/MathStart-Python/actions/runs/{run}/artifacts/{artifact}',
                   manifest_checks=manifest_checks, checked_command_receipts=commands,
                   retained_zip=target.name, retained_zip_sha256=sha(target.read_bytes()),
                   retained_zip_bytes=target.stat().st_size, deduplicated_members=duplicates,
                   all_downloaded_member_bytes_retained=True, missing_manifest_members=missing,
                   all_manifest_bytes_available=not missing, result='INCOMPLETE' if missing else 'PASS')
    save(HERE/f'{run}-artifact-reconciliation.json', receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k != 'missing_manifest_members'} | {'missing_manifest_member_count': len(missing)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('zip', type=Path)
    parser.add_argument('digest')
    parser.add_argument('run')
    parser.add_argument('artifact')
    parser.add_argument('--allow-missing-manifest-members', action='store_true', help='Historical incomplete evidence only; never PASS')
    args = parser.parse_args()
    collect(args.zip, args.digest, args.run, args.artifact, args.allow_missing_manifest_members)
