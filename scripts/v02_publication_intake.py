"""R03 independent restoration. Never executes code from the source package."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import stat
import subprocess
import sys
import time
import zipfile

BASE = '0c03197e23f69a233c0fcf8bdffa336feca20b92'
BASE_TREE = '1ff96bde5c938b1d00159e9ee1349f5db1f44d9a'
TREE = 'dbad1e853dff354c5d3255755afb5cc32e0ad279'
ARCHIVE_SHA = '57cad8b19e75bda674ce1ac9ddcf9c92a6b57daa2a3b4bd1f39e528c1a77cd0a'
EXCEPTIONS_SHA = 'fa62cf5f4c9b3aaf91864b9face548a5f45759390fb7bedd9cdef5ae6e7c2e18'
PREFIX = 'docs/acceptance/MS7-MIG-V02/publication-byte-audit/round3/'
ATTRS = ['text', 'eol', 'filter', 'working-tree-encoding', 'ident', 'crlf',
         'diff', 'whitespace', 'merge', 'binary', 'export-ignore', 'export-subst', 'encoding']
REPO = Path(__file__).resolve().parents[1]
RECORDS = REPO / 'docs/acceptance/MS7-MIG-R03'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))


def environment(home):
    home.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith(('GIT_', 'PYTHON'))}
    env.update(HOME=str(home), XDG_CONFIG_HOME=str(home), GIT_CONFIG_NOSYSTEM='1',
               GIT_ATTR_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, LC_ALL='C',
               GIT_TERMINAL_PROMPT='0', GIT_OPTIONAL_LOCKS='0')
    # Apply to verifier subprocesses too; neither global config nor a task PATH is trusted.
    settings = {'core.attributesFile': os.devnull, 'core.autocrlf': 'false',
                'core.whitespace': 'blank-at-eol,blank-at-eof,space-before-tab',
                'core.fsmonitor': 'false', 'core.longpaths': 'true',
                'core.hooksPath': str(home), 'color.ui': 'false'}
    env['GIT_CONFIG_COUNT'] = str(len(settings))
    for i, (key, value) in enumerate(settings.items()):
        env[f'GIT_CONFIG_KEY_{i}'] = key
        env[f'GIT_CONFIG_VALUE_{i}'] = value
    return env


class Runner:
    def __init__(self, output):
        self.output = output
        self.output.mkdir(parents=True, exist_ok=True)
        self.env = environment(output / 'empty-home')
        self.git_exe = shutil.which('git')
        require(self.git_exe is not None, 'GIT_UNAVAILABLE')
        self.env['PATH'] = str(Path(self.git_exe).parent) + os.pathsep + self.env['PATH']
        self.receipts = []

    def run(self, name, argv, cwd, data=None, expected=0, timeout=180):
        started = time.monotonic()
        p = subprocess.run(list(map(str, argv)), cwd=cwd, env=self.env,
                           input=data, capture_output=True, timeout=timeout)
        stem = self.output / f'{len(self.receipts):04d}-{name}'
        stem.with_suffix('.stdout').write_bytes(p.stdout)
        stem.with_suffix('.stderr').write_bytes(p.stderr)
        receipt = dict(name=name, argv=list(map(str, argv)), cwd=str(cwd),
                       exit_code=p.returncode, expected_exit=expected,
                       stdout_sha256=sha(p.stdout), stderr_sha256=sha(p.stderr),
                       stdin_sha256=sha(data) if data is not None else None,
                       stdout_path=stem.with_suffix('.stdout').name,
                       stderr_path=stem.with_suffix('.stderr').name,
                       timeout_seconds=timeout, elapsed_seconds=time.monotonic()-started)
        self.receipts.append(receipt)
        save(self.output / 'commands.json', self.receipts)
        require(expected is None or p.returncode == expected,
                f'{name}: expected exit {expected}, actual {p.returncode}: {p.stderr[:500]!r}')
        return p

    def git(self, root, *args, data=None, expected=0, name=None):
        return self.run(name or args[0], [self.git_exe, *args], root, data, expected).stdout


def safe_extract(archive, dest):
    require(not dest.exists(), 'EXTRACTION_DESTINATION_EXISTS')
    require(sha(archive.read_bytes()) == ARCHIVE_SHA, 'SOURCE_ARCHIVE_SHA256')
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        require(len(names) == len(set(names)) == 234, 'PACKAGE_MEMBER_SET')
        require(len(set(n.casefold() for n in names)) == len(names), 'CASE_COLLISION')
        for item in z.infolist():
            p = PurePosixPath(item.filename)
            require(not p.is_absolute() and str(p) == item.filename and
                    all(x not in ('', '.', '..', '.git') and ':' not in x and
                        '\\' not in x and not x.endswith((' ', '.')) for x in p.parts),
                    'UNSAFE_PACKAGE_PATH: ' + item.filename)
            require(stat.S_IFMT(item.external_attr >> 16) in (0, stat.S_IFREG),
                    'NON_REGULAR_PACKAGE_MEMBER: ' + item.filename)
        inventory = json.loads(z.read('package-inventory.json'))
        members = inventory['members']
        require(inventory['count_excluding_self'] == len(members) == 233, 'PACKAGE_COUNT')
        require({r['path'] for r in members} == set(names)-{'package-inventory.json'}, 'PACKAGE_INVENTORY_SET')
        for r in members:
            raw = z.read(r['path'])
            require(len(raw) == r['size'] and sha(raw) == r['sha256'], 'PACKAGE_MEMBER_BYTES: '+r['path'])
        dest.mkdir(parents=True)
        for name in names:
            target = dest / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(name))
    return inventory


def tree_entries(runner, root, ref):
    result = {}
    for entry in runner.git(root, 'ls-tree', '-r', '-z', ref).split(b'\0'):
        if entry:
            meta, path = entry.split(b'\t', 1)
            mode, kind, oid = meta.decode().split()
            require(kind == 'blob', 'NON_BLOB_TREE_ENTRY')
            result[path.decode()] = dict(mode=mode, oid=oid)
    return result


def attributes(runner, root, paths, all_attrs=False, working=False):
    args = ['check-attr'] + ([] if working else ['--cached'])
    args += ['-z', '--stdin'] + (['-a'] if all_attrs else ATTRS)
    raw = runner.git(root, *args, data=('\0'.join(paths)+'\0').encode())
    parts = raw.split(b'\0')[:-1]
    require(len(parts) % 3 == 0, 'ATTRIBUTE_RESPONSE')
    result = {p: {} for p in paths}
    for p, key, value in zip(parts[::3], parts[1::3], parts[2::3]):
        result[p.decode()][key.decode()] = value.decode()
    return result


def restore(archive, output):
    require(not output.exists(), 'NEW_ISOLATED_OUTPUT_REQUIRED')
    output.mkdir(parents=True)
    runner = Runner(output / 'raw')
    runner.run('python-version', [sys.executable, '-I', '-B', '--version'], output)
    runner.git(output, '--version')
    package = output / 'package'
    safe_extract(archive, package)
    inv = json.loads((package/'transport/inventory.json').read_bytes())
    records = inv['files']
    old = zipfile.ZipFile(RECORDS/'v02-transport-reference-documents-20261014.zip')
    old_inv = json.loads(old.read('inventory.json'))
    require(inv['base_sha'] == BASE and records == old_inv['files'], 'PRIOR_151_INVENTORY_MISMATCH')
    require(inv['expected_tree_oid'] == TREE, 'PACKAGE_TREE_PIN')
    paths = [r['path'] for r in records]
    require(len(paths) == len(set(paths)) == 151, 'ADDITION_COUNT')
    require(set(paths) == {p.relative_to(package/'snapshot').as_posix()
                           for p in (package/'snapshot').rglob('*') if p.is_file()}, 'SNAPSHOT_PATH_SET')
    intake = json.loads((RECORDS/'v02-publication-intake-20261013.json').read_bytes())
    doc = json.loads((RECORDS/'v02-publication-document-reconciliation-20261013.json').read_bytes())
    bindings_raw = (package/'snapshot'/PREFIX/'owner-handoff-bindings.json').read_bytes()
    require(sha(bindings_raw) == 'a3151ad6a39066a9cd01b952f9aa3fb89c5e124d0adac21438aea3aade024100', 'PRIOR_BINDINGS_DIGEST')
    bindings = json.loads(bindings_raw)
    require(bindings['inputs'] == intake['expected_control_inputs_from_documents'], 'PRIOR_CONTROL_TUPLES')
    policy = json.loads((package/'snapshot'/PREFIX/'exception-policy.json').read_bytes())
    compact = (json.dumps(policy['whitespace_exceptions'], sort_keys=True, separators=(',', ':'))+'\n').encode()
    require(sha(compact) == EXCEPTIONS_SHA == bindings['exception_set_sha256'], 'APPROVED_EXCEPTION_DIGEST')
    require(bindings['exception_paths'] == intake['approved_exception_paths'], 'APPROVED_40_PATHS')
    by_path = {r['path']: r for r in records}
    for r in doc['exception_records_from_auditor_appendix']:
        actual = by_path[r['path']]
        require((actual['blob_oid'], actual['sha256'], actual['size']) ==
                (r['blob_oid'], r['blob_sha256'], r['blob_bytes']), 'AUDITOR_EXCEPTION_BYTES: '+r['path'])
    refs = zipfile.ZipFile(RECORDS/'v02-publication-reference-documents-20261013.zip')
    for name in ['owner-handoff.md', 'owner-handoff-bindings.json', 'report-v3.md']:
        require(refs.read(name) == (package/'snapshot'/PREFIX/name).read_bytes(), 'ORIGINAL_REFERENCE: '+name)
    require(sha(refs.read('Independent-Round3-Re-Audit-Report.md')) ==
            '2c9718820233175eb2623dedd7721e80ffc5896ec9b1489d2b5edefccd93775d', 'AUDITOR_REPORT_PIN')
    root = output/'snapshot'
    root.mkdir()
    runner.git(root, 'init', '--template=', '--initial-branch=r03-isolated-snapshot')
    runner.git(root, 'config', 'core.filemode', 'true')
    runner.git(root, 'config', 'core.autocrlf', 'false')
    pack = (package/'transport/baseline.pack').read_bytes()
    base_inv = json.loads((package/'transport/baseline-inventory.json').read_bytes())
    require(sha(pack) == base_inv['pack_sha256'] and len(pack) == base_inv['pack_bytes'], 'BASE_PACK_BYTES')
    runner.git(root, 'unpack-objects', '-r', data=pack)
    actual_objects = runner.git(root, 'cat-file', '--batch-all-objects', '--batch-check=%(objectname)').decode().splitlines()
    require(sorted(actual_objects) == sorted(base_inv['objects']) and len(actual_objects) == 2092, 'BASE_OBJECT_SET')
    require(runner.git(root, 'cat-file', '-t', BASE).strip() == b'commit', 'BASE_COMMIT_TYPE')
    require(runner.git(root, 'rev-parse', BASE+'^{tree}').decode().strip() == BASE_TREE, 'BASE_TREE_PIN')
    (root/'.git/shallow').write_text(BASE+'\n', encoding='ascii')
    runner.git(root, 'update-ref', 'HEAD', BASE)
    runner.git(root, 'read-tree', BASE)
    base_entries = tree_entries(runner, root, BASE)
    require(len(base_entries) == 1672 and not set(base_entries).intersection(paths), 'BASE_1672_PLUS_ADDITIONS')
    verified = []
    for r in records:
        raw = (package/'snapshot'/r['path']).read_bytes()
        oid = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require((sha(raw), oid, len(raw), r['mode']) ==
                (r['sha256'], r['blob_oid'], r['size'], '100644'), 'REAL_BLOB_METADATA: '+r['path'])
        verified.append(dict(path=r['path'], sha256=sha(raw), oid=oid, size=len(raw), mode=r['mode']))
    raw_names = ('\n'.join((package/'snapshot'/p).as_posix() for p in paths)+'\n').encode()
    oids = runner.git(root, 'hash-object', '-w', '--no-filters', '--stdin-paths', data=raw_names).decode().splitlines()
    require(oids == [r['blob_oid'] for r in records], 'GIT_REAL_BLOB_OIDS')
    index = ''.join(f"{r['mode']} {r['blob_oid']}\t{r['path']}\0" for r in records).encode()
    runner.git(root, 'update-index', '-z', '--index-info', data=index)
    actual_tree = runner.git(root, 'write-tree').decode().strip()
    require(actual_tree == TREE, f'TREE: expected {TREE}, actual {actual_tree}')
    require(len(tree_entries(runner, root, TREE)) == 1823, 'FULL_1823_ENTRIES')
    runner.git(root, 'checkout-index', '--all')
    runner.git(root, 'fsck', '--full', '--no-reflogs')
    require(not runner.git(root, 'diff', '--name-only'), 'DIRTY_RESTORED_WORKTREE')
    require(not runner.git(root, 'ls-files', '--others'), 'UNTRACKED_RESTORED_FILES')
    for all_attrs in (False, True):
        for working in (False, True):
            observed = attributes(runner, root, paths, all_attrs, working)
            key = 'attributes_all' if all_attrs else 'attributes'
            require(observed == {r['path']: r[key] for r in records}, 'EFFECTIVE_METADATA_'+key)
    for p, expected in bindings['inputs'].items():
        raw = (root/p).read_bytes()
        entry = tree_entries(runner, root, TREE)[p]
        actual = dict(blob_oid=entry['oid'], blob_sha256=sha(raw), blob_bytes=len(raw),
                      mode=entry['mode'], attributes=attributes(runner, root, [p])[p],
                      attributes_all=attributes(runner, root, [p], True)[p])
        require(actual == expected, 'REAL_PRIOR_CONTROL_BINDING: '+p)
    for r in records:
        require((root/r['path']).read_bytes() == (package/'snapshot'/r['path']).read_bytes(), 'CHECKOUT_BYTES: '+r['path'])
    raw_paths = [r['path'] for r in policy['preserve_raw_bytes']]
    require(len(raw_paths) == len(set(raw_paths)) == 73 and set(bindings['exception_paths']) <= set(raw_paths), 'RAW73_EXCEPTION40')
    for row in json.loads((package/'transport/whitespace/receipts.json').read_bytes()):
        name = row['name']
        args = [] if name.startswith('ordinary') else ['-c', 'core.whitespace=cr-at-eol']
        args += ['diff', '--cached', '--check']
        if name.endswith('scoped'):
            args += ['--', '.', *[':(exclude,literal)'+p for p in bindings['exception_paths']]]
        result = runner.run(name, [runner.git_exe, *args], root, expected=row['exit_code'])
        for stream in ('stdout', 'stderr'):
            actual = getattr(result, stream)
            require(actual == (package/f'transport/whitespace/{name}.{stream}').read_bytes(), 'ORIGINAL_WHITESPACE_RAW: '+name)
            require(sha(actual) == row[stream+'_sha256'], 'WHITESPACE_STREAM_PIN')
    receipt = dict(result='PASS', archive_sha256=ARCHIVE_SHA, base_sha=BASE,
                   actual_checkout_sha=BASE, representation='STAGED_INDEX_AND_TREE_NO_IMPLEMENTATION_COMMIT',
                   implementation_sha=None, tree=actual_tree, base_entries=1672, additions=151,
                   total_entries=1823, controls_against_prior_bindings='PASS',
                   original_reference_documents='PASS', effective_13_and_full_attributes='PASS',
                   raw_preserved=73, exceptions=40, raw_not_exempt=33,
                   full_whitespace='FAIL/2_EXACT_APPROVED_RAW', scoped_whitespace='PASS/0',
                   python=sys.version, platform=platform.platform(), verified_files=verified)
    save(output/'snapshot-verification.json', receipt)
    return runner, root, package, bindings, policy


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    restore(args.archive.resolve(), args.output.resolve())
    print('PASS: independently restored and verified original151 staged/tree snapshot')
