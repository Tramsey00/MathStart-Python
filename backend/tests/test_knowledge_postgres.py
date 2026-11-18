"""MS-N007 acceptance on explicitly reserved disposable PostgreSQL only."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import os
import subprocess
import sys
from threading import Barrier
import unittest
from uuid import uuid4

from alembic import command
import sqlalchemy as sa

from backend import release_migrate
from backend.content.import_pilot_knowledge import import_pilot, read_fixture
from backend.content.topic_skill_model import content_page, topic_skill
from backend.content.topic_skills import TopicSkillError, read_topic_skills
from backend.knowledge.graph import GraphError, validate_dag
from backend.knowledge.models import skill, skill_dependency
from backend.knowledge.repository import read_pilot_graph
from backend.migrations.runtime_privileges import grant_runtime_privileges
from backend.migrations.schema import HEAD, assert_baseline, inventory
from backend.migrations.upgrade import configuration, fresh
from backend.models.baseline import metadata, utc_now
from backend.tests import test_postgres as disposable


SYNTHETIC_KEY = 'synthetic-schema-key-for-n007-tests-only'
TOPICS = {'uproshhenie-vyrazhenij-raskrytie-skobok': 19004, 'reshenie-linejnyh-uravnenij': 27019}


def package():
    return tuple(read_fixture(name) for name in (
        'pilot-skills-v1.json', 'pilot-dependencies-v1.json', 'pilot-topic-skills-v1.json',
    ))


def rows(connection, table):
    return connection.execute(sa.select(table).order_by(*table.primary_key.columns)).all()


def seed_topics(engine):
    with engine.begin() as connection:
        connection.execute(metadata.tables['content_grade'].insert(), dict(id=6601, slug='6-klass', title='6'))
        connection.execute(metadata.tables['content_subject'].insert(),
                           dict(id=6602, grade_id=6601, slug='matematika', title='Math'))
        connection.execute(metadata.tables['content_section'].insert(), dict(
            id=6603, subject_id=6602, slug='preobrazovanie-bukvennyh-vyrazhenij', title='Algebra',
        ))
        for slug, page_id in {**TOPICS, 'unmapped-probe': 38808}.items():
            connection.execute(content_page.insert(), dict(id=page_id, slug=slug, title=slug, page_type='topic',
                                                           is_published=True, grade_id=6601, subject_id=6602,
                                                           section_id=6603))


class KnowledgePostgreSQLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        disposable.PostgreSQLTests.setUpClass()
        cls.fixture = disposable.PostgreSQLTests()

    @classmethod
    def tearDownClass(cls):
        disposable.PostgreSQLTests.tearDownClass()

    @staticmethod
    def import_cli(engine):
        environment = {**os.environ, 'MATHSTART_DB_BACKEND': 'postgresql',
                       'MATHSTART_DATABASE_URL': engine.url.render_as_string(hide_password=False)}
        return subprocess.run([sys.executable, '-m', 'backend.content.import_pilot_knowledge', '--apply'],
                              env=environment, capture_output=True, timeout=30)

    def test_fresh_repeat_exact_persisted_graph_and_read_dtos(self):
        with self.fixture.database() as engine:
            plan = release_migrate.preview(engine, SYNTHETIC_KEY, 'FRESH')
            self.assertEqual(release_migrate.apply(engine, SYNTHETIC_KEY, plan,
                             release_migrate.plan_digest(plan), maintenance=True)['head'], HEAD)
            with engine.connect() as connection:
                self.assertIsNone(read_pilot_graph(connection))
            seed_topics(engine)
            first = self.import_cli(engine)
            self.assertEqual(first.returncode, 0, first.stderr.decode())
            self.assertEqual(json.loads(first.stdout), {
                'status': 'IMPORTED', 'graph_version': 'pilot-v1', 'skills': 10, 'dependencies': 13,
                'topic_mappings': 2, 'mappings_added': 2, 'content_page_ids': TOPICS,
            })
            with engine.connect() as connection:
                snapshot = [rows(connection, table) for table in (skill, skill_dependency, topic_skill, content_page)]
                graph = read_pilot_graph(connection)
                raw_skills, raw_edges, _ = package()
                self.assertEqual({(node.code, node.name) for node in graph.skills},
                                 {(node['code'], node['name']) for node in raw_skills['skills']})
                self.assertEqual({(edge.prerequisite, edge.dependent, edge.weight) for edge in graph.dependencies},
                                 {(edge['prerequisite'], edge['dependent'], edge['weight']) for edge in raw_edges['edges']})
                self.assertEqual(graph.external_prerequisite.code, 'basic_arithmetic')
                self.assertEqual(graph.ancestors('linear_parentheses'), (
                    ('combine_like_terms', 1), ('expand_parentheses', 1), ('linear_one_step', 1),
                    ('distributive_property', 2), ('equation_balance', 2), ('sign_rules_add_sub', 2),
                ))
                self.assertEqual(graph.ancestors('linear_parentheses', 0), ())
                with self.assertRaises(GraphError):
                    graph.ancestors('linear_parentheses', True)
                with self.assertRaises(GraphError):
                    graph.ancestors('basic_arithmetic')
                for slug, code in (('uproshhenie-vyrazhenij-raskrytie-skobok', 'expand_parentheses'),
                                   ('reshenie-linejnyh-uravnenij', 'linear_one_step')):
                    link, = read_topic_skills(connection, TOPICS[slug])
                    self.assertEqual((link.skill_code, link.role, link.importance, link.position, link.mapping_version),
                                     (code, 'PRIMARY', 1, 0, 'pilot-v1'))
                self.assertEqual(read_topic_skills(connection, 38808), ())
                self.assertIsNone(read_topic_skills(connection, 99999))
            second = self.import_cli(engine)
            self.assertEqual(second.returncode, 0, second.stderr.decode())
            self.assertEqual(json.loads(second.stdout)['status'], 'UNCHANGED')
            with engine.connect() as connection:
                self.assertEqual(snapshot, [rows(connection, table) for table in
                                           (skill, skill_dependency, topic_skill, content_page)])

    def test_reviewed_upgrade_preserves_all_prior_rows_and_sequence_state(self):
        with self.fixture.database() as engine:
            with engine.begin() as connection:
                command.upgrade(configuration(connection), 'v01_0003')
                source = assert_baseline(connection, 'B', allow_protocol=True, require_history=False,
                                         target_head='v01_0003')
            self.fixture.seed(engine, 'C')
            seed_topics(engine)
            with engine.begin() as connection:
                migrations = metadata.tables['django_migrations']
                connection.execute(migrations.insert().values(app='content', name='retained_history', applied=utc_now()))
                recovery = metadata.tables['identity_recovery_address']
                connection.execute(recovery.insert().values(user_id=901, email='synthetic@example.invalid'))
                tables = [metadata.tables[name] for name in source['tables'] if name != 'alembic_version']
                before = [rows(connection, table) for table in tables]
                before_sequences = inventory(connection)['sequences']
            plan = release_migrate.preview(engine, SYNTHETIC_KEY, 'TARGET_0003')
            self.assertEqual(release_migrate.apply(engine, SYNTHETIC_KEY, plan,
                             release_migrate.plan_digest(plan), maintenance=True)['head'], HEAD)
            with engine.connect() as connection:
                self.assertIsNone(read_pilot_graph(connection))
            self.assertEqual(import_pilot(engine, *package())['content_page_ids'], TOPICS)
            with engine.connect() as connection:
                self.assertEqual(before, [rows(connection, table) for table in tables])
                self.assertEqual(before_sequences, inventory(connection)['sequences'])

    def test_two_concurrent_imports_publish_once(self):
        with self.fixture.database() as engine:
            with engine.begin() as connection:
                fresh(connection)
            seed_topics(engine)
            ready = Barrier(2, timeout=10)

            def publish():
                ready.wait()
                return import_pilot(engine, *package())

            with ThreadPoolExecutor(max_workers=2) as workers:
                jobs = [workers.submit(publish) for _ in range(2)]
                self.assertCountEqual([job.result(timeout=15)['status'] for job in jobs], ['IMPORTED', 'UNCHANGED'])
            with engine.connect() as connection:
                self.assertEqual([len(rows(connection, table)) for table in (skill, skill_dependency, topic_skill)],
                                 [10, 13, 2])

    def test_refusals_and_late_mapping_conflict_leave_no_partial_import(self):
        with self.fixture.database() as engine:
            with engine.begin() as connection:
                fresh(connection)
            seed_topics(engine)
            skills, edges, mappings = package()
            for patch in (
                {'prerequisite': 'unknown'}, {'prerequisite': 'negative_numbers'}, {'weight': True},
                {'prerequisite': 'negative_numbers', 'dependent': 'integer_number_line'},
                edges['edges'][1],
            ):
                corrupt = deepcopy(edges)
                corrupt['edges'][0].update(patch)
                with self.subTest(patch=patch), self.assertRaises(GraphError):
                    import_pilot(engine, skills, corrupt, mappings)
            with self.assertRaisesRegex(GraphError, 'Cyclic'):
                validate_dag(('a', 'b'), (('a', 'b'), ('b', 'a')))
            duplicate = deepcopy(skills)
            duplicate['skills'].append(duplicate['skills'][0])
            with self.assertRaisesRegex(GraphError, 'Duplicate skill'):
                import_pilot(engine, duplicate, edges, mappings)
            wrong_mapping = deepcopy(mappings)
            wrong_mapping['mappings'][0]['skill_code'] = 'linear_parentheses'
            with self.assertRaisesRegex(TopicSkillError, 'approved mapping'):
                import_pilot(engine, skills, edges, wrong_mapping)
            page_id = next(iter(TOPICS.values()))
            for patch in (dict(is_published=False), dict(page_type='static'), dict(slug='wrong-slug'),
                          dict(section_id=None)):
                with engine.begin() as connection:
                    connection.execute(content_page.update().where(content_page.c.id == page_id).values(**patch))
                with self.subTest(patch=patch), self.assertRaises(TopicSkillError):
                    import_pilot(engine, skills, edges, mappings)
                with engine.begin() as connection:
                    connection.execute(content_page.update().where(content_page.c.id == page_id).values(
                        is_published=True, page_type='topic', slug=next(iter(TOPICS)), section_id=6603,
                    ))
            with engine.begin() as connection:
                other = uuid4()
                connection.execute(skill.insert().values(id=other, code='synthetic', name='Other', active=True,
                                                         graph_version='unrelated'))
                connection.execute(topic_skill.insert().values(id=uuid4(), content_page_id=page_id, skill_id=other,
                                   role='SECONDARY', importance=1, position=1, mapping_version='pilot-v1'))
                before = rows(connection, topic_skill)
            with self.assertRaisesRegex(TopicSkillError, 'Installed pilot mappings'):
                import_pilot(engine, skills, edges, mappings)
            with engine.connect() as connection:
                self.assertIsNone(read_pilot_graph(connection))
                self.assertEqual(rows(connection, skill_dependency), [])
                self.assertEqual(rows(connection, topic_skill), before)

    def test_database_constraints_and_archived_reads(self):
        with self.fixture.database() as engine:
            with engine.begin() as connection:
                fresh(connection)
            seed_topics(engine)
            import_pilot(engine, *package())
            with engine.begin() as connection:
                node = dict(connection.execute(sa.select(skill).where(skill.c.code == 'expand_parentheses')).mappings().one())
                link = dict(connection.execute(sa.select(topic_skill).where(topic_skill.c.skill_id == node['id'])).mappings().one())
                edge = dict(connection.execute(sa.select(skill_dependency).limit(1)).mappings().one())
                for statement in (
                    skill.insert().values({**node, 'id': uuid4()}),
                    topic_skill.insert().values({**link, 'id': uuid4()}),
                    topic_skill.update().where(topic_skill.c.id == link['id']).values(content_page_id=9876543),
                    topic_skill.update().where(topic_skill.c.id == link['id']).values(importance=-1),
                    topic_skill.update().where(topic_skill.c.id == link['id']).values(role='BAD'),
                    skill_dependency.insert().values({**edge, 'id': uuid4()}),
                    skill_dependency.insert().values({**edge, 'id': uuid4(), 'dependent_id': edge['prerequisite_id']}),
                    skill_dependency.insert().values({**edge, 'id': uuid4(), 'dependent_id': uuid4()}),
                    skill_dependency.update().where(skill_dependency.c.id == edge['id']).values(weight=2),
                    skill.delete().where(skill.c.id == node['id']),
                    content_page.delete().where(content_page.c.id == link['content_page_id']),
                ):
                    with self.subTest(statement=statement), self.assertRaises(sa.exc.IntegrityError), connection.begin_nested():
                        connection.execute(statement)

                connection.execute(skill.update().where(skill.c.id == node['id']).values(active=False))
                self.assertEqual(read_topic_skills(connection, link['content_page_id']), ())
                connection.execute(content_page.update().where(content_page.c.id == link['content_page_id'])
                                   .values(is_published=False))
                self.assertIsNone(read_topic_skills(connection, link['content_page_id']))
                self.assertEqual(len(rows(connection, topic_skill)), 2)

    def test_runtime_can_read_graph_and_topic_skills_with_select_only(self):
        with self.fixture.database() as engine:
            with engine.begin() as connection:
                fresh(connection)
            seed_topics(engine)
            import_pilot(engine, *package())
            with engine.connect() as connection, connection.begin() as transaction:
                connection.exec_driver_sql('CREATE ROLE local_runtime NOLOGIN')
                grant_runtime_privileges(connection.connection.driver_connection)
                connection.exec_driver_sql('SET LOCAL ROLE local_runtime')
                self.assertEqual(len(read_pilot_graph(connection).skills), 10)
                self.assertEqual(len(read_topic_skills(connection, next(iter(TOPICS.values())))), 1)
                for table in (skill, skill_dependency, topic_skill):
                    with self.assertRaises(sa.exc.ProgrammingError) as denied, connection.begin_nested():
                        connection.execute(table.delete())
                    self.assertEqual(denied.exception.orig.sqlstate, '42501')
                transaction.rollback()
