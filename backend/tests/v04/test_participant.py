"""Real PostgreSQL + React builds + owned HTTP publication/recovery rehearsal."""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import threading
import time
import unittest
import uuid
from unittest.mock import patch

import httpx
import sqlalchemy as sa
from sqlalchemy.engine import make_url
import uvicorn

from backend.content.artifact_pins import PublicationArtifactPins
from backend.content.build import encoded
from backend.content.editions import snapshot, project_updates, apply_updates
from backend.content.participant import PreparedPublication, check_database, digest
from backend.content.projection import delivery_candidate, build_index_candidate, ReviewedSource
from backend.content.publication import PublisherAuthority, PublicationConflict, descriptor
from backend.content.releases import active_descriptor
from backend.content.publish import finish, main
from backend.content.observation import PublicationObserver
from backend.staff.publication import observe
from backend.infrastructure.http.app import create_app
from backend.infrastructure.http.signing import Signer
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.upgrade import require_disposable, fresh
from backend.models.baseline import ContentPage
from backend.models.protocol import ActiveReleaseDescriptor, PublicationJournal
from backend.content.verified_release_cache import VerifiedReleaseStore
from frontend.build_public import build_public
from frontend.rendering import PublicRenderer


class PreparedPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Never clear or reuse the caller's content, authority or original DB.
        cls.parent = sa.create_engine(os.environ['MATHSTART_V04_DATABASE_URL'], hide_parameters=True)
        with cls.parent.begin() as c:
            require_disposable(c)
        cls.name = 'test_ms7_mig_v01_participant_' + uuid.uuid4().hex[:20]
        with cls.parent.connect().execution_options(isolation_level='AUTOCOMMIT') as c:
            c.exec_driver_sql('CREATE DATABASE ' + cls.name)
        cls.engine = sa.create_engine(cls.parent.url.set(database=cls.name), hide_parameters=True)
        cls.temp = tempfile.TemporaryDirectory(prefix='publication-participant-')
        cls.root = Path(cls.temp.name)
        cls.release_root, cls.artifact_root = cls.root / 'releases', cls.root / 'artifacts'
        cls.inputs, cls.outputs = cls.root / 'inputs', cls.root / 'outputs'
        cls.inputs.mkdir(); cls.outputs.mkdir()
        cls.socket = socket.socket(); cls.socket.bind(('127.0.0.1', 0))
        cls.origin = 'http://127.0.0.1:' + str(cls.socket.getsockname()[1])
        try:
            with cls.engine.begin() as c:
                c.exec_driver_sql("COMMENT ON DATABASE " + cls.name + " IS 'MS7-MIG-V01 disposable synthetic test database'")
                fresh(c)
            with UnitOfWork(cls.engine) as uow:
                home = ContentPage(slug='synthetic-home', page_type='home', title='Synthetic home', body_html='<h1>Synthetic home</h1>', is_published=True)
                topic = ContentPage(slug='synthetic-topic', page_type='topic', title='Synthetic topic', body_html='<h1>Synthetic topic</h1><p>Original body</p>', is_published=True)
                uow.session.add_all([home, topic]); uow.session.flush()
                cls.topic = topic.id
                uow.commit()
            cls.editions, cls.handoffs = [], []
            with UnitOfWork(cls.engine) as uow:
                first = snapshot(uow.session)
            second = deepcopy(first)
            row = next(r for r in second['content_contentpage'] if r['id'] == cls.topic)
            row['body_html'] = '<h1>Synthetic topic</h1><p>Published new body</p>'
            third = deepcopy(second)
            next(r for r in third['content_contentpage'] if r['id'] == cls.topic)['is_published'] = False
            cls.editions = [first, second, third]
            for index, state in enumerate(cls.editions):
                release_id = 'synthetic-r' + str(index + 1)
                with UnitOfWork(cls.engine) as uow:
                    changes = cls.changes(first, state)
                    apply_updates(uow.session, changes, digest(first), digest(state))
                    cls.write_inputs(uow, release_id)
                receipt_raw = (cls.inputs / release_id / 'receipt.json').read_bytes()
                receipt = json.loads(receipt_raw)
                output = cls.outputs / release_id
                # Actual React Router/Node build for each edition, never a
                # renamed copy of an older output manifest.
                print('REAL_REACT_BUILD ' + release_id, flush=True)
                build_public(cls.inputs, release_id, receipt['manifest_digest'], output, cls.origin, sha256(receipt_raw).hexdigest())
                cls.handoffs.append({'release_id': release_id, 'manifest_digest': receipt['manifest_digest'],
                    'input_receipt_digest': sha256(receipt_raw).hexdigest(),
                    'output_manifest_digest': sha256((output / 'output-manifest.json').read_bytes()).hexdigest()})
            cls.pins = PublicationArtifactPins(cls.engine, {})
            cls.renderer = PublicRenderer(cls.artifact_root, cls.pins)
            cls.app = create_app(cls.engine, Signer('synthetic-publication-rehearsal-key'),
                        release_store=VerifiedReleaseStore(cls.release_root), render_page=cls.renderer, public_origin=cls.origin)
            cls.server = uvicorn.Server(uvicorn.Config(cls.app, log_level='error', proxy_headers=False))
            cls.thread = threading.Thread(target=cls.server.run, kwargs={'sockets': [cls.socket]}, daemon=True)
            cls.thread.start()
            deadline = time.monotonic() + 10
            while not cls.server.started and time.monotonic() < deadline:
                time.sleep(.05)
            if not cls.server.started:
                raise RuntimeError('Owned HTTP runtime failed to start')
        except BaseException:
            cls.cleanup()
            raise

    @classmethod
    def cleanup(cls):
        if hasattr(cls, 'server'):
            cls.server.should_exit = True
            cls.thread.join(timeout=10)
            if cls.thread.is_alive():
                raise RuntimeError('Owned HTTP runtime failed to stop')
        cls.socket.close(); cls.engine.dispose()
        with cls.parent.connect().execution_options(isolation_level='AUTOCOMMIT') as c:
            # Exact generated name, marked synthetic database, no FORCE drop.
            if not re.fullmatch('test_ms7_mig_v01_participant_[a-f0-9]{20}', cls.name):
                raise RuntimeError('Owned database identity mismatch')
            marker = c.scalar(sa.text("SELECT shobj_description(oid, 'pg_database') FROM pg_database WHERE datname=:name"), {'name': cls.name})
            if marker != 'MS7-MIG-V01 disposable synthetic test database':
                raise RuntimeError('Owned database marker mismatch')
            c.exec_driver_sql('DROP DATABASE ' + cls.name)
        cls.parent.dispose(); cls.temp.cleanup()

    @classmethod
    def tearDownClass(cls):
        cls.cleanup()

    @staticmethod
    def changes(before, after):
        result = []
        for name in before:
            for old, new in zip(before[name], after[name], strict=True):
                if old != new:
                    result.append({'table': name, 'before': old, 'after': new})
        return result

    @classmethod
    def write_inputs(cls, uow, release_id):
        deliveries = {}
        css = b'/* owned publication cache rehearsal */\n'
        asset = {'url': '/static/synthetic.css', 'storage_key': 'static/synthetic.css', 'kind': 'style',
                 'sha256': sha256(css).hexdigest(), 'order': 0, 'lifecycle': 'none'}
        for page in uow.session.scalars(sa.select(ContentPage).where(ContentPage.is_published.is_(True)).order_by(ContentPage.id)):
            deliveries[page.id] = delivery_candidate(uow, page.slug, ReviewedSource('synthetic/' + page.slug + '.md', 'a' * 64, (asset,)))
        index = build_index_candidate(uow, release_id, deliveries)
        files = {'index.json': encoded(index), 'static/synthetic.css': css,
                 **{f'pages/{pk}.json': encoded(page) for pk, page in deliveries.items()}}
        target = cls.inputs / release_id; target.mkdir()
        for name, raw in files.items():
            path = target / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        receipt = {'version': 'build-input-receipt-v1', 'source_sha': '0' * 40, 'release_id': release_id,
            'manifest_digest': sha256(files['index.json']).hexdigest(), 'pages': len(deliveries),
            'topics': len(index['catalogue']['topics']), 'assets': 1, 'activation': 'NOT_PERFORMED',
            'files': [{'path': name, 'sha256': sha256(raw).hexdigest(), 'size': len(raw)} for name, raw in files.items()]}
        (target / 'receipt.json').write_bytes(encoded(receipt))

    def setUp(self):
        # Each case retains immutable bytes but starts with its own clean
        # authority and exact original synthetic domain rows.
        from backend.models.protocol import history, active, gate, journal
        with self.engine.begin() as c:
            for table in (active, gate, history, journal):
                c.execute(sa.delete(table))
        with UnitOfWork(self.engine) as uow:
            current = snapshot(uow.session)
            apply_updates(uow.session, self.changes(current, self.editions[0]), digest(current), digest(self.editions[0]))
            uow.commit()

    def prepared(self, index):
        with UnitOfWork(self.engine) as uow:
            before = snapshot(uow.session)
            previous = descriptor(uow.session.get(ActiveReleaseDescriptor, 'public'))
        plan = {'version': 'prepared-publication-v1', 'kind': 'unpublish' if index == 2 else 'publish',
                **self.handoffs[index], 'previous': previous, 'origin': self.origin,
                'before_digest': digest(before), 'after_digest': digest(self.editions[index]),
                'changes': self.changes(before, self.editions[index])}
        participant = PreparedPublication(plan, input_root=self.inputs, output_root=self.outputs / plan['release_id'],
                    release_root=self.release_root, artifact_root=self.artifact_root)
        return plan, participant, PublisherAuthority(self.engine, participant, lease_seconds=120)

    def publish(self, index):
        plan, participant, authority = self.prepared(index)
        token, _ = authority.claim('public', 'publish-' + str(index), plan, uuid.uuid4())
        self.assertEqual(finish(authority, token), 'COMPLETE')
        return plan, participant, authority, token

    def observation(self):
        with UnitOfWork(self.engine) as uow:
            return observe(uow, self.topic, 'public', PublicationObserver(VerifiedReleaseStore(self.release_root)))

    def test_real_publish_unpublish_recovery_and_old_pinned_render(self):
        _, _, first_authority, first = self.publish(0)
        self.assertEqual(self.observation()['state'], 'IN_SYNC')
        with UnitOfWork(self.engine) as uow:
            selected = VerifiedReleaseStore(self.release_root).load(active_descriptor(uow, 'public'))
        plan, participant, authority = self.prepared(1)
        token, _ = authority.claim('public', 'publish-1', plan, uuid.uuid4())
        before_commit = self.observation()
        self.assertEqual(before_commit['state'], 'PENDING')
        self.assertEqual(before_commit['active'], before_commit['db_edition'])
        authority.stage(token); authority.commit(token)
        after_commit = self.observation()
        self.assertEqual(after_commit['db_edition']['release_id'], plan['release_id'])
        self.assertNotEqual(after_commit['active'], after_commit['db_edition'])
        authority.intent(token); authority.activate(token)
        # Lost activation acknowledgement: committed domain data is not applied
        # twice; recovery must read the actual durable next descriptor.
        authority.uncertain(token); authority.renew(token, surrender=True)
        self.assertEqual(self.observation()['state'], 'RECOVERY_REQUIRED')
        self.assertEqual(self.observation()['pending']['ownership'], 'TAKEOVER_ELIGIBLE')
        recovered = authority.takeover('public', token.operation_id, token.generation, uuid.uuid4())
        with patch.object(participant, 'apply', side_effect=AssertionError('Committed domain apply repeated')):
            self.assertEqual(finish(authority, recovered), 'COMPLETE')
        page = selected.pages[self.topic]
        self.assertIn('Original body', self.renderer(page, selected.renderer_context(page, {}), self.origin + '/synthetic-topic/'))
        self.assertEqual(first_authority.complete(first), 'COMPLETE')
        with httpx.Client(trust_env=False) as client:
            self.assertIn('Published new body', client.get(self.origin + '/synthetic-topic/').text)
        self.publish(2)
        self.assertFalse(self.observation()['db_edition']['page_published'])
        self.assertEqual(self.observation()['state'], 'IN_SYNC')
        with httpx.Client(trust_env=False) as client:
            self.assertEqual(client.get(self.origin + '/synthetic-topic/').status_code, 404)
            self.assertNotIn('/synthetic-topic/', client.get(self.origin + '/sitemap.xml').text)
        with UnitOfWork(self.engine) as uow:
            row = uow.session.get(ContentPage, self.topic)
            self.assertIsNotNone(row); self.assertFalse(row.is_published)

    def test_failed_public_probe_retains_pending_and_recovery_rechecks_http(self):
        plan, participant, authority = self.prepared(0)
        token, _ = authority.claim('public', 'publish-0', plan, uuid.uuid4())
        authority.stage(token); authority.commit(token); authority.intent(token); authority.activate(token)
        with patch('backend.content.participant.httpx.Client', side_effect=RuntimeError('synthetic transport failure')):
            with self.assertRaises(PublicationConflict):
                authority.complete(token)
        self.assertEqual(authority.inspect(token)['phase'], 'RECOVERY_REQUIRED')
        self.assertEqual(self.observation()['pending']['failure_code'], 'HEALTH_FAILED')
        authority.renew(token, surrender=True)
        recovered = authority.takeover('public', token.operation_id, token.generation, uuid.uuid4())
        self.assertEqual(finish(authority, recovered), 'COMPLETE')

    def test_stale_source_refuses_claim_and_does_not_replace_database(self):
        self.publish(0)
        plan, _, authority = self.prepared(1)
        with self.engine.begin() as c:
            c.execute(sa.update(ContentPage).where(ContentPage.id == self.topic).values(title='Concurrent preserved edit'))
        with self.assertRaises(PublicationConflict) as error:
            authority.claim('public', 'publish-1', plan, uuid.uuid4())
        self.assertEqual(error.exception.code, 'SOURCE_CONFLICT')
        with UnitOfWork(self.engine) as uow:
            self.assertEqual(uow.session.get(ContentPage, self.topic).title, 'Concurrent preserved edit')

    def test_changed_plan_cannot_reuse_cached_verification_or_output_pin(self):
        plan, participant, authority = self.prepared(0)
        changed = {**plan, 'after_digest': 'f' * 64}
        with UnitOfWork(self.engine) as uow, self.assertRaises(PublicationConflict):
            participant.check_admission(uow.session, changed)
        token, _ = authority.claim('public', 'publish-0', plan, uuid.uuid4())
        authority.stage(token); authority.commit(token); authority.intent(token); authority.activate(token)
        pin = {'release_id': plan['release_id'], 'manifest_digest': plan['manifest_digest']}
        self.assertEqual(self.pins(pin), plan['output_manifest_digest'])
        with self.engine.begin() as c:
            c.execute(sa.update(PublicationJournal).where(PublicationJournal.id == token.operation_id).values(plan=changed))
        with self.assertRaises(Exception):
            self.pins(pin)

    def test_partial_tree_install_is_restartable_and_never_overwrites_conflicts(self):
        plan, participant, authority = self.prepared(0)
        token, _ = authority.claim('public', 'publish-0', plan, uuid.uuid4())
        original = participant._install
        calls = []
        def fail_between_trees(source, target):
            calls.append(target)
            if len(calls) == 2:
                raise OSError('synthetic second resource install failure')
            return original(source, target)
        with patch.object(participant, '_install', side_effect=fail_between_trees):
            with self.assertRaises(OSError):
                authority.stage(token)
        self.assertEqual(authority.inspect(token)['phase'], 'VALIDATED')
        self.assertEqual(finish(authority, token), 'COMPLETE')
        public = self.artifact_root / plan['release_id'] / 'index.html'
        before = public.read_bytes()
        try:
            public.write_bytes(b'conflicting immutable file')
            with self.assertRaises(PublicationConflict) as error:
                participant.stage(token, plan, digest(plan))
            self.assertEqual(error.exception.code, 'ARTIFACT_CONFLICT')
            self.assertEqual(public.read_bytes(), b'conflicting immutable file')
        finally:
            public.write_bytes(before)

    def test_operator_cli_plan_publish_unpublish_and_status(self):
        env = {'MATHSTART_DATABASE_URL': self.engine.url.render_as_string(hide_password=False)}
        roots = ['--input-root', str(self.inputs), '--release-root', str(self.release_root), '--artifact-root', str(self.artifact_root)]
        with patch.dict(os.environ, env):
            for index in (0, 1, 2):
                plan, _, _ = self.prepared(index)
                changes = self.root / ('cli-changes-' + str(index) + '.json')
                changes.write_bytes(encoded(plan['changes']))
                output = self.outputs / plan['release_id']
                target = self.root / ('cli-plan-' + str(index) + '.json')
                common = [*roots, '--output-root', str(output)]
                with redirect_stdout(StringIO()) as stream, redirect_stderr(StringIO()) as errors:
                    code = main(['plan', *common, '--plan', str(target), '--changes', str(changes), '--kind', plan['kind'],
                                 '--origin', self.origin, '--output-digest', plan['output_manifest_digest']])
                self.assertEqual(code, 0, errors.getvalue())
                self.assertEqual(json.loads(target.read_bytes()), plan)
                owner = str(uuid.uuid4())
                with redirect_stdout(StringIO()) as stream, redirect_stderr(StringIO()) as errors:
                    code = main([plan['kind'], *common, '--plan', str(target), '--key', 'cli-' + str(index), '--owner', owner])
                self.assertEqual(code, 0, errors.getvalue())
                result = json.loads(stream.getvalue())
                self.assertEqual(result['phase'], 'COMPLETE')
                with redirect_stdout(StringIO()) as stream:
                    self.assertEqual(main(['status', '--operation-id', result['token']['operation_id']]), 0)
                self.assertEqual(json.loads(stream.getvalue())['operation']['phase'], 'COMPLETE')
                # Terminal ACK reads the journal without requiring retained
                # original build handoffs or touching the active descriptor.
                with redirect_stdout(StringIO()), redirect_stderr(StringIO()) as errors:
                    self.assertEqual(main(['resume', '--operation-id', result['token']['operation_id'],
                        '--owner', owner, '--generation', str(result['token']['generation'])]), 0, errors.getvalue())
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                self.assertEqual(main(['publish', *common, '--plan', str(target), '--key', 'wrong-kind', '--owner', owner]), 1)

    def test_precommit_abort_and_lease_controls_do_not_need_candidate_files(self):
        _, _, _, _ = self.publish(0)
        plan, participant, authority = self.prepared(1)
        owner = uuid.uuid4()
        token, _ = authority.claim('public', 'abort-next', plan, owner)
        env = {'MATHSTART_DATABASE_URL': self.engine.url.render_as_string(hide_password=False)}
        control = ['--operation-id', str(token.operation_id), '--generation', str(token.generation), '--owner', str(owner)]
        with patch.dict(os.environ, env), patch.object(PreparedPublication, '__init__', side_effect=AssertionError('Candidate unavailable')):
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()) as errors:
                self.assertEqual(main(['renew', *control]), 0, errors.getvalue())
                self.assertEqual(main(['abort', *control, '--release-root', str(self.release_root)]), 0, errors.getvalue())
        self.assertEqual(authority.inspect(token)['phase'], 'FAILED_PRECOMMIT')
        with UnitOfWork(self.engine) as uow:
            self.assertEqual(snapshot(uow.session), self.editions[0])
            self.assertEqual(uow.session.get(ActiveReleaseDescriptor, 'public').release_id, 'synthetic-r1')


if __name__ == '__main__':
    unittest.main()
