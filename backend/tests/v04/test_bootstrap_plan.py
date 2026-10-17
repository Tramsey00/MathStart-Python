"""General bootstrap on owned DBs: real P1/React/HTTP and retained private facts."""
from contextlib import redirect_stdout
from collections import deque
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import time
import unittest
import uuid
from unittest.mock import patch

import httpx
import sqlalchemy as sa
import uvicorn

from backend.content.editions import snapshot, apply_updates
from backend.content.participant import PreparedPublication
from backend.content.preparation import prepare_sources
from backend.content.publication import PublisherAuthority, PublicationConflict
from backend.content.public_runtime import create_public_app
from backend.content.publish import finish
from backend.infrastructure.http.signing import Signer
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.upgrade import fresh, require_disposable, advance_sequences
from backend.models.baseline import User, Group, StudentProfile, IdentityReceipt, LoginWindow, metadata
from backend.users.bootstrap import seed_permissions
from backend.users.security import Security
from backend.users.service import IdentityService
from backend.verification_suite import owned_database
from frontend.build_public import build_public

ROOT = Path(__file__).resolve().parents[3]
COUNTS = {'content_grade': 6, 'content_subject': 12, 'content_section': 63,
          'content_contentpage': 279, 'content_lessonpublication': 263,
          'content_mediaasset': 29, 'content_redirect': 282}
PRIVATE = tuple(name for name in metadata.tables if name.startswith(('auth_', 'users_')) or name in
                {'django_admin_log', 'django_content_type', 'django_session', 'django_migrations',
                 'target_session', 'target_receipt_bridge', 'target_identity_cutover'})


class BootstrapPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = sa.create_engine(os.environ['MATHSTART_V04_DATABASE_URL'], hide_parameters=True)
        with cls.parent.connect() as c:
            require_disposable(c)
        cls.admin = sa.create_engine(cls.parent.url.set(database='postgres'), isolation_level='AUTOCOMMIT', hide_parameters=True)
        cls.sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()

    @classmethod
    def tearDownClass(cls):
        cls.admin.dispose(); cls.parent.dispose()

    def setUp(self):
        self.owned = owned_database(self.admin, self.parent.url, 'bootstrap')
        self.engine = self.owned.__enter__()
        self.addCleanup(self.owned.__exit__, None, None, None)
        self.temp = tempfile.TemporaryDirectory(prefix='bootstrap-plan-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.key = 'synthetic-bootstrap-publisher-key'
        with self.engine.begin() as c:
            fresh(c)
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            seed_permissions(s)
            user = User(username='preservedBootstrapUser', password='!retained-unusable', is_active=True)
            group = Group(name='Retained bootstrap group')
            s.add_all([user, group]); s.flush()
            self.user_id = user.id
            s.execute(sa.insert(metadata.tables['auth_user_groups']).values(user_id=user.id, group_id=group.id))
            s.add(StudentProfile(user_id=user.id, selected_grade_id=None, onboarding_mode=None, onboarding_complete=False))
            now = s.scalar(sa.select(sa.func.clock_timestamp()))
            s.add(IdentityReceipt(scope='user:' + str(user.id), operation='complete_onboarding', key_digest='1' * 64,
                request_digest='2' * 64, user_id=user.id, status=200, response={'synthetic': 'retained-result'},
                expires_at=now + timedelta(days=7)))
            s.add(IdentityReceipt(scope='anonymous:retained-pending', operation='register', key_digest='3' * 64,
                request_digest='4' * 64, expires_at=now + timedelta(days=7)))
            s.add(LoginWindow(id=uuid.uuid4(), ip_digest='5' * 64, started_at=now, count=3))
            _, self.session_token, _ = Security(self.engine, self.key, 'http://127.0.0.1:8121', secure=False).issue(s, user, now)
            uow.commit()

    def private(self):
        with self.engine.connect() as c:
            return {name: [dict(row) for row in c.execute(sa.select(metadata.tables[name])
                    .order_by(*metadata.tables[name].primary_key)).mappings()] for name in PRIVATE}

    def state(self):
        with UnitOfWork(self.engine) as uow:
            return snapshot(uow.session)

    def sequences(self):
        with self.engine.connect() as c:
            return list(c.execute(sa.text('SELECT sequencename,last_value FROM pg_sequences '
                                         'WHERE schemaname=current_schema() ORDER BY sequencename')))

    def prepare(self, *, dry_run=False):
        return prepare_sources(self.engine, ROOT, self.root / 'inputs', 'bootstrap-' + uuid.uuid4().hex,
                               self.sha, bootstrap=True, dry_run=dry_run)

    def test_full_bootstrap_dry_run_and_fixture_cli_do_not_touch_private_rows_or_sequences(self):
        from backend.cli import main
        before, private, sequences = self.state(), self.private(), self.sequences()
        preview = self.prepare(dry_run=True)
        self.assertEqual(preview['selected'], 279)
        self.assertEqual(preview['changes'], sum(COUNTS.values()))
        self.assertEqual(preview['effects'], 'NONE')
        self.assertFalse((self.root / 'inputs').exists())
        env = {'MATHSTART_DATABASE_URL': self.engine.url.render_as_string(hide_password=False), 'MATHSTART_DB_BACKEND': 'postgresql'}
        with patch.dict(os.environ, env), redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(['bootstrap', '--disposable', '--dry-run', '--source-sha', self.sha]), 0)
        self.assertEqual(json.loads(output.getvalue())['effects'], 'NONE')
        from backend.content.publish import main as publish_main
        with patch.dict(os.environ, env), redirect_stdout(io.StringIO()) as output:
            self.assertEqual(publish_main(['prepare-bootstrap', '--dry-run', '--source-sha', self.sha,
                '--release-id', 'bootstrap-cli-preview', '--input-root', str(self.root / 'absent'),
                '--changes', str(self.root / 'absent-edition.json')]), 0)
        self.assertEqual(json.loads(output.getvalue())['effects'], 'NONE')
        self.assertFalse((self.root / 'absent').exists())
        self.assertFalse((self.root / 'absent-edition.json').exists())
        self.assertEqual(self.state(), before)
        self.assertEqual(self.private(), private)
        self.assertEqual(self.sequences(), sequences)

    def test_existing_retired_rows_and_timestamps_are_kept_and_runtime_edits_refused(self):
        table = metadata.tables['content_contentpage']
        with self.engine.begin() as c:
            for number, slug in enumerate(('materialy', 'pamyatki'), 50001):
                c.execute(sa.insert(table).values(id=number, slug=slug, title='Retained retirement', page_type='static',
                    order=0, body_html='Retained historical body', page_css='', page_js='', seo_title='', seo_description='',
                    is_published=True, created_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
                    updated_at=datetime(2021, 1, 1, tzinfo=timezone.utc)))
            advance_sequences(c)
        retained = self.state()['content_contentpage']
        private = self.private()
        prepared = self.prepare()
        with UnitOfWork(self.engine) as uow:
            apply_updates(uow.session, prepared['changes'], prepared['before_digest'], prepared['after_digest'])
            uow.commit()
        state = self.state()
        for old in retained:
            self.assertEqual(next(row for row in state['content_contentpage'] if row['id'] == old['id']), {**old, 'is_published': False})
        self.assertEqual(len(state['content_contentpage']), 281)
        for name, count in COUNTS.items():
            self.assertEqual(len(state[name]), count + (2 if name == 'content_contentpage' else 0))
        self.assertEqual(self.private(), private)
        self.assertEqual(self.prepare(dry_run=True)['changes'], 0)
        with self.engine.begin() as c:
            c.execute(sa.update(metadata.tables['content_grade']).values(description='Retained runtime edit'))
        changed = self.state()
        with self.assertRaises(PublicationConflict) as rejected:
            self.prepare(dry_run=True)
        self.assertEqual(rejected.exception.code, 'SOURCE_CONFLICT')
        self.assertEqual(self.state(), changed)
        self.assertEqual(self.private(), private)

    def test_real_full_bootstrap_publication_preserves_auth_profiles_receipts_sessions_and_media(self):
        private = self.private()
        prepared = self.prepare()
        self.assertEqual(self.private(), private)
        self.assertTrue(all(not rows for rows in self.state().values()))
        listener = socket.socket(); listener.bind(('127.0.0.1', 0))
        self.addCleanup(listener.close)
        origin = 'http://127.0.0.1:' + str(listener.getsockname()[1])
        output = self.root / 'output'
        build_public(self.root / 'inputs', prepared['release_id'], prepared['manifest_digest'], output,
                     origin, prepared['input_receipt_digest'])
        plan = {'version': 'prepared-publication-v1', 'kind': 'publish', 'previous': None, 'origin': origin,
                **{key: prepared[key] for key in ('release_id', 'manifest_digest', 'input_receipt_digest',
                                                'before_digest', 'after_digest', 'changes')},
                'output_manifest_digest': sha256((output / 'output-manifest.json').read_bytes()).hexdigest()}
        releases, artifacts = self.root / 'releases', self.root / 'artifacts'
        participant = PreparedPublication(plan, input_root=self.root / 'inputs', output_root=output,
                                         release_root=releases, artifact_root=artifacts)
        security = Security(self.engine, self.key, origin, secure=False)
        app = create_public_app(self.engine, Signer(self.key), release_root=releases, artifact_root=artifacts,
                                artifact_digests={}, origin=origin, identity_service=IdentityService(security))
        server = uvicorn.Server(uvicorn.Config(app, log_level='error', proxy_headers=False))
        thread = threading.Thread(target=server.run, kwargs={'sockets': [listener]}, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 10
            while not server.started and time.monotonic() < deadline:
                time.sleep(.05)
            self.assertTrue(server.started)
            authority = PublisherAuthority(self.engine, participant, lease_seconds=120)
            token, _ = authority.claim('public', 'full-bootstrap', plan, uuid.uuid4())
            probes, measured = deque(maxlen=5), {'requests': 0, 'maximum_seconds': 0}
            send = httpx.Client.send
            def observed(client, request, *args, **kwargs):
                started = time.monotonic()
                item = {'path': request.url.path}
                try:
                    result = send(client, request, *args, **kwargs)
                    item.update(status=result.status_code, cache=result.headers.get('cache-control'))
                    return result
                except Exception as error:
                    item['failure_class'] = type(error).__name__
                    raise
                finally:
                    elapsed = round(time.monotonic() - started, 3)
                    item['seconds'] = elapsed
                    probes.append(item)
                    measured['requests'] += 1
                    measured['maximum_seconds'] = max(measured['maximum_seconds'], elapsed)
            with patch.object(httpx.Client, 'send', observed):
                try:
                    self.assertEqual(finish(authority, token), 'COMPLETE')
                except PublicationConflict as error:
                    self.fail(json.dumps({'publication_error': error.code, **measured, 'last_public_probes': list(probes)}))
            print(json.dumps({'full_bootstrap_public_probes': measured}), flush=True)
            for name, count in COUNTS.items():
                self.assertEqual(len(self.state()[name]), count)
            self.assertEqual(self.private(), private)
            state, sequences = self.state(), self.sequences()
            self.assertEqual(self.prepare(dry_run=True)['changes'], 0)
            self.assertEqual(self.state(), state)
            self.assertEqual(self.sequences(), sequences)
            with httpx.Client(trust_env=False) as client:
                self.assertEqual(client.get(origin + '/').status_code, 200)
                client.cookies.set('sessionid', self.session_token)
                response = client.get(origin + '/api/v1/users/me/')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()['data']['id'], self.user_id)
            self.assertEqual(self.private(), private)
        finally:
            server.should_exit = True
            thread.join(timeout=10)
            if thread.is_alive():
                raise RuntimeError('Owned bootstrap HTTP runtime survived cleanup')


if __name__ == '__main__':
    unittest.main()
