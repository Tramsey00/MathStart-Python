"""Exact content-table fingerprints and guarded prepared-edition updates.

Publisher plans contain full before/after rows, never arbitrary SQL or auth
tables. A null before row means an explicit, reviewed new content identity.
Preparation never consumes a sequence; inserts occur only under the P1 gate.
Sequence advancement is monotone and last, with ordinary PostgreSQL gaps after
an aborted transaction permitted. Rows/history are never deleted here.
"""
from datetime import datetime, timezone
from hashlib import sha256
import uuid
from itertools import groupby

import sqlalchemy as sa

from backend.content.build import encoded
from backend.content.publication import PublicationConflict
from backend.infrastructure.locks import TABLE_ORDER
from backend.models.baseline import metadata

TABLES = tuple(sorted((name for name in metadata.tables if name.startswith('content_')),
                      key=lambda name: TABLE_ORDER[name]))


def normalized(row):
    result = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            if value.tzinfo is None:
                raise PublicationConflict('INVALID_EDITION')
            value = value.astimezone(timezone.utc).isoformat(timespec='microseconds')
        elif isinstance(value, uuid.UUID):
            value = str(value)
        result[key] = value
    return result


def snapshot(session, *, lock=False):
    result = {}
    for name in TABLES:
        table = metadata.tables[name]
        query = sa.select(table).order_by(*table.primary_key.columns)
        if lock:
            query = query.with_for_update()
        result[name] = [normalized(row) for row in session.execute(query).mappings()]
    return result


def fingerprint(session, *, lock=False):
    return sha256(encoded(snapshot(session, lock=lock))).hexdigest()


def decoded(table, row):
    if not isinstance(row, dict) or set(row) != set(table.c.keys()):
        raise PublicationConflict('INVALID_EDITION')
    result = {}
    for column in table.c:
        value = row[column.name]
        if value is None:
            if not column.nullable:
                raise PublicationConflict('INVALID_EDITION')
        elif isinstance(column.type, sa.DateTime):
            if not isinstance(value, str):
                raise PublicationConflict('INVALID_EDITION')
            try:
                value = datetime.fromisoformat(value)
                if value.tzinfo is None:
                    raise ValueError()
            except ValueError:
                raise PublicationConflict('INVALID_EDITION') from None
        elif isinstance(column.type, sa.Uuid):
            try:
                value = uuid.UUID(value)
            except (TypeError, ValueError, AttributeError):
                raise PublicationConflict('INVALID_EDITION') from None
        elif isinstance(column.type, sa.Boolean):
            if type(value) is not bool:
                raise PublicationConflict('INVALID_EDITION')
        elif isinstance(column.type, sa.Integer):
            if type(value) is not int:
                raise PublicationConflict('INVALID_EDITION')
        elif isinstance(column.type, (sa.String, sa.Text)):
            if not isinstance(value, str):
                raise PublicationConflict('INVALID_EDITION')
        result[column.name] = value
    return result


def project_updates(before, changes):
    """Validate updates/inserts without SQL, sequences or filesystem effects."""
    from copy import deepcopy
    if not isinstance(before, dict) or set(before) != set(TABLES) or not isinstance(changes, list):
        raise PublicationConflict('INVALID_EDITION')
    result, rows = deepcopy(before), {}
    for name in TABLES:
        table = metadata.tables[name]
        indexed = {}
        for row in result[name]:
            canonical = normalized(decoded(table, row))
            keys = tuple(canonical[c.name] for c in table.primary_key)
            if keys in indexed or canonical != row:
                raise PublicationConflict('INVALID_EDITION')
            indexed[keys] = row
        rows[name] = indexed
    seen = set()
    for change in changes:
        if (not isinstance(change, dict) or set(change) != {'table', 'before', 'after'}
                or change['table'] not in TABLES):
            raise PublicationConflict('INVALID_EDITION')
        table = metadata.tables[change['table']]
        old = normalized(decoded(table, change['before'])) if change['before'] is not None else None
        new = normalized(decoded(table, change['after']))
        keys = tuple(new[c.name] for c in table.primary_key)
        if (old is not None and keys != tuple(old[c.name] for c in table.primary_key)
                or old is None and any(type(value) is not int or not 0 < value < 2**63 for value in keys)
                or (table.name, keys) in seen):
            raise PublicationConflict('INVALID_EDITION')
        seen.add((table.name, keys))
        current = rows[table.name].get(keys)
        if current != old:
            raise PublicationConflict('SOURCE_CONFLICT')
        if old is None:
            rows[table.name][keys] = new
        else:
            current.update(new)
    for name in TABLES:
        result[name] = [row for _, row in sorted(rows[name].items())]
    return result


def apply_updates(session, changes, before_digest, after_digest):
    """Called inside the P1 gate transaction; a caller must never commit alone.

    Sorted full content row locks follow the gate and precede journal rank9.
    Fingerprints include catalogue, media, redirects and publication metadata,
    so a stale plan cannot silently replace a concurrent runtime edit.
    """
    if not isinstance(changes, list):
        raise PublicationConflict('INVALID_EDITION')
    current_state = snapshot(session, lock=True)
    if sha256(encoded(current_state)).hexdigest() != before_digest:
        raise PublicationConflict('SOURCE_CONFLICT')
    # Validate all full rows, PK uniqueness and absence claims before any DML.
    project_updates(current_state, changes)
    prepared, seen = [], set()
    for change in changes:
        if not isinstance(change, dict) or set(change) != {'table', 'before', 'after'} or change['table'] not in TABLES:
            raise PublicationConflict('INVALID_EDITION')
        table = metadata.tables[change['table']]
        before = decoded(table, change['before']) if change['before'] is not None else None
        after = decoded(table, change['after'])
        keys = tuple(after[c.name] for c in table.primary_key)
        if (before is not None and keys != tuple(before[c.name] for c in table.primary_key)
                or (table.name, keys) in seen):
            raise PublicationConflict('INVALID_EDITION')
        seen.add((table.name, keys))
        predicate = sa.and_(*(c == after[c.name] for c in table.primary_key))
        current = session.execute(sa.select(table).where(predicate)).mappings().first()
        if ((before is None and current is not None)
                or before is not None and (current is None or normalized(current) != normalized(before))):
            raise PublicationConflict('SOURCE_CONFLICT')
        prepared.append((TABLE_ORDER[table.name], keys, table, predicate, after, before is None))
    inserted = set()
    ordered = sorted(prepared, key=lambda row: row[:2])
    # Consecutive inserts share a table/column set. Send them as one DBAPI batch
    # instead of one network roundtrip per bootstrap row, while retaining the
    # existing parent/PK order and every interleaved update's original position.
    for (_, name, is_insert), items in groupby(ordered, key=lambda row: (row[0], row[2].name, row[5])):
        batch = list(items)
        table = batch[0][2]
        if is_insert:
            session.execute(sa.insert(table), [row[4] for row in batch])
            inserted.add(name)
        else:
            for _, _, _, predicate, after, _ in batch:
                session.execute(sa.update(table).where(predicate).values(**after))
    if fingerprint(session) != after_digest:
        raise PublicationConflict('EDITION_CONFLICT')
    # Explicit prepared PKs must not collide with later ordinary ORM inserts.
    # setval cannot roll back: run only after complete row/fingerprint checks,
    # never in preparation/dry-run, and never rewind an already-ahead sequence.
    for name in sorted(inserted, key=lambda item: TABLE_ORDER[item]):
        table = metadata.tables[name]
        column = next(iter(table.primary_key))
        sequence = session.scalar(sa.text('SELECT pg_get_serial_sequence(:table_name,:column_name)'),
                                  {'table_name': name, 'column_name': column.name})
        if sequence is None:
            raise PublicationConflict('INVALID_EDITION')
        maximum = session.scalar(sa.select(sa.func.max(column)))
        session.execute(sa.text('SELECT setval(CAST(:sequence AS regclass), '
            'GREATEST(COALESCE(pg_sequence_last_value(CAST(:sequence AS regclass)), 0), :maximum), true)'),
            {'sequence': sequence, 'maximum': maximum})
