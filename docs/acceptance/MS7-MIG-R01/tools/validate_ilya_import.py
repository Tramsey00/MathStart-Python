"""Read-only evidence checks; no DB access, package execution or source repair.

Run from candidate: python docs/acceptance/MS7-MIG-R01/tools/validate_ilya_import.py
--ref INDEX (after staging), or --ref HEAD. Report excludes its own digest.
Optional --archive verifies the externally supplied original ZIP as well.
"""
import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

PRIOR = '43b4fa10aec2af589c51857d037e973215557255'
INPUT = '8c11edadc8debc81432d1db1145feac504f09061'
PREFIX = 'docs/acceptance/MS7-MIG-R01/ilya-20261007'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ref', default='INDEX')
    parser.add_argument('--archive', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[4]
    records = root / 'docs/acceptance/MS7-MIG-R01'
    folder = root / PREFIX
    package = folder / 'package'
    def git(*argv):
        return subprocess.check_output(['git', '-C', str(root), *argv])
    def blob(name, ref=args.ref):
        return git('show', (':' if ref == 'INDEX' else ref + ':') + name)
    def sha(b):
        return hashlib.sha256(b).hexdigest()
    receipt = json.loads((folder / 'import-receipt.json').read_text(encoding='utf-8'))
    assert receipt['canonical_source_sha'] == INPUT
    files = receipt['files']
    assert {x['path'] for x in files} == {p.relative_to(package).as_posix() for p in package.rglob('*') if p.is_file()}
    archive = zipfile.ZipFile(args.archive) if args.archive else None
    if archive:
        assert sha(args.archive.read_bytes()) == receipt['archive_sha256']
        assert set(archive.namelist()) == {x['path'] for x in files}
        assert archive.testzip() is None
    for f in files:
        name = PREFIX + '/package/' + f['path']
        b = (root / name).read_bytes()
        assert len(b) == f['size'] and sha(b) == f['sha256'], name
        staged = blob(name)
        assert staged == b, name
        oid = hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()
        assert oid == f['git_blob_oid'], name
        if archive:
            assert archive.read(f['path']) == b, name
    if archive:
        archive.close()
    m = json.loads((package / 'PACKAGE-MANIFEST.json').read_text(encoding='utf-8'))
    assert {x['path'] for x in m['files']} == {x['path'] for x in files} - {'PACKAGE-MANIFEST.json'}
    for f in m['files']:
        b = (package / f['path']).read_bytes()
        assert len(b) == f['size'] and sha(b) == f['sha256']
    provenance = json.loads((package / 'EXPORT-PROVENANCE.json').read_text(encoding='utf-8'))
    for f in provenance['files']:
        b = (package / f['path']).read_bytes()
        assert len(b) == f['export_size'] and sha(b) == f['export_sha256']
    (folder / 'import-validation.json').touch(exist_ok=True)
    links = []
    for p in folder.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'):
                continue
            assert (p.parent / target.split('#')[0]).resolve().exists(), (p, target)
            links.append({'file':p.relative_to(root).as_posix(), 'target':target})
    old = json.loads(blob('docs/acceptance/MS7-MIG-R01/old-to-new-evidence.json', PRIOR))
    current = json.loads((records / 'old-to-new-evidence.json').read_text(encoding='utf-8'))
    assert [x['original_result'] for x in old['records']] == [x['original_result'] for x in current['records']]
    assert old['D08'] == current['D08']
    preserved = ['source-manifest.json', 'runtime-data-manifest.json',
                 'rendered-runtime-digests.json', 'github-audit.json',
                 'acceptance-reconciliation-20261007.json', 'ci-first-head.json',
                 'evidence/corrected-commands.json']
    for name in preserved:
        path = 'docs/acceptance/MS7-MIG-R01/' + name
        assert blob(path, PRIOR) == blob(path), name
    # All original application/frozen contract Git blobs must be unchanged
    # relative to the prior candidate, including the complete original tree.
    source = json.loads((records / 'source-manifest.json').read_text(encoding='utf-8'))
    def tree_oids(ref):
        result = {}
        if ref == 'INDEX':
            data = git('ls-files', '--stage', '-z')
            for entry in data.split(b'\0'):
                if not entry:
                    continue
                metadata, path = entry.split(b'\t', 1)
                mode, oid, stage = metadata.split()
                assert stage == b'0', path
                result[path.decode('utf-8')] = oid
        else:
            data = git('ls-tree', '-r', '-z', ref)
            for entry in data.split(b'\0'):
                if not entry:
                    continue
                metadata, path = entry.split(b'\t', 1)
                mode, kind, oid = metadata.split()
                result[path.decode('utf-8')] = oid
        return result
    old_oids, new_oids = tree_oids(PRIOR), tree_oids(args.ref)
    for f in source['files']:
        if f['path'] == '.gitattributes':
            continue
        assert old_oids[f['path']] == new_oids[f['path']], f['path']
    followup = json.loads((folder / 'follow-up-F01-F04.json').read_text(encoding='utf-8'))
    for f in followup['findings']:
        for path in f['source_files']:
            assert (root / path).is_file(), path
        for path in f['evidence']:
            assert (package / path).is_file(), path
    result = {'result':'PASS', 'checked_git_ref':args.ref,
              'source_sha':INPUT, 'prior_candidate_head':PRIOR,
              'archive_sha256':receipt['archive_sha256'],
              'original_zip_checked':bool(args.archive),
              'imported_files_exact_checkout_and_git_blobs':len(files),
              'imported_bytes':sum(x['size'] for x in files),
              'package_manifest_entries':len(m['files']),
              'export_provenance_entries':len(provenance['files']),
              'relative_links_verified':len(links),
              'frozen_snapshot_files_unchanged':preserved,
              'historical_original_result_objects_unchanged':True,
              'original_application_contract_tree_unchanged_from_prior':True,
              'D08_preserved_closed':True,
              'F01_F04_status':'MANDATORY / NOT_IMPLEMENTED / ASSIGNMENT_PENDING',
              'MIG_BASE_SHA':'PENDING', 'R01':'INCOMPLETE', 'MIG_G0':'PENDING',
              'links':links}
    (folder / 'import-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'links'}, ensure_ascii=True))

if __name__ == '__main__':
    main()
