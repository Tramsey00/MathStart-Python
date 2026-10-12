"""R02 total order. Services acquire needed locks, never restart inside a UoW."""
from hashlib import sha256
import sqlalchemy as sa

TABLE_ORDER = {
    'target_publication_gate': (1, 0), 'auth_user': (3, 0),
    'auth_group': (4, 0), 'auth_user_groups': (4, 1),
    'auth_user_user_permissions': (4, 2), 'auth_group_permissions': (4, 3),
    'auth_permission': (4, 4), 'django_content_type': (4, 5), 'django_admin_log': (4, 6),
    'users_identityreceipt': (4, 7), 'target_receipt_bridge': (4, 8), 'target_session': (4, 9),
    'users_studentprofile': (5, 0), 'content_grade': (6, 0),
    'content_subject': (6, 1), 'content_section': (6, 2),
    'content_contentpage': (7, 0), 'content_lessonpublication': (7, 1),
    'content_mediaasset': (8, 0), 'content_redirect': (8, 1),
    'target_publication_journal': (9, 0), 'target_active_release': (9, 1),
}


class LockOrderViolation(RuntimeError):
    pass


class OrderedLocks:
    def __init__(self, session):
        self.session = session
        self.previous = (0, 0, ())

    def _advance(self, token):
        if token < self.previous:
            raise LockOrderViolation('Restart at outer orchestration boundary: lock order inversion')
        self.previous = token

    def namespace(self, domain, scope):
        self._advance((2, 0, (domain, scope)))
        if self.session.bind.dialect.name != 'postgresql':
            raise RuntimeError('Namespace locks require PostgreSQL')
        digest = sha256((domain + '\0' + scope).encode()).digest()[:8]
        self.session.execute(sa.text('SELECT pg_advisory_xact_lock(:key)'),
                             {'key': int.from_bytes(digest, 'big', signed=True)})

    def rows(self, table, keys, *, order_column=None):
        if table.name == 'users_loginwindow':
            raise LockOrderViolation('LoginWindow requires an independent budget transaction')
        if self.session.bind.dialect.name != 'postgresql':
            raise RuntimeError('Row locks require PostgreSQL')
        if table.name == 'users_identityreceipt':
            return self.receipts(table, keys)
        rank, subrank = TABLE_ORDER[table.name]
        pk = next(iter(table.primary_key))
        required_order = {'users_studentprofile': 'user_id', 'content_lessonpublication': 'page_id'}.get(table.name, pk.name)
        if order_column is not None and order_column != required_order:
            raise LockOrderViolation('Row order must match the R02 stable key')
        order = table.c[required_order]
        rows = self.session.execute(sa.select(table).where(pk.in_(keys)).order_by(order)).mappings().all()
        acquired = set()
        for row in rows:
            if table.name == 'users_identityreceipt':
                stable = tuple(row[name] for name in ('scope', 'operation', 'key_digest'))
            elif table.name == 'users_studentprofile':
                stable = (row['user_id'],)
            elif table.name == 'content_lessonpublication':
                stable = (row['page_id'],)
            else:
                stable = (row[order.name],)
            self._advance((rank, subrank, stable))
            acquired.update(self.session.scalars(sa.select(pk).where(pk == row[pk.name]).with_for_update()))
        return frozenset(acquired)

    def receipts(self, table, keys):
        rows = self.session.execute(sa.select(table).where(table.c.id.in_(keys))
                                    .order_by(table.c.scope, table.c.operation, table.c.key_digest)).mappings().all()
        acquired = set()
        for row in rows:
            self._advance((4, 7, (row['scope'], row['operation'], row['key_digest'])))
            acquired.update(self.session.scalars(sa.select(table.c.id).where(table.c.id == row['id']).with_for_update()))
        return frozenset(acquired)
