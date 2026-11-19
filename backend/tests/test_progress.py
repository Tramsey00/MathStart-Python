"""N012 parity and owned PostgreSQL integration. No provider or protected DB."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
from threading import Barrier
import unittest
from unittest.mock import patch
from uuid import UUID, uuid4

from alembic import command
import sqlalchemy as sa
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from scripts import r03_contract_reference as oracle, r03a_contract_reference as completion_oracle
from backend.progress import _r03_v1 as r03, _r03a_v1 as r03a
from backend.progress.contracts import Delivery, CompletedAttempt
from backend.progress.service import ProgressService, canonical_event
from backend.progress.models import event, completion, state, attempt_binding, receipt, PROGRESS_TABLES
from backend.progress.http import decimal_json
from backend.assessment.models import exercise, version, validation, exercise_skill
from backend.assessment.templates import TEMPLATES
from backend.assessment.completion_read import verify_exercise_mapping, verify_version_skills
from backend.assessment.attempt_models import attempt as assessed_attempt
from backend.assessment.attempts import AttemptService
from backend.infrastructure.http.app import create_app
from backend.infrastructure.http.signing import Signer
from backend.knowledge.models import skill
from backend.models.baseline import User, utc_now
from backend.tests.test_assessment_bank import seed
from backend.migrations.upgrade import configuration
from backend.migrations.schema import HEAD, assert_baseline, inventory
from backend.migrations.runtime_privileges import grant_runtime_privileges
from backend import release_migrate
from backend.users.security import Security, SessionIdentity
from backend.users.service import IdentityService

FIXTURES = Path('specs/progress/fixtures')
KEY = 'synthetic-n012-isolated-test-signing-key'
ORIGIN = 'https://mathstart.example'
ADMIN = os.getenv('MATHSTART_N012_TEST_ADMIN_URL')
CODE = 'negative_numbers'
BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


class ParityTests(unittest.TestCase):
    def test_numerical_source_is_identical_and_all_golden_cases_match(self):
        self.assertEqual(Path('scripts/r03_contract_reference.py').read_bytes(), Path('backend/progress/_r03_v1.py').read_bytes())
        adapted = Path('backend/progress/_r03a_v1.py').read_text().replace('from . import _r03_v1 as frozen', 'from scripts import r03_contract_reference as frozen')
        self.assertEqual(adapted, Path('scripts/r03a_contract_reference.py').read_text())
        data = json.loads((FIXTURES/'progress-v1-cases.json').read_text())
        for case in data['cases']:
            with self.subTest(case=case['id']):
                result = r03.replay(case['events'], case['user_id'], case['skill_id'])
                self.assertEqual(result, oracle.replay(case['events'], case['user_id'], case['skill_id']))
                for key, expected in case['expected'].items(): self.assertEqual(result['state'][key], expected)
        for case in data['arithmetic_cases']:
            self.assertEqual(str(r03.clamp_round(case['input'])), case['expected'])

    def test_completion_datasets_and_legacy_versions_match(self):
        datasets = json.loads((FIXTURES/'completion-v1-cases.json').read_text())['datasets']
        for name, case in datasets.items():
            scopes = {(v['user_id'], v['skill_id']) for v in case['events'] + case['facts']}
            for owner, code in scopes:
                with self.subTest(dataset=name, owner=owner, skill=code):
                    try:
                        expected = completion_oracle.replay_v1_1(case['events'], case['facts'], owner, code, authority=case['authority'])
                    except oracle.ContractError:
                        with self.assertRaises(r03.ContractError): r03a.replay_v1_1(case['events'], case['facts'], owner, code, authority=case['authority'])
                    else:
                        self.assertEqual(r03a.replay_v1_1(case['events'], case['facts'], owner, code, authority=case['authority']), expected)
        legacy = {c['id']: c for c in json.loads((FIXTURES/'progress-v1-cases.json').read_text())['cases']}
        for case in json.loads((FIXTURES/'progress-v1.1-parity.json').read_text())['cases']:
            original = legacy[case['legacy_case_id']]
            self.assertEqual(r03a.import_progress_v1_completions(original['events'], original['user_id'], original['skill_id'], authority=case['authority']),
                completion_oracle.import_progress_v1_completions(original['events'], original['user_id'], original['skill_id'], authority=case['authority']))

    def test_no_float_and_immutable_delivery(self):
        with self.assertRaises(r03.ContractError): Delivery(events=[{'difficulty': 1.0}])
        data = {'x': ['original']}
        delivery = Delivery(events=[data]); data['x'][0] = 'mutated'
        detached = delivery.events; detached[0]['x'][0] = 'mutated again'
        self.assertEqual(delivery.events, [{'x': ['original']}])
        from decimal import Decimal
        self.assertEqual(decimal_json({'n': Decimal('0.10')}), '{"n":0.10}')


@unittest.skipUnless(ADMIN, 'Explicit owned MS-N012 PostgreSQL server required')
class PostgreSQLProgressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = make_url(ADMIN)
        if (url.drivername, url.host, url.database) != ('postgresql+psycopg','127.0.0.1','postgres') or not url.port:
            raise RuntimeError('Unreserved PostgreSQL endpoint')
        cls.url = url
        cls.admin = sa.create_engine(url, isolation_level='AUTOCOMMIT', hide_parameters=True)
        cls.addClassCleanup(cls.admin.dispose)
        with cls.admin.connect() as c:
            if c.scalar(sa.text("SELECT shobj_description(oid,'pg_database') FROM pg_database WHERE datname=current_database()")) != 'MS-N012 disposable PostgreSQL server':
                raise RuntimeError('Missing N012 marker')

    @contextmanager
    def database(self):
        name = 'test_n012_' + uuid4().hex
        with self.admin.connect() as c: c.exec_driver_sql('CREATE DATABASE ' + name)
        engine = sa.create_engine(self.url.set(database=name), hide_parameters=True)
        try: yield engine
        finally:
            engine.dispose()
            with self.admin.connect() as c: c.exec_driver_sql('DROP DATABASE ' + name + ' WITH (FORCE)')

    def setUp(self):
        self.context = self.database(); self.engine = self.context.__enter__()
        self.addCleanup(self.context.__exit__, None, None, None)
        plan = release_migrate.preview(self.engine, KEY, 'FRESH')
        release_migrate.apply(self.engine, KEY, plan, release_migrate.plan_digest(plan), maintenance=True)
        self.topics = seed(self.engine)
        self.sources = {}
        def read(session, attempt_id):
            if attempt_id not in self.sources: raise r03.ContractError('No verified source')
            return self.sources[attempt_id]
        def fixture_binding(session, source):
            # Explicit trusted Assessment projection fixture stands in for N013.
            # The real adapter must also find a durable COMPLETED row, absent in N009.
            verify_exercise_mapping(session, source)
            if session.scalar(sa.select(assessed_attempt.c.id).where(assessed_attempt.c.id == UUID(source.attempt_id))):
                verify_version_skills(session, source)
            elif self.sources.get(source.attempt_id) != source:
                raise r03.ContractError('Unverified synthetic projection')
        self.service = ProgressService(read_completion=read, verify_binding=fixture_binding)
        self.security = Security(self.engine, KEY, ORIGIN)
        self.identity = IdentityService(self.security)
        self.owner, self.token = self.user()
        self.other, self.other_token = self.user()
        self.eid, self.vid = uuid4(), uuid4()
        with self.engine.begin() as c:
            self.sid = c.scalar(sa.select(skill.c.id).where(skill.c.code == CODE))
            c.execute(exercise.insert().values(id=self.eid, code='synthetic_' + uuid4().hex, topic_id=1, created_at=utc_now()))
            c.execute(version.insert().values(id=self.vid, exercise_id=self.eid, version=1, status='DRAFT', mode='FINAL_ANSWER',
                difficulty=3, statement='Synthetic binding', public_schema=TEMPLATES['integer-final-v1'].public_contract(),
                schema_code='integer-final-v1', provenance='synthetic-N012', digest='a'*64))
            c.execute(validation.insert().values(version_id=self.vid, checker_type='integer_exact', checker_version=1,
                answer_key='private-synthetic-key', accepted_variants=[], validation_spec={}, canonical_solution=['private-solution'], digest='b'*64))
            c.execute(exercise_skill.insert().values(version_id=self.vid, skill_id=self.sid, role='PRIMARY'))
            c.execute(version.update().where(version.c.id == self.vid).values(status='PUBLISHED'))

    def user(self):
        with Session(self.engine) as s, s.begin():
            user = User(username='n012_' + uuid4().hex[:16]); s.add(user); s.flush()
            issued, token, _ = self.security.issue(s, user, utc_now())
            return SessionIdentity(user.id, issued.id, issued.lineage_id, issued.revocation_epoch), token

    def delivery(self, number=1, *, kind='CORRECT_FIRST_TRY', neutral=False, owner=None, attempt_id=None):
        user = (owner or self.owner).user_id
        attempt_id = attempt_id or str(uuid4())
        time = (BASE + timedelta(minutes=number)).isoformat(timespec='microseconds').replace('+00:00','Z')
        fact = dict(completion_id=str(uuid4()), user_id=str(user), skill_id=CODE, attempt_id=attempt_id,
            outcome='UNSUPPORTED' if neutral else 'CORRECT', independent_correct=not neutral and kind=='CORRECT_FIRST_TRY',
            completed_at=time, policy_version='progress-v1.1')
        events = [] if neutral else [dict(event_id=str(uuid4()), user_id=str(user), skill_id=CODE, attempt_id=attempt_id,
            event_kind=kind, occurred_at=time, completed_at=time, policy_version='progress-v1', evidence_ref='validated-final',
            difficulty='medium', hint_used=kind=='CORRECT_AFTER_HINT', reveal_used=False)]
        delivery = Delivery(events=events, facts=[fact])
        self.sources[attempt_id] = CompletedAttempt(attempt_id,user,str(self.vid),'FINAL_ANSWER','COMPLETED',time,
            ((CODE,fact['outcome'],fact['independent_correct']),),delivery)
        return delivery

    def ingest(self, delivery):
        with Session(self.engine) as s, s.begin(): return self.service.ingest(s, delivery)

    def projection(self):
        with self.engine.connect() as c:
            return c.execute(sa.select(state).where(state.c.user_id == self.owner.user_id, state.c.skill_id == self.sid)).first()

    def test_late_delivery_replay_all_fields_and_legacy_reducer(self):
        deliveries = [self.delivery(i) for i in (3,1,2)]
        for d in deliveries: self.ingest(d)
        before = self.projection()
        with Session(self.engine) as s, s.begin():
            replayed = self.service.replay(s,self.owner.user_id,CODE)
            legacy = self.service.replay(s,self.owner.user_id,CODE,policy='progress-v1')
        self.assertEqual(before.result,replayed)
        all_events = [e for d in deliveries for e in d.events]
        self.assertEqual(legacy, oracle.replay(all_events,str(self.owner.user_id),CODE))
        expected = completion_oracle.replay_v1_1(all_events,[d.facts[0] for d in deliveries],str(self.owner.user_id),CODE,
            authority={'context_version':'assessment-completion-v1','records':[{'fact':d.facts[0],'attempt_state':'COMPLETED','mapped_skill_ids':[CODE]} for d in deliveries]})
        self.assertEqual(replayed,expected)

    def test_neutral_downgrade_preserves_all_numbers_last_updated_and_numeric_cache(self):
        with Session(self.engine) as s, s.begin(): self.service.self_report(s,self.owner.user_id,{CODE})
        # Move fixture self-report before all assessed events using the explicit legacy importer instead.
        # Its native HTTP timestamp is current; use another fresh owner for a canonical historical stream.
        self.owner,self.token = self.user()
        old_report = canonical_event(dict(event_id='retained-self-report',user_id=str(self.owner.user_id),skill_id=CODE,
            event_kind='SELF_REPORTED_KNOWN',occurred_at='2025-12-01T00:00:00Z',policy_version='progress-v1'))
        with Session(self.engine) as s,s.begin():
            self.service.import_legacy(s,Delivery(events=[old_report]),{'context_version':'legacy-completion-v1','records':[]})
        for i in range(11): self.ingest(self.delivery(i+1,kind='CORRECT_AFTER_HINT' if i<8 else 'CORRECT_FIRST_TRY'))
        before = self.projection()
        self.assertEqual(before.status,'MASTERED')
        with patch('backend.progress._r03_v1.replay',side_effect=AssertionError('Neutral fact must not run numerical reducer')):
            for i in range(12,20): self.ingest(self.delivery(i,neutral=True))
        after = self.projection()
        self.assertEqual(after.status,'LEARNING')
        for field in ('mastery','confidence','evidence_count','last_updated','numerical','event_digest'):
            self.assertEqual(getattr(before,field),getattr(after,field),field)
        self.assertEqual(after.result['recent_window']['independent_correct_count'],2)
        with Session(self.engine) as s,s.begin(): self.assertEqual(self.service.replay(s,self.owner.user_id,CODE),after.result)

    def test_global_identity_conflicts_and_atomic_refusal(self):
        original = self.delivery(); self.ingest(original)
        original_source = self.sources[original.facts[0]['attempt_id']]
        before = self.projection()
        self.assertEqual(self.ingest(original)['duplicates'],2)
        for field in ('completion_id','source'):
            newer = self.delivery(2,owner=self.other)
            facts = newer.facts
            if field=='completion_id': facts[0]['completion_id']=original.facts[0]['completion_id']
            else:
                facts[0]['attempt_id']=original.facts[0]['attempt_id']
                newer=Delivery(events=[],facts=facts)
                source=CompletedAttempt(facts[0]['attempt_id'],self.other.user_id,str(self.vid),'FINAL_ANSWER','COMPLETED',facts[0]['completed_at'],
                    ((CODE,'CORRECT',True),),newer)
                self.sources[source.attempt_id]=source
            if field=='completion_id':
                newer=Delivery(events=newer.events,facts=facts)
                self.sources[facts[0]['attempt_id']]=replace(self.sources[facts[0]['attempt_id']],evidence=newer)
            with self.assertRaises(r03.IdentityConflict): self.ingest(newer)
        same_source = original.facts
        same_source[0]['completion_id'] = str(uuid4())
        changed = Delivery(facts=same_source)
        self.sources[same_source[0]['attempt_id']] = replace(original_source, evidence=changed)
        with self.assertRaises(r03.IdentityConflict): self.ingest(changed)
        self.assertEqual(self.projection().result,before.result)
        # A caught service failure still cannot commit partial history.
        candidate=self.delivery(4)
        with Session(self.engine) as s,s.begin():
            with patch.object(self.service,'_scope',side_effect=RuntimeError('synthetic failure')):
                with self.assertRaises(RuntimeError): self.service.ingest(s,candidate)
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(sa.func.count()).select_from(completion)),1)

    def test_two_workers_concurrent_duplicate_and_different_sources(self):
        d=self.delivery()
        barrier=Barrier(2)
        def write(delivery):
            barrier.wait(timeout=10)
            return self.ingest(delivery)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(write,d) for _ in range(2)]
            results=[f.result(timeout=20) for f in futures]
        self.assertEqual(sorted(r['duplicates'] for r in results),[0,2])
        barrier=Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(write,self.delivery(i)) for i in (3,2)]
            for f in futures:f.result(timeout=20)
        self.assertEqual(self.projection().evidence_count,3)

    def test_two_workers_conflicting_global_id_cannot_partition_by_owner(self):
        first=self.delivery()
        second=self.delivery(2,owner=self.other)
        facts=second.facts;facts[0]['completion_id']=first.facts[0]['completion_id']
        second=Delivery(events=second.events,facts=facts)
        self.sources[facts[0]['attempt_id']]=replace(self.sources[facts[0]['attempt_id']],evidence=second)
        barrier=Barrier(2)
        def write(d):
            barrier.wait(timeout=10)
            try:return self.ingest(d)
            except r03.IdentityConflict:return 'conflict'
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(write,d) for d in (first,second)]
            results=[f.result(timeout=20) for f in futures]
        self.assertEqual(results.count('conflict'),1)
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(sa.func.count()).select_from(completion)),1)
            self.assertEqual(c.scalar(sa.select(sa.func.count()).select_from(event)),1)

    def test_pending_self_check_forged_owner_and_skill_cannot_create_facts(self):
        d=self.delivery(); source=self.sources[d.facts[0]['attempt_id']]
        for altered in (replace(source,state='SUBMITTED'),replace(source,mode='SELF_CHECK'),
                        replace(source,user_id=self.other.user_id),replace(source,skills=(('linear_one_step','CORRECT',True),))):
            self.sources[source.attempt_id]=altered
            with self.assertRaises(r03.ContractError):self.ingest(d)
        attempts=AttemptService(self.identity,Signer(KEY),public_release=lambda uow: type('Release',(),{'page':lambda obj,slug:self.topics[slug]})())
        body={'exercise_id':str(self.eid),'contract_version':1,'version':1}
        created,_=attempts.mutate(self.owner,'create_attempt','/api/v1/attempts/',body,'create',str(uuid4()))
        pk=created['data']['id']
        fake=self.delivery(attempt_id=pk)
        with self.assertRaises(r03.ContractError):self.ingest(fake)
        with Session(self.engine) as s,s.begin():
            with self.assertRaises(r03.ContractError):ProgressService().ingest(s,fake)
        with self.engine.connect() as c:self.assertEqual(c.scalar(sa.select(sa.func.count()).select_from(completion)),0)

    def test_self_report_batch_rejection_is_atomic_and_postassessment_is_refused(self):
        self.ingest(self.delivery())
        with Session(self.engine) as s,s.begin():
            with self.assertRaises(r03.ContractError):
                self.service.self_report(s,self.owner.user_id,{'combine_like_terms',CODE})
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(sa.func.count()).select_from(event).where(event.c.event_kind=='SELF_REPORTED_KNOWN')),0)

    def test_self_report_http_privacy_pagination_no_get_writes_and_replay(self):
        app=create_app(self.engine,Signer(KEY),identity_service=self.identity,public_origin=ORIGIN)
        release = type('Release', (), {'index': {'catalogue': {'topics': list(self.topics.values())}}})()
        with patch('backend.infrastructure.http.app.active_release', return_value=release), TestClient(app,base_url=ORIGIN) as client:
            self.assertEqual(client.get('/api/v1/progress/skills/').status_code,401)
            client.cookies.set('sessionid',self.token)
            with self.engine.connect() as c:self.assertEqual(c.scalar(sa.select(sa.func.count()).select_from(state)),0)
            read=client.get('/api/v1/progress/skills/?page_size=1')
            self.assertEqual(read.status_code,200)
            cursor=read.json()['meta']['pagination']['next_cursor']
            self.assertTrue(cursor)
            with self.engine.connect() as c:self.assertEqual(c.scalar(sa.select(sa.func.count()).select_from(state)),0)
            self.assertEqual(client.post('/api/v1/progress/self-reports/',json={'skill_codes':[CODE]}).status_code,403)
            csrf=client.get('/api/v1/auth/csrf/').json()['data']['csrf_token']
            headers={'Origin':ORIGIN,'X-CSRFToken':csrf,'Idempotency-Key':'self-key'}
            result=client.post('/api/v1/progress/self-reports/',json={'skill_codes':[CODE]},headers=headers)
            self.assertEqual(result.status_code,200)
            self.assertEqual(result.json(),client.post('/api/v1/progress/self-reports/',json={'skill_codes':[CODE]},headers=headers).json())
            headers['Idempotency-Key']='another-key'
            self.assertEqual(client.post('/api/v1/progress/self-reports/',json={'skill_codes':[CODE]},headers=headers).json()['data']['already_reported_skill_codes'],[CODE])
            self.assertEqual(client.get('/api/v1/progress/events/').json()['data'][0]['policy_version'],'progress-v1')
            skills=client.get('/api/v1/progress/skills/').json()['data']
            self.assertEqual(next(s for s in skills if s['skill_code']==CODE)['mastery'],60)
            before_topics=client.get('/api/v1/progress/topics/')
            self.assertEqual(before_topics.status_code,200)
            headers['Idempotency-Key']='bad-skill'
            self.assertEqual(client.post('/api/v1/progress/self-reports/',json={'skill_codes':['not-a-skill']},headers=headers).status_code,400)
            # A neutral fact is visible as completion history, never a fake event.
            d=self.delivery(2,neutral=True);self.ingest(d)
            self.assertEqual(client.get('/api/v1/progress/topics/').json()['data'],before_topics.json()['data'])
            history=client.get('/api/v1/progress/completions/')
            self.assertEqual(history.status_code,200)
            self.assertEqual(history.json()['data'][0]['outcome'],'UNSUPPORTED')
            self.assertNotIn('private-synthetic-key',history.text)
            client.cookies.set('sessionid',self.other_token)
            self.assertEqual(client.get('/api/v1/progress/events/').json()['data'],[])
            self.assertEqual(client.get('/api/v1/progress/completions/').json()['data'],[])
            self.assertEqual(client.get('/api/v1/progress/skills/?page_size=1&cursor='+cursor).status_code,400)
            self.assertEqual(client.get('/api/v1/progress/skills/?user_id='+str(self.owner.user_id)).status_code,400)
        self.assertEqual(self.projection().mastery,60)

    def test_legacy_import_preserves_ids_and_native_source_without_finalized_row_is_refused(self):
        d=self.delivery()
        e=d.events[0];e['event_id']='retained-stable-event';e['attempt_id']='retained-stable-attempt'
        f=d.facts[0];f['attempt_id']=e['attempt_id']
        authority={'context_version':'legacy-completion-v1','records':[{'fact':f,'attempt_state':'LEGACY_COMPLETION','mapped_skill_ids':[CODE]}]}
        with Session(self.engine) as s,s.begin():self.service.import_legacy(s,Delivery(events=[e],facts=[f]),authority)
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(event.c.event_id)),'retained-stable-event')
            self.assertEqual(c.scalar(sa.select(completion.c.attempt_id)),'retained-stable-attempt')
        with Session(self.engine) as s,s.begin():
            legacy=self.service.replay(s,self.owner.user_id,CODE,policy='progress-v1')
        self.assertEqual(legacy,oracle.replay([e],str(self.owner.user_id),CODE))
        source=self.sources[d.facts[0]['attempt_id']]
        with Session(self.engine) as s:
            with self.assertRaises(r03.ContractError):verify_version_skills(s,source)

    def test_negative_reveal_optional_completion_time_and_delivery_orders(self):
        for kind in ('WRONG_ATTEMPT', 'MISCONCEPTION_DETECTED', 'ANSWER_REVEALED'):
            for inline in (False, True):
                for event_first in (False, True):
                    with self.subTest(kind=kind, inline=inline, event_first=event_first):
                        self.owner, self.token = self.user()
                        original = self.delivery(kind=kind)
                        e, f = original.events[0], original.facts[0]
                        f.update(outcome='WRONG', independent_correct=False)
                        if not inline: e.pop('completed_at')
                        if kind == 'MISCONCEPTION_DETECTED':
                            e.update(misconception_code='sign_error', confirmed=True, source_kind='STEP')
                        if kind == 'ANSWER_REVEALED':
                            e.pop('difficulty'); e['reveal_used'] = True
                        full = Delivery(events=[e], facts=[f])
                        source = self.sources[f['attempt_id']]
                        self.sources[f['attempt_id']] = replace(source, evidence=full, skills=((CODE,'WRONG',False),))
                        parts = [Delivery(events=[e]), Delivery(facts=[f])]
                        if not event_first: parts.reverse()
                        for part in parts: self.ingest(part)
                        before = self.projection().result
                        with Session(self.engine) as session, session.begin():
                            self.assertEqual(self.service.replay(session,self.owner.user_id,CODE),before)
                        self.assertEqual(before, completion_oracle.replay_v1_1([e],[f],str(self.owner.user_id),CODE,
                            authority={'context_version':'assessment-completion-v1','records':[
                                {'fact':f,'attempt_state':'COMPLETED','mapped_skill_ids':[CODE]}]}))

    def test_completion_time_mismatch_refuses_atomic_batch_in_both_orders(self):
        for event_first in (False, True):
            for bad_kind in ('event', 'fact'):
                with self.subTest(event_first=event_first, bad_kind=bad_kind):
                    self.owner, self.token = self.user()
                    d = self.delivery(kind='WRONG_ATTEMPT')
                    e, f = d.events[0], d.facts[0]
                    f.update(outcome='WRONG',independent_correct=False)
                    full = Delivery(events=[e],facts=[f])
                    source = replace(self.sources[f['attempt_id']],evidence=full,skills=((CODE,'WRONG',False),))
                    self.sources[source.attempt_id] = source
                    self.ingest(Delivery(events=[e]) if event_first else Delivery(facts=[f]))
                    before = self.projection().result
                    bad_e,bad_f = deepcopy(e),deepcopy(f)
                    target = bad_e if bad_kind == 'event' else bad_f
                    target['completed_at'] = '2026-01-02T00:00:00Z'
                    # Even if included in the source payload, inline time must match source terminal time.
                    bad = Delivery(events=[bad_e],facts=[bad_f])
                    self.sources[source.attempt_id] = replace(source,evidence=bad)
                    valid = self.delivery(5)
                    with self.engine.connect() as c:
                        counts = [c.scalar(sa.select(sa.func.count()).select_from(t)) for t in (event,completion,attempt_binding)]
                    with Session(self.engine) as session, session.begin():
                        with self.assertRaises(r03.ContractError):
                            self.service.ingest(session,Delivery(events=valid.events+bad.events,facts=valid.facts+bad.facts))
                    with self.engine.connect() as c:
                        self.assertEqual(counts,[c.scalar(sa.select(sa.func.count()).select_from(t)) for t in (event,completion,attempt_binding)])
                    self.assertEqual(before,self.projection().result)

    def test_legacy_extra_fact_is_not_imported_or_projected(self):
        original = self.delivery()
        extra = self.delivery(2,neutral=True).facts[0]
        facts = original.facts + [extra]
        authority = {'context_version':'legacy-completion-v1','records':[
            {'fact':f,'attempt_state':'LEGACY_COMPLETION','mapped_skill_ids':[CODE]} for f in facts]}
        confirmed, expected = completion_oracle.import_progress_v1_completions(original.events,
            str(self.owner.user_id),CODE,authority=authority)
        self.assertEqual(confirmed,original.facts)
        with Session(self.engine) as session, session.begin():
            self.service.import_legacy(session,Delivery(events=original.events,facts=facts),authority)
        with self.engine.connect() as c:
            self.assertEqual(list(c.scalars(sa.select(completion.c.payload))),confirmed)
            self.assertIsNone(c.scalar(sa.select(attempt_binding.c.attempt_id).where(attempt_binding.c.attempt_id==extra['attempt_id'])))
        self.assertEqual(self.projection().result,expected)

    def test_topic_progress_uses_active_skills_and_pinned_content_catalogue(self):
        from backend.content.topic_skill_model import topic_skill, content_page
        self.ingest(self.delivery())
        with self.engine.begin() as c:
            topic_id = c.scalar(sa.select(topic_skill.c.content_page_id).order_by(topic_skill.c.content_page_id))
            inactive = c.scalar(sa.select(topic_skill.c.skill_id).where(topic_skill.c.content_page_id==topic_id))
            c.execute(skill.update().where(skill.c.id==inactive).values(active=False))
            c.execute(topic_skill.insert().values(id=uuid4(),content_page_id=topic_id,skill_id=self.sid,
                role='PRIMARY',importance=1,position=1,mapping_version='n012-test'))
            # A mutable, published source page absent from the pinned edition must not appear.
            c.execute(content_page.insert().values(id=9999,slug='source-only',title='Source only',page_type='topic',is_published=True))
            c.execute(topic_skill.insert().values(id=uuid4(),content_page_id=9999,skill_id=self.sid,
                role='PRIMARY',importance=1,position=0,mapping_version='n012-test'))
        release = type('Release',(),{'index':{'catalogue':{'topics':[{'id':topic_id,'slug':'pinned-topic'}]}}})()
        app=create_app(self.engine,Signer(KEY),identity_service=self.identity,public_origin=ORIGIN)
        with patch('backend.infrastructure.http.app.active_release',return_value=release), TestClient(app,base_url=ORIGIN) as client:
            client.cookies.set('sessionid',self.token)
            result=client.get('/api/v1/progress/topics/')
            self.assertEqual(result.status_code,200)
            self.assertEqual(result.json()['data'],[{'topic':{'id':topic_id,'slug':'pinned-topic'},
                'mastery':float(self.projection().mastery),'confidence':float(self.projection().confidence),
                'assessed_skill_count':1,'total_skill_count':1}])
            with self.engine.begin() as c:c.execute(skill.update().where(skill.c.id==self.sid).values(active=False))
            self.assertEqual(client.get('/api/v1/progress/topics/').json()['data'],[])

    def test_fresh_upgrade_acl_and_immutable_history(self):
        with self.engine.connect() as c:assert_baseline(c,'FRESH',allow_protocol=True,require_history=False)
        with self.database() as old:
            with old.begin() as c:command.upgrade(configuration(c),'v01_0007')
            seed(old)
            with old.connect() as c:
                retained=inventory(c)['sequences']
                retained_skills=c.execute(sa.select(skill).order_by(skill.c.id)).all()
            plan=release_migrate.preview(old,KEY,'TARGET_0007')
            release_migrate.apply(old,KEY,plan,release_migrate.plan_digest(plan),maintenance=True)
            with old.connect() as c:
                assert_baseline(c,'FRESH',allow_protocol=True,require_history=False)
                self.assertEqual(inventory(c)['sequences'],retained)
                self.assertEqual(c.execute(sa.select(skill).order_by(skill.c.id)).all(),retained_skills)
        self.ingest(self.delivery())
        for table in PROGRESS_TABLES:
            with self.assertRaises(sa.exc.IntegrityError),self.engine.begin() as c:c.exec_driver_sql('TRUNCATE '+table.name+' CASCADE')
        with self.assertRaises(sa.exc.IntegrityError),self.engine.begin() as c:c.execute(event.delete())
        with self.engine.begin() as c:
            c.exec_driver_sql('DO $$ BEGIN CREATE ROLE local_runtime; EXCEPTION WHEN duplicate_object THEN NULL; END $$')
            grant_runtime_privileges(c.connection.driver_connection)
        runtime=sa.create_engine(self.engine.url,hide_parameters=True);self.addCleanup(runtime.dispose)
        @sa.event.listens_for(runtime,'connect')
        def role(conn,record):
            with conn.cursor() as cursor:cursor.execute('SET ROLE local_runtime')
            conn.commit()
        with Session(runtime) as s,s.begin():self.service.self_report(s,self.other.user_id,{CODE})
        with self.assertRaises(sa.exc.ProgrammingError),runtime.begin() as c:c.execute(completion.delete())
