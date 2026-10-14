"""Verify downloaded CI artifacts and retain raw bytes with one content dedup."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT/'docs/acceptance/MS7-MIG-R03/v02-source-snapshot-20261014.zip'
SOURCE_SHA = '57cad8b19e75bda674ce1ac9ddcf9c92a6b57daa2a3b4bd1f39e528c1a77cd0a'
RUNS = {
    '38596554853': ('65dd589ed259ec85ee6879f7434fef7a9d85913d62f62b0b7efbcc429519611b', '11910915146'),
    '38596739924': ('f52fcb18f4a4ecd4343fcf2efe363c23ec7f856b2995f4666b3fdd3717ca3de2', '11909044256'),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def collect(run, digest, artifact):
    original = ROOT/f'var/r03-v02-publication-{run}-1.zip'
    assert sha(original.read_bytes()) == digest
    assert sha(SOURCE.read_bytes()) == SOURCE_SHA
    target = HERE/f'linux-{run}-raw.zip'
    duplicates = []
    with zipfile.ZipFile(original) as source, zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as compact:
        names = source.namelist()
        assert len(names) == len(set(names))
        prefix = 'v02-publication-linux/'
        manifest = json.loads(source.read(prefix+'evidence-manifest.json'))
        for row in manifest:
            raw = source.read(prefix+row['path'])
            assert sha(raw) == row['sha256'] and len(raw) == row['size'], row['path']
        commands = 0
        for name in names:
            if name.endswith('/commands.json'):
                for row in json.loads(source.read(name)):
                    for stream in ('stdout', 'stderr'):
                        raw = source.read(name.rsplit('/', 1)[0]+'/'+row[stream+'_path'])
                        assert sha(raw) == row[stream+'_sha256']
                    assert row['expected_exit'] is None or row['exit_code'] == row['expected_exit']
                    commands += 1
        result = json.loads(source.read(prefix+'result.json'))
        negative = json.loads(source.read(prefix+'negative-results.json'))
        snapshot = json.loads(source.read(prefix+'restored/snapshot-verification.json'))
        provenance = json.loads(source.read('v02-publication-provenance/workflow.json'))
        assert result['result'] == result['post_negative_positive'] == 'PASS'
        assert result['implementation_sha'] is None and result['ref_kind'] == 'tree'
        assert len(negative) == result['negative_cases'] == 17
        assert all(row['result'] == 'PASS_EXPECTED_REJECTION' for row in negative)
        assert snapshot['base_entries'] == 1672 and snapshot['additions'] == 151 and snapshot['total_entries'] == 1823
        assert snapshot['tree'] == 'dbad1e853dff354c5d3255755afb5cc32e0ad279'
        assert provenance['actual_owner_checkout_sha'] == result['owner_control_revision']
        for name in names:
            raw = source.read(name)
            if len(raw) == SOURCE.stat().st_size and sha(raw) == SOURCE_SHA:
                assert raw == SOURCE.read_bytes()
                duplicates.append(dict(artifact_path=name, size=len(raw), sha256=SOURCE_SHA,
                                       exact_bytes_at_repository_path=SOURCE.relative_to(ROOT).as_posix()))
            else:
                compact.writestr(name, raw)
        compact.writestr('duplicate-byte-map.json', json.dumps(duplicates, indent=2)+'\n')
        summary = json.loads(json.dumps(result))
        for value in summary['verifier'].values():
            if isinstance(value, dict) and 'by_path' in value:
                value['by_path_raw_location'] = prefix+'result.json (inside retained raw ZIP)'
                del value['by_path']
        for short, data in [('result', summary), ('negative-results', negative), ('snapshot-verification', snapshot), ('provenance', provenance)]:
            (HERE/f'{run}-{short}.json').write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    receipt = dict(run_id=run, artifact_id=artifact, original_zip_sha256=digest,
                   original_zip_bytes=original.stat().st_size, original_members=len(names),
                   original_url=f'https://github.com/Tramsey00/MathStart-Python/actions/runs/{run}/artifacts/{artifact}',
                   checked_evidence_manifest_rows=len(manifest), checked_command_receipts=commands,
                   retained_zip=target.name, retained_zip_sha256=sha(target.read_bytes()),
                   retained_zip_bytes=target.stat().st_size, deduplicated_members=duplicates,
                   all_original_bytes_retained=True, result='PASS')
    (HERE/f'{run}-artifact-reconciliation.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    for run, (digest, artifact) in RUNS.items():
        collect(run, digest, artifact)
