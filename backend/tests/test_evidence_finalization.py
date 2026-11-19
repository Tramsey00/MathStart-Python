"""N013 HTTP, finalization, recovery and replay on explicitly owned PostgreSQL."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime
import multiprocessing
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from threading import Barrier, Event
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from uuid import UUID, uuid4

from alembic import command
from psycopg import sql
import sqlalchemy as sa
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from backend import release_migrate
from backend.assessment.analysis import analyze_submission
from backend.assessment.attempt_models import analysis_record, attempt, completion_fact, exposure, hint, step
from backend.assessment.attempts import AttemptService, snapshot_digest
from backend.assessment.checker_spec import template_validation_spec
from backend.assessment.completion_read import read_completed_attempt
from backend.assessment.finalization import FinalizationService
from backend.assessment.models import exercise, exercise_skill, validation, version
from backend.assessment.package import digest
from backend.assessment.templates import TEMPLATES
from backend.infrastructure.database import DatabaseUnavailable
from backend.infrastructure.http.app import create_app
from backend.infrastructure.http.signing import Signer
from backend.infrastructure.http.transport import APIError
from backend.infrastructure.uow import UnitOfWork
from backend.knowledge.models import skill
from backend.math_validation.model import BatchResult, ParseReason, failed
from backend.math_validation.parser import _worker_command, parse_batch
from backend.migrations.runtime_privileges import grant_runtime_privileges
from backend.migrations.upgrade import configuration
from backend.models.baseline import User, utc_now
from backend.progress.models import completion, event, state
from backend.progress.service import ProgressService
from backend.tests.test_assessment_bank import seed
from backend.tests import test_local_schema_upgrade_postgres as local_checks
from backend.users.security import Security, SessionIdentity
from backend.users.service import IdentityService
from scripts import container_dev as compose, team_local as host

ADMIN = os.getenv('MATHSTART_N013_TEST_ADMIN_URL')
MARKER = 'MS-N013 disposable PostgreSQL'
KEY = 'synthetic-n013-isolated-signing-material'
ORIGIN = 'https://mathstart.example'
PRIMARY = 'equation_balance'
SECONDARY = 'linear_one_step'
PRIVATE = 'synthetic-private-reveal-probe'


def run_interrupted_analysis(url, identity, accepted, entered, release):
    engine = sa.create_engine(url, hide_parameters=True)
    service = FinalizationService(AttemptService(IdentityService(Security(engine, KEY, ORIGIN)), Signer(KEY)))

    def wait_inside_analyzer(*args, **kwargs):
        entered.set()
        if not release.wait(30):
            raise RuntimeError('Expected test process termination')
        return analyze_submission(*args, **kwargs)

    with patch('backend.assessment.finalization.analyze_submission', side_effect=wait_inside_analyzer):
        service.resume(identity, accepted)


@unittest.skipUnless(ADMIN, 'Requires an explicitly marked disposable N013 PostgreSQL server')
class PostgreSQLFinalizationTests(unittest.TestCase):
    installed_database = local_checks.LocalSchemaUpgradeTests.installed_database
    host_setup = local_checks.LocalSchemaUpgradeTests.host_setup
    host_command = staticmethod(local_checks.LocalSchemaUpgradeTests.host_command)
    compose_setup = local_checks.LocalSchemaUpgradeTests.compose_setup
    assert_head = local_checks.LocalSchemaUpgradeTests.assert_head
    assert_compose_complete = local_checks.LocalSchemaUpgradeTests.assert_compose_complete

    @classmethod
    def setUpClass(cls):
        url = make_url(ADMIN)
        if (url.drivername, url.host, url.database) != ('postgresql+psycopg', '127.0.0.1', 'postgres') or not url.port:
            raise RuntimeError('Expected loopback disposable PostgreSQL')
        cls.admin = sa.create_engine(url, isolation_level='AUTOCOMMIT', hide_parameters=True)
        cls.addClassCleanup(cls.admin.dispose)
        with cls.admin.begin() as conn:
            marker = conn.scalar(sa.text("SELECT shobj_description(oid,'pg_database') FROM pg_database "
                                         "WHERE datname=current_database()"))
            if marker != MARKER:
                raise RuntimeError('Missing N013 disposable-server reservation')
            for role in ('local_schema', 'local_runtime'):
                if not conn.scalar(sa.text('SELECT 1 FROM pg_roles WHERE rolname=:role'), {'role': role}):
                    conn.connection.driver_connection.execute(sql.SQL('CREATE ROLE {}').format(sql.Identifier(role)))
                conn.connection.driver_connection.execute(sql.SQL('ALTER ROLE {} LOGIN PASSWORD {}').format(
                    sql.Identifier(role), sql.Literal(url.password)))
        cls.engine = cls.enterClassContext(cls.database())
        cls.apply(cls.engine, 'FRESH')
        cls.topics = seed(cls.engine)
        cls.runtime = cls.runtime_engine(cls.engine)
        cls.addClassCleanup(cls.runtime.dispose)
        local_checks.TEMP.mkdir(parents=True, exist_ok=True)

    @classmethod
    @contextmanager
    def database(cls):
        name = 'test_n013_' + uuid4().hex
        with cls.admin.begin() as conn:
            conn.exec_driver_sql(f'CREATE DATABASE {name}')
        engine = sa.create_engine(cls.admin.url.set(database=name), hide_parameters=True)
        try:
            yield engine
        finally:
            engine.dispose()
            with cls.admin.begin() as conn:
                conn.exec_driver_sql(f'DROP DATABASE {name} WITH (FORCE)')

    @staticmethod
    def apply(engine, profile):
        engine.dispose()  # The reviewed apply requires the operator to drain other clients.
        plan = release_migrate.preview(engine, KEY, profile)
        release_migrate.apply(engine, KEY, plan, release_migrate.plan_digest(plan), maintenance=True)
        with engine.begin() as conn:
            grant_runtime_privileges(conn.connection.driver_connection)

    @staticmethod
    def runtime_engine(engine):
        runtime = sa.create_engine(engine.url, hide_parameters=True)

        @sa.event.listens_for(runtime, 'connect')
        def use_runtime(connection, _):
            connection.execute('SET ROLE local_runtime')
            connection.commit()

        return runtime

    def setUp(self):
        self.security = Security(self.runtime, KEY, ORIGIN)
        self.identity = IdentityService(self.security)
        self.release = SimpleNamespace(page=lambda slug: self.topics[slug])
        self.app = create_app(self.runtime, Signer(KEY), identity_service=self.identity, public_origin=ORIGIN)
        self.owner, self.token = self.new_user(self.runtime)
        self.eid, self.vid = self.publish(self.engine, self.topics)

    @staticmethod
    def new_user(engine):
        with Session(engine) as session, session.begin():
            user = User(username='n013_' + uuid4().hex)
            session.add(user)
            session.flush()
            row, token, _ = Security(engine, KEY, ORIGIN).issue(session, user, utc_now())
            return SessionIdentity(user.id, row.id, row.lineage_id, row.revocation_epoch), token

    @staticmethod
    def publish(engine, topics, schema='integer-final-v1', anchor=None, *, hints=False):
        eid, vid = uuid4(), uuid4()
        template = TEMPLATES[schema]
        public = template.public_contract()
        if hints:
            public.update(allowed_help_actions=['HINT', 'REVEAL'], hint_policy={'allowed': True, 'levels': [1]})
        spec = template_validation_spec(template)
        if anchor:
            spec.update(equation_answer_mode='SOLUTION', initial_state={
                'schema_version': 1, 'kind': 'EQUATION', 'parser_profile': template.parser, 'text': anchor})
        key = '4' if anchor else '-2'
        with engine.begin() as conn:
            conn.execute(exercise.insert().values(id=eid, code='n013_' + uuid4().hex,
                topic_id=next(iter(topics.values()))['id'], created_at=utc_now()))
            conn.execute(version.insert().values(id=vid, exercise_id=eid, version=1, status='DRAFT',
                mode=template.mode, difficulty=3, statement='Synthetic N013 exercise',
                public_schema=public, schema_code=schema, provenance='synthetic', digest='a' * 64))
            conn.execute(validation.insert().values(version_id=vid, checker_type=template.checker,
                checker_version=2 if anchor else 1, answer_key=key, accepted_variants=[],
                validation_spec=spec, canonical_solution=[PRIVATE], digest='b' * 64))
            for code, role in ((PRIMARY, 'PRIMARY'), (SECONDARY, 'SECONDARY')):
                conn.execute(exercise_skill.insert().values(version_id=vid, role=role,
                    skill_id=conn.scalar(sa.select(skill.c.id).where(skill.c.code == code))))
            if hints:
                reviewed = {'version_id': str(vid), 'level': 1, 'text': 'Синтетическая подсказка'}
                conn.execute(hint.insert().values(**(reviewed | {'version_id': vid}), reviewed_digest=digest(reviewed)))
            conn.execute(version.update().where(version.c.id == vid).values(status='PUBLISHED'))
        return eid, vid

    @contextmanager
    def client(self, token=None, *, raise_server_exceptions=True):
        with TestClient(self.app, base_url=ORIGIN, raise_server_exceptions=raise_server_exceptions) as client:
            client.cookies.set('sessionid', token or self.token)
            csrf = client.get('/api/v1/auth/csrf/').json()['data']['csrf_token']
            yield client, {'X-CSRFToken': csrf, 'Origin': ORIGIN}

    def draft(self, client, headers, *, eid=None, payload=None, steps=()):
        with patch('backend.infrastructure.http.app.active_release', return_value=self.release):
            created = client.post('/api/v1/attempts/', json={'exercise_id': str(eid or self.eid),
                'version': 1, 'contract_version': 1}, headers=headers | {'Idempotency-Key': str(uuid4())})
        self.assertEqual(created.status_code, 201, created.text)
        path = '/api/v1/attempts/' + created.json()['data']['id'] + '/'
        saved = client.put(path + 'draft/', headers=headers, json={'contract_version': 1, 'expected_revision': 1,
            'draft': {'payload': {'answer': '  −2  '} if payload is None else payload, 'steps': list(steps)}})
        self.assertEqual(saved.status_code, 200, saved.text)
        return path

    def submit(self, client, headers, path, key, revision=2):
        return client.post(path + 'submit/', headers=headers | {'Idempotency-Key': key},
                           json={'contract_version': 1, 'expected_revision': revision})

    def safe_read(self, client, path):
        reply = client.get(path)
        self.assertEqual(reply.status_code, 200, reply.text)
        self.assertEqual(reply.headers['Cache-Control'], 'private, no-store')
        for private in (PRIVATE, 'validation_spec', 'accepted_variants', 'answer_key', 'checker_digest'):
            self.assertNotIn(private, reply.text)
        return reply.json()['data']

    def events(self):
        with self.engine.connect() as conn:
            return conn.scalars(sa.select(event.c.payload).where(event.c.user_id == self.owner.user_id)).all()

    def test_http_result_authority_positive_once_and_full_replay(self):
        with self.client() as (client, headers):
            path = self.draft(client, headers)
            first = self.submit(client, headers, path, 'submit-first')
            self.assertEqual(first.status_code, 202, first.text)
            self.assertEqual(first.json()['data']['state'], 'SUBMITTED')
            result = self.safe_read(client, path)
            self.assertEqual(result['state'], 'COMPLETED')
            self.assertEqual(result['operation_id'], first.json()['data']['operation_id'])
            self.assertEqual(result['snapshot_digest'], first.json()['data']['snapshot_digest'])
            self.assertEqual(result['draft']['payload']['answer'], '  −2  ')
            self.assertEqual(result['result']['outcome'], 'CORRECT')
            self.assertTrue(result['eligibility']['independent'])
            self.assertEqual(self.submit(client, headers, path, 'submit-first').json(), first.json())
            changed = self.submit(client, headers, path, 'submit-first', 1)
            self.assertEqual(changed.json()['error']['code'], 'IDEMPOTENCY_CONFLICT')

            second_path = self.draft(client, headers)
            self.assertEqual(self.submit(client, headers, second_path, 'submit-second').status_code, 202)
            repeated = self.safe_read(client, second_path)
            self.assertEqual(repeated['result']['outcome'], 'CORRECT')
            self.assertEqual(repeated['eligibility']['reason'], 'ALREADY_CREDITED')

            revealed = client.post(path + 'reveal/', headers=headers | {'Idempotency-Key': 'late-reveal'},
                                   json={'contract_version': 1, 'confirm': True})
            self.assertEqual(revealed.status_code, 200, revealed.text)
            self.assertIn(PRIVATE, revealed.text)
            late = self.safe_read(client, path)
            self.assertEqual(late['result'], result['result'])
            self.assertEqual(late['eligibility'], result['eligibility'])
            self.assertGreaterEqual(datetime.fromisoformat(late['exposure']['revealed_at']),
                                    datetime.fromisoformat(late['completed_at']))

        self.assertEqual([e['event_kind'] for e in self.events()], ['CORRECT_FIRST_TRY'])
        self.assertEqual(self.events()[0]['policy_version'], 'progress-v1')
        with Session(self.runtime) as session:
            source = read_completed_attempt(session, result['id'])
            self.assertEqual(len(source.evidence.facts), 2)
            self.assertEqual({f['policy_version'] for f in source.evidence.facts}, {'progress-v1.1'})
            facts = session.scalars(sa.select(completion.c.payload).where(completion.c.user_id == self.owner.user_id)).all()
            self.assertEqual(len(facts), 4)
            self.assertEqual({fact['completion_id'] for fact in facts if fact['attempt_id'] == result['id']},
                             {fact['completion_id'] for fact in source.evidence.facts})
            live = session.execute(sa.select(skill.c.code, state.c.result).join(skill, skill.c.id == state.c.skill_id)
                                   .where(state.c.user_id == self.owner.user_id)).all()
            self.assertEqual({row.code for row in live}, {PRIMARY, SECONDARY})
            for code, projection in live:
                self.assertEqual(projection, ProgressService().replay(session, self.owner.user_id, code))
                self.assertEqual(projection['state']['reducer_version'], 'progress-v1.1')

    def test_worker_failure_rollback_and_lost_commit_ack_recover_exact_operation(self):
        with self.client() as (client, headers):
            path = self.draft(client, headers)

            def failed_batch(items):
                return BatchResult(tuple(failed(item, ParseReason.WORKER_FAILURE) for item in items))

            with patch('backend.solution_analyzer.deterministic.parse_batch', side_effect=failed_batch):
                accepted = self.submit(client, headers, path, 'recovery').json()
            self.assertEqual(self.safe_read(client, path)['state'], 'SUBMITTED')

            ingest = ProgressService.ingest

            def fail_after_ingest(service, session, delivery):
                ingest(service, session, delivery)
                raise DatabaseUnavailable('synthetic failure before commit')

            with patch.object(ProgressService, 'ingest', fail_after_ingest):
                self.assertEqual(self.submit(client, headers, path, 'recovery').json(), accepted)
            self.assertEqual(self.safe_read(client, path)['state'], 'SUBMITTED')
            self.assertEqual(self.events(), [])
            pk = UUID(accepted['data']['id'])
            with self.engine.connect() as conn:
                for table in (analysis_record, completion_fact):
                    self.assertIsNone(conn.scalar(sa.select(table.c.attempt_id).where(table.c.attempt_id == pk)))
                self.assertFalse(conn.scalar(sa.select(exposure.c.positive_credit_used).where(
                    exposure.c.user_id == self.owner.user_id, exposure.c.version_id == self.vid)))

            class LostAck(UnitOfWork):
                def commit(self):
                    super().commit()
                    raise DatabaseUnavailable('synthetic failure after commit')

            with patch('backend.assessment.finalization.UnitOfWork', LostAck):
                self.assertEqual(self.submit(client, headers, path, 'recovery').json(), accepted)
            self.assertEqual(self.safe_read(client, path)['state'], 'COMPLETED')
            self.assertEqual(self.submit(client, headers, path, 'recovery').json(), accepted)
            self.assertEqual(len(self.events()), 1)

    def test_student_cpu_budget_interrupts_running_normalization(self):
        root = str(Path(__file__).resolve().parents[2])
        code = f"""import sys
sys.path.insert(0, {root!r})
from backend.math_validation import _worker
normalize_once = _worker.normalize
def keep_computing(text, profile):
    while True:
        normalize_once(text, profile)
_worker.normalize = keep_computing
_worker.main()
"""
        self.assert_student_budget_completion([sys.executable, '-I', '-S', '-B', '-c', code])

    def test_student_timeout_message_is_terminal_without_evidence(self):
        budget_worker = [sys.executable, '-I', '-S', '-B', '-c',
                         'import json, sys; json.load(sys.stdin); print(json.dumps({"reason": "TIMEOUT"}), flush=True)']
        self.assert_student_budget_completion(budget_worker)

    def assert_student_budget_completion(self, budget_worker):
        with self.client() as (client, headers):
            path = self.draft(client, headers)
            with patch('backend.math_validation.parser._worker_command',
                       side_effect=[_worker_command(), budget_worker]):
                accepted = self.submit(client, headers, path, 'budget')
                self.assertEqual(accepted.status_code, 202, accepted.text)
                receipt = accepted.json()
            terminal = self.safe_read(client, path)
            self.assertEqual(terminal['state'], 'COMPLETED')
            self.assertEqual(terminal['result']['outcome'], 'UNSUPPORTED')
            self.assertFalse(terminal['result']['positive_credit_awarded'])
            self.assertEqual(self.submit(client, headers, path, 'budget').json(), receipt)
            self.assertEqual(self.safe_read(client, path), terminal)
            self.assertEqual(self.events(), [])

    def test_worker_startup_delay_keeps_same_submission_recoverable(self):
        slow_worker = [sys.executable, '-I', '-S', '-B', '-c', 'import time; time.sleep(10)']
        self.assert_parse_timeout_recoverable([_worker_command(), slow_worker], ParseReason.WORKER_TIMEOUT)

    def test_server_reference_budget_timeout_keeps_same_submission_recoverable(self):
        budget_worker = [sys.executable, '-I', '-S', '-B', '-c',
                         'import json, sys; json.load(sys.stdin); print(json.dumps({"reason": "TIMEOUT"}), flush=True)']
        self.assert_parse_timeout_recoverable([budget_worker], ParseReason.TIMEOUT)

    def assert_parse_timeout_recoverable(self, commands, expected_reason):
        reasons = []

        def observe_batch(items):
            batch = parse_batch(items)
            reasons.extend(result.reason for result in batch.results)
            return batch

        with self.client() as (client, headers):
            path = self.draft(client, headers)
            with patch('backend.math_validation.parser._worker_command', side_effect=commands) as launch:
                with patch('backend.solution_analyzer.deterministic.parse_batch', side_effect=observe_batch):
                    receipt = self.submit(client, headers, path, 'timeout-recovery').json()
            self.assertEqual(launch.call_count, len(commands))
            self.assertEqual(reasons[-1], expected_reason)
            pending = self.safe_read(client, path)
            self.assertEqual(pending['state'], 'SUBMITTED')
            self.assertEqual(self.events(), [])
            self.assertEqual(self.submit(client, headers, path, 'timeout-recovery').json(), receipt)
            completed = self.safe_read(client, path)
            self.assertEqual(completed['operation_id'], pending['operation_id'])
            self.assertEqual(completed['state'], 'COMPLETED')
            self.assertTrue(completed['result']['positive_credit_awarded'])
            self.assertEqual(len(self.events()), 1)

    def test_resume_after_process_dies_inside_analyzer(self):
        with self.client() as (client, headers):
            path = self.draft(client, headers)
            with patch.object(FinalizationService, 'resume'):
                receipt = self.submit(client, headers, path, 'interrupted').json()
            ctx = multiprocessing.get_context('spawn')
            entered, release = ctx.Event(), ctx.Event()
            process = ctx.Process(target=run_interrupted_analysis, args=(
                self.runtime.url.set(username='local_runtime'), self.owner, receipt['data'], entered, release))
            process.start()
            try:
                self.assertTrue(entered.wait(20))
                with patch('backend.assessment.finalization.analyze_submission') as analyzer:
                    self.assertEqual(self.submit(client, headers, path, 'interrupted').json(), receipt)
                    analyzer.assert_not_called()
                self.assertEqual(self.safe_read(client, path)['state'], 'SUBMITTED')
            finally:
                process.terminate()
                process.join(10)
            self.assertFalse(process.is_alive())
            self.assertEqual(self.submit(client, headers, path, 'interrupted').json(), receipt)
            self.assertEqual(self.safe_read(client, path)['state'], 'COMPLETED')
            self.assertEqual(len(self.events()), 1)

    def test_lost_submit_ack_before_analysis_can_resume(self):
        from backend.infrastructure.http import transport

        render = transport.json_response

        def lose_acceptance(body, status=200):
            if status == 202:
                raise DatabaseUnavailable('synthetic disconnect after the receipt commit')
            return render(body, status)

        with self.client(raise_server_exceptions=False) as (client, headers):
            path = self.draft(client, headers)
            with patch.object(transport, 'json_response', side_effect=lose_acceptance):
                # The exception occurs before a BackgroundTask has been scheduled.
                self.assertEqual(self.submit(client, headers, path, 'lost').status_code, 503)
            pending = self.safe_read(client, path)
            self.assertEqual(pending['state'], 'SUBMITTED')
            self.assertEqual(self.events(), [])
            replayed = self.submit(client, headers, path, 'lost')
            self.assertEqual(replayed.status_code, 202)
            self.assertEqual(replayed.json()['data']['operation_id'], pending['operation_id'])
            self.assertEqual(self.safe_read(client, path)['state'], 'COMPLETED')
            self.assertEqual(len(self.events()), 1)

    def test_parallel_finalize_and_repeat_with_same_snapshot(self):
        with self.client() as (client, headers):
            path = self.draft(client, headers)
            with patch.object(FinalizationService, 'resume'):
                accepted = self.submit(client, headers, path, 'race').json()['data']
            service = FinalizationService(AttemptService(self.identity, Signer(KEY)))
            ids = UUID(accepted['id']), UUID(accepted['operation_id'])
            with self.assertRaises(APIError):
                service.finalize(self.owner, *ids, '0' * 64)
            entered, release = Event(), Event()

            def analyze_together(*args, **kwargs):
                entered.set()
                if not release.wait(10):
                    raise RuntimeError('Expected concurrent submit retry')
                return analyze_submission(*args, **kwargs)

            def retry():
                with self.client() as (retry_client, retry_headers):
                    return self.submit(retry_client, retry_headers, path, 'race').json()['data']

            with patch('backend.assessment.finalization.analyze_submission', side_effect=analyze_together) as analyzer, \
                    ThreadPoolExecutor(max_workers=2) as workers:
                first = workers.submit(retry)
                try:
                    self.assertTrue(entered.wait(10))
                    self.assertEqual(retry(), accepted)
                finally:
                    release.set()
                self.assertEqual(first.result(15), accepted)
                analyzer.assert_called_once()
            self.assertEqual(self.safe_read(client, path)['state'], 'COMPLETED')
            with self.engine.connect() as conn:
                self.assertEqual(conn.scalar(sa.select(sa.func.count()).select_from(analysis_record)
                    .where(analysis_record.c.attempt_id == ids[0])), 1)
            self.assertEqual(len(self.events()), 1)

    def test_two_attempts_share_one_hinted_positive_credit(self):
        eid, _ = self.publish(self.engine, self.topics, hints=True)
        barrier = Barrier(2, timeout=15)

        def analyze_together(*args, **kwargs):
            result = analyze_submission(*args, **kwargs)
            barrier.wait()
            return result

        def submit(path):
            with self.client() as (client, headers):
                return self.submit(client, headers, path, str(uuid4())).status_code

        with self.client() as (client, headers):
            paths = [self.draft(client, headers, eid=eid) for _ in range(2)]
            reply = client.post(paths[0] + 'hints/', headers=headers | {'Idempotency-Key': 'hint'},
                                json={'contract_version': 1, 'level': 1})
            self.assertEqual(reply.status_code, 200, reply.text)
            with patch('backend.assessment.finalization.analyze_submission', side_effect=analyze_together), \
                    ThreadPoolExecutor(max_workers=2) as workers:
                self.assertEqual(list(workers.map(submit, paths)), [202, 202])
            results = [self.safe_read(client, path) for path in paths]
            self.assertEqual({r['eligibility']['reason'] for r in results}, {'HINT_EXPOSURE', 'ALREADY_CREDITED'})
            self.assertTrue(all(r['result']['outcome'] == 'CORRECT' and not r['eligibility']['independent']
                                for r in results))
            self.assertEqual([e['event_kind'] for e in self.events()], ['CORRECT_AFTER_HINT'])

    def test_reveal_during_analysis_and_foreign_csrf_gates(self):
        entered, proceed = Event(), Event()

        def blocked_analysis(*args, **kwargs):
            entered.set()
            if not proceed.wait(10):
                raise RuntimeError('Test did not release Analyzer')
            return analyze_submission(*args, **kwargs)

        with self.client() as (client, headers):
            path = self.draft(client, headers)
            self.assertEqual(self.submit(client, {}, path, 'missing-csrf').status_code, 403)
            _, foreign_token = self.new_user(self.runtime)
            with self.client(foreign_token) as (foreign, foreign_headers):
                self.assertEqual(foreign.get(path).status_code, 404)
                self.assertEqual(self.submit(foreign, foreign_headers, path, 'foreign').status_code, 404)

            def submit():
                with self.client() as (worker, worker_headers):
                    return self.submit(worker, worker_headers, path, 'before-reveal')

            with patch('backend.assessment.finalization.analyze_submission', side_effect=blocked_analysis), \
                    ThreadPoolExecutor(max_workers=1) as workers:
                pending = workers.submit(submit)
                try:
                    self.assertTrue(entered.wait(10))
                    self.assertEqual(self.safe_read(client, path)['state'], 'SUBMITTED')
                    revealed = client.post(path + 'reveal/', headers=headers | {'Idempotency-Key': 'before-completion'},
                                           json={'contract_version': 1, 'confirm': True})
                    self.assertEqual(revealed.status_code, 200, revealed.text)
                finally:
                    proceed.set()
                self.assertEqual(pending.result(10).status_code, 202)
            result = self.safe_read(client, path)
            self.assertEqual(result['result']['outcome'], 'CORRECT')
            self.assertEqual(result['eligibility']['reason'], 'REVEAL_EXPOSURE')
            self.assertLessEqual(datetime.fromisoformat(result['exposure']['revealed_at']),
                                 datetime.fromisoformat(result['completed_at']))
            self.assertEqual(self.events(), [])

    def test_old_steps_supported_final_without_proof_and_single_proven_defect(self):
        old, _ = self.publish(self.engine, self.topics, 'arithmetic-steps-v1')
        anchored, _ = self.publish(self.engine, self.topics, 'equation-steps-v1', 'x+3=7')
        with self.client() as (client, headers):
            steps = [
                dict(step_no=1, step_type='MATH_EXPRESSION', payload={'expression': '1-3'}, raw_text='  1-3 '),
                dict(step_no=2, step_type='FINAL_STATEMENT', payload={'answer': '-2'}, raw_text=' -2 '),
            ]
            path = self.draft(client, headers, eid=old, payload={}, steps=steps)
            self.assertEqual(self.submit(client, headers, path, 'legacy').status_code, 202)
            legacy = self.safe_read(client, path)['result']
            self.assertEqual(legacy['outcome'], 'INDETERMINATE')
            self.assertIn('Итоговый ответ верен', legacy['safe_feedback'])
            self.assertIsNone(legacy['first_error_step_id'])
            self.assertEqual(self.events(), [])

            path = self.draft(client, headers, payload={'answer': 'sin(1)'})
            self.assertEqual(self.submit(client, headers, path, 'unsupported').status_code, 202)
            self.assertEqual(self.safe_read(client, path)['result']['outcome'], 'UNSUPPORTED')
            self.assertEqual(self.events(), [])

            steps[0].update(step_type='EQUATION_STATE', payload={'expression': '(x+3)-3=7'})
            steps[1].update(payload={'answer': '4'})
            path = self.draft(client, headers, eid=anchored, payload={}, steps=steps)
            self.assertEqual(self.submit(client, headers, path, 'defect').status_code, 202)
            wrong = self.safe_read(client, path)
            self.assertEqual(wrong['result']['outcome'], 'WRONG')
            self.assertEqual(wrong['result']['first_error_step_id'], wrong['steps'][0]['step_id'])
            self.assertEqual([e['event_kind'] for e in self.events()], ['MISCONCEPTION_DETECTED'])

    def test_reviewed_n012_update_preserves_pending_snapshot_and_acl(self):
        with self.database() as old:
            with old.begin() as conn:
                command.upgrade(configuration(conn), 'v01_0008')
            topics = seed(old)
            eid, vid = self.publish(old, topics, 'arithmetic-steps-v1')
            owner, token = self.new_user(old)
            identity = IdentityService(Security(old, KEY, ORIGIN))
            service = AttemptService(identity, Signer(KEY),
                public_release=lambda _uow: SimpleNamespace(page=lambda slug: topics[slug]))
            route = '/api/v1/attempts/'
            data, _ = service.mutate(owner, 'create_attempt', route, {'exercise_id': str(eid), 'version': 1,
                'contract_version': 1}, 'create', str(uuid4()))
            raw_id = data['data']['id']
            path = f'{route}{raw_id}/'
            draft = {'payload': {}, 'steps': [
                dict(step_no=1, step_type='MATH_EXPRESSION', payload={'expression': '1-3'}, raw_text='  1 - 3 '),
                dict(step_no=2, step_type='FINAL_STATEMENT', payload={'answer': '-2'}, raw_text='  -2  '),
            ]}
            service.mutate(owner, 'update_draft', path + 'draft/', {'contract_version': 1, 'expected_revision': 1,
                'draft': draft}, None, str(uuid4()), raw_id)
            submit = {'contract_version': 1, 'expected_revision': 2}
            accepted, _ = service.mutate(owner, 'submit_attempt', path + 'submit/', submit, 'old', str(uuid4()), raw_id)
            before = service.get(owner, raw_id)
            with Session(old) as session, session.begin():
                ProgressService().self_report(session, owner.user_id, {PRIMARY})
                prior_event = session.scalar(sa.select(event.c.payload))
            self.apply(old, 'TARGET_0008')
            self.assertEqual(service.get(owner, raw_id), before)
            runtime = self.runtime_engine(old)
            try:
                with runtime.connect() as conn:
                    self.assertTrue(conn.scalar(sa.text("SELECT has_column_privilege(current_user,"
                                                         "'assessment_exercise_validation','validation_spec','SELECT')")))
                    self.assertFalse(conn.scalar(sa.text("SELECT has_table_privilege(current_user,"
                                                          "'assessment_exercise_validation','SELECT')")))
                    self.assertFalse(conn.scalar(sa.text("SELECT has_table_privilege(current_user,"
                                                          "'assessment_analysis_record','UPDATE')")))
                active = AttemptService(IdentityService(Security(runtime, KEY, ORIGIN)), Signer(KEY))
                app = create_app(runtime, Signer(KEY), identity_service=active.identity, public_origin=ORIGIN)
                with TestClient(app, base_url=ORIGIN) as client:
                    client.cookies.set('sessionid', token)
                    csrf = client.get('/api/v1/auth/csrf/').json()['data']['csrf_token']
                    retry = client.post(path + 'submit/', json=submit,
                        headers={'Origin': ORIGIN, 'X-CSRFToken': csrf, 'Idempotency-Key': 'old'})
                    self.assertEqual(retry.json(), accepted)
                    terminal = self.safe_read(client, path)
                self.assertEqual(terminal['state'], 'COMPLETED')
                for key in ('id', 'revision', 'operation_id', 'snapshot_digest', 'draft', 'steps'):
                    self.assertEqual(terminal[key], before[key])
                with Session(runtime) as session:
                    self.assertEqual(session.scalar(sa.select(event.c.payload)), prior_event)
                    row = session.execute(sa.select(attempt).where(attempt.c.id == UUID(raw_id))).one()
                    v = session.execute(sa.select(version).where(version.c.id == vid)).one()
                    self.assertEqual(snapshot_digest(row, v, terminal['steps'], row.revision), row.snapshot_digest)
            finally:
                runtime.dispose()
            with self.assertRaises(sa.exc.IntegrityError), old.begin() as conn:
                conn.execute(analysis_record.delete())
            with self.assertRaises(sa.exc.IntegrityError), old.begin() as conn:
                conn.execute(step.update().values(raw_text='changed'))

    def test_windows_host_and_compose_operator_upgrade_from_n012(self):
        self.fixture = self
        source, profile = 'v01_0008', 'TARGET_0008'
        for mode in ('host', 'compose'):
            with (self.subTest(mode=mode), self.installed_database(source) as (schema, runtime, values),
                  TemporaryDirectory(prefix='ms-n013-', dir=local_checks.TEMP) as directory):
                local = Path(directory)
                if mode == 'host':
                    with self.host_setup(local, values):
                        self.assertEqual(self.host_command('schema-preview', profile=profile), 0)
                        plan = host.read_json(local / 'schema-target-0008.json')
                        self.assertEqual(plan['profile'], profile)
                        self.assertEqual(self.host_command('schema-apply', '0' * 64, profile=profile), 1)
                        self.assert_head(schema, source)
                        self.assertEqual(self.host_command('schema-apply', release_migrate.plan_digest(plan),
                                                           profile=profile), 0)
                else:
                    with self.compose_setup(local, values, source) as (installed, migrations):
                        self.assertEqual(compose.schema_update(SimpleNamespace(schema_digest=None)), 42)
                        review = compose.read(compose.REVIEW)
                        self.assertEqual(review['summary']['profile'], profile)
                        self.assert_head(schema, source)
                        self.assertEqual(compose.schema_update(SimpleNamespace(schema_digest=review['digest'])), 0)
                        self.assert_compose_complete(installed, migrations)
                self.assert_head(schema, 'v01_0009')
                with runtime.connect() as conn:
                    self.assertEqual(conn.scalar(sa.text('SELECT username FROM auth_user')), 'retained')
                    self.assertIsNone(conn.scalar(sa.select(analysis_record.c.operation_id)))
