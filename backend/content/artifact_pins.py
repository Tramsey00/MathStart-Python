"""Resolve a trusted output pin for the already selected immutable release."""
import re
from collections import OrderedDict
from threading import RLock
from time import monotonic

import sqlalchemy as sa

from backend.content.build import encoded
from backend.infrastructure.http.transport import unavailable
from backend.infrastructure.uow import UnitOfWork
from backend.models.protocol import PublicationJournal
from hashlib import sha256


class PublicationArtifactPins:
    def __init__(self, engine, initial_pins, namespace='public'):
        self.engine, self.initial, self.namespace = engine, dict(initial_pins), namespace
        self._verified, self._lock = OrderedDict(), RLock()

    def _verify(self, row, pin):
        if (row is None or not row['db_committed'] or row['activation_status'] != 'APPLIED'
                or row['manifest_digest'] != pin['manifest_digest']):
            raise unavailable()
        plan = row['plan']
        initial = self.initial.get(pin['release_id'])
        if not isinstance(plan, dict):
            raise unavailable()
        if plan.get('version') != 'prepared-publication-v1':
            if initial is None:
                raise unavailable()
            return initial
        output = plan.get('output_manifest_digest')
        if (sha256(encoded(plan)).hexdigest() != row['plan_digest']
                or plan.get('release_id') != pin['release_id']
                or plan.get('manifest_digest') != pin['manifest_digest']
                or not isinstance(output, str) or not re.fullmatch('[a-f0-9]{64}', output)
                or initial is not None and initial != output):
            raise unavailable()
        return output

    def __call__(self, pin):
        # A render that selected R1 continues to resolve R1 even if R2 activates
        # concurrently. No lookup of the latest active pointer is performed.
        with UnitOfWork(self.engine) as uow:
            uow.session.execute(sa.text('SET TRANSACTION READ ONLY'))
            table = PublicationJournal.__table__
            predicate = sa.and_(table.c.namespace == self.namespace, table.c.release_id == pin['release_id'])
            if self.engine.dialect.name != 'postgresql':
                return self._verify(uow.session.execute(sa.select(table).where(predicate)).mappings().first(), pin)
            # Recheck committed authority on EVERY call. PostgreSQL changes xmin
            # on any UPDATE, including a changed plan with an unchanged digest.
            # ctid and a short bounded lifetime also prevent long-lived xid reuse.
            columns = [table.c.id, table.c.db_committed, table.c.activation_status,
                       table.c.release_id, table.c.manifest_digest, table.c.plan_digest,
                       sa.literal_column('xmin::text').label('row_xid'),
                       sa.literal_column('ctid::text').label('row_tid')]
            row = uow.session.execute(sa.select(*columns).where(predicate)).mappings().first()
            if (row is None or not row['db_committed'] or row['activation_status'] != 'APPLIED'
                    or row['manifest_digest'] != pin['manifest_digest']):
                raise unavailable()
            key = (*row.values(), self.initial.get(pin['release_id']))
            with self._lock:
                hit = self._verified.get(key)
                if hit is not None and monotonic() - hit[0] < 30:
                    self._verified.move_to_end(key)
                    return hit[1]
            # The next READ COMMITTED statement may see a newer row. Bind the
            # verification/cache key to that same full-row statement, never the
            # metadata snapshot above. No lock is held during DB or hashing.
            row = uow.session.execute(sa.select(*columns, table.c.plan).where(predicate)).mappings().first()
            output = self._verify(row, pin)
            key = (*[row[name] for name in row if name != 'plan'], self.initial.get(pin['release_id']))
            with self._lock:
                self._verified[key] = (monotonic(), output)
                self._verified.move_to_end(key)
                while len(self._verified) > 16:
                    self._verified.popitem(last=False)
            return output
