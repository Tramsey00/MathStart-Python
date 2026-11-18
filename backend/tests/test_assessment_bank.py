"""MS-N008 checks run only against an explicitly marked disposable PostgreSQL server."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import os
import unittest
from unittest.mock import patch
from uuid import uuid4

from alembic import command
import sqlalchemy as sa
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from backend import release_migrate
from backend.assessment.bank import apply_bank, archive
from backend.assessment.models import exercise, exercise_skill, validation, version
from backend.assessment.package import BankError, TOPICS, read_package, validate_rows
from backend.assessment.reads import public_dto
from backend.assessment.templates import TEMPLATES
from backend.content.import_pilot_knowledge import import_pilot, read_fixture
from backend.content.topic_skill_model import content_page, topic_skill
from backend.infrastructure.http.app import create_app
from backend.infrastructure.http.contracts import validator
from backend.infrastructure.http.signing import Signer
from backend.infrastructure.http.transport import APIError, missing
from backend.knowledge.models import skill, skill_dependency
from backend.migrations.runtime_privileges import grant_runtime_privileges
from backend.migrations.schema import HEAD, assert_baseline, inventory
from backend.migrations.upgrade import configuration
from backend.models.baseline import User, metadata, utc_now
from backend.users.security import Security

KEY = 'synthetic-n008-test-signing-material'
ORIGIN = 'https://mathstart.example'
ADMIN_URL = os.getenv('MATHSTART_N008_TEST_ADMIN_URL')
PACKAGE = os.getenv('MATHSTART_N008_TEST_PACKAGE')
MARKER = 'MS-N008 disposable PostgreSQL server'
SENTINEL = 'N008-private-nested-probe-7a19'


def stored(conn, table):
    return conn.execute(sa.select(table).order_by(*table.primary_key.columns)).all()


def seed(engine):
    with engine.begin() as conn:
        conn.execute(metadata.tables['content_grade'].insert().values(id=801, slug='6-klass', title='6'))
        conn.execute(metadata.tables['content_subject'].insert().values(
            id=802, grade_id=801, slug='matematika', title='Математика'))
        sections = {slug: 810 + i for i, slug in enumerate(sorted(set(TOPICS.values())))}
        conn.execute(metadata.tables['content_section'].insert(), [
            dict(id=pk, subject_id=802, slug=slug, title=slug) for slug, pk in sections.items()
        ])
        topics = {}
        for i, (slug, section) in enumerate(TOPICS.items(), 1):
            conn.execute(content_page.insert().values(id=i, slug=slug, title=slug, page_type='topic',
                is_published=True, grade_id=801, subject_id=802, section_id=sections[section]))
            topics[slug] = {'id': i, 'slug': slug, 'page_type': 'topic'}
    import_pilot(engine, *(read_fixture(name) for name in (
        'pilot-skills-v1.json', 'pilot-dependencies-v1.json', 'pilot-topic-skills-v1.json',
    )))
    return topics


class PublicContractTests(unittest.TestCase):
    def test_all_templates_match_contract_and_reject_unknown_or_nested_private_values(self):
        exercise_id = uuid4()
        for code, template in TEMPLATES.items():
            row = SimpleNamespace(id=exercise_id, version_id=uuid4(), code='sample', topic_id=1, slug='topic',
                statement='Synthetic prompt', mode=template.mode, schema_code=code,
                public_schema=template.public_contract(), difficulty=2, version=1)
            self.assertTrue(validator('PublicExerciseDTO').is_valid(public_dto(row, ['skill'])), code)
            if row.public_schema['input_schema']:
                row.public_schema['input_schema']['fields'][0]['metadata'] = {'accepted_variants': [SENTINEL]}
            else:
                row.public_schema['reveal_policy']['secret'] = [SENTINEL]
            with self.assertRaises(APIError) as refused:
                public_dto(row, ['skill'])
            self.assertEqual(refused.exception.status, 503)
        row.schema_code = 'unknown'
        with self.assertRaises(APIError):
            public_dto(row, ['skill'])


@unittest.skipUnless(ADMIN_URL and PACKAGE, 'Set both isolated MS-N008 test inputs')
class PostgreSQLBankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = make_url(ADMIN_URL)
        if (url.drivername, url.host, url.database) != ('postgresql+psycopg', '127.0.0.1', 'postgres') or not url.port:
            raise RuntimeError('Requires a marked, isolated loopback PostgreSQL server')
        cls.admin = sa.create_engine(url, isolation_level='AUTOCOMMIT', hide_parameters=True)
        cls.addClassCleanup(cls.admin.dispose)
        with cls.admin.connect() as conn:
            marker = conn.scalar(sa.text("SELECT shobj_description(oid, 'pg_database') FROM pg_database "
                                         "WHERE datname=current_database()"))
            if marker != MARKER:
                raise RuntimeError('Missing MS-N008 disposable server marker')
        cls.url = url

    def setUp(self):
        name = 'test_n008_' + uuid4().hex
        with self.admin.connect() as conn:
            conn.execute(sa.text('CREATE DATABASE ' + name))
        self.addCleanup(self.drop_database, name)
        self.engine = sa.create_engine(self.url.set(database=name), hide_parameters=True)
        self.addCleanup(self.engine.dispose)
        self.rows, self.coverage, _ = read_package(Path(PACKAGE))

    def drop_database(self, name):
        with self.admin.connect() as conn:
            conn.execute(sa.text('DROP DATABASE ' + name + ' WITH (FORCE)'))

    def migrate(self, profile):
        plan = release_migrate.preview(self.engine, KEY, profile)
        receipt = release_migrate.apply(self.engine, KEY, plan, release_migrate.plan_digest(plan), maintenance=True)
        self.assertEqual(receipt['head'], HEAD)

    def test_n007_upgrade_keeps_topics_skills_mappings_and_prior_history(self):
        with self.engine.begin() as conn:
            command.upgrade(configuration(conn), 'v01_0004')
        seed(self.engine)
        retained = (content_page, skill, skill_dependency, topic_skill, metadata.tables['django_migrations'])
        with self.engine.begin() as conn:
            conn.execute(retained[-1].insert().values(app='content', name='synthetic_retained', applied=utc_now()))
            before = [stored(conn, table) for table in retained]
            sequences = inventory(conn)['sequences']
        self.migrate('TARGET_0004')
        with self.engine.connect() as conn:
            self.assertEqual(before, [stored(conn, table) for table in retained])
            self.assertEqual(sequences, inventory(conn)['sequences'])
            self.assertEqual([], stored(conn, exercise))

    def test_fresh_import_rollback_seal_archive_and_replace(self):
        self.migrate('FRESH')
        seed(self.engine)
        with self.engine.begin() as conn:
            # Role is isolated to this disposable server, shared by this class's databases.
            conn.execute(sa.text("DO $$ BEGIN CREATE ROLE local_runtime; "
                                 "EXCEPTION WHEN duplicate_object THEN NULL; END $$"))
            grant_runtime_privileges(conn.connection.driver_connection)
            self.assertFalse(conn.scalar(sa.text("SELECT has_table_privilege('local_runtime', "
                                                 "'assessment_exercise_validation', 'SELECT')")))
            self.assertTrue(conn.scalar(sa.text("SELECT has_table_privilege('local_runtime', "
                                                "'assessment_exercise_version', 'SELECT')")))
        self.assertEqual(self.coverage['assessed'], 40)
        self.assertEqual(apply_bank(self.engine, self.rows, 'import'), 43)
        self.assertEqual(apply_bank(self.engine, self.rows, 'import'), 0)
        invalid = deepcopy(self.rows)
        invalid[0]['version'] = 2
        invalid[-1]['statement'] += ' conflict'
        with self.assertRaises(BankError):
            apply_bank(self.engine, invalid, 'import')
        with self.engine.connect() as conn:
            self.assertEqual(len(stored(conn, version)), 43)
            self.assertTrue(all(row.status == 'DRAFT' for row in stored(conn, version)))
        with self.assertRaises(BankError):
            validate_rows(self.rows[:-1])
        self.assertEqual(apply_bank(self.engine, self.rows, 'publish'), 43)
        self.assertEqual(apply_bank(self.engine, self.rows, 'publish'), 0)
        with self.engine.connect() as conn:
            original = conn.execute(sa.select(version).join(exercise).where(
                exercise.c.code == self.rows[0]['code'])).mappings().one()
        old_id = original['id']
        forbidden = [
            version.update().where(version.c.id == old_id).values(statement='changed'),
            validation.update().where(validation.c.version_id == old_id).values(answer_key=SENTINEL),
            exercise_skill.delete().where(exercise_skill.c.version_id == old_id),
            version.delete().where(version.c.id == old_id),
        ]
        for operation in forbidden:
            with self.assertRaises(sa.exc.IntegrityError), self.engine.begin() as conn:
                conn.execute(operation)
        self.assertEqual(archive(self.engine, self.rows[0]['code'], 1), 1)
        self.assertEqual(archive(self.engine, self.rows[0]['code'], 1), 0)
        with self.assertRaises(BankError):
            apply_bank(self.engine, self.rows, 'publish')
        second_bank = deepcopy(self.rows)
        second_bank[0].update(version=2, statement=self.rows[0]['statement'] + ' Укажите целое число.')
        self.assertEqual(apply_bank(self.engine, second_bank, 'import'), 1)
        self.assertEqual(apply_bank(self.engine, second_bank, 'publish'), 1)
        with self.engine.connect() as conn:
            old = conn.execute(sa.select(version).where(version.c.id == old_id)).mappings().one()
            self.assertEqual(old, {**original, 'status': 'ARCHIVED'})
            self.assertIsNotNone(conn.scalar(sa.select(validation.c.version_id).where(validation.c.version_id == old_id)))
            self.assertIsNotNone(conn.scalar(sa.select(exercise_skill.c.version_id).where(exercise_skill.c.version_id == old_id)))
            assert_baseline(conn, 'FRESH', allow_protocol=True, require_history=False)

    def test_http_access_order_and_private_nested_values(self):
        self.migrate('FRESH')
        topics = seed(self.engine)
        package = deepcopy(self.rows)
        structured = next(row for row in package if isinstance(row['answer'], dict))
        structured['variants'] = [{**structured['answer'], next(iter(structured['answer'])): SENTINEL}]
        apply_bank(self.engine, package, 'import')
        apply_bank(self.engine, package, 'publish')
        security = Security(self.engine, KEY, ORIGIN)
        with Session(self.engine) as session, session.begin():
            user = User(username='n008-synthetic')
            session.add(user)
            session.flush()
            _, session_token, _ = security.issue(session, user, utc_now())

        def public_topic(slug):
            if slug not in topics:
                raise missing()
            return topics[slug]

        app = create_app(self.engine, Signer(KEY), authenticate=security.identity, public_origin=ORIGIN)
        with patch('backend.infrastructure.http.app.active_release',
                   return_value=SimpleNamespace(page=public_topic)), TestClient(app, base_url=ORIGIN) as client:
            api = '/api/v1'
            path = f"{api}/topics/{structured['topic']}/exercises/"
            guest = client.get(path)
            self.assertEqual(guest.status_code, 200)
            self.assertEqual([row['interaction_mode'] for row in guest.json()['data']], ['SELF_CHECK'])
            self_check_id = guest.json()['data'][0]['id']
            self.assertEqual(client.get(f'{api}/exercises/{self_check_id}/').status_code, 200)
            self.assertEqual(client.get(f'{api}/exercises/{uuid4()}/').status_code, 401)
            client.cookies.set('sessionid', session_token)
            enrolled = client.get(path, params={'page_size': 1})
            self.assertEqual(enrolled.status_code, 200)
            token = enrolled.json()['meta']['pagination']['next_cursor']
            self.assertTrue(token)
            full = client.get(path)
            self.assertEqual(full.status_code, 200)
            records = full.json()['data']
            self.assertEqual(len(records), self.coverage['topics'][structured['topic']])
            result = next(row for row in records if row['code'] == structured['code'])
            for response in (full, client.get(f"{api}/exercises/{result['id']}/")):
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.headers['cache-control'], 'private, no-store')
                for marker in (SENTINEL, 'answer_key', 'accepted_variants', 'canonical_solution', 'validation_spec'):
                    self.assertNotIn(marker, response.text)
            client.cookies.clear()
            self.assertEqual(client.get(path, params={'page_size': 1, 'cursor': token}).status_code, 400)
            self.assertEqual(client.get(f"{api}/exercises/{result['id']}/").status_code, 401)
            archive(self.engine, structured['code'], structured['version'])
            client.cookies.set('sessionid', session_token)
            self.assertEqual(client.get(f"{api}/exercises/{result['id']}/").status_code, 404)
