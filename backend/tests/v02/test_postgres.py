"""PG16 acceptance: new UUID databases at the dedicated V02 container only."""
import os
import unittest
import uuid
import json
import subprocess
import sys

import sqlalchemy as sa
from sqlalchemy.engine import make_url

from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.tests.v02.test_http import HTTPAssertions
from backend.staff.reads import POLICY, effective_order
from backend.tests.legacy_tools import legacy_python
from backend.tests.v02.oracle_environment import comparator_environment

ADMIN = os.environ.get('MATHSTART_V02_TEST_ADMIN_URL')


@unittest.skipUnless(ADMIN, 'NOT RUN: dedicated disposable PostgreSQL URL is required')
class PostgreSQLHTTPTests(HTTPAssertions, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = make_url(ADMIN)
        if (url.drivername, url.host, url.database) != ('postgresql+psycopg', '127.0.0.1', 'postgres') or url.port not in {15441, 55441}:
            raise RuntimeError('Refusing unreserved/shared database endpoint')
        cls.admin = sa.create_engine(url, isolation_level='AUTOCOMMIT', hide_parameters=True, connect_args={'connect_timeout': 5})
        with cls.admin.connect() as c:
            cls.version = c.scalar(sa.text('SHOW server_version'))
            if int(cls.version.split('.')[0]) != 16:
                raise RuntimeError('PostgreSQL 16 required for this acceptance')

    @classmethod
    def tearDownClass(cls):
        cls.admin.dispose()

    def setUp(self):
        # V01 fresh() deliberately requires its rehearsal prefix and marker.
        # The V02 run owns this new UUID DB; it does not weaken that existing guard.
        self.name = 'test_ms7_mig_v01_v02_' + uuid.uuid4().hex
        self.quoted = self.admin.dialect.identifier_preparer.quote(self.name)
        with self.admin.connect() as c:
            c.execute(sa.text('CREATE DATABASE ' + self.quoted))
            c.execute(sa.text("COMMENT ON DATABASE " + self.quoted + " IS 'MS7-MIG-V01 disposable synthetic test database'"))
        self.engine = create_engine(DatabaseConfig(make_url(ADMIN).set(database=self.name)))
        self.prepare()

    def tearDown(self):
        self.finish()
        self.engine.dispose()
        # Only this method's newly created marked UUID database, never existing data.
        with self.admin.connect() as c:
            c.execute(sa.text('DROP DATABASE ' + self.quoted + ' WITH (FORCE)'))

    def test_all_staff_sort_columns_search_and_keysets_match_django_admin(self):
        cases = []
        for resource, policy in POLICY.items():
            cases.append({'resource': resource, 'sort': 'default'})
            for field in policy['allowed_fields']:
                for sign in ['', '-']:
                    cases.append({'resource': resource, 'sort': sign + field})
            if len(policy['allowed_fields']) >= 2:
                cases.append({'resource': resource, 'sort': '-' + policy['allowed_fields'][0] + ',' + policy['allowed_fields'][1]})
            cases.append({'resource': resource, 'q': '"Private draft"'})
            cases.append({'resource': resource, 'q': 'Straße'})
        environment = comparator_environment(self.engine.url, self.name, self.files.name)
        result = subprocess.run([legacy_python(), '-m', 'backend.tests.v02.legacy_comparator'],
            input=json.dumps(cases).encode(), capture_output=True, env=environment, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace')[-1600:])
        self.actor = 902
        for oracle in json.loads(result.stdout):
            case = oracle['case']
            with self.subTest(case=case):
                self.assertEqual(effective_order(case['resource'], case.get('sort')), oracle['ordering'])
                params = {k: v for k, v in case.items() if k != 'resource'}
                params['page_size'] = 1
                ids = []
                while True:
                    response = self.client.get(f'/api/v1/staff/{case["resource"]}/', params=params)
                    self.assertEqual(response.status_code, 200, response.text)
                    body = response.json()
                    ids += [r['id'] for r in body['data']]
                    cursor = body['meta']['pagination']['next_cursor']
                    if cursor is None:
                        break
                    params['cursor'] = cursor
                self.assertEqual(ids, oracle['ids'])

    def test_content_projections_seo_catalogue_match_django_and_do_not_activate(self):
        from backend.content.projection import ReviewedSource, delivery_candidate, build_index_candidate
        from backend.infrastructure.uow import UnitOfWork
        from backend.models.baseline import ContentPage
        from backend.models.protocol import active
        environment = comparator_environment(self.engine.url, self.name, self.files.name)
        result = subprocess.run([legacy_python(), '-m', 'backend.tests.v02.legacy_comparator'],
            input=b'[{"resource":"__content"}]', capture_output=True, env=environment, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace')[-1000:])
        oracle = json.loads(result.stdout)[0]
        with UnitOfWork(self.engine) as uow:
            before = dict(uow.session.execute(sa.select(active)).mappings().one())
            pages = list(uow.session.scalars(sa.select(ContentPage).where(ContentPage.is_published.is_(True))))
            deliveries = {p.id: delivery_candidate(uow, p.slug,
                ReviewedSource(f'site_content/pages/{p.slug}/page.json', '1' * 64, ())) for p in pages}
            index = build_index_candidate(uow, 'candidate-never-activated', deliveries)
            self.assertEqual([t['id'] for t in index['catalogue']['topics']], oracle['ids'])
            self.assertEqual({str(pk): d['seo'] for pk, d in deliveries.items()}, oracle['seo'])
            self.assertEqual(before, dict(uow.session.execute(sa.select(active)).mappings().one()))
            self.assertNotIn(303, [p['id'] for p in index['pages']])
            self.assertNotIn('PRIVATE-DRAFT-SENTINEL', json.dumps(index))
