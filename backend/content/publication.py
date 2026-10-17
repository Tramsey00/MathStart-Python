"""PostgreSQL P1 authority for the publisher's domain/artifact participant.

This is an internal service, not an HTTP API or an alternate filesystem pointer.
The participant owns content snapshots, reviewed immutable staging and public
probes. Slow staging/probes run outside transactions; their exact operation and
plan receipts are rechecked under the current fence before accepting results.
"""
from dataclasses import dataclass
from datetime import timedelta
from hashlib import sha256
import json
import re
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from backend.content.build import encoded
from backend.infrastructure.uow import UnitOfWork
from backend.models.protocol import (PublicationGate as Gate, PublicationJournal as Journal,
                                    ActiveReleaseDescriptor as Active, PublicationHistory as History)

TERMINAL = {'COMPLETE', 'FAILED_PRECOMMIT'}
DESCRIPTOR_FIELDS = ('operation_id', 'release_id', 'manifest_digest', 'fence_generation')


class PublicationConflict(RuntimeError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)  # Never put private plan/owner/path data in errors.


@dataclass(frozen=True)
class OwnerToken:
    namespace: str
    operation_id: uuid.UUID
    owner_id: uuid.UUID
    generation: int


@dataclass(frozen=True)
class WorkReceipt:
    operation_id: uuid.UUID
    owner_id: uuid.UUID
    generation: int
    plan_digest: str
    release_id: str
    manifest_digest: str
    # Nonempty digest of the participant's complete staged/public verification.
    verification_digest: str


def descriptor(row):
    if row is None:
        return None
    return {name: str(getattr(row, name)) if name == 'operation_id' else getattr(row, name)
            for name in DESCRIPTOR_FIELDS}


def frozen(value):
    return json.loads(encoded(value))


def now(session):
    return session.scalar(sa.select(sa.func.clock_timestamp()))


def token_for(row):
    return OwnerToken(row.namespace, row.id, row.owner_id, row.fence_generation)


class PublisherAuthority:
    def __init__(self, engine, participant, *, lease_seconds=60):
        if engine.dialect.name != 'postgresql':
            raise ValueError('Publication authority requires PostgreSQL')
        if type(lease_seconds) is not int or not 1 <= lease_seconds <= 3600:
            raise ValueError('Positive bounded publication lease required')
        if not all(callable(getattr(participant, name, None)) for name in
                   ['check_admission', 'apply', 'stage', 'verify_stage', 'verify_public', 'check_complete']):
            raise ValueError('Complete publisher participant required')
        self.engine, self.participant = engine, participant
        self.lease = timedelta(seconds=lease_seconds)

    def _gate(self, session, namespace, *, create=False):
        if not isinstance(namespace, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,120}', namespace):
            raise ValueError('Explicit publication namespace required')
        if create:
            table = sa.inspect(Gate).local_table
            session.execute(insert(table).values(namespace=namespace, fence_generation=0)
                            .on_conflict_do_nothing(index_elements=['namespace']))
        row = session.scalar(sa.select(Gate).where(Gate.namespace == namespace).with_for_update())
        if row is None:
            raise PublicationConflict('MISSING_GATE')
        return row

    def _guard(self, session, gate, token, operation):
        # Call again immediately before the guarded write/flush. Time read
        # before a row-lock wait cannot establish an unexpired lease.
        if (gate.pending_operation_id != token.operation_id or gate.owner_id != token.owner_id
                or gate.fence_generation != token.generation or gate.lease_until is None
                or gate.lease_until <= now(session) or operation is None
                or operation.owner_id != token.owner_id or operation.fence_generation != token.generation
                or operation.namespace != token.namespace or operation.lease_until != gate.lease_until
                or operation.phase in TERMINAL):
            raise PublicationConflict('FENCED')

    def _owned(self, session, token):
        gate = self._gate(session, token.namespace)
        operation = session.get(Journal, token.operation_id)
        self._guard(session, gate, token, operation)
        return gate, operation

    def _write_guard(self, session, token, *, clear=False, renew=False, surrender=False):
        """Final SQL linearization barrier, after all domain/journal flushes.

        A SELECT-time lease check alone leaves a gap before guarded DML. This
        conditional write uses DB time at the statement and rolls the entire
        unit of work back on expiry, including already-flushed domain writes.
        """
        table = sa.inspect(Gate).local_table
        values = {'fence_generation': token.generation}
        if clear:
            values.update(pending_operation_id=None, owner_id=None, lease_until=None)
        elif renew:
            values['lease_until'] = sa.func.clock_timestamp() if surrender else sa.func.clock_timestamp() + self.lease
        result = session.execute(sa.update(table).where(
            table.c.namespace == token.namespace, table.c.pending_operation_id == token.operation_id,
            table.c.owner_id == token.owner_id, table.c.fence_generation == token.generation,
            table.c.lease_until > sa.func.clock_timestamp()).values(**values).returning(table.c.lease_until)).first()
        if result is None:
            raise PublicationConflict('FENCED')
        return result[0]

    def _record(self, session, operation, phase, error=None):
        operation.phase, operation.error_code, operation.updated_at = phase, error, now(session)
        session.add(History(operation_id=operation.id, owner_id=operation.owner_id,
                            fence_generation=operation.fence_generation, phase=phase,
                            recorded_at=operation.updated_at, error_code=error))

    def _advance_generation(self, gate):
        if gate.fence_generation >= 2**63 - 1:
            raise PublicationConflict('FENCE_EXHAUSTED')
        gate.fence_generation += 1

    def claim(self, namespace, key, plan, owner):
        plan = frozen(plan)
        if (not isinstance(key, str) or not key or not isinstance(owner, uuid.UUID)
                or not isinstance(plan, dict) or not {'release_id', 'manifest_digest', 'previous'}.issubset(plan)
                or not isinstance(plan['release_id'], str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,120}', plan['release_id'])
                or not isinstance(plan['manifest_digest'], str) or not re.fullmatch(r'[a-f0-9]{64}', plan['manifest_digest'])):
            raise ValueError('Explicit frozen publication identity required')
        digest, key_digest = sha256(encoded(plan)).hexdigest(), sha256(key.encode()).hexdigest()
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            gate = self._gate(s, namespace, create=True)
            existing = s.scalar(sa.select(Journal).where(Journal.namespace == namespace, Journal.key_digest == key_digest))
            if existing:
                if existing.plan_digest != digest:
                    raise PublicationConflict('IDEMPOTENCY_CONFLICT')
                if existing.phase not in TERMINAL and existing.owner_id != owner:
                    raise PublicationConflict('OWNER_BUSY')
                # Lookup is read-only, even after later publications. Returning
                # an old token never grants it authority to change current.
                return token_for(existing), existing.phase
            if gate.pending_operation_id is not None:
                raise PublicationConflict('BUSY')
            if s.scalar(sa.select(Journal.id).where(Journal.namespace == namespace, Journal.release_id == plan['release_id'])):
                raise PublicationConflict('RELEASE_CONFLICT')
            active = s.get(Active, namespace)
            if descriptor(active) != plan['previous']:
                raise PublicationConflict('POINTER_CONFLICT')
            if active is not None:
                prior = s.get(Journal, active.operation_id)
                if (prior is None or prior.phase != 'COMPLETE' or not prior.db_committed
                        or prior.activation_status != 'APPLIED' or prior.release_id != active.release_id
                        or prior.manifest_digest != active.manifest_digest):
                    raise PublicationConflict('EDITION_CONFLICT')
            # Concrete participant verifies active==DB and expected source.
            self.participant.check_admission(s, frozen(plan))
            self._advance_generation(gate)
            instant = now(s)
            operation = Journal(id=uuid.uuid4(), namespace=namespace, key_digest=key_digest,
                plan_digest=digest, plan=plan, release_id=plan['release_id'], manifest_digest=plan['manifest_digest'],
                owner_id=owner, fence_generation=gate.fence_generation, lease_until=instant + self.lease,
                phase='VALIDATED', db_committed=False, activation_status='NOT_STARTED',
                error_code=None, created_at=instant, updated_at=instant)
            s.add(operation)
            gate.pending_operation_id, gate.owner_id, gate.lease_until = operation.id, owner, operation.lease_until
            self._record(s, operation, 'VALIDATED')
            s.flush()
            self._write_guard(s, token_for(operation))
            uow.commit()
            return token_for(operation), operation.phase

    def inspect(self, token):
        with UnitOfWork(self.engine) as uow:
            row = uow.session.get(Journal, token.operation_id)
            if row is None or row.namespace != token.namespace:
                raise PublicationConflict('MISSING_OPERATION')
            return {'token': token_for(row), 'phase': row.phase, 'db_committed': row.db_committed,
                    'activation_status': row.activation_status, 'plan': frozen(row.plan), 'plan_digest': row.plan_digest}

    def renew(self, token, *, surrender=False):
        with UnitOfWork(self.engine) as uow:
            gate, row = self._owned(uow.session, token)
            row.lease_until = self._write_guard(uow.session, token, renew=True, surrender=surrender)
            row.updated_at = now(uow.session)
            uow.commit()

    def takeover(self, namespace, operation_id, observed_generation, owner):
        if not isinstance(owner, uuid.UUID) or type(observed_generation) is not int:
            raise ValueError('Observed generation and recovery owner required')
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            gate = self._gate(s, namespace)
            if gate.pending_operation_id != operation_id or gate.fence_generation != observed_generation:
                raise PublicationConflict('CLAIM_CONFLICT')
            row = s.get(Journal, operation_id)
            if row is None or row.phase in TERMINAL:
                raise PublicationConflict('CLAIM_CONFLICT')
            if (row.owner_id != gate.owner_id or row.fence_generation != gate.fence_generation
                    or row.lease_until != gate.lease_until):
                raise PublicationConflict('CLAIM_CONFLICT')
            if gate.lease_until is None or gate.lease_until > now(s):
                raise PublicationConflict('OWNER_BUSY')
            self._advance_generation(gate)
            gate.owner_id = row.owner_id = owner
            row.fence_generation = gate.fence_generation
            gate.lease_until = row.lease_until = now(s) + self.lease
            self._record(s, row, 'RECOVERY_REQUIRED' if row.db_committed else row.phase,
                         'OWNER_LOST' if row.db_committed else None)
            s.flush()
            self._write_guard(s, token_for(row))
            uow.commit()
            return token_for(row)

    def _receipt(self, row, receipt):
        if (type(receipt) is not WorkReceipt or receipt.operation_id != row.id
                or receipt.owner_id != row.owner_id or receipt.generation != row.fence_generation
                or receipt.plan_digest != row.plan_digest or receipt.release_id != row.release_id
                or receipt.manifest_digest != row.manifest_digest
                or not re.fullmatch(r'[a-f0-9]{64}', receipt.verification_digest)):
            raise PublicationConflict('VERIFICATION_CONFLICT')

    def stage(self, token):
        # Verify ownership before starting effects, then accept only under the
        # same current token. Participant may only write immutable owned paths.
        with UnitOfWork(self.engine) as uow:
            _, row = self._owned(uow.session, token)
            if row.phase not in {'VALIDATED', 'STAGED'}:
                raise PublicationConflict('INVALID_PHASE')
            plan, digest = frozen(row.plan), row.plan_digest
        receipt = self.participant.stage(token, plan, digest)
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            gate, row = self._owned(s, token)
            self._receipt(row, receipt)
            if row.phase not in {'VALIDATED', 'STAGED'}:
                raise PublicationConflict('INVALID_PHASE')
            self._guard(s, gate, token, row)
            if row.phase != 'STAGED':
                self._record(s, row, 'STAGED')
            s.flush()
            self._write_guard(s, token)
            uow.commit()
        return receipt

    def commit(self, token):
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            gate, row = self._owned(s, token)
            if row.db_committed:
                return row.phase  # Never call domain apply twice after lost ACK.
            if row.phase != 'STAGED':
                raise PublicationConflict('INVALID_PHASE')
            if descriptor(s.get(Active, token.namespace)) != row.plan['previous']:
                raise PublicationConflict('POINTER_CONFLICT')
            self.participant.apply(s, frozen(row.plan))
            self._guard(s, gate, token, row)
            row.db_committed = True
            self._record(s, row, 'DB_COMMITTED')
            s.flush()
            self._write_guard(s, token)
            uow.commit()
            return row.phase

    def intent(self, token):
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            gate, row = self._owned(s, token)
            if row.phase not in {'DB_COMMITTED', 'ACTIVATING'} or not row.db_committed:
                raise PublicationConflict('INVALID_PHASE')
            self._guard(s, gate, token, row)
            if row.phase != 'ACTIVATING':
                row.activation_status = 'UNKNOWN'
                self._record(s, row, 'ACTIVATING')
            s.flush()
            self._write_guard(s, token)
            uow.commit()

    def _is_next(self, active, row):
        return (active is not None and active.operation_id == row.id and active.release_id == row.release_id
                and active.manifest_digest == row.manifest_digest and 0 < active.fence_generation <= row.fence_generation)

    def activate(self, token):
        # Stage verification can be repeated without rebuilding. This must
        # revalidate finalized bytes, not infer integrity from mtime/size.
        with UnitOfWork(self.engine) as uow:
            _, row = self._owned(uow.session, token)
            if row.phase not in {'ACTIVATING', 'ACTIVATED'}:
                raise PublicationConflict('INVALID_PHASE')
            plan, digest = frozen(row.plan), row.plan_digest
        receipt = self.participant.verify_stage(token, plan, digest)
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            gate, row = self._owned(s, token)
            self._receipt(row, receipt)
            if row.phase not in {'ACTIVATING', 'ACTIVATED'} or not row.db_committed:
                raise PublicationConflict('INVALID_PHASE')
            active = s.get(Active, token.namespace)
            if row.phase == 'ACTIVATED' and self._is_next(active, row):
                return 'ALREADY_ACTIVATED'
            if not self._is_next(active, row):
                if descriptor(active) != row.plan['previous']:
                    raise PublicationConflict('POINTER_CONFLICT')
                self._guard(s, gate, token, row)
                if active is None:
                    active = Active(namespace=token.namespace)
                    s.add(active)
                active.operation_id, active.release_id = row.id, row.release_id
                active.manifest_digest, active.fence_generation = row.manifest_digest, token.generation
            self._guard(s, gate, token, row)
            row.activation_status = 'APPLIED'
            self._record(s, row, 'ACTIVATED')
            s.flush()
            self._write_guard(s, token)
            uow.commit()

    def uncertain(self, token, error='ACTIVATION_UNKNOWN'):
        if error not in {'ACTIVATION_UNKNOWN', 'PUBLIC_VERIFICATION_FAILED'}:
            raise ValueError('Sanitized recovery code required')
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            gate, row = self._owned(s, token)
            if not row.db_committed:
                raise PublicationConflict('INVALID_PHASE')
            self._guard(s, gate, token, row)
            if row.activation_status != 'APPLIED':
                row.activation_status = 'UNKNOWN'
            self._record(s, row, 'RECOVERY_REQUIRED', error)
            s.flush()
            self._write_guard(s, token)
            uow.commit()

    def reconcile(self, token):
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            gate, row = self._owned(s, token)
            active = s.get(Active, token.namespace)
            if row.phase == 'ACTIVATED' and self._is_next(active, row):
                return 'APPLIED'
            if row.phase == 'DB_COMMITTED' and row.activation_status == 'NOT_APPLIED' and descriptor(active) == row.plan['previous']:
                return 'NOT_APPLIED'
            if row.phase != 'RECOVERY_REQUIRED' or not row.db_committed:
                raise PublicationConflict('INVALID_PHASE')
            if self._is_next(active, row):
                phase, status = 'ACTIVATED', 'APPLIED'
            elif descriptor(active) == row.plan['previous']:
                phase, status = 'DB_COMMITTED', 'NOT_APPLIED'
            else:
                self._record(s, row, 'RECOVERY_REQUIRED', 'POINTER_CONFLICT')
                self._guard(s, gate, token, row)
                s.flush()
                self._write_guard(s, token)
                uow.commit()
                raise PublicationConflict('POINTER_CONFLICT')
            self._guard(s, gate, token, row)
            row.activation_status = status
            self._record(s, row, phase)
            s.flush()
            self._write_guard(s, token)
            uow.commit()
            return status

    def complete(self, token):
        # Terminal lookup stays read-only even after a later release became
        # active. An old acknowledgement must never switch that pointer back.
        observed = self.inspect(token)
        if observed['phase'] == 'COMPLETE':
            if observed['token'] != token:
                raise PublicationConflict('FENCED')
            return 'COMPLETE'
        with UnitOfWork(self.engine) as uow:
            _, row = self._owned(uow.session, token)
            if row.phase != 'ACTIVATED':
                raise PublicationConflict('INVALID_PHASE')
            plan, digest = frozen(row.plan), row.plan_digest
        try:
            receipt = self.participant.verify_public(token, plan, digest)
        except Exception:
            self.uncertain(token, 'PUBLIC_VERIFICATION_FAILED')
            raise PublicationConflict('PUBLIC_VERIFICATION_FAILED') from None
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            gate, row = self._owned(s, token)
            self._receipt(row, receipt)
            if row.phase != 'ACTIVATED' or not self._is_next(s.get(Active, token.namespace), row):
                raise PublicationConflict('POINTER_CONFLICT')
            self.participant.check_complete(s, frozen(row.plan))
            self._guard(s, gate, token, row)
            self._record(s, row, 'COMPLETE')
            s.flush()
            self._write_guard(s, token, clear=True)
            uow.commit()
            return 'COMPLETE'

    def fail_precommit(self, token):
        observed = self.inspect(token)
        if observed['phase'] == 'FAILED_PRECOMMIT':
            if observed['token'] != token:
                raise PublicationConflict('FENCED')
            return 'FAILED_PRECOMMIT'
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            gate, row = self._owned(s, token)
            if row.db_committed or row.phase not in {'VALIDATED', 'STAGED'}:
                raise PublicationConflict('INVALID_PHASE')
            if descriptor(s.get(Active, token.namespace)) != row.plan['previous']:
                raise PublicationConflict('POINTER_CONFLICT')
            self.participant.check_admission(s, frozen(row.plan))
            self._guard(s, gate, token, row)
            self._record(s, row, 'FAILED_PRECOMMIT')
            s.flush()
            self._write_guard(s, token, clear=True)
            uow.commit()
