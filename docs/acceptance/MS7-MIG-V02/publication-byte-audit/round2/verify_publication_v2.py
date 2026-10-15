"""Blob-based publication proposal checker. An independent owner anchor is a gate."""
import argparse
from collections import defaultdict
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import sys

PREFIX = 'docs/acceptance/MS7-MIG-V02/publication-byte-audit/round2/'
POLICY = PREFIX + 'exception-policy.json'
MANIFEST = PREFIX + 'publication-manifest-v2.json'
VERIFIER = PREFIX + 'verify_publication_v2.py'
BASE = '0c03197e23f69a233c0fcf8bdffa336feca20b92'
PROPOSED_POLICY_SHA256 = '09fff1895df489f707000f4a1fec8f6ddd62d1666d2b1c44c94b16ca8ae1741f'
OWNER_PENDING = 'OWNER_EXCEPTION_APPROVAL_PENDING'
ATTRIBUTES = ('text', 'eol', 'diff', 'whitespace')


class GateError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise GateError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def decode_json(raw, label):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, label + ': DUPLICATE_KEY')
            result[key] = value
        return result
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs)
    except (ValueError, UnicodeError) as error:
        raise GateError(label + ': INVALID_JSON') from error


def validate_policy(raw):
    require(digest(raw) == PROPOSED_POLICY_SHA256, 'POLICY_DIGEST_MISMATCH')
    policy = decode_json(raw, 'policy')
    require(policy['input_sha'] == BASE, 'POLICY_BASE')
    require(policy['approval_status'] == OWNER_PENDING, 'PROPOSAL_APPROVAL_STATUS')
    raw_paths = [item['path'] for item in policy['preserve_raw_bytes']]
    except_paths = [item['path'] for item in policy['whitespace_exceptions']]
    require(len(raw_paths) == len(set(raw_paths)) == 73, 'RAW_SET')
    require(len(except_paths) == len(set(except_paths)) == 40, 'EXCEPTION_SET')
    require(set(except_paths) <= set(raw_paths), 'EXCEPTION_NOT_RAW')
    require(policy['ordinary_diagnostics'] == 3887 and policy['cr_at_eol_diagnostics'] == 6, 'DIAGNOSTIC_COUNTS')
    return policy


def canonical_work(raw, attributes):
    require(attributes['diff'] == 'unspecified' and attributes['whitespace'] == 'unspecified', 'SUPPRESSION_ATTRIBUTE')
    if attributes['text'] == 'unset':
        return raw
    require(attributes['text'] in ('auto', 'set') and attributes['eol'] == 'lf', 'UNSUPPORTED_TEXT_ATTRIBUTES')
    return raw.replace(b'\r\n', b'\n')


class GitView:
    def __init__(self, root, reference=None):
        self.root = Path(root).resolve()
        self.reference = reference
        self.environment = {**os.environ, 'LC_ALL': 'C', 'GIT_OPTIONAL_LOCKS': '0'}
        self.cache = {}
        if reference is None:
            raw = self.git('ls-files', '--stage', '-z')
            self.entries = {}
            for entry in raw.split(b'\0'):
                if not entry:
                    continue
                metadata, path = entry.split(b'\t', 1)
                mode, oid, stage = metadata.decode().split()
                require(stage == '0', 'UNMERGED_INDEX')
                self.entries[path.decode()] = {'mode': mode, 'oid': oid}
        else:
            self.entries = {}
            for entry in self.git('ls-tree', '-r', '-z', reference).split(b'\0'):
                if not entry:
                    continue
                metadata, path = entry.split(b'\t', 1)
                mode, kind, oid = metadata.decode().split()
                require(kind == 'blob', 'NON_BLOB_ENTRY')
                self.entries[path.decode()] = {'mode': mode, 'oid': oid}

    def git(self, *args, input=None):
        result = subprocess.run(['git', '-c', 'color.ui=false', *args], cwd=self.root,
                                env=self.environment, input=input, capture_output=True)
        require(result.returncode == 0, 'GIT_COMMAND_FAILED: ' + ' '.join(args[:3]))
        return result.stdout

    def load_blobs(self, paths):
        oids = list(dict.fromkeys(self.entries[path]['oid'] for path in paths))
        output = self.git('cat-file', '--batch', input=('\n'.join(oids) + '\n').encode())
        offset = 0
        for oid in oids:
            end = output.index(b'\n', offset)
            actual, kind, length = output[offset:end].decode().split()
            require(actual == oid and kind == 'blob', 'OBJECT_TYPE_OID')
            size = int(length)
            offset = end + 1
            self.cache[oid] = output[offset:offset + size]
            require(len(self.cache[oid]) == size and output[offset + size:offset + size + 1] == b'\n', 'BATCH_SIZE')
            offset += size + 1
        require(offset == len(output), 'BATCH_EXTRA_BYTES')

    def blob(self, path):
        require(path in self.entries, 'MISSING_INDEX_PATH: ' + path)
        oid = self.entries[path]['oid']
        if oid not in self.cache:
            self.load_blobs([path])
        return self.cache[oid]

    def paths(self):
        args = ['diff', '--cached', '--name-status', '-z'] if self.reference is None else ['diff', '--name-status', '-z', BASE, self.reference]
        items = self.git(*args).split(b'\0')[:-1]
        require(len(items) % 2 == 0, 'UNSUPPORTED_PATH_STATUS')
        result = []
        for status, path in zip(items[::2], items[1::2]):
            require(status == b'A', 'EXISTING_BASELINE_CHANGE')
            result.append(path.decode())
        return result

    def attributes(self, paths, working=False):
        args = ['check-attr']
        if not working:
            args += ['--cached'] if self.reference is None else ['--source', self.reference]
        args += ['-z', '--stdin', *ATTRIBUTES]
        parts = self.git(*args, input=b'\0'.join(path.encode() for path in paths) + b'\0').split(b'\0')[:-1]
        require(len(parts) == len(paths) * len(ATTRIBUTES) * 3, 'ATTRIBUTE_RESPONSE')
        result = defaultdict(dict)
        for path, attr, value in zip(parts[::3], parts[1::3], parts[2::3]):
            result[path.decode()][attr.decode()] = value.decode()
        return dict(result)


def diagnostic_check(view, cr_at_eol=False, exclusions=()):
    args = ['git', '-c', 'color.ui=false']
    if cr_at_eol:
        args += ['-c', 'core.whitespace=cr-at-eol']
    args += ['diff', '--cached', '--check'] if view.reference is None else ['diff', '--check', BASE, view.reference]
    if exclusions:
        args += ['--', '.', *[':(exclude,literal)' + path for path in exclusions]]
    result = subprocess.run(args, cwd=view.root, env=view.environment, capture_output=True)
    require(not result.stderr, 'UNKNOWN_GIT_DIAGNOSTIC_STDERR')
    groups = defaultdict(list)
    for line in result.stdout.split(b'\n'):
        if not line:
            continue
        match = re.fullmatch(rb'([^\n]+):(\d+): ([^\n]+)\.', line)
        if match:
            path, number, reason = match.groups()
            groups[path.decode()].append({'line': int(number), 'reason': reason.decode()})
        else:
            require(line.startswith(b'+'), 'UNKNOWN_GIT_DIAGNOSTIC_FORMAT')
    return {'exit_code': result.returncode, 'by_path': dict(groups),
            'count': sum(map(len, groups.values())), 'stream_sha256': digest(result.stdout)}


def validate_diagnostics(policy, ordinary, cr_at_eol):
    for name, actual, key, count in [('ordinary', ordinary, 'ordinary', 3887),
                                     ('cr-at-eol', cr_at_eol, 'cr_at_eol', 6)]:
        expected = {item['path']: item[key] for item in policy['whitespace_exceptions'] if item[key]}
        require(actual['exit_code'] == 2 and actual['count'] == count and actual['by_path'] == expected,
                'UNKNOWN_OR_CHANGED_WHITESPACE_DIAGNOSTICS: ' + name)


def verify(view, policy):
    require(view.git('rev-parse', 'HEAD').decode().strip() == BASE if view.reference is None else True, 'BASE_HEAD')
    paths = view.paths()
    require(set(paths) == set(policy['publication_paths']) and len(paths) == len(policy['publication_paths']), 'PUBLICATION_PATH_SET')
    view.load_blobs(paths)
    manifest = decode_json(view.blob(MANIFEST), 'manifest')
    require(manifest['input_sha'] == BASE and manifest['tested_implementation_sha'] is None, 'MANIFEST_SOURCE')
    require(manifest['publication_status'] == 'PENDING_PUBLICATION', 'MANIFEST_PUBLICATION')
    require(set(manifest['files']) | {MANIFEST} == set(paths) and len(manifest['files']) == len(paths) - 1, 'MANIFEST_PATH_SET')
    require(manifest['file_count_including_self'] == len(paths), 'MANIFEST_COUNT')
    attributes = view.attributes(paths)
    work_attrs = view.attributes(paths, working=True)
    for path in paths:
        actual = view.entries[path]
        raw = view.blob(path)
        if path != MANIFEST:
            record = manifest['files'][path]
            require(record['blob_oid'] == actual['oid'], 'BLOB_OID: ' + path)
            require(record['blob_sha256'] == digest(raw), 'BLOB_SHA256: ' + path)
            require(record['blob_bytes'] == len(raw), 'BLOB_SIZE: ' + path)
            require(record['mode'] == actual['mode'] == '100644', 'FILE_MODE: ' + path)
            require(record['attributes'] == attributes[path], 'INDEX_ATTRIBUTES: ' + path)
        require(work_attrs[path] == attributes[path], 'WORK_ATTRIBUTES: ' + path)
        absolute = view.root / path
        require(absolute.is_file() and not absolute.is_symlink(), 'MISSING_OR_SYMLINK_WORK_PATH: ' + path)
        require(canonical_work(absolute.read_bytes(), attributes[path]) == raw, 'WORK_BLOB_CONTENT: ' + path)
    for path, previous in policy['unchanged_original128_blobs'].items():
        require(view.entries[path]['oid'] == previous['oid'] and digest(view.blob(path)) == previous['sha256']
                and len(view.blob(path)) == previous['bytes'], 'ORIGINAL128_BLOB_MUTATION: ' + path)
    for item in policy['preserve_raw_bytes']:
        path = item['path']
        require(attributes[path]['text'] == 'unset', 'RAW_ATTRIBUTES: ' + path)
        require(view.blob(path) == (view.root / path).read_bytes(), 'RAW_WORK_MUTATION: ' + path)
        require(digest(view.blob(path)) == item['blob_sha256'] and view.entries[path]['oid'] == item['blob_oid']
                and len(view.blob(path)) == item['bytes'], 'RAW_BLOB_MUTATION: ' + path)
    frozen = decode_json(view.blob('docs/acceptance/MS7-MIG-V02/frozen-ownership.json'), 'frozen')['checked_frozen_files']
    frozen_paths = [item['path'] for item in frozen]
    frozen_attrs = view.attributes(frozen_paths)
    view.load_blobs(frozen_paths)
    for item in frozen:
        path = item['path']
        base_blob = view.git('show', BASE + ':' + path)
        require(digest(base_blob) == item['input_blob_sha256'] == item['head_blob_sha256'] == digest(view.blob(path)), 'FROZEN_BLOB: ' + path)
        require(canonical_work((view.root / path).read_bytes(), frozen_attrs[path]) == canonical_work(base_blob, frozen_attrs[path]), 'FROZEN_WORK: ' + path)
    ordinary = diagnostic_check(view)
    cr_at_eol = diagnostic_check(view, True)
    validate_diagnostics(policy, ordinary, cr_at_eol)
    excludes = [item['path'] for item in policy['whitespace_exceptions']]
    scoped = diagnostic_check(view, exclusions=excludes)
    scoped_cr = diagnostic_check(view, True, excludes)
    require(scoped['exit_code'] == scoped_cr['exit_code'] == scoped['count'] == scoped_cr['count'] == 0, 'SCOPED_WHITESPACE_FAIL')
    return {'publication_paths': len(paths), 'raw_preserved': 73, 'whitespace_exceptions': 40,
            'frozen_unchanged': len(frozen), 'original128_blobs_unchanged': True,
            'ordinary': ordinary, 'cr-at-eol': cr_at_eol, 'scoped-ordinary': scoped, 'scoped-cr-at-eol': scoped_cr}


def validate_owner_anchor(view, policy_raw, anchor_path, anchor_digest):
    path = Path(anchor_path).resolve()
    require(not path.is_relative_to(view.root), 'ANCHOR_WITHIN_MUTABLE_CHECKOUT')
    raw = path.read_bytes()
    require(digest(raw) == anchor_digest, 'EXTERNAL_ANCHOR_DIGEST')
    anchor = decode_json(raw, 'anchor')
    require(anchor.get('owner') == 'Ruslan' and anchor.get('decision') == 'APPROVED', 'OWNER_DECISION_REQUIRED')
    require(anchor.get('policy_blob_sha256') == digest(policy_raw), 'OWNER_POLICY_DIGEST')
    require(anchor.get('verifier_blob_sha256') == digest(view.blob(VERIFIER)), 'OWNER_VERIFIER_DIGEST')
    require(anchor.get('manifest_blob_sha256') == digest(view.blob(MANIFEST)), 'OWNER_MANIFEST_DIGEST')
    require(Path(__file__).read_bytes().replace(b'\r\n', b'\n') == view.blob(VERIFIER), 'EXECUTED_VERIFIER_NOT_PINNED_SOURCE')
    return 'OWNER_EXCEPTION_APPROVED_BY_EXTERNAL_ANCHOR'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--ref', help='Optional Git tree/commit representation; no commit is created')
    parser.add_argument('--local-proposal', action='store_true', help='Technical conformance only; never owner approval')
    parser.add_argument('--owner-anchor', type=Path)
    parser.add_argument('--owner-anchor-sha256', help='Digest supplied by independently controlled CI/config, never by task evidence')
    args = parser.parse_args(argv)
    try:
        view = GitView(args.root, args.ref)
        raw = view.blob(POLICY)
        policy = validate_policy(raw)
        result = verify(view, policy)
        status = OWNER_PENDING
        if args.owner_anchor or args.owner_anchor_sha256:
            require(not args.local_proposal and args.owner_anchor and args.owner_anchor_sha256, 'OWNER_ANCHOR_ARGUMENTS')
            status = validate_owner_anchor(view, raw, args.owner_anchor, args.owner_anchor_sha256)
        result.update({'local_conformance': 'PASS', 'owner_exception_status': status,
                       'independent_joint_tamper_protection': 'REQUIRES_EXTERNAL_OWNER_CONTROLLED_EXECUTABLE_AND_ANCHOR',
                       'tested_implementation_sha': None, 'publication_status': 'PENDING_PUBLICATION'})
        print(json.dumps(result))
        return 0 if args.local_proposal or status != OWNER_PENDING else 3
    except (GateError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'local_conformance': 'FAIL', 'error': str(error), 'owner_exception_status': OWNER_PENDING}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
