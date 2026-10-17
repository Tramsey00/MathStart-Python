"""Resolve a trusted output pin for the already selected immutable release."""
import re

import sqlalchemy as sa

from backend.content.build import encoded
from backend.content.publication import frozen
from backend.infrastructure.http.transport import unavailable
from backend.infrastructure.uow import UnitOfWork
from backend.models.protocol import PublicationJournal
from hashlib import sha256


class PublicationArtifactPins:
    def __init__(self, engine, initial_pins, namespace='public'):
        self.engine, self.initial, self.namespace = engine, dict(initial_pins), namespace

    def __call__(self, pin):
        # A render that selected R1 continues to resolve R1 even if R2 activates
        # concurrently. No lookup of the latest active pointer is performed.
        with UnitOfWork(self.engine) as uow:
            uow.session.execute(sa.text('SET TRANSACTION READ ONLY'))
            row = uow.session.scalar(sa.select(PublicationJournal).where(
                PublicationJournal.namespace == self.namespace,
                PublicationJournal.release_id == pin['release_id']))
            if (row is None or not row.db_committed or row.activation_status != 'APPLIED'
                    or row.manifest_digest != pin['manifest_digest']):
                raise unavailable()
            plan = frozen(row.plan)
            initial = self.initial.get(pin['release_id'])
            if plan.get('version') != 'prepared-publication-v1':
                # Explicit legacy initial pins remain usable, with their exact
                # descriptor/input binding checked by the ordinary renderer.
                if initial is None:
                    raise unavailable()
                return initial
            output = plan.get('output_manifest_digest')
            if (sha256(encoded(plan)).hexdigest() != row.plan_digest
                    or plan.get('release_id') != pin['release_id']
                    or plan.get('manifest_digest') != pin['manifest_digest']
                    or not isinstance(output, str) or not re.fullmatch('[a-f0-9]{64}', output)
                    or initial is not None and initial != output):
                raise unavailable()
            return output
