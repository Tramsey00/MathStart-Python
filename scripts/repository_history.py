"""Explicit current documentation retirement; no wildcard history fallback."""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
import subprocess

SOURCE = 'b29a7ccdd07784cfcfd19278cbe59b30c83cd4ea'
MANIFEST = 'specs/maintenance/repository-cleanup.json'


@lru_cache(maxsize=8)
def _original_metadata(root, names):
    # Git objects at SOURCE are immutable; only these original digests are cached.
    # Current working files are checked afresh on every repository_changes call.
    result = subprocess.run(['git', 'cat-file', '--batch'], cwd=root,
                            input=''.join(SOURCE + ':' + name + '\n' for name in names).encode(),
                            capture_output=True, check=True, timeout=60).stdout
    metadata = {}
    offset = 0
    for name in names:
        end = result.index(b'\n', offset)
        fields = result[offset:end].split()
        if len(fields) != 3 or fields[1] != b'blob':
            raise ValueError('Cleanup source blob missing: ' + name)
        size = int(fields[2])
        raw = result[end + 1:end + 1 + size]
        metadata[name] = (size, hashlib.sha256(raw).hexdigest())
        offset = end + size + 2
    return metadata


def repository_changes(root):
    root = Path(root).resolve()
    path = root / MANIFEST
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('source_commit') != SOURCE or not data.get('authority'):
        raise ValueError('Unexpected repository cleanup authority/source')
    rows = data['files']
    if len({r['path'] for r in rows}) != len(rows):
        raise ValueError('Duplicate repository cleanup path')
    for row in rows:
        name = row['path']
        target = root / name
        if not name or Path(name).is_absolute() or '..' in Path(name).parts or not target.resolve().is_relative_to(root):
            raise ValueError('Repository cleanup path escaped')
        if not row.get('reason') or row['action'] not in {'removed', 'updated'}:
            raise ValueError('Invalid repository cleanup disposition')
        if target.is_symlink():
            raise ValueError('Cleanup destination is a symlink: ' + name)
        if row['action'] == 'removed':
            if target.exists():
                raise ValueError('Retired document reintroduced: ' + name)
        elif not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != row['after_sha256']:
            raise ValueError('Unreviewed repository change: ' + name)
    originals = _original_metadata(str(root), tuple(row['path'] for row in rows))
    for row in rows:
        size, digest = originals[row['path']]
        if size != row['before_bytes'] or digest != row['before_sha256']:
            raise ValueError('Cleanup original bytes changed: ' + row['path'])
    return {row['path']: row for row in rows}


def retired_document(path, root):
    row = repository_changes(root).get(path)
    if row is None or row['action'] != 'removed':
        raise ValueError('Not an explicitly retired document: ' + path)
    return subprocess.check_output(['git', 'show', SOURCE + ':' + path], cwd=root)


def verify_document_translations(root):
    """Bind translated future requirements to the same source and exact reviewed text."""
    root = Path(root)
    data = json.loads((root / MANIFEST).read_text(encoding='utf-8'))
    row = data.get('requirements_translation', {})
    if (row.get('path') != 'specs/product/learning-requirements.md' or
            row.get('language') != 'ru' or row.get('source_commit') != SOURCE or
            row.get('source_path') != 'docs/specifications/technical-spec-v7.2-draft.md' or
            row.get('sections') != [6, 7, 8, 9, 10, 11, 14, 15, 16]):
        raise ValueError('Unreviewed requirements translation source')
    if hashlib.sha256((root / row['path']).read_bytes()).hexdigest() != row.get('after_sha256'):
        raise ValueError('Unreviewed translated requirements text')
