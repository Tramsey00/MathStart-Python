"""Read-only coherent active/committed/pending publication representation."""
from backend.content.editions import fingerprint
from backend.content.participant import check_database
from backend.content.releases import Descriptor, active_descriptor
from backend.content.participant import digest
from backend.infrastructure.http.transport import unavailable, missing, timestamp
from backend.models.baseline import ContentPage
from backend.staff.publication import authority_sample
from hashlib import sha256


def page_edition(release, page_id):
    page = release.pages.get(page_id)
    return {'release_id': release.descriptor.release_id, 'manifest_digest': release.descriptor.manifest_digest,
            'page_published': page is not None,
            'page_digest': sha256(release.page_raw[page_id]).hexdigest() if page else None,
            'canonical_path': page['seo']['canonical_path'] if page else None}


class PublicationObserver:
    def __init__(self, store, namespace='public'):
        self.store, self.namespace = store, namespace

    def __call__(self, uow, page_id):
        a, g, j, leased = authority_sample(uow, self.namespace)
        uow.session.expire_all()
        if uow.session.get(ContentPage, page_id) is None:
            raise missing()
        if g is None or a is None:
            raise unavailable()
        selected = active_descriptor(uow, self.namespace)
        if (selected.operation_id != a['operation_id'] or selected.release_id != a['release_id']
                or selected.manifest_digest != a['manifest_digest'] or selected.fence_generation != a['fence_generation']):
            raise unavailable()
        active = self.store.load(selected)
        committed = active
        if j is not None and j['db_committed']:
            committed = self.store.load(Descriptor(j['id'], j['release_id'], j['manifest_digest'], j['fence_generation']))
        if j is not None and j['plan'].get('version') == 'prepared-publication-v1':
            if j['namespace'] != self.namespace or digest(j['plan']) != j['plan_digest']:
                raise unavailable()
            expected = j['plan']['after_digest' if j['db_committed'] else 'before_digest']
            if fingerprint(uow.session) != expected:
                raise unavailable()
        check_database(uow.session, committed)
        pending = None
        if j is not None:
            # The frozen wire contract calls a failed public health probe
            # HEALTH_FAILED. The private journal retains its more precise code.
            failure = 'HEALTH_FAILED' if j['error_code'] == 'PUBLIC_VERIFICATION_FAILED' else j['error_code']
            pending = {'operation_id': str(j['id']), 'next_release': j['release_id'], 'manifest_digest': j['manifest_digest'],
                       'stage': j['phase'], 'failure_code': failure, 'updated_at': timestamp(j['updated_at']),
                       'fence_generation': j['fence_generation'], 'ownership': 'LEASED' if leased else 'TAKEOVER_ELIGIBLE',
                       'db_committed': j['db_committed'], 'activation_status': j['activation_status']}
        from sqlalchemy import select, func
        return {'page_id': page_id, 'observed_at': timestamp(uow.session.scalar(select(func.clock_timestamp()))),
                'state': 'RECOVERY_REQUIRED' if j is not None and j['phase'] == 'RECOVERY_REQUIRED' else 'PENDING' if j else 'IN_SYNC',
                'active': page_edition(active, page_id), 'db_edition': page_edition(committed, page_id), 'pending': pending}
