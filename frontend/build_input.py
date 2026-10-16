"""Validate the trusted handoff receipt before interpreting any build inputs."""
from hashlib import sha256
import json
from pathlib import Path
from uuid import UUID
from backend.content.releases import Descriptor, ReleaseStore, inside


def verified_release(input_root, release_id, manifest_digest, receipt_digest):
    if not isinstance(receipt_digest, str) or len(receipt_digest) != 64:
        raise ValueError('Trusted build receipt digest required')
    root = inside(input_root, release_id)
    raw = inside(root, 'receipt.json').read_bytes()
    if sha256(raw).hexdigest() != receipt_digest:
        raise ValueError('Build receipt digest mismatch')
    receipt = json.loads(raw)
    if (receipt.get('version') != 'build-input-receipt-v1'
            or receipt.get('release_id') != release_id
            or receipt.get('manifest_digest') != manifest_digest):
        raise ValueError('Build receipt identity mismatch')
    seen = set()
    for item in receipt['files']:
        if item['path'] in seen:
            raise ValueError('Duplicate receipt file')
        seen.add(item['path'])
        payload = inside(root, item['path']).read_bytes()
        if len(payload) != item['size'] or sha256(payload).hexdigest() != item['sha256']:
            raise ValueError('Build input bytes mismatch')
    actual = {p.relative_to(root).as_posix() for p in Path(root).rglob('*') if p.is_file()} - {'receipt.json'}
    if actual != seen or 'index.json' not in seen:
        raise ValueError('Build input coverage mismatch')
    release=ReleaseStore(input_root).load(Descriptor(UUID(int=0), release_id, manifest_digest, 1))
    if (receipt.get('pages') != len(release.pages)
            or receipt.get('topics') != sum(p['page_type']=='topic' for p in release.pages.values())
            or receipt.get('assets') != len(release.assets)):
        raise ValueError('Build receipt coverage counts mismatch')
    return release
