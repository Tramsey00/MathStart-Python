"""Owner-controlled R03 gate. No candidate executable, anchor or pins are accepted."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import zipfile

# -I intentionally removes the script directory from sys.path. Load one exact
# sibling from the pinned owner checkout, never from the candidate/PYTHONPATH.
spec = importlib.util.spec_from_file_location('r03_intake', Path(__file__).with_name('v02_publication_intake.py'))
intake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intake)
BASE, TREE, PREFIX = intake.BASE, intake.TREE, intake.PREFIX
require, sha, save = intake.require, intake.sha, intake.save
OWNER = intake.REPO / 'specs/migration/r03-v1/v02-publication'
PINS_SHA = 'eb32a3245275649e9a69c67ea17001cfd4b8ff0cd7a30e63bcac325692c9c591'
ANCHOR_SHA = '5a9a7a65dab43afe4e353b51523d86f3a15de2e371d19efacc8127ae6d0dbfd7'


def pins():
    raw = (OWNER/'approved-pins.json').read_bytes()
    require(sha(raw) == PINS_SHA, 'OWNER_PINS_DIGEST')
    result = json.loads(raw)
    require(result['anchor_sha256'] == ANCHOR_SHA, 'OWNER_ANCHOR_PIN')
    return result


def materialize_controls(output):
    data = pins()
    require(sha((OWNER/'trusted-controls.zip').read_bytes()) == data['controls_zip_sha256'], 'OWNER_CONTROLS_ARCHIVE_DIGEST')
    require(not output.exists(), 'NEW_CONTROL_DIRECTORY_REQUIRED')
    output.mkdir(parents=True)
    with zipfile.ZipFile(OWNER/'trusted-controls.zip') as archive:
        require(set(archive.namelist()) == set(data['controls']) and len(archive.namelist()) == 6, 'OWNER_CONTROL_SET')
        for name, record in data['controls'].items():
            raw = archive.read(name)
            require(sha(raw) == record['sha256'] and len(raw) == record['size'], 'OWNER_CONTROL_DIGEST: '+name)
            (output/name).write_bytes(raw)
    (output/'owner-approval-v3.json').write_bytes((OWNER/'owner-approval-v3.json').read_bytes())
    check_controls(output)
    return output


def check_controls(controls):
    data = pins()
    for name, record in data['controls'].items():
        path = controls/name
        require(path.is_file() and not path.is_symlink(), 'OWNER_CONTROL_TYPE: '+name)
        raw = path.read_bytes()
        require(sha(raw) == record['sha256'] and len(raw) == record['size'], 'OWNER_CONTROL_DIGEST: '+name)
    raw = (controls/'owner-approval-v3.json').read_bytes()
    require(sha(raw) == ANCHOR_SHA, 'OWNER_ANCHOR_DIGEST')
    anchor = json.loads(raw)
    require('_fixture' not in anchor and anchor.get('owner') == 'Ruslan' and anchor.get('decision') == 'APPROVED', 'REAL_OWNER_ANCHOR_REQUIRED')
    return data


def owner_revision(runner, revision):
    require(re.fullmatch('[0-9a-f]{40}', revision) is not None, 'FULL_OWNER_REVISION_REQUIRED')
    actual = runner.git(intake.REPO, 'rev-parse', 'HEAD').decode().strip()
    require(actual == revision, 'OWNER_CHECKOUT_REVISION')
    paths = ['scripts/v02_publication_intake.py', 'scripts/v02_publication_gate.py',
             'specs/migration/r03-v1/v02-publication/approved-pins.json',
             'specs/migration/r03-v1/v02-publication/owner-approval-v3.json',
             'specs/migration/r03-v1/v02-publication/trusted-controls.zip',
             'docs/acceptance/MS7-MIG-R03/v02-source-snapshot-20261014.zip',
             'docs/acceptance/MS7-MIG-R03/v02-publication-intake-20261013.json',
             'docs/acceptance/MS7-MIG-R03/v02-publication-document-reconciliation-20261013.json',
             'docs/acceptance/MS7-MIG-R03/v02-publication-reference-documents-20261013.zip',
             'docs/acceptance/MS7-MIG-R03/v02-transport-reference-documents-20261014.zip']
    for path in paths:
        actual_bytes = (intake.REPO/path).read_bytes()
        expected = runner.git(intake.REPO, 'show', revision+':'+path)
        require(actual_bytes == expected, 'DIRTY_OWNER_CONTROL: '+path)
    return actual


def candidate_preflight(runner, root, ref, controls, representation):
    require(re.fullmatch('[0-9a-f]{40}', ref) is not None, 'FULL_CANDIDATE_REF_REQUIRED')
    require(not controls.resolve().is_relative_to(root.resolve()), 'CONTROLS_WITHIN_CANDIDATE')
    require(not intake.REPO.is_relative_to(root.resolve()), 'OWNER_CHECKOUT_WITHIN_CANDIDATE')
    require(not root.is_symlink() and (root/'.git').is_dir() and not (root/'.git').is_symlink(), 'ISOLATED_GIT_DIRECTORY_REQUIRED')
    info = root/'.git/info/attributes'
    require(not info.exists() or not info.read_bytes().strip(), 'UNAPPROVED_INFO_ATTRIBUTES')
    require(not (root/'.git/objects/info/alternates').exists(), 'EXTERNAL_OBJECT_ALTERNATES')
    # Disallow executable/filter/include config before asking Git to inspect data.
    raw = runner.git(root, 'config', '--local', '--no-includes', '--null', '--list')
    allowed = {'core.repositoryformatversion', 'core.filemode', 'core.bare', 'core.logallrefupdates',
               'core.symlinks', 'core.ignorecase', 'core.autocrlf', 'core.longpaths', 'core.precomposeunicode',
               'remote.origin.url', 'remote.origin.fetch'}
    for item in raw.split(b'\0'):
        if item:
            key = item.split(b'\n', 1)[0].decode().lower()
            require(key in allowed, 'UNAPPROVED_LOCAL_GIT_CONFIG: '+key)
    head = runner.git(root, 'rev-parse', 'HEAD').decode().strip()
    kind = runner.git(root, 'cat-file', '-t', ref).decode().strip()
    tree = runner.git(root, 'rev-parse', ref+'^{tree}').decode().strip()
    if representation == 'staged-tree':
        require(kind == 'tree' and ref == TREE and head == BASE, 'STAGED_TREE_PROVENANCE')
    else:
        require(kind == 'commit' and head == ref, 'PUBLISHED_HEAD_PROVENANCE')
        require(runner.git(root, 'show', '-s', '--format=%P', ref).decode().strip() == BASE,
                'PUBLISHED_BASE_PARENT')
    require(tree == TREE, 'CANDIDATE_TREE_PIN')
    require(runner.git(root, 'write-tree').decode().strip() == tree, 'INDEX_REF_MISMATCH')
    require(not runner.git(root, 'ls-files', '--others'), 'UNTRACKED_CANDIDATE_FILES')
    policy = json.loads((controls/'exception-policy.json').read_bytes())
    bindings = json.loads((controls/'owner-handoff-bindings.json').read_bytes())
    names = policy['publication_paths'] + ['.gitattributes']
    for all_attrs in (False, True):
        key = 'attributes_all' if all_attrs else 'attributes'
        expected = {}
        raw_paths = {r['path'] for r in policy['preserve_raw_bytes']}
        for path in names:
            expected[path] = (policy['raw_publication_metadata'] if path in raw_paths else policy['default_publication_metadata'])[key]
        for working in (False, True):
            require(intake.attributes(runner, root, names, all_attrs, working) == expected, 'CANDIDATE_EFFECTIVE_'+key)
    for name, record in pins()['controls'].items():
        path = root/record['candidate_path']
        require(path.is_file() and not path.is_symlink() and path.read_bytes() == (controls/name).read_bytes(), 'CANDIDATE_CONTROL_BYTES: '+name)
    # No ext-diff/textconv; config and effective representation attributes checked above.
    require(not runner.git(root, 'diff', '--no-ext-diff', '--no-textconv', '--name-only'), 'DIRTY_CANDIDATE_CHECKOUT')
    return dict(actual_checkout_sha=head, reviewed_ref=ref, ref_kind=kind, tree=tree,
                implementation_sha=ref if kind == 'commit' else None, representation=representation,
                anchor_sha256=ANCHOR_SHA, pins_sha256=PINS_SHA)


def execute_verifier(runner, root, ref, controls, name, expected=0):
    # This must remain immediately before exec. Candidate paths cannot supply code/pins.
    check_controls(controls)
    argv = [sys.executable, '-I', '-B', controls/'verify_publication_v3.py', '--root', root,
            '--ref', ref, '--owner-anchor', controls/'owner-approval-v3.json',
            '--owner-anchor-sha256', ANCHOR_SHA]
    result = runner.run(name, argv, controls, expected=expected, timeout=240)
    receipt = json.loads(result.stdout)
    if expected == 0:
        require(receipt.get('local_conformance') == 'PASS' and
                receipt.get('owner_exception_status') == 'OWNER_EXCEPTION_APPROVED_BY_EXTERNAL_ANCHOR', 'VERIFIER_APPROVAL_RESULT')
    return receipt


def gate(runner, root, ref, controls, representation):
    check_controls(controls)
    receipt = candidate_preflight(runner, root, ref, controls, representation)
    receipt['verifier'] = execute_verifier(runner, root, ref, controls, 'external-verifier')
    # The verifier's JSON contains diagnostic sets and stream hashes. Retain the
    # actual Git streams independently too, including after commit publication.
    exclusions = json.loads((controls/'owner-handoff-bindings.json').read_bytes())['exception_paths']
    streams = {'ordinary-full': 'c1b69b199ac5cd41c665d656a72587d36ff0d13dc04a82c0a4c3d75086da20fb',
               'cr-at-eol-full': '5837278beb0d2ef638db564512c6913f9ae02346d204ba7b75c059aaef373f63'}
    for cr in (False, True):
        for scoped in (False, True):
            name = ('cr-at-eol' if cr else 'ordinary') + ('-scoped' if scoped else '-full')
            args = [runner.git_exe] + (['-c', 'core.whitespace=cr-at-eol'] if cr else [])
            args += ['diff', '--no-ext-diff', '--no-textconv', '--check', BASE, ref]
            if scoped:
                args += ['--', '.', *[':(exclude,literal)'+p for p in exclusions]]
            result = runner.run('gate-'+name, args, root, expected=0 if scoped else 2)
            require(not result.stderr and sha(result.stdout) == (sha(b'') if scoped else streams[name]),
                    'GATE_WHITESPACE_STREAM_PIN: '+name)
    receipt['result'] = 'PASS'
    return receipt


def negatives(runner, root, package, controls, output):
    """Real immutable snapshot reused only after restoring all touched bytes/index."""
    results = []
    policy_path = PREFIX+'exception-policy.json'
    manifest_path = PREFIX+'publication-manifest-v3.json'
    bindings_path = PREFIX+'owner-handoff-bindings.json'
    verifier_path = PREFIX+'verify_publication_v3.py'
    policy = json.loads((controls/'exception-policy.json').read_bytes())
    marker = output/'MUST-NOT-EXECUTE'
    malicious = ("from pathlib import Path\nPath("+repr(str(marker))+ ").write_text('executed')\nraise SystemExit(0)\n").encode()

    def rejected_control(name, filename, mutated, reason):
        path = controls/filename
        original = path.read_bytes()
        try:
            path.write_bytes(mutated)
            # Run the real pre-execution boundary in a separate Python process;
            # preserve argv/stdout/stderr/exit1, plus explicit nonexecution proof.
            probe = '''import importlib.util,json,sys
from pathlib import Path
s=importlib.util.spec_from_file_location('r03_gate_probe',sys.argv[1])
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
r=m.intake.Runner(Path(sys.argv[5]))
try:
 m.execute_verifier(r,Path(sys.argv[2]),sys.argv[3],Path(sys.argv[4]),'unexpected-verifier')
except RuntimeError as error:
 print(json.dumps({'error':str(error),'verifier_spawned':bool(r.receipts)}))
 sys.exit(1)
sys.exit(0)
'''
            result = runner.run(name, [sys.executable, '-I', '-B', '-c', probe,
                                Path(__file__).resolve(), root, TREE, controls, output/('probe-'+name)],
                                output, expected=1)
            receipt = json.loads(result.stdout)
            require(receipt['error'] == reason, name+': WRONG_REJECTION: '+str(receipt))
            require(not receipt['verifier_spawned'] and not marker.exists(), 'REPLACEMENT_EXECUTED')
            results.append(dict(case=name, result='PASS_EXPECTED_REJECTION', layer='PRE_EXECUTION',
                                actual_reason=receipt['error'], verifier_spawned=False, exit_code=1,
                                before_sha256=sha(original), after_sha256=sha(mutated)))
        finally:
            path.write_bytes(original)

    rejected_control('trusted-executable-replacement', 'verify_publication_v3.py', malicious,
                     'OWNER_CONTROL_DIGEST: verify_publication_v3.py')
    for name in ['exception-policy.json', 'publication-manifest-v3.json', 'owner-handoff-bindings.json', 'root.gitattributes', 'v02.gitattributes']:
        rejected_control('trusted-'+name, name, (controls/name).read_bytes()+b'\n', 'OWNER_CONTROL_DIGEST: '+name)
    rejected_control('trusted-anchor-replacement', 'owner-approval-v3.json', (controls/'owner-approval-v3.json').read_bytes()+b'\n', 'OWNER_ANCHOR_DIGEST')

    def mutate_case(name, mutations, reason, mode=None):
        originals = {p: (root/p).read_bytes() for p in mutations}
        original_modes = {p: (root/p).stat().st_mode for p in mutations}
        try:
            for p, raw in mutations.items():
                (root/p).write_bytes(raw)
                oid = runner.git(root, 'hash-object', '-w', '--stdin', data=raw).decode().strip()
                runner.git(root, 'update-index', '--cacheinfo', (mode or '100644')+','+oid+','+p)
                if mode == '100755' and os.name != 'nt':
                    (root/p).chmod(0o755)
            mutated_tree = runner.git(root, 'write-tree').decode().strip()
            # Production bootstrap refuses all divergent trees, without pin regeneration.
            try:
                candidate_preflight(runner, root, mutated_tree, controls, 'staged-tree')
            except RuntimeError as error:
                require(str(error) == 'STAGED_TREE_PROVENANCE', 'WRONG_BOOTSTRAP_TREE_REJECTION')
            else:
                raise RuntimeError('MUTATED_TREE_ACCEPTED')
            # Exercise the *unchanged* trusted verifier itself as a lower-layer attack
            # probe. This is not a production approval path and never changes pins.
            receipt = execute_verifier(runner, root, mutated_tree, controls, name, expected=1)
            require(receipt.get('error', '').startswith(reason), name+': WRONG_REASON: '+str(receipt))
            require(not marker.exists(), 'CANDIDATE_EXECUTABLE_RAN')
            results.append(dict(case=name, result='PASS_EXPECTED_REJECTION', layer='BOOTSTRAP_AND_VERIFIER',
                                actual_reason=receipt['error'], expected_reason=reason,
                                mutated_tree=mutated_tree, approved_tree=TREE,
                                mutations=[dict(path=p, before_sha256=sha(originals[p]), after_sha256=sha(raw),
                                                git_mode=mode or '100644') for p, raw in mutations.items()]))
        finally:
            runner.git(root, 'read-tree', TREE)
            for p, raw in originals.items():
                (root/p).write_bytes(raw)
                (root/p).chmod(original_modes[p])
            require(runner.git(root, 'write-tree').decode().strip() == TREE, 'NEGATIVE_RESET_TREE')

    mutate_case('candidate-policy-byte', {policy_path: (root/policy_path).read_bytes()+b'\n'}, 'POLICY_DIGEST_MISMATCH')
    # Valid JSON with changed metadata proves manifest self-pin enforcement by
    # derived bindings, even though manifest omits its own circular content pin.
    manifest_raw = (root/manifest_path).read_bytes()
    mutate_case('candidate-manifest-byte', {manifest_path: manifest_raw+b'\n'}, 'HANDOFF_BINDINGS_CONTENT')
    mutate_case('candidate-bindings-byte', {bindings_path: (root/bindings_path).read_bytes()+b'\n'}, 'HANDOFF_BINDINGS_CONTENT')
    mutate_case('manifest-mode-same-bytes', {manifest_path: manifest_raw}, 'FIXED_MODE: '+manifest_path, mode='100755')
    attr_path = 'docs/acceptance/MS7-MIG-V02/.gitattributes'
    mutate_case('manifest-attributes-same-bytes', {attr_path: (root/attr_path).read_bytes()+b'\npublication-byte-audit/round3/publication-manifest-v3.json -text\n'}, 'BLOB_OID: '+attr_path)
    raw_path = policy['preserve_raw_bytes'][0]['path']
    raw = (root/raw_path).read_bytes()
    require(b'\r\n' in raw, 'RAW_NEGATIVE_CRLF_PRECONDITION')
    mutate_case('raw-crlf-byte-mutation', {raw_path: raw.replace(b'\r\n', b'\n', 1)}, 'BLOB_OID: '+raw_path)
    changed = json.loads((controls/'exception-policy.json').read_bytes())
    changed['whitespace_exceptions'].append(dict(changed['whitespace_exceptions'][0], path='backend/content/__init__.py'))
    mutate_case('exception-set-expansion', {policy_path: intake.canonical(changed)}, 'POLICY_DIGEST_MISMATCH')
    # New whitespace in a non-exempt pinned file is rejected before diagnostic
    # comparison by its immutable content pin. Also retain the real scoped FAIL/2.
    path = 'backend/content/__init__.py'
    changed_raw = (root/path).read_bytes()+b'# new whitespace outside40 \n'
    original = (root/path).read_bytes()
    try:
        (root/path).write_bytes(changed_raw)
        oid = runner.git(root, 'hash-object', '-w', '--stdin', data=changed_raw).decode().strip()
        runner.git(root, 'update-index', '--cacheinfo', '100644,'+oid+','+path)
        args = [runner.git_exe, 'diff', '--cached', '--check', '--', '.',
                *[':(exclude,literal)'+p for p in json.loads((controls/'owner-handoff-bindings.json').read_bytes())['exception_paths']]]
        diagnostic = runner.run('new-whitespace-scoped', args, root, expected=2)
        require(b'backend/content/__init__.py:' in diagnostic.stdout and b'trailing whitespace.' in diagnostic.stdout, 'NEW_WHITESPACE_DIAGNOSTIC_MISSING')
    finally:
        runner.git(root, 'read-tree', TREE)
        (root/path).write_bytes(original)
    mutate_case('new-whitespace-outside40', {path: changed_raw}, 'BLOB_OID: '+path)
    altered_pins = json.loads((root/bindings_path).read_bytes())
    altered_pins['inputs'][verifier_path]['blob_sha256'] = sha(malicious)
    altered_pins['inputs'][policy_path]['blob_sha256'] = sha(intake.canonical(changed))
    mutate_case('joint-candidate-verifier-policy-pins', {
        verifier_path: malicious, policy_path: intake.canonical(changed),
        bindings_path: intake.canonical(altered_pins)}, 'POLICY_DIGEST_MISMATCH')
    # Effective attributes without changing tracked bytes must also fail.
    info = root/'.git/info/attributes'
    info.parent.mkdir(exist_ok=True)
    try:
        info.write_bytes((manifest_path+' -text\n').encode())
        try:
            candidate_preflight(runner, root, TREE, controls, 'staged-tree')
        except RuntimeError as error:
            require(str(error) == 'UNAPPROVED_INFO_ATTRIBUTES', 'INFO_ATTRIBUTES_REASON')
        else:
            raise RuntimeError('INFO_ATTRIBUTES_ACCEPTED')
        receipt = execute_verifier(runner, root, TREE, controls, 'effective-manifest-attributes', expected=1)
        require(receipt.get('error') == 'FIXED_ATTRIBUTES: '+manifest_path, 'EFFECTIVE_ATTRIBUTE_REASON')
        results.append(dict(case='effective-manifest-attributes-same-blobs', result='PASS_EXPECTED_REJECTION',
                            layer='BOOTSTRAP_AND_VERIFIER', actual_reason=receipt['error'], tree=TREE))
    finally:
        info.unlink()
    save(output/'negative-results.json', results)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['suite', 'published'])
    parser.add_argument('--owner-revision', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--root', type=Path)
    parser.add_argument('--ref')
    args = parser.parse_args()
    output = args.output.resolve()
    require(not output.exists(), 'NEW_EVIDENCE_DIRECTORY_REQUIRED')
    output.mkdir(parents=True)
    runner = intake.Runner(output/'gate-raw')
    try:
        revision = owner_revision(runner, args.owner_revision)
        controls = materialize_controls(output/'owner-controlled')
        if args.command == 'suite':
            require(args.root is None and args.ref is None, 'SUITE_USES_ONLY_PINNED_SOURCE')
            _, root, package, _, _ = intake.restore(intake.RECORDS/'v02-source-snapshot-20261014.zip', output/'restored')
            receipt = gate(runner, root, TREE, controls, 'staged-tree')
            save(output/'positive.json', receipt)
            cases = negatives(runner, root, package, controls, output)
            receipt['negative_cases'] = len(cases)
            receipt['post_negative_positive'] = gate(runner, root, TREE, controls, 'staged-tree')['result']
        else:
            require(args.root is not None and args.ref is not None, 'EXACT_PUBLISHED_REF_REQUIRED')
            root = args.root.resolve()
            require(not output.is_relative_to(root), 'EVIDENCE_WITHIN_CANDIDATE')
            receipt = gate(runner, root, args.ref, controls, 'published-commit')
        receipt.update(owner_control_revision=revision, workflow_event_sha=os.environ.get('GITHUB_SHA'),
                       run_url=('https://github.com/'+os.environ.get('GITHUB_REPOSITORY', '')+'/actions/runs/'+os.environ['GITHUB_RUN_ID']) if 'GITHUB_RUN_ID' in os.environ else None,
                       task_approval=False, merge_performed=False, publication_authorized=False)
        save(output/'result.json', receipt)
        print(json.dumps({k: v for k, v in receipt.items() if k != 'verifier'}, indent=2))
    except Exception as error:
        save(output/'failure.json', dict(result='FAIL', error=str(error), owner_revision=args.owner_revision))
        raise
    finally:
        files = [dict(path=p.relative_to(output).as_posix(), size=p.stat().st_size, sha256=sha(p.read_bytes()))
                 for p in output.rglob('*') if p.is_file() and '.git' not in p.parts and
                 'snapshot' not in p.relative_to(output).parts and 'package' not in p.relative_to(output).parts]
        save(output/'evidence-manifest.json', files)


if __name__ == '__main__':
    main()
