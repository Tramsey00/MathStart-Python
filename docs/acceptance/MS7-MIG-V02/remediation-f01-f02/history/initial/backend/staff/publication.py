"""V02 coherent read boundary; V04 owns edition representation and activation."""
from datetime import datetime, timezone

import sqlalchemy as sa

from backend.models.protocol import active, gate, journal
from backend.infrastructure.http.contracts import validate
from backend.infrastructure.http.transport import unavailable


def authority_sample(uow, namespace):
    # Core selects avoid the ORM identity map caching the first authority read.
    a = uow.session.execute(sa.select(active).where(active.c.namespace == namespace)).mappings().first()
    g = uow.session.execute(sa.select(gate).where(gate.c.namespace == namespace)).mappings().first()
    j = None
    if g and g['pending_operation_id']:
        j = uow.session.execute(sa.select(journal).where(journal.c.id == g['pending_operation_id'])).mappings().first()
    now = uow.session.scalar(sa.select(sa.func.clock_timestamp())) if uow.session.bind.dialect.name == 'postgresql' else datetime.now(timezone.utc)
    leased = None
    if g and g['lease_until']:
        lease = g['lease_until']
        if lease.tzinfo is None and uow.session.bind.dialect.name == 'sqlite':
            lease = lease.replace(tzinfo=timezone.utc)
        leased = lease > now
    return (dict(a) if a else None, dict(g) if g else None, dict(j) if j else None, leased)


def observe(uow, page_id, namespace, edition_reader):
    if edition_reader is None:
        raise unavailable()
    for _ in range(3):
        before = authority_sample(uow, namespace)
        # V04 provider reads immutable active/DB editions, never a mixed DB/files view.
        data = edition_reader(uow, page_id)
        after = authority_sample(uow, namespace)
        if before != after:
            continue
        validate(data, 'PublicationObservableState', True)
        a, g, j, leased = after
        if g is None:
            raise unavailable()
        if data['page_id'] != page_id:
            raise unavailable()
        if data['active'] is not None:
            if (a is None or data['active']['release_id'] != a['release_id']
                    or data['active']['manifest_digest'] != a['manifest_digest']):
                raise unavailable()
        if j is not None:
            if (g is None or g['owner_id'] != j['owner_id'] or g['fence_generation'] != j['fence_generation']
                    or g['lease_until'] != j['lease_until']):
                raise unavailable()
            p = data['pending']
            if (p is None or p['operation_id'] != str(j['id']) or p['next_release'] != j['release_id']
                    or p['manifest_digest'] != j['manifest_digest'] or p['stage'] != j['phase']
                    or p['fence_generation'] != g['fence_generation'] or p['db_committed'] != j['db_committed']
                    or p['activation_status'] != j['activation_status']
                    or p['ownership'] != ('LEASED' if leased else 'TAKEOVER_ELIGIBLE')):
                raise unavailable()
            if p['db_committed'] and (data['db_edition']['release_id'] != p['next_release']
                    or data['db_edition']['manifest_digest'] != p['manifest_digest']):
                raise unavailable()
        elif data['pending'] is not None:
            raise unavailable()
        if data['state'] == 'IN_SYNC' and data['active'] != data['db_edition']:
            raise unavailable()
        return data
    raise unavailable()
