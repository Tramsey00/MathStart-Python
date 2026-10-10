"""Preflight all PROTECT blockers, then apply baseline CASCADE/SET_NULL.

Caller owns transaction and ordered namespace/row locks. Bulk deletion uses one
combined plan: no mutations before the entire set has passed protection checks.
"""
from collections import defaultdict
from dataclasses import dataclass
import sqlalchemy as sa
from backend.models.baseline import metadata, SNAPSHOT


class ProtectedDeletion(RuntimeError):
    pass


class RestrictedDeletion(RuntimeError):
    pass


class DeletionPlanChanged(RuntimeError):
    pass


RELATIONS = [(m['table'], f['column'], f['relationship']['to_table'], f['relationship']['to_column'],
              f['relationship']['on_delete_service'])
             for m in SNAPSHOT['models'] for f in m['fields'] if 'relationship' in f]


def plan_deletion(session, table_name, identities):
    planned = defaultdict(set)
    root = metadata.tables[table_name]
    planned[table_name].update(session.scalars(sa.select(next(iter(root.primary_key)))
                                              .where(next(iter(root.primary_key)).in_(identities))))
    changed = True
    while changed:
        changed = False
        for child, column, parent, parent_key, action in RELATIONS:
            if action != 'CASCADE' or not planned[parent]:
                continue
            table = metadata.tables[child]
            pk = next(iter(table.primary_key))
            found = set(session.scalars(sa.select(pk).where(table.c[column].in_(planned[parent]))))
            if found - planned[child]:
                planned[child].update(found)
                changed = True
    # PROTECT always rejects, even if the protected child is in this same batch.
    for child, column, parent, parent_key, action in RELATIONS:
        if action not in {'PROTECT', 'RESTRICT'} or not planned[parent]:
            continue
        table = metadata.tables[child]
        pk = next(iter(table.primary_key))
        found = set(session.scalars(sa.select(pk).where(table.c[column].in_(planned[parent]))))
        if action == 'PROTECT' and found:
            raise ProtectedDeletion('Protected related evidence exists')
        if action == 'RESTRICT' and found - planned[child]:
            raise RestrictedDeletion('Restricted related evidence exists')
    return {name: frozenset(keys) for name, keys in planned.items() if keys}


@dataclass(frozen=True)
class CollectionPlan:
    deleted: dict
    set_null: dict
    locks: dict


def plan_collection(session, table_name, identities):
    deleted = plan_deletion(session, table_name, identities)
    set_null = {}
    locks = {name: set(keys) for name, keys in deleted.items()}
    for child, column, parent, parent_key, action in RELATIONS:
        if action == 'SET_NULL' and deleted.get(parent):
            table = metadata.tables[child]
            found = frozenset(session.scalars(sa.select(next(iter(table.primary_key)))
                    .where(table.c[column].in_(deleted[parent]))))
            if found:
                set_null[child, column] = found
                locks.setdefault(child, set()).update(found)
    # Deferred PostgreSQL FK checks can lock retained referenced parents after
    # SET_NULL updates. Include their complete reference closure BEFORE locking
    # any row, otherwise crossed pages can still invert parent/page locks at
    # COMMIT. This uses the same R02 table/stable-key order, not a retry/skip.
    changed = True
    while changed:
        changed = False
        for child, column, parent, parent_key, action in RELATIONS:
            if not locks.get(child):
                continue
            table = metadata.tables[child]
            references = set(session.scalars(sa.select(table.c[column]).where(
                next(iter(table.primary_key)).in_(locks[child]), table.c[column].is_not(None))))
            previous = locks.setdefault(parent, set())
            if references - previous:
                previous.update(references)
                changed = True
    return CollectionPlan(deleted, set_null, {name: frozenset(keys) for name, keys in locks.items() if keys})


def delete_collected(session, table_name, identities, *, locks=None):
    from .locks import TABLE_ORDER, OrderedLocks
    identities = tuple(identities)
    planned = plan_collection(session, table_name, identities)
    if session.bind.dialect.name == 'postgresql':
        locks = locks or OrderedLocks(session)
        acquired = {}
        for name in sorted(planned.locks, key=lambda n: TABLE_ORDER[n]):
            table = metadata.tables[name]
            if name == 'users_identityreceipt':
                acquired[name] = locks.receipts(table, planned.locks[name])
            else:
                order = {'users_studentprofile': 'user_id', 'content_lessonpublication': 'page_id'}.get(name)
                acquired[name] = locks.rows(table, planned.locks[name], order_column=order)
        # Repeat PROTECT/RESTRICT and both dependency sets under the acquired
        # locks. A changed plan requires rollback/restart at the outer boundary.
        current = plan_collection(session, table_name, identities)
        # A concurrent disjoint deletion may remove now-unneeded referenced
        # parents. A held superset is safe; changed mutations or any newly needed
        # lock are not. Never acquire a lower-ranked lock during revalidation.
        if (current.deleted != planned.deleted or current.set_null != planned.set_null or
                any(keys - acquired.get(name, frozenset()) for name, keys in current.locks.items())):
            raise DeletionPlanChanged('Restart outer transaction: related rows changed')
    for (child, column), keys in sorted(planned.set_null.items(), key=lambda item: (TABLE_ORDER[item[0][0]], item[0][1])):
        table = metadata.tables[child]
        session.execute(sa.update(table).where(next(iter(table.primary_key)).in_(keys)).values({column: None}))
    # Deferred physical FKs permit one atomic collector transaction. Delete leaf
    # tables first also supports explicit SQLite compatibility without deferral.
    for table in reversed(metadata.sorted_tables):
        if table.name in planned.deleted:
            pk = next(iter(table.primary_key))
            session.execute(sa.delete(table).where(pk.in_(planned.deleted[table.name])))
