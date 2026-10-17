"""Real PG P1 crash/fence tests; fixture participant is not the content CLI.

An actual Grade row represents a domain write, immutable files represent the
staged resource. Assertions inspect durable DB facts rather than an in-memory
transition model. HTTP/content artifact acceptance is a separate integration.
"""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
from threading import Barrier, Event
import unittest
import uuid

import sqlalchemy as sa

from backend.content.build import encoded
from backend.content.publication import PublisherAuthority, PublicationConflict, WorkReceipt, descriptor
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.upgrade import require_disposable
from backend.models.baseline import Grade
from backend.models.protocol import (PublicationGate as Gate, PublicationJournal as Journal,
                                    ActiveReleaseDescriptor as Active, PublicationHistory as History)


class FixtureParticipant:
    def __init__(self, engine, root, grade_id):
        self.engine, self.root, self.grade_id = engine, root, grade_id
        self.apply_calls = 0
        self.stage_hook = self.probe_hook = self.apply_hook = None

    def check_admission(self, session, plan):
        if session.scalar(sa.select(Grade.title).where(Grade.id == self.grade_id)) != plan['before']:
            raise PublicationConflict('SOURCE_CONFLICT')

    def apply(self, session, plan):
        self.check_admission(session, plan)
        self.apply_calls += 1
        row = session.scalar(sa.select(Grade).where(Grade.id == self.grade_id).with_for_update())
        row.title = plan['after']
        session.flush()
        if self.apply_hook:
            self.apply_hook(session)

    def check_complete(self, session, plan):
        if session.scalar(sa.select(Grade.title).where(Grade.id == self.grade_id)) != plan['after']:
            raise PublicationConflict('EDITION_CONFLICT')

    def receipt(self, token, plan, digest, raw):
        return WorkReceipt(token.operation_id, token.owner_id, token.generation, digest,
                           plan['release_id'], plan['manifest_digest'], sha256(raw).hexdigest())

    def path(self, token):
        return self.root / str(token.operation_id) / 'final.json'

    def stage(self, token, plan, digest):
        if self.stage_hook:
            self.stage_hook()
        raw = encoded(plan)
        final = self.path(token)
        final.parent.mkdir(parents=True, exist_ok=True)
        temporary = final.parent / ('generation-' + str(token.generation) + '-' + uuid.uuid4().hex)
        with temporary.open('xb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            try:
                os.link(temporary, final)  # Exclusive atomic immutable install.
            except FileExistsError:
                pass
        finally:
            temporary.unlink()
        return self.verify_stage(token, plan, digest)

    def verify_stage(self, token, plan, digest):
        raw = self.path(token).read_bytes()
        if raw != encoded(plan):
            raise PublicationConflict('ARTIFACT_CONFLICT')
        return self.receipt(token, plan, digest, raw)

    def verify_public(self, token, plan, digest):
        if self.probe_hook:
            self.probe_hook()
        with UnitOfWork(self.engine) as uow:
            active = uow.session.get(Active, token.namespace)
            if active is None or active.operation_id != token.operation_id or active.manifest_digest != plan['manifest_digest']:
                raise PublicationConflict('PUBLIC_VERIFICATION_FAILED')
            self.check_complete(uow.session, plan)
            return self.receipt(token, plan, digest, encoded(descriptor(active)))


class PostgreSQLPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = sa.create_engine(os.environ['MATHSTART_V04_DATABASE_URL'], hide_parameters=True)
        with cls.engine.begin() as connection:
            require_disposable(connection)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        self.namespace = 'protocol-' + uuid.uuid4().hex
        self.temp = tempfile.TemporaryDirectory()
        with UnitOfWork(self.engine) as uow:
            grade = Grade(title='Before', slug=self.namespace, order=99)
            uow.session.add(grade)
            uow.session.flush()
            self.grade_id = grade.id
            uow.commit()
        self.participant = FixtureParticipant(self.engine, Path(self.temp.name), self.grade_id)
        self.service = PublisherAuthority(self.engine, self.participant, lease_seconds=30)
        self.owner = uuid.uuid4()

    def tearDown(self):
        with self.engine.begin() as c:
            ids = sa.select(Journal.id).where(Journal.namespace == self.namespace)
            c.execute(sa.delete(History).where(History.operation_id.in_(ids)))
            c.execute(sa.delete(Active).where(Active.namespace == self.namespace))
            c.execute(sa.delete(Gate).where(Gate.namespace == self.namespace))
            c.execute(sa.delete(Journal).where(Journal.namespace == self.namespace))
            c.execute(sa.delete(Grade).where(Grade.id == self.grade_id))
        self.temp.cleanup()

    def plan(self, **changes):
        return {'release_id': 'release-' + uuid.uuid4().hex, 'manifest_digest': 'a' * 64,
                'previous': None, 'before': 'Before', 'after': 'After', **changes}

    def claim(self, plan=None, key='one'):
        token, phase = self.service.claim(self.namespace, key, plan or self.plan(), self.owner)
        self.assertEqual(phase, 'VALIDATED')
        return token

    def assert_conflict(self, code, call, *args, **kwargs):
        with self.assertRaises(PublicationConflict) as error:
            call(*args, **kwargs)
        self.assertEqual(error.exception.code, code)

    def expire(self, token):
        self.service.renew(token, surrender=True)

    def value(self):
        with self.engine.connect() as c:
            return c.scalar(sa.select(Grade.title).where(Grade.id == self.grade_id))

    def test_legacy_history_stops_publication_before_any_gate_or_domain_write(self):
        from backend.infrastructure.http.transport import APIError
        from backend.models.baseline import metadata
        table = metadata.tables['django_migrations']
        with self.engine.begin() as c:
            record = c.scalar(sa.insert(table).values(app='synthetic_' + uuid.uuid4().hex,
                name='0001_initial', applied=sa.func.clock_timestamp()).returning(table.c.id))
        try:
            with self.assertRaises(APIError) as rejected:
                self.service.claim(self.namespace, 'legacy-writer', self.plan(), self.owner)
            self.assertEqual(rejected.exception.status, 503)
            self.assertEqual(self.value(), 'Before')
            with self.engine.connect() as c:
                self.assertIsNone(c.scalar(sa.select(Gate.namespace).where(Gate.namespace == self.namespace)))
                self.assertIsNone(c.scalar(sa.select(Journal.id).where(Journal.namespace == self.namespace)))
        finally:
            with self.engine.begin() as c:
                c.execute(sa.delete(table).where(table.c.id == record))

    def test_domain_commit_once_and_terminal_ack_never_reactivates_old_release(self):
        plan = self.plan()
        token = self.claim(plan)
        self.service.stage(token)
        self.assertEqual(self.value(), 'Before')
        self.assertEqual(self.service.commit(token), 'DB_COMMITTED')
        self.assertEqual(self.service.commit(token), 'DB_COMMITTED')
        self.assertEqual(self.participant.apply_calls, 1)
        self.assertEqual(self.value(), 'After')
        self.service.intent(token)
        self.service.activate(token)
        self.assertEqual(self.service.activate(token), 'ALREADY_ACTIVATED')
        self.assertEqual(self.service.complete(token), 'COMPLETE')
        with UnitOfWork(self.engine) as uow:
            previous = descriptor(uow.session.get(Active, self.namespace))
        second = self.claim(self.plan(previous=previous, before='After', after='Third'), key='two')
        self.service.stage(second); self.service.commit(second); self.service.intent(second); self.service.activate(second); self.service.complete(second)
        self.assertEqual(self.service.complete(token), 'COMPLETE')
        self.assertEqual(self.value(), 'Third')
        with UnitOfWork(self.engine) as uow:
            self.assertEqual(uow.session.get(Active, self.namespace).operation_id, second.operation_id)
            self.assertEqual(uow.session.get(Gate, self.namespace).fence_generation, 2)
            self.assertIsNone(uow.session.get(Gate, self.namespace).pending_operation_id)
        repeated, status = self.service.claim(self.namespace, 'one', plan, uuid.uuid4())
        self.assertEqual((repeated.operation_id, status), (token.operation_id, 'COMPLETE'))

    def test_same_key_changed_plan_and_foreign_owner_do_not_gain_authority(self):
        plan = self.plan(); token = self.claim(plan)
        self.assert_conflict('IDEMPOTENCY_CONFLICT', self.service.claim, self.namespace, 'one', {**plan, 'after': 'Other'}, self.owner)
        self.assert_conflict('OWNER_BUSY', self.service.claim, self.namespace, 'one', plan, uuid.uuid4())
        self.assertEqual(self.service.claim(self.namespace, 'one', plan, self.owner), (token, 'VALIDATED'))
        self.assert_conflict('BUSY', self.service.claim, self.namespace, 'two', self.plan(), self.owner)

    def test_expired_pending_does_not_admit_new_operation_or_renew_old_owner(self):
        token = self.claim(); self.expire(token)
        self.assert_conflict('FENCED', self.service.renew, token)
        self.assert_conflict('BUSY', self.service.claim, self.namespace, 'two', self.plan(), self.owner)
        current = self.service.takeover(self.namespace, token.operation_id, token.generation, uuid.uuid4())
        self.assertEqual(current.generation, token.generation + 1)
        self.assert_conflict('FENCED', self.service.fail_precommit, token)
        self.service.fail_precommit(current)
        self.assertEqual(self.service.fail_precommit(current), 'FAILED_PRECOMMIT')

    def test_competing_takeovers_have_one_winner_and_never_replace_operation(self):
        token = self.claim(); self.expire(token); barrier = Barrier(2)
        def recover(_):
            barrier.wait(timeout=10)
            try:
                return self.service.takeover(self.namespace, token.operation_id, token.generation, uuid.uuid4())
            except PublicationConflict as error:
                return error.code
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(recover, range(2)))
        self.assertEqual(sum(not isinstance(r, str) for r in results), 1)
        self.assertIn('CLAIM_CONFLICT', results)

    def test_postcommit_takeover_reconciles_previous_without_reapplying_domain(self):
        token = self.claim(); self.service.stage(token); self.service.commit(token); self.expire(token)
        current = self.service.takeover(self.namespace, token.operation_id, token.generation, uuid.uuid4())
        self.assertEqual(self.service.inspect(current)['phase'], 'RECOVERY_REQUIRED')
        self.assertEqual(self.service.reconcile(current), 'NOT_APPLIED')
        self.assertEqual(self.service.reconcile(current), 'NOT_APPLIED')
        self.service.commit(current)
        self.assertEqual(self.participant.apply_calls, 1)
        self.service.intent(current); self.service.activate(current); self.service.complete(current)
        for method in [self.service.commit, self.service.intent, self.service.activate, self.service.complete, self.service.renew, self.service.fail_precommit]:
            self.assert_conflict('FENCED', method, token)

    def test_lost_activation_ack_reconciles_exact_next_after_takeover(self):
        token = self.claim(); self.service.stage(token); self.service.commit(token); self.service.intent(token); self.service.activate(token)
        self.expire(token)
        current = self.service.takeover(self.namespace, token.operation_id, token.generation, uuid.uuid4())
        self.assertEqual(self.service.reconcile(current), 'APPLIED')
        self.assertEqual(self.service.reconcile(current), 'APPLIED')
        self.assertEqual(self.service.complete(current), 'COMPLETE')
        self.assertEqual(self.participant.apply_calls, 1)

    def test_changed_domain_before_commit_rolls_back_and_retains_pending(self):
        token = self.claim(); self.service.stage(token)
        with self.engine.begin() as c:
            c.execute(sa.update(Grade).where(Grade.id == self.grade_id).values(title='Concurrent change'))
        self.assert_conflict('SOURCE_CONFLICT', self.service.commit, token)
        self.assertFalse(self.service.inspect(token)['db_committed'])
        self.assertEqual(self.value(), 'Concurrent change')

    def test_lease_expiry_inside_domain_apply_rolls_back_domain_and_journal(self):
        self.service = PublisherAuthority(self.engine, self.participant, lease_seconds=1)
        token = self.claim(); self.service.stage(token)
        def invalidate(session):
            # Real database time passes after the domain SQL write. The final
            # check must roll it back even though ownership was valid on entry.
            session.execute(sa.text('SELECT pg_sleep(1.1)'))
        self.participant.apply_hook = invalidate
        self.assert_conflict('FENCED', self.service.commit, token)
        self.assertEqual(self.value(), 'Before')
        self.assertFalse(self.service.inspect(token)['db_committed'])

    def test_corrupt_immutable_artifact_does_not_switch_active(self):
        token = self.claim(); self.service.stage(token); self.service.commit(token); self.service.intent(token)
        self.participant.path(token).write_bytes(b'corrupt')
        self.assert_conflict('ARTIFACT_CONFLICT', self.service.activate, token)
        with UnitOfWork(self.engine) as uow:
            self.assertIsNone(uow.session.get(Active, self.namespace))
            self.assertEqual(uow.session.get(Journal, token.operation_id).phase, 'ACTIVATING')

    def test_sql_barrier_rejects_expiry_after_python_guard_and_domain_flush(self):
        self.service = PublisherAuthority(self.engine, self.participant, lease_seconds=1)
        token = self.claim(); self.service.stage(token)
        original = self.service._write_guard
        def delayed(session, owner, **options):
            if session.get(Journal, token.operation_id).phase == 'DB_COMMITTED':
                session.execute(sa.text('SELECT pg_sleep(1.1)'))
            return original(session, owner, **options)
        self.service._write_guard = delayed
        self.assert_conflict('FENCED', self.service.commit, token)
        self.assertEqual(self.value(), 'Before')
        self.assertEqual(self.service.inspect(token)['phase'], 'STAGED')
        self.assertFalse(self.service.inspect(token)['db_committed'])

    def test_delayed_stage_cannot_advance_after_takeover(self):
        token = self.claim(); entered, release = Event(), Event()
        def wait():
            entered.set()
            if not release.wait(10):
                raise RuntimeError('Stage coordination deadline')
        self.participant.stage_hook = wait
        with ThreadPoolExecutor(max_workers=1) as pool:
            stage = pool.submit(self.service.stage, token)
            try:
                self.assertTrue(entered.wait(10)); self.expire(token)
                current = self.service.takeover(self.namespace, token.operation_id, token.generation, uuid.uuid4())
            finally:
                release.set()
            self.assert_conflict('FENCED', stage.result, timeout=10)
        self.assertEqual(self.service.inspect(current)['phase'], 'VALIDATED')
        self.assertEqual(self.value(), 'Before')

    def test_failed_public_probe_keeps_pending_and_blocks_next_publish(self):
        token = self.claim(); self.service.stage(token); self.service.commit(token); self.service.intent(token); self.service.activate(token)
        def fail():
            raise PublicationConflict('PUBLIC_VERIFICATION_FAILED')
        self.participant.probe_hook = fail
        self.assert_conflict('PUBLIC_VERIFICATION_FAILED', self.service.complete, token)
        self.assertEqual(self.service.inspect(token)['phase'], 'RECOVERY_REQUIRED')
        self.assertEqual(self.service.inspect(token)['activation_status'], 'APPLIED')
        self.assert_conflict('BUSY', self.service.claim, self.namespace, 'two', self.plan(), self.owner)
        self.assert_conflict('INVALID_PHASE', self.service.fail_precommit, token)

    def test_verification_receipt_is_bound_to_current_owner_and_generation(self):
        token = self.claim(); receipt = self.service.stage(token); self.expire(token)
        current = self.service.takeover(self.namespace, token.operation_id, token.generation, uuid.uuid4())
        original = self.participant.stage
        self.participant.stage = lambda *args: receipt
        self.assert_conflict('VERIFICATION_CONFLICT', self.service.stage, current)
        self.participant.stage = original
        self.service.stage(current)

    def test_delayed_activation_loses_to_takeover_without_switching_pointer(self):
        token = self.claim(); self.service.stage(token); self.service.commit(token); self.service.intent(token)
        entered, release = Event(), Event()
        original = self.participant.verify_stage
        def verify(*args):
            entered.set()
            if not release.wait(10):
                raise RuntimeError('Activation coordination deadline')
            return original(*args)
        self.participant.verify_stage = verify
        with ThreadPoolExecutor(max_workers=1) as pool:
            activation = pool.submit(self.service.activate, token)
            try:
                self.assertTrue(entered.wait(10)); self.expire(token)
                current = self.service.takeover(self.namespace, token.operation_id, token.generation, uuid.uuid4())
            finally:
                release.set()
            self.assert_conflict('FENCED', activation.result, timeout=10)
        with UnitOfWork(self.engine) as uow:
            self.assertIsNone(uow.session.get(Active, self.namespace))
        self.assertEqual(self.service.reconcile(current), 'NOT_APPLIED')

    def test_delayed_public_probe_cannot_acknowledge_or_clear_new_owner_pending(self):
        token = self.claim(); self.service.stage(token); self.service.commit(token); self.service.intent(token); self.service.activate(token)
        entered, release = Event(), Event()
        def wait():
            entered.set()
            if not release.wait(10):
                raise RuntimeError('Probe coordination deadline')
        self.participant.probe_hook = wait
        with ThreadPoolExecutor(max_workers=1) as pool:
            completion = pool.submit(self.service.complete, token)
            try:
                self.assertTrue(entered.wait(10)); self.expire(token)
                current = self.service.takeover(self.namespace, token.operation_id, token.generation, uuid.uuid4())
            finally:
                release.set()
            self.assert_conflict('FENCED', completion.result, timeout=10)
        with UnitOfWork(self.engine) as uow:
            gate = uow.session.get(Gate, self.namespace)
            self.assertEqual((gate.pending_operation_id, gate.owner_id), (current.operation_id, current.owner_id))
        self.participant.probe_hook = None
        self.assertEqual(self.service.reconcile(current), 'APPLIED')
        self.service.complete(current)

    def test_unrelated_corrupt_pointer_is_never_overwritten_or_released(self):
        token = self.claim(); self.service.stage(token); self.service.commit(token); self.service.intent(token); self.service.activate(token); self.service.complete(token)
        with UnitOfWork(self.engine) as uow:
            previous = descriptor(uow.session.get(Active, self.namespace))
        current = self.claim(self.plan(previous=previous, before='After', after='Third'), key='two')
        self.service.stage(current); self.service.commit(current); self.service.uncertain(current)
        with self.engine.begin() as c:
            c.execute(sa.update(Active).where(Active.namespace == self.namespace).values(manifest_digest='c' * 64))
        self.assert_conflict('POINTER_CONFLICT', self.service.reconcile, current)
        with UnitOfWork(self.engine) as uow:
            self.assertEqual(uow.session.get(Active, self.namespace).manifest_digest, 'c' * 64)
            self.assertEqual(uow.session.get(Gate, self.namespace).pending_operation_id, current.operation_id)
            row = uow.session.get(Journal, current.operation_id)
            self.assertEqual((row.phase, row.error_code, row.db_committed), ('RECOVERY_REQUIRED', 'POINTER_CONFLICT', True))

    def test_plan_is_detached_and_fence_overflow_never_wraps(self):
        plan = self.plan(); token = self.claim(plan)
        plan['after'] = 'Caller mutation'
        self.assertEqual(self.service.inspect(token)['plan']['after'], 'After')
        self.service.fail_precommit(token)
        with self.engine.begin() as c:
            c.execute(sa.update(Gate).where(Gate.namespace == self.namespace).values(fence_generation=2**63 - 1))
        self.assert_conflict('FENCE_EXHAUSTED', self.service.claim, self.namespace, 'overflow', self.plan(), self.owner)
        with UnitOfWork(self.engine) as uow:
            self.assertIsNone(uow.session.get(Gate, self.namespace).pending_operation_id)
            self.assertEqual(uow.session.scalar(sa.select(sa.func.count()).select_from(Journal).where(Journal.namespace == self.namespace)), 1)


if __name__ == '__main__':
    unittest.main()
