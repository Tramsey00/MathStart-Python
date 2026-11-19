"""N009 focused contracts and real PG races/crashes on a marked owned server only."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import timedelta
import json
import os
from pathlib import Path
import subprocess
import sys
from threading import Barrier
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from uuid import UUID, uuid4

from alembic import command
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.engine import make_url
from starlette.testclient import TestClient

from backend import release_migrate
from backend.assessment.attempt_models import action, attempt, event, exposure, hint, step
from backend.assessment.attempts import AttemptService, validate_draft
from backend.assessment.models import exercise, exercise_skill, validation, version
from backend.assessment.package import digest
from backend.assessment.templates import TEMPLATES
from backend.infrastructure.http.app import create_app
from backend.infrastructure.http.contracts import validator
from backend.infrastructure.http.signing import Signer
from backend.infrastructure.http.transport import APIError
from backend.infrastructure.uow import UnitOfWork
from backend.knowledge.models import skill
from backend.migrations.schema import HEAD, assert_baseline, inventory
from backend.migrations.upgrade import configuration
from backend.migrations.runtime_privileges import grant_runtime_privileges
from backend.models.baseline import metadata, User, utc_now
from backend.models.protocol import TargetSession
from backend.tests.test_assessment_bank import seed
from backend.users.security import Security, SessionIdentity
from backend.users.service import IdentityService

KEY = 'synthetic-n009-signing-material-no-provider'
ORIGIN = 'https://mathstart.example'
ADMIN = os.getenv('MATHSTART_N009_TEST_ADMIN_URL')
MARKER = 'MS-N009 disposable PostgreSQL server'
SECRET = 'synthetic-private-reveal-n009'


class DraftShapeTests(unittest.TestCase):
    def test_frozen_r02_equation_serialization(self):
        exchange = json.loads(Path('specs/exercises/fixtures/step-submission.exchange-v1.json').read_text(encoding='utf-8'))
        v = SimpleNamespace(schema_code='equation-steps-v1', mode='STEP_BY_STEP',
                            public_schema=TEMPLATES['equation-steps-v1'].public_contract())
        validate_draft({'payload': {}, 'steps': [exchange['request']['submitted_step']]}, v, complete=True)

    def test_raw_order_limits_and_untrusted_server_fields(self):
        v = SimpleNamespace(schema_code='equation-steps-v1', mode='STEP_BY_STEP',
                            public_schema=TEMPLATES['equation-steps-v1'].public_contract())
        draft = {'payload': {}, 'steps': [{'step_no': 1, 'step_type': 'EQUATION_STATE',
                  'payload': {'expression': ' −x = 2,5 '}, 'raw_text': ' −x = 2,5 '}]}
        before = deepcopy(draft)
        validate_draft(draft, v, complete=True)
        self.assertEqual(draft, before)
        for change in ({'step_no': 2}, {'step_id': str(uuid4())}, {'normalized_repr': 'x'},
                       {'parse_status': 'OK'}, {'raw_text': 'a' * 513}, {'payload': {'hidden': 'x'}}):
            invalid = deepcopy(draft)
            invalid['steps'][0].update(change)
            with self.subTest(change=change), self.assertRaises(APIError):
                validate_draft(invalid, v)
        with self.assertRaises(APIError):
            validate_draft({'payload': {}, 'steps': draft['steps'] * 41}, v)


@unittest.skipUnless(ADMIN, 'Requires explicitly owned MS-N009 PostgreSQL server')
class PostgreSQLAttemptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = make_url(ADMIN)
        if (url.drivername, url.host, url.database) != ('postgresql+psycopg', '127.0.0.1', 'postgres') or not url.port:
            raise RuntimeError('Requires marked loopback disposable server')
        cls.admin = sa.create_engine(url, isolation_level='AUTOCOMMIT', hide_parameters=True,
                                     connect_args={'connect_timeout': 5})
        cls.addClassCleanup(cls.admin.dispose)
        with cls.admin.connect() as c:
            marker = c.scalar(sa.text("SELECT shobj_description(oid,'pg_database') FROM pg_database WHERE datname=current_database()"))
            if marker != MARKER:
                raise RuntimeError('Missing MS-N009 server reservation marker')
        cls.name = 'test_n009_' + uuid4().hex
        with cls.admin.connect() as c:
            c.execute(sa.text('CREATE DATABASE ' + cls.name))
        cls.addClassCleanup(cls.drop_database, cls.name)
        cls.url = url.set(database=cls.name)
        cls.engine = sa.create_engine(cls.url, hide_parameters=True, connect_args={'connect_timeout': 5})
        cls.addClassCleanup(cls.engine.dispose)
        plan = release_migrate.preview(cls.engine, KEY, 'FRESH')
        release_migrate.apply(cls.engine, KEY, plan, release_migrate.plan_digest(plan), maintenance=True)
        cls.topics = seed(cls.engine)
        cls.security = Security(cls.engine, KEY, ORIGIN)
        cls.identity_service = IdentityService(cls.security)
        cls.service = AttemptService(cls.identity_service, Signer(KEY),
            public_release=lambda uow: SimpleNamespace(page=lambda slug: cls.topics[slug]))

    @classmethod
    def drop_database(cls, name):
        if not name.startswith('test_n009_'):
            raise RuntimeError('Not an owned database')
        with cls.admin.connect() as c:
            c.execute(sa.text('DROP DATABASE ' + name + ' WITH (FORCE)'))

    def setUp(self):
        self.owner, self.token = self.new_identity()
        self.other, self.other_token = self.new_identity()
        self.eid, self.vid = self.new_exercise()

    def new_identity(self, user_id=None):
        with Session(self.engine) as s, s.begin():
            user = s.get(User, user_id) if user_id else User(username='n009_' + uuid4().hex[:16])
            if not user_id:
                s.add(user)
                s.flush()
            row, token, _ = self.security.issue(s, user, utc_now())
            identity = SessionIdentity(user.id, row.id, row.lineage_id, row.revocation_epoch)
        return identity, token

    def new_exercise(self, schema='integer-final-v1', hints=False):
        eid, vid = uuid4(), uuid4()
        template = TEMPLATES[schema]
        public = template.public_contract()
        if hints:
            public['allowed_help_actions'] = ['HINT', 'REVEAL']
            public['hint_policy'] = {'allowed': True, 'levels': [1, 2, 3]}
        with self.engine.begin() as c:
            topic_id = next(iter(self.topics.values()))['id']
            c.execute(exercise.insert().values(id=eid, code='n009_' + uuid4().hex, topic_id=topic_id, created_at=utc_now()))
            c.execute(version.insert().values(id=vid, exercise_id=eid, version=1, status='DRAFT', mode=template.mode,
                difficulty=1, statement='Synthetic problem', public_schema=public, schema_code=schema,
                provenance='synthetic test only', digest='a' * 64))
            c.execute(validation.insert().values(version_id=vid, checker_type=template.checker, checker_version=1,
                answer_key=SECRET, accepted_variants=[SECRET+'variant'], validation_spec={'private': SECRET},
                canonical_solution=[SECRET+'solution'], digest='b' * 64))
            c.execute(exercise_skill.insert().values(version_id=vid, skill_id=c.scalar(sa.select(skill.c.id).limit(1)), role='PRIMARY'))
            if hints:
                for level in (1, 2, 3):
                    text = f'Synthetic reviewed strategy {level}'
                    c.execute(hint.insert().values(version_id=vid, level=level, text=text,
                        reviewed_digest=digest({'version_id': str(vid), 'level': level, 'text': text})))
            c.execute(version.update().where(version.c.id == vid).values(status='PUBLISHED'))
        return eid, vid

    def call(self, operation, body, pk=None, key=None, identity=None):
        suffix = {'create_attempt': '', 'update_draft': 'draft/', 'submit_attempt': 'submit/',
                  'abandon_attempt': 'abandon/', 'request_hint': 'hints/', 'reveal_attempt': 'reveal/'}[operation]
        route = f'/api/v1/attempts/{pk}/{suffix}' if pk else '/api/v1/attempts/'
        return self.service.mutate(identity or self.owner, operation, route, body,
                                   key or str(uuid4()), str(uuid4()), str(pk) if pk else None)

    def create(self, eid=None, previous=None, key=None):
        body = {'exercise_id': str(eid or self.eid), 'contract_version': 1, 'version': 1}
        if previous:
            body['previous_attempt_id'] = previous
        return self.call('create_attempt', body, key=key)[0]['data']

    def save(self, pk, revision=1, draft=None):
        return self.call('update_draft', {'expected_revision': revision, 'contract_version': 1,
                         'draft': draft or {'payload': {'answer': ' −2,5 '}, 'steps': []}}, pk)[0]['data']

    def test_lifecycle_snapshot_replay_conflict_correction_and_archive(self):
        first = self.create(key='create')
        self.assertEqual(first, self.create(key='create'))
        pk = first['id']
        saved = self.save(pk)
        self.assertEqual(saved['draft']['payload']['answer'], ' −2,5 ')
        body = {'expected_revision': 2, 'contract_version': 1}
        submitted, status = self.call('submit_attempt', body, pk, 'submit')
        self.assertEqual(status, 202)
        self.assertTrue(validator('PendingAttemptResponse').is_valid(submitted))
        self.assertEqual(self.call('submit_attempt', body, pk, 'submit'), (submitted, 202))
        for operation, payload, key, code in (
            ('submit_attempt', dict(body, expected_revision=1), 'submit', 'IDEMPOTENCY_CONFLICT'),
            ('update_draft', dict(body, draft=saved['draft']), None, 'STATE_CONFLICT'),
            ('abandon_attempt', body, None, 'STATE_CONFLICT')):
            with self.subTest(operation=operation), self.assertRaises(APIError) as error:
                self.call(operation, payload, pk, key)
            self.assertEqual(error.exception.code, code)
        corrected = self.create(previous=pk)
        self.assertEqual(corrected['previous_attempt_id'], pk)
        abandoned, _ = self.call('abandon_attempt', {'expected_revision': 1, 'contract_version': 1}, corrected['id'], 'abandon')
        self.assertEqual(abandoned['data']['state'], 'ABANDONED')
        with self.engine.begin() as c:
            c.execute(version.update().where(version.c.id == self.vid).values(status='ARCHIVED'))
        self.assertEqual(self.service.get(self.owner, pk)['exercise_version']['id'], str(self.vid))
        self.assertEqual(self.call('submit_attempt', body, pk, 'submit'), (submitted, 202))
        with self.assertRaises(APIError):
            self.create()
        self.assertEqual(self.service.get(self.owner, pk)['snapshot_digest'], submitted['data']['snapshot_digest'])

    def test_steps_stable_ids_order_and_db_freeze(self):
        eid, _ = self.new_exercise('equation-steps-v1')
        pk = self.create(eid)['id']
        draft = {'payload': {}, 'steps': [{'step_no': 1, 'step_type': 'EQUATION_STATE',
                  'payload': {'expression': ' −x = 2,5 '}, 'raw_text': 'raw −x = 2,5'}]}
        first = self.save(pk, draft=draft)
        second = self.save(pk, 2, draft)
        self.assertEqual(first['steps'][0]['step_id'], second['steps'][0]['step_id'])
        self.assertIsNone(second['steps'][0]['normalized_repr'])
        self.call('submit_attempt', {'expected_revision': 3, 'contract_version': 1}, pk)
        for statement in (attempt.update().where(attempt.c.id == UUID(pk)).values(draft={}),
                          step.delete().where(step.c.attempt_id == UUID(pk))):
            with self.assertRaises(sa.exc.IntegrityError), self.engine.begin() as c:
                c.execute(statement)

    def test_exposure_reveal_pending_and_new_attempt_do_not_reset(self):
        pk = self.create()['id']
        self.save(pk)
        submitted, _ = self.call('submit_attempt', {'expected_revision': 2, 'contract_version': 1}, pk)
        revealed, _ = self.call('reveal_attempt', {'contract_version': 1, 'confirm': True}, pk, 'reveal')
        self.assertIn(SECRET, revealed['data']['revealed_content']['answer'])
        self.assertEqual(revealed['data']['attempt']['snapshot_digest'], submitted['data']['snapshot_digest'])
        self.assertEqual(self.call('reveal_attempt', {'contract_version': 1, 'confirm': True}, pk, 'reveal')[0], revealed)
        corrected = self.create(previous=pk)
        self.assertEqual(corrected['eligibility']['reason'], 'REVEAL_EXPOSURE')
        self.assertFalse(corrected['eligibility']['positive_credit_eligible'])
        self.assertNotIn(SECRET, json.dumps(self.service.get(self.owner, pk)))
        with self.assertRaises(sa.exc.IntegrityError), self.engine.begin() as c:
            c.execute(exposure.update().where(exposure.c.user_id == self.owner.user_id).values(revealed_at=None))

    def test_self_check_and_reviewed_hint_policy(self):
        eid, _ = self.new_exercise('self-check-v1')
        pk = self.create(eid)['id']
        with self.assertRaises(APIError):
            self.call('submit_attempt', {'expected_revision': 1, 'contract_version': 1}, pk)
        result, _ = self.call('reveal_attempt', {'contract_version': 1, 'confirm': True}, pk)
        self.assertEqual(result['data']['attempt']['state'], 'REVIEWED')
        self.assertEqual(result['data']['attempt']['eligibility']['reason'], 'SELF_CHECK')
        eid, vid = self.new_exercise(hints=True)
        pk = self.create(eid)['id']
        self.save(pk)
        response, _ = self.call('request_hint', {'contract_version': 1, 'level': 2}, pk, 'hint')
        self.assertEqual(self.call('request_hint', {'contract_version': 1, 'level': 2}, pk, 'hint')[0], response)
        self.assertEqual(self.service.get(self.owner, pk)['revision'], 2)
        lower, _ = self.call('request_hint', {'contract_version': 1, 'level': 1}, pk)
        self.assertEqual(lower['data']['exposure']['max_help_level'], 2)
        self.assertNotIn(SECRET, json.dumps(response))
        self.call('abandon_attempt', {'expected_revision': 2, 'contract_version': 1}, pk)
        next_attempt = self.create(eid, pk)
        self.assertEqual(next_attempt['eligibility']['reason'], 'HINT_EXPOSURE')
        with self.assertRaises(APIError):
            self.call('request_hint', {'contract_version': 1, 'level': 1}, self.create()['id'])

    def race(self, left, right):
        barrier = Barrier(2)
        def run(fn):
            barrier.wait(timeout=10)
            try:
                return fn()
            except APIError as error:
                return error.code
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(run, fn) for fn in (left, right)]
            return [f.result(timeout=20) for f in futures]

    def test_real_two_session_edit_submit_race(self):
        pk = self.create()['id']
        self.save(pk)
        second, _ = self.new_identity(self.owner.user_id)
        results = self.race(lambda: self.save(pk, 2), lambda: self.call('submit_attempt',
            {'expected_revision': 2, 'contract_version': 1}, pk, identity=second))
        self.assertEqual(sum(isinstance(r, str) for r in results), 1, results)
        self.assertIn(next(r for r in results if isinstance(r, str)), ('REVISION_CONFLICT', 'STATE_CONFLICT'))
        self.assertEqual(self.service.get(self.owner, pk)['revision'], 3)

    def test_real_duplicate_create_race_and_help_submit_race(self):
        second, _ = self.new_identity(self.owner.user_id)
        body = {'exercise_id': str(self.eid), 'contract_version': 1, 'version': 1}
        results = self.race(lambda: self.call('create_attempt', body, key='race'),
                            lambda: self.call('create_attempt', body, key='race', identity=second))
        self.assertEqual(results[0], results[1])
        pk = results[0][0]['data']['id']
        self.save(pk)
        results = self.race(lambda: self.call('reveal_attempt', {'contract_version': 1, 'confirm': True}, pk),
            lambda: self.call('submit_attempt', {'expected_revision': 2, 'contract_version': 1}, pk, identity=second))
        self.assertFalse(any(isinstance(r, str) for r in results))
        canonical = self.service.get(self.owner, pk)
        self.assertEqual(canonical['state'], 'SUBMITTED')
        self.assertIsNotNone(canonical['exposure']['revealed_at'])
        self.assertFalse(canonical['eligibility']['positive_credit_eligible'])

    def test_hint_submit_race_and_permanent_key_scope(self):
        eid, vid = self.new_exercise(hints=True)
        pk = self.create(eid)['id']
        self.save(pk)
        second, _ = self.new_identity(self.owner.user_id)
        results = self.race(lambda: self.call('request_hint', {'contract_version': 1, 'level': 3}, pk, 'hint-race'),
            lambda: self.call('submit_attempt', {'expected_revision': 2, 'contract_version': 1}, pk, identity=second))
        self.assertFalse(any(isinstance(r, str) for r in results))
        canonical = self.service.get(self.owner, pk)
        self.assertEqual(canonical['exposure']['max_help_level'], 3)
        self.assertFalse(canonical['eligibility']['independent'])
        other = self.create(eid, pk)['id']
        with self.assertRaises(APIError) as error:
            self.call('request_hint', {'contract_version': 1, 'level': 3}, other, 'hint-race')
        self.assertEqual(error.exception.code, 'IDEMPOTENCY_CONFLICT')
        # No short-lived IdentityReceipt is the authority for these actions.
        with self.engine.begin() as c:
            c.execute(metadata.tables['users_identityreceipt'].delete().where(
                metadata.tables['users_identityreceipt'].c.scope == 'user:' + str(self.owner.user_id)))
        self.assertEqual(self.call('request_hint', {'contract_version': 1, 'level': 3}, pk, 'hint-race'), results[0])

    def test_process_crash_before_commit_and_lost_ack_after_commit(self):
        code = """
import os,sys
from types import SimpleNamespace
from uuid import UUID,uuid4
import sqlalchemy as sa
from backend.assessment.attempts import AttemptService
from backend.infrastructure.http.signing import Signer
from backend.infrastructure.uow import UnitOfWork
from backend.users.security import SessionIdentity
engine=sa.create_engine(sys.argv[1],connect_args={'connect_timeout':5})
identity=SessionIdentity(int(sys.argv[2]),UUID(sys.argv[3]),UUID(sys.argv[4]),int(sys.argv[5]))
service=AttemptService(SimpleNamespace(engine=engine,security=SimpleNamespace(keys=(sys.argv[6],))),Signer(sys.argv[6]))
original=UnitOfWork.commit
def crash(self):
 if sys.argv[8]=='after':original(self)
 os._exit(74 if sys.argv[8]=='after' else 73)
UnitOfWork.commit=crash
operation=sys.argv[9]
body={'expected_revision':2,'contract_version':1} if operation=='submit_attempt' else {'contract_version':1,'confirm':True}
suffix='submit/' if operation=='submit_attempt' else 'reveal/'
service.mutate(identity,operation,f'/api/v1/attempts/{sys.argv[7]}/{suffix}',body,'crash-key',str(uuid4()),sys.argv[7])
"""
        for operation in ('submit_attempt', 'reveal_attempt'):
            # Separate owner/version avoids an already used key or prior exposure.
            if operation == 'reveal_attempt':
                self.owner, _ = self.new_identity()
            pk = self.create()['id']
            self.save(pk)
            for phase, expected in (('before', 73), ('after', 74)):
                process = subprocess.run([sys.executable, '-c', code, self.url.render_as_string(hide_password=False),
                    str(self.owner.user_id), str(self.owner.session_id), str(self.owner.lineage_id),
                    str(self.owner.revocation_epoch), KEY, pk, phase, operation], capture_output=True, timeout=20)
                self.assertEqual(process.returncode, expected, process.stderr.decode())
                self.assertEqual(process.stdout, b'')  # no pre-commit disclosure
                canonical = self.service.get(self.owner, pk)
                if operation == 'submit_attempt':
                    self.assertEqual(canonical['state'], 'STARTED' if phase == 'before' else 'SUBMITTED')
                else:
                    self.assertEqual(canonical['exposure']['revealed_at'] is None, phase == 'before')
            body = {'expected_revision': 2, 'contract_version': 1} if operation == 'submit_attempt' else {'contract_version': 1, 'confirm': True}
            replay, status = self.call(operation, body, pk, 'crash-key')
            self.assertEqual(status, 202 if operation == 'submit_attempt' else 200)
            with self.engine.connect() as c:
                self.assertEqual(c.scalar(sa.select(sa.func.count()).select_from(action).where(
                    action.c.attempt_id == UUID(pk), action.c.operation == operation)), 1)

    def test_http_auth_csrf_owner_revision_privacy_and_logout_retry(self):
        app = create_app(self.engine, Signer(KEY), identity_service=self.identity_service, public_origin=ORIGIN)
        pk = self.create()['id']
        with TestClient(app, base_url=ORIGIN) as client:
            body = {'expected_revision': 1, 'contract_version': 1}
            path = f'/api/v1/attempts/{pk}/abandon/'
            self.assertEqual(client.post(path, json=body).status_code, 401)
            client.cookies.set('sessionid', self.token)
            self.assertEqual(client.post(path, json=body).status_code, 403)
            token = client.get('/api/v1/auth/csrf/').json()['data']['csrf_token']
            headers = {'X-CSRFToken': token, 'Origin': ORIGIN, 'Idempotency-Key': 'http-key'}
            client.cookies.set('sessionid', self.other_token)
            missing = client.get(f'/api/v1/attempts/{uuid4()}/')
            foreign = client.get(f'/api/v1/attempts/{pk}/')
            self.assertEqual((foreign.status_code, missing.status_code), (404, 404))
            self.assertEqual(foreign.json()['error']['code'], missing.json()['error']['code'])
            self.assertNotIn(pk, foreign.text)
            self.assertEqual(client.post(path, json=body, headers=headers).status_code, 404)
            client.cookies.set('sessionid', self.token)
            self.save(pk)
            stale = client.put(f'/api/v1/attempts/{pk}/draft/', json=dict(body,draft={'payload':{},'steps':[]}),headers=headers)
            self.assertEqual(stale.status_code, 409)
            self.assertTrue(validator('RevisionConflict').is_valid(stale.json()))
            self.assertEqual(stale.json()['error']['current_revision'], 2)
            success = client.post(path, json=dict(body, expected_revision=2), headers=headers)
            self.assertEqual(success.status_code, 200)
            listing = client.get('/api/v1/attempts/?page_size=1')
            self.assertEqual(listing.status_code, 200)
            self.assertNotIn(SECRET, listing.text)
            self.assertEqual(client.get('/api/v1/attempts/not-uuid/').status_code, 400)
            self.identity_service.logout(self.owner)
            self.assertEqual(client.post(path, json=dict(body,expected_revision=2), headers=headers).status_code, 401)
            relogin, _ = self.new_identity(self.owner.user_id)
            replay, _ = self.call('abandon_attempt', dict(body, expected_revision=2), pk, 'http-key', identity=relogin)
            self.assertEqual(replay, success.json())
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(sa.func.count()).select_from(action).where(
                action.c.attempt_id == UUID(pk), action.c.operation == 'abandon_attempt')), 1)

    def test_guest_gates_all_mutations_without_domain_writes(self):
        app = create_app(self.engine, Signer(KEY), identity_service=self.identity_service, public_origin=ORIGIN)
        pk = self.create()['id']
        with self.engine.connect() as c:
            before = [c.scalar(sa.select(sa.func.count()).select_from(t)) for t in (attempt, exposure, action, event)]
        with TestClient(app, base_url=ORIGIN) as client:
            for method, path, body in (
                ('post', '/api/v1/attempts/', {'exercise_id': str(self.eid), 'contract_version': 1, 'version': 1}),
                ('put', f'/api/v1/attempts/{pk}/draft/', {'expected_revision': 1, 'contract_version': 1, 'draft': {'payload': {}, 'steps': []}}),
                ('post', f'/api/v1/attempts/{pk}/submit/', {'expected_revision': 1, 'contract_version': 1}),
                ('post', f'/api/v1/attempts/{pk}/hints/', {'contract_version': 1, 'level': 1}),
                ('post', f'/api/v1/attempts/{pk}/reveal/', {'contract_version': 1, 'confirm': True}),
                ('post', f'/api/v1/attempts/{pk}/abandon/', {'expected_revision': 1, 'contract_version': 1}),
            ):
                response = getattr(client, method)(path, json=body)
                self.assertEqual(response.status_code, 401, path)
                self.assertNotIn(SECRET, response.text)
            client.cookies.set('sessionid', self.token)
            self.assertEqual(client.get(f'/api/v1/attempts/{pk}/').status_code, 200)
            self.assertEqual(client.get('/api/v1/attempts/').status_code, 200)
        with self.engine.connect() as c:
            self.assertEqual(before, [c.scalar(sa.select(sa.func.count()).select_from(t)) for t in (attempt, exposure, action, event)])

    def test_http_create_save_submit_reveal_and_active_topic_binding(self):
        app = create_app(self.engine, Signer(KEY), identity_service=self.identity_service, public_origin=ORIGIN)
        body = {'exercise_id': str(self.eid), 'contract_version': 1, 'version': 1}
        release = SimpleNamespace(page=lambda slug: self.topics[slug])
        with TestClient(app, base_url=ORIGIN) as client:
            client.cookies.set('sessionid', self.token)
            token = client.get('/api/v1/auth/csrf/').json()['data']['csrf_token']
            headers = {'Origin': ORIGIN, 'X-CSRFToken': token, 'Idempotency-Key': str(uuid4())}
            with patch('backend.infrastructure.http.app.active_release', return_value=release):
                created = client.post('/api/v1/attempts/', json=body, headers=headers)
            self.assertEqual(created.status_code, 201)
            self.assertTrue(validator('AttemptResponse').is_valid(created.json()))
            pk = created.json()['data']['id']
            draft = {'payload': {'answer': ' −2,5 '}, 'steps': []}
            saved = client.put(f'/api/v1/attempts/{pk}/draft/', json={
                'contract_version': 1, 'expected_revision': 1, 'draft': draft}, headers=headers)
            self.assertEqual(saved.status_code, 200)
            submitted = client.post(f'/api/v1/attempts/{pk}/submit/',
                json={'contract_version': 1, 'expected_revision': 2}, headers=headers)
            self.assertEqual(submitted.status_code, 202)
            self.assertTrue(validator('PendingAttemptResponse').is_valid(submitted.json()))
            self.assertEqual(client.get(f'/api/v1/attempts/{pk}/').json()['data']['draft'], draft)
            revealed = client.post(f'/api/v1/attempts/{pk}/reveal/',
                json={'contract_version': 1, 'confirm': True}, headers=headers)
            self.assertEqual(revealed.status_code, 200)
            self.assertTrue(validator('RevealResultResponse').is_valid(revealed.json()))
            self.assertIn(SECRET, revealed.text)
            self.assertNotIn(SECRET, client.get(f'/api/v1/attempts/{pk}/').text)
            with patch('backend.infrastructure.http.app.active_release', return_value=SimpleNamespace(
                    page=lambda slug: {'id': -1, 'page_type': 'topic'})):
                refused = client.post('/api/v1/attempts/', json=body,
                    headers={**headers, 'Idempotency-Key': str(uuid4())})
            self.assertEqual(refused.status_code, 503)

    def test_get_is_a_coherent_snapshot_during_another_tab_save(self):
        eid, _ = self.new_exercise('equation-steps-v1')
        pk = self.create(eid)['id']
        draft = {'payload': {}, 'steps': [{'step_no': 1, 'step_type': 'EQUATION_STATE',
                  'payload': {'expression': 'x=1'}, 'raw_text': 'x=1'}]}
        saved = self.save(pk, draft=draft)
        second, _ = self.new_identity(self.owner.user_id)
        original = self.service.dto
        entered = False
        def concurrent_save(session, row, *args, **kwargs):
            nonlocal entered
            if not entered:
                entered = True
                updated = deepcopy(draft)
                updated['steps'][0].update(payload={'expression': 'x=2'}, raw_text='x=2')
                self.call('update_draft', {'expected_revision': 2, 'contract_version': 1, 'draft': updated}, pk, identity=second)
            return original(session, row, *args, **kwargs)
        with patch.object(self.service, 'dto', side_effect=concurrent_save):
            observed = self.service.get(self.owner, pk)
        self.assertEqual(observed, saved)
        self.assertEqual(self.service.get(self.owner, pk)['revision'], 3)

    def test_fresh_schema_upgrade_retains_history_and_guards(self):
        with self.engine.connect() as c:
            assert_baseline(c, 'FRESH', allow_protocol=True, require_history=False)
        name = 'test_n009_' + uuid4().hex
        with self.admin.connect() as c:
            c.execute(sa.text('CREATE DATABASE ' + name))
        self.addCleanup(self.drop_database, name)
        engine = sa.create_engine(self.url.set(database=name))
        self.addCleanup(engine.dispose)
        with engine.begin() as c:
            command.upgrade(configuration(c), 'v01_0006')
        topics = seed(engine)
        with patch.object(self, 'engine', engine):
            self.new_exercise()
        bank_tables = (exercise, version, validation, exercise_skill)
        with engine.begin() as c:
            before = inventory(c)
            retained = c.execute(sa.select(skill)).all()
            retained_bank = [c.execute(sa.select(table).order_by(*table.primary_key.columns)).all() for table in bank_tables]
        plan = release_migrate.preview(engine, KEY, 'TARGET_0006')
        result = release_migrate.apply(engine, KEY, plan, release_migrate.plan_digest(plan), maintenance=True)
        self.assertEqual(result['head'], HEAD)
        with engine.connect() as c:
            assert_baseline(c, 'FRESH', allow_protocol=True, require_history=False)
            self.assertEqual(c.execute(sa.select(skill)).all(), retained)
            self.assertEqual([c.execute(sa.select(table).order_by(*table.primary_key.columns)).all()
                              for table in bank_tables], retained_bank)
            self.assertEqual(inventory(c)['sequences'], before['sequences'])
        pk = self.create()['id']
        for table in (attempt, action, exposure, event, step, hint):
            with self.assertRaises(sa.exc.IntegrityError), self.engine.begin() as c:
                c.exec_driver_sql(f'TRUNCATE {table.name} CASCADE')
        with self.assertRaises(sa.exc.IntegrityError), self.engine.begin() as c:
            c.execute(action.update().where(action.c.attempt_id == UUID(pk)).values(status=200))

    def test_runtime_privileges_do_not_grant_checker_or_ddl(self):
        with self.engine.begin() as c:
            c.execute(sa.text('DO $$ BEGIN CREATE ROLE local_runtime; EXCEPTION WHEN duplicate_object THEN NULL; END $$'))
            grant_runtime_privileges(c.connection.driver_connection)
            self.assertFalse(c.scalar(sa.text("SELECT has_table_privilege('local_runtime','assessment_exercise_validation','SELECT')")))
            self.assertFalse(c.scalar(sa.text("SELECT has_column_privilege('local_runtime','assessment_exercise_validation','validation_spec','SELECT')")))
            self.assertTrue(c.scalar(sa.text("SELECT has_column_privilege('local_runtime','assessment_exercise_validation','canonical_solution','SELECT')")))
        runtime = sa.create_engine(self.url, hide_parameters=True)
        self.addCleanup(runtime.dispose)
        @sa.event.listens_for(runtime, 'connect')
        def assume_runtime(connection, record):
            with connection.cursor() as cursor:
                cursor.execute('SET ROLE local_runtime')
            connection.commit()
        identity = IdentityService(Security(runtime, KEY, ORIGIN))
        service = AttemptService(identity, Signer(KEY), public_release=self.service.public_release)
        with patch.object(self, 'service', service):
            pk = self.create()['id']
            self.save(pk)
            submitted, status = self.call('submit_attempt', {'expected_revision': 2, 'contract_version': 1}, pk)
            self.assertEqual(status, 202)
            revealed, status = self.call('reveal_attempt', {'contract_version': 1, 'confirm': True}, pk)
            self.assertEqual(status, 200)
            self.assertIn(SECRET, revealed['data']['revealed_content']['answer'])
            self.assertEqual(service.get(self.owner, pk)['snapshot_digest'], submitted['data']['snapshot_digest'])
        with self.assertRaises(sa.exc.IntegrityError), runtime.begin() as c:
            c.execute(version.update().where(version.c.id == self.vid).values(provenance='forbidden runtime edit'))
        with self.assertRaises(sa.exc.ProgrammingError), runtime.connect() as c:
            c.execute(sa.select(validation.c.validation_spec))
