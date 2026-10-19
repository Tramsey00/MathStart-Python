"""Explicit retired evidence access; current content never falls back to history."""
import json
from scripts.check_migration_preservation import ROOT, dispositions, historical_artifact


def retired_bytes(path, root=ROOT):
    row = dispositions(root).get(path)
    if row is None or row['action'] not in {'removed', 'moved', 'moved_updated'}:
        raise ValueError('Not an explicitly retired artifact: ' + path)
    if (root / path).exists() or (root / path).is_symlink():
        raise ValueError('Retired artifact reintroduced: ' + path)
    return historical_artifact(path, root)


def retired_json(path, root=ROOT):
    return json.loads(retired_bytes(path, root))
