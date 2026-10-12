"""Persistence operations only; no password/login/HTTP/publication behavior."""
from typing import Protocol, TypeVar
import sqlalchemy as sa

T = TypeVar('T')


class RepositoryPort(Protocol[T]):
    def get(self, identity) -> T | None: ...
    def add(self, entity: T) -> None: ...
    def save(self, entity: T, *, fields: set[str] | None = None) -> None: ...
    def import_historical(self, values: dict): ...


class Repository:
    def __init__(self, session, model):
        self.session, self.model = session, model

    def get(self, identity):
        return self.session.get(self.model, identity)

    def add(self, entity):
        if not isinstance(entity, self.model):
            raise TypeError('Wrong repository model')
        self.session.add(entity)

    def save(self, entity, *, fields=None):
        from backend.models.baseline import utc_now
        if fields is None:
            # Ordinary mapper pre-save rules run at flush, including inserts.
            self.session.add(entity)
            if sa.inspect(entity).persistent:
                # Django save() runs auto_now even when no attribute is dirty.
                for column in sa.inspect(self.model).columns:
                    if column.info.get('baseline_field', {}).get('auto_now'):
                        setattr(entity, column.name, utc_now())
            self.session.flush([entity])
            return
        table = sa.inspect(self.model).local_table
        state = sa.inspect(entity)
        if not state.persistent or not fields <= set(table.c.keys()) or fields & {c.name for c in table.primary_key}:
            raise ValueError('update_fields requires a persistent entity and non-PK columns')
        if not fields:
            return
        for column in table.c:
            if column.name in fields and column.info.get('baseline_field', {}).get('auto_now'):
                setattr(entity, column.name, utc_now())
        pk = next(iter(table.primary_key))
        with self.session.no_autoflush:
            self.session.execute(sa.update(table).where(pk == state.identity[0])
                                 .values(**{name: getattr(entity, name) for name in fields}))
        # Discard dirty excluded attributes just as a reload after Django's
        # save(update_fields=...) does; no later ORM flush can leak those writes.
        self.session.expire(entity)

    def import_historical(self, values):
        """Explicit Core import preserves supplied IDs and historical instants.

        Require every auto timestamp and PK rather than silently manufacturing
        history. Caller owns transaction, schema validation and source evidence.
        Ordinary add/save never opt out of mapper pre-save behavior.
        """
        table = sa.inspect(self.model).local_table
        required = {column.name for column in table.c if column.primary_key or
                    column.info.get('baseline_field', {}).get('auto_now_add') or
                    column.info.get('baseline_field', {}).get('auto_now')}
        if not required <= values.keys() or not values.keys() <= set(table.c.keys()):
            raise ValueError('Historical import requires explicit PK/auto timestamps and known columns')
        with self.session.no_autoflush:
            result = self.session.execute(sa.insert(table).values(**values))
        return result.inserted_primary_key[0]

    def update_fields(self, identity, values):
        table = sa.inspect(self.model).local_table
        if not set(values) <= set(table.c.keys()) or set(values) & {c.name for c in table.primary_key}:
            raise ValueError('Invalid field update')
        key = next(iter(table.primary_key))
        self.session.execute(sa.update(table).where(key == identity).values(**values))

    def bulk_update(self, identities, values):
        # Mirrors QuerySet.update: no implicit timestamp or collector behavior.
        table = sa.inspect(self.model).local_table
        key = next(iter(table.primary_key))
        if not set(values) <= set(table.c.keys()) or key.name in values:
            raise ValueError('Invalid bulk update')
        self.session.execute(sa.update(table).where(key.in_(identities)).values(**values))
