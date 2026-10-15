"""Real Git metadata/anchor probes in a separate checkout; no source mutations."""
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid


def main():
    source = Path.cwd().resolve()
    prefix = 'docs/acceptance/MS7-MIG-V02/publication-byte-audit/round3/'
    folder = source / prefix
    spec = importlib.util.spec_from_file_location('metadata_checker', folder / 'verify_publication_v3.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    M, P, V, B = checker.MANIFEST, checker.POLICY, checker.VERIFIER, checker.BINDINGS
    environment = {**os.environ, 'GIT_OPTIONAL_LOCKS': '0', 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONIOENCODING': 'utf-8'}
    scratch = (source / 'var' / ('r3c' + uuid.uuid4().hex[:7])).resolve()
    if not scratch.is_relative_to((source / 'var').resolve()):
        raise RuntimeError('Scratch containment')
    scratch.mkdir()

    def git(*args, cwd=scratch, input=None):
        result = subprocess.run(['git', *args], cwd=cwd, env=environment, input=input, capture_output=True)
        if result.returncode:
            raise RuntimeError((args[:3], result.returncode, result.stderr.decode(errors='replace')[:300]))
        return result.stdout

    git('init', '--quiet', '--initial-branch', 'ms7-mig-v02-content')
    git('config', 'core.longpaths', 'true')
    git('config', 'core.autocrlf', 'false')
    objects = Path(git('rev-parse', '--path-format=absolute', '--git-path', 'objects', cwd=source).decode().strip()).resolve()
    (scratch / '.git/objects/info/alternates').write_bytes((objects.as_posix() + '\n').encode())
    git('update-ref', 'refs/heads/ms7-mig-v02-content', checker.BASE)
    source_index = Path(git('rev-parse', '--path-format=absolute', '--git-path', 'index', cwd=source).decode().strip())
    original_index = source_index.read_bytes()
    shutil.copyfile(source_index, scratch / '.git/index')
    git('checkout-index', '--all', '--force')
    baseline_index = (scratch / '.git/index').read_bytes()
    policy = checker.validate_policy((folder / 'exception-policy.json').read_bytes())
    baseline = {path: (scratch / path).read_bytes() for path in policy['publication_paths']}
    reviewed = {path: sha256(git('show', ':' + path)).hexdigest() for path in (M, P, V)}
    runner = scratch.parent / (scratch.name + '-pinned-v3.py')
    runner.write_bytes(git('show', ':' + V))
    fixture = checker.handoff_bindings(checker.GitView(scratch), policy)
    anchor = {'version': 'MS7-MIG-V02-owner-metadata-anchor-v3', 'owner': 'Ruslan', 'decision': 'APPROVED',
              'inputs': fixture['inputs'], 'exception_set_sha256': fixture['exception_set_sha256'],
              'exception_paths': fixture['exception_paths'], '_fixture': 'SYNTHETIC ONLY — NOT OWNER APPROVAL'}
    anchor_file = scratch.parent / (scratch.name + '-synthetic-metadata-anchor.json')
    anchor_bytes = checker.canonical_json(anchor)
    anchor_file.write_bytes(anchor_bytes)
    cases = []

    def run(name, expected=1, anchored=False, ref=None, expected_error=None):
        view = checker.GitView(scratch, ref)
        attributes = view.attributes([M, P, V], all_attributes=False)
        declared = view.attributes([M, P, V], all_attributes=True)
        snapshot = {path: {**view.entries[path], 'sha256': sha256(view.blob(path)).hexdigest(),
                    'bytes': len(view.blob(path)), 'attributes': attributes[path], 'attributes_all': declared[path]}
                    for path in (M, P, V)}
        argv = [sys.executable, '-B', str(runner), '--root', str(scratch)]
        argv += ['--owner-anchor', str(anchor_file), '--owner-anchor-sha256', sha256(anchor_bytes).hexdigest()] if anchored else ['--local-proposal']
        if ref:
            argv += ['--ref', ref]
        result = subprocess.run(argv, cwd=source, env=environment, capture_output=True, timeout=120)
        output = json.loads(result.stdout)
        correct = result.returncode == expected and (not expected_error or output.get('error', '').startswith(expected_error))
        record = {'case': name, 'actual_exit': result.returncode, 'expected_exit': expected,
                  'result': 'PASS' if correct else 'FAIL', 'error': output.get('error'),
                  'snapshot': snapshot, 'tree_oid_not_commit': ref,
                  'reviewed_byte_pins_unchanged': all(snapshot[path]['sha256'] == reviewed[path] for path in reviewed),
                  'anchor': 'SYNTHETIC_METADATA_FIXTURE_NOT_APPROVAL' if anchored else 'NONE',
                  'owner_status': output.get('owner_exception_status'), 'argv': argv,
                  'stdout_sha256': sha256(result.stdout).hexdigest(), 'stderr_sha256': sha256(result.stderr).hexdigest()}
        if output.get('local_conformance') == 'PASS':
            record['checks'] = {key: {'exit_code': output[key]['exit_code'], 'count': output[key]['count']}
                                for key in ('ordinary', 'cr-at-eol', 'scoped-ordinary', 'scoped-cr-at-eol')}
        cases.append(record)
        print(json.dumps({'case': name, 'actual_exit': result.returncode, 'expected_exit': expected, 'error': output.get('error'), 'result': record['result']}), flush=True)
        if not correct:
            raise RuntimeError(record)

    def restore(paths=()):
        for path in paths:
            (scratch / path).write_bytes(baseline[path])
        info = scratch / '.git/info/attributes'
        if info.exists():
            info.unlink()
        (scratch / '.git/index').write_bytes(baseline_index)

    def stage_raw(path, raw):
        (scratch / path).write_bytes(raw)
        oid = git('hash-object', '-w', '--stdin', input=raw).decode().strip()
        git('update-index', '--cacheinfo', '100644', oid, path)

    for profile in ('false', 'true', 'input'):
        git('config', 'core.autocrlf', profile)
        git('checkout-index', '--all', '--force')
        run('clean_checkout_autocrlf_' + profile, 0)
    run('correct_metadata_synthetic_anchor_fixture', 0, anchored=True)
    git('update-index', '--chmod=+x', M)
    run('original_reproduction_manifest100755', expected_error='FIXED_MODE: ' + M)
    run('original_reproduction_manifest100755_with_anchor', anchored=True, expected_error='FIXED_MODE: ' + M)
    tree = git('write-tree').decode().strip()
    run('original_reproduction_manifest100755_tree', ref=tree, expected_error='FIXED_MODE: ' + M)
    restore()
    for attr in ('-text', 'eol=crlf', 'filter=unapproved', 'working-tree-encoding=UTF-16LE-BOM',
                 'ident', 'export-subst', 'unrecognized-interpreter=enabled'):
        (scratch / '.git/info/attributes').write_bytes((M + ' ' + attr + '\n').encode())
        run('manifest_attribute_' + attr, expected_error='FIXED_')
        if attr == '-text':
            run('original_reproduction_manifest_minus_text_with_anchor', anchored=True, expected_error='FIXED_ATTRIBUTES: ' + M)
        restore()
    for path in (P, V, 'docs/acceptance/MS7-MIG-V02/.gitattributes'):
        (scratch / '.git/info/attributes').write_bytes((path + ' filter=unapproved\n').encode())
        run('trusted_input_filter_' + Path(path).name, expected_error='FIXED_ATTRIBUTES: ')
        restore()
    (scratch / '.git/info/attributes').write_bytes(b'/.gitattributes filter=unapproved\n')
    run('root_attributes_file_filter', expected_error='TRUSTED_ATTRIBUTES_EFFECTIVE: ')
    restore()
    attrfile = 'docs/acceptance/MS7-MIG-V02/.gitattributes'
    rule = ('\npublication-byte-audit/round3/publication-manifest-v3.json -text\n').encode()
    stage_raw(attrfile, baseline[attrfile] + rule)
    run('manifest_sha_unchanged_staged_gitattributes_changed')
    # Rebind its ordinary manifest record: fixed self metadata must still reject.
    data = json.loads(baseline[M])
    view = checker.GitView(scratch)
    data['files'][attrfile].update(blob_oid=view.entries[attrfile]['oid'], blob_sha256=sha256(view.blob(attrfile)).hexdigest(), blob_bytes=len(view.blob(attrfile)))
    stage_raw(M, checker.canonical_json(data))
    run('staged_gitattributes_plus_rebound_manifest_still_rejected', expected_error='FIXED_ATTRIBUTES: ' + M)
    restore([attrfile, M])
    changed_manifest = json.loads(baseline[M])
    changed_manifest['recorded_at_utc'] += '-tampered'
    stage_raw(M, checker.canonical_json(changed_manifest))
    run('manifest_bytes_changed')
    # Even with regenerated in-scope handoff, the reviewed external tuple rejects it.
    stage_raw(B, checker.canonical_json(checker.handoff_bindings(checker.GitView(scratch), policy)))
    run('manifest_bytes_changed_rebound_handoff_with_anchor', anchored=True, expected_error='OWNER_INPUT_BYTES_AND_METADATA')
    restore([M, B])
    mutated = json.loads(baseline[P])
    mutated['whitespace_exceptions'][0]['blob_sha256'] = '0' * 64
    stage_raw(P, checker.canonical_json(mutated))
    run('policy_entry_changed', expected_error='POLICY_DIGEST_MISMATCH')
    restore([P])
    report = checker.PREFIX + 'report-v3.md'
    stage_raw(report, baseline[report] + b'new defect \t\n')
    data = json.loads(baseline[M])
    view = checker.GitView(scratch)
    data['files'][report].update(blob_oid=view.entries[report]['oid'], blob_sha256=sha256(view.blob(report)).hexdigest(), blob_bytes=len(view.blob(report)))
    stage_raw(M, checker.canonical_json(data))
    stage_raw(B, checker.canonical_json(checker.handoff_bindings(checker.GitView(scratch), policy)))
    run('unknown_whitespace_outside40_after_manifest_handoff_rebind', expected_error='UNKNOWN_OR_CHANGED_WHITESPACE_DIAGNOSTICS')
    restore([report, M, B])
    stage_raw(B, baseline[B] + b' ')
    run('derived_handoff_bytes_changed', expected_error='HANDOFF_BINDINGS_CONTENT')
    restore([B])
    git('update-index', '--chmod=+x', B)
    run('derived_handoff_mode_changed', expected_error='FIXED_MODE: ' + B)
    restore()
    run('metadata_and_mode_restored_local', 0)
    run('metadata_and_mode_restored_correct_synthetic_anchor', 0, anchored=True)
    replacement = b'print("invented local PASS")\n'
    cases.append({'case': 'joint_code_policy_replacement_external_before_execution_pin',
                  'result': 'PASS', 'actual_pin_match': sha256(replacement).hexdigest() == reviewed[V],
                  'expected_pin_match': False, 'security_claim': 'Simulation only; no local independent boundary or deployed R03 gate',
                  'P01': 'PENDING', 'reviewed_verifier_sha256': reviewed[V]})
    if source_index.read_bytes() != original_index:
        raise RuntimeError('Source index drift')
    result = {'cases': cases, 'scratch': str(scratch), 'source_index_unchanged': True,
              'code_policy_manifest_reviewed_pins': reviewed, 'platform': 'Windows',
              'owner_approval': 'PENDING; synthetic anchors only', 'no_commit': True, 'databases_used': False}
    (source / 'var/v02-r3-probes.json').write_bytes(checker.canonical_json(result))
    print('ALL ROUND3 SCOPED CASES MATCH EXPECTATIONS; OWNER ANCHOR PENDING', flush=True)


if __name__ == '__main__':
    main()
