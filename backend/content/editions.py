"""Exact content-table fingerprints and guarded prepared-edition updates.

Publisher plans contain full before/after rows, never arbitrary SQL or auth
tables. This layer does not allocate IDs, delete content, update user data, or
pretend a dry-run can roll PostgreSQL sequences back. Fresh/bootstrap allocation
and reviewed source rendering are owned by the publisher's orchestration.
"""
from datetime import datetime
from hashlib import sha256
import uuid

import sqlalchemy as sa

from backend.content.build import encoded
from backend.content.publication import PublicationConflict
from backend.infrastructure.locks import TABLE_ORDER
from backend.models.baseline import metadata

TABLES = tuple(sorted((name for name in metadata.tables if name.startswith('content_')),
                      key=lambda name: TABLE_ORDER[name]))


def normalized(row):
    return {key: value.isoformat(timespec='microseconds') if isinstance(value, datetime)
            else str(value) if isinstance(value, uuid.UUID) else value for key, value in row.items()}


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


def apply_updates(session, changes, before_digest, after_digest):
    """Called inside the P1 gate transaction; a caller must never commit alone.

    Sorted full content row locks follow the gate and precede journal rank9.
    Fingerprints include catalogue, media, redirects and publication metadata,
    so a stale plan cannot silently replace a concurrent runtime edit.
    """
    if not isinstance(changes, list) or not changes:
        raise PublicationConflict('INVALID_EDITION')
    if fingerprint(session, lock=True) != before_digest:
        raise PublicationConflict('SOURCE_CONFLICT')
    prepared, seen = [], set()
    for change in changes:
        if not isinstance(change, dict) or set(change) != {'table', 'before', 'after'} or change['table'] not in TABLES:
            raise PublicationConflict('INVALID_EDITION')
        table = metadata.tables[change['table']]
        before, after = decoded(table, change['before']), decoded(table, change['after'])
        keys = tuple(before[c.name] for c in table.primary_key)
        if keys != tuple(after[c.name] for c in table.primary_key) or (table.name, keys) in seen:
            raise PublicationConflict('INVALID_EDITION')
        seen.add((table.name, keys))
        predicate = sa.and_(*(c == before[c.name] for c in table.primary_key))
        current = session.execute(sa.select(table).where(predicate)).mappings().first()
        if current is None or normalized(current) != normalized(before):
            raise PublicationConflict('SOURCE_CONFLICT')
        prepared.append((TABLE_ORDER[table.name], keys, table, predicate, after))
    for _, _, table, predicate, after in sorted(prepared, key=lambda row: row[:2]):
        session.execute(sa.update(table).where(predicate).values(**after))
    if fingerprint(session) != after_digest:
        raise PublicationConflict('EDITION_CONFLICT')
