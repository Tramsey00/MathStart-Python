import json
from contextlib import ExitStack
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
import uuid

from backend.content.participant import digest
from scripts import container_dev as dev


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        stack = ExitStack()
        self.addCleanup(stack.close)
        root = Path(stack.enter_context(TemporaryDirectory())).resolve()
        local = root / 'var/compose'
        work = root / 'runtime/work/example'
        serving = root / 'runtime/serving'
        self.state = local / 'state.json'
        self.review = local / 'review.json'
        self.release = 'dev-fixture'
        self.op = uuid.uuid4()
        self.source = 'a' * 40
        output = b'{"fixture":true}'
        plan = dict(release_id=self.release, origin='http://127.0.0.1:8133',
                    manifest_digest='b' * 64, input_receipt_digest='c' * 64,
                    output_manifest_digest=sha256(output).hexdigest())
        self.args = SimpleNamespace(operation_id=self.op, content_digest=digest(plan))
        dev.save(self.state, dict(schema_code='schema', work=dict(path=str(work), release=self.release,
                                                                 key='schema:content')))
        for path in (work / 'inputs', serving / 'releases'):
            dev.save(path / self.release / 'receipt.json',
                     dict(source_sha=self.source, manifest_digest=plan['manifest_digest']))
        dev.save(work / 'publication.json', plan)
        copy = local / 'plans/example/publication.json'
        dev.save(copy, plan)
        dev.save(self.review, dict(kind='content', digest=self.args.content_digest,
                                   path=str(copy.relative_to(root))))
        (work / 'output').mkdir()
        (work / 'output/output-manifest.json').write_bytes(output)
        private, schema = local / 'api-env.json', local / 'schema-env.json'
        dev.save(private, dict(MATHSTART_PUBLIC_ORIGIN=plan['origin'],
                               MATHSTART_PUBLIC_ARTIFACT_DIGESTS=json.dumps(
                                   {self.release: plan['output_manifest_digest']})))
        dev.save(schema, dict(MATHSTART_DATABASE_URL='postgresql+psycopg://local_schema@db:5432/mathstart_dev'))
        stack.enter_context(patch.multiple(dev, ROOT=root, LOCAL=local, STATE=self.state, REVIEW=self.review,
                                           PRIVATE=private, SCHEMA=schema, SERVING=serving, RUNTIME_WORK=work.parent))
        stack.enter_context(patch.object(dev, 'git', side_effect=lambda action,*_: self.source if action == 'merge-base' else ''))
        stack.enter_context(patch.object(dev, 'check_public_origin'))
        stack.enter_context(patch.object(dev, 'content_digest', side_effect=lambda *, dev=False: 'hmr' if dev else 'content'))
        self.verify = stack.enter_context(patch('backend.content.artifacts.verify_public_artifacts'))
        engine = stack.enter_context(patch('backend.infrastructure.database.create_engine')).return_value
        self.connection = engine.begin.return_value.__enter__.return_value
        self.query = self.connection.execute.return_value.one_or_none
        self.row = ['COMPLETE','APPLIED',True,None,self.args.content_digest,self.release,plan['manifest_digest'],2,
                    self.op,self.release,plan['manifest_digest'],None,None,None,2,1,plan,False]
        self.query.side_effect = lambda: tuple(self.row)

    def assert_recorded(self):
        state = dev.read(self.state)
        self.assertEqual((state['release'], state['content_digest'], state['dev_content_digest']),
                         (self.release, 'content', 'hmr'))

    def test_success_and_repeat(self):
        self.assertEqual(dev.reconcile(self.args), 0)
        self.assert_recorded()
        self.assertFalse(self.review.exists())
        self.assertEqual(self.verify.call_count, 2)
        with patch.object(dev, 'save') as save:
            self.assertEqual(dev.reconcile(self.args), 0)
            save.assert_not_called()

    def test_wrong_digest(self):
        self.args.content_digest = 'e' * 64
        with self.assertRaisesRegex(RuntimeError, 'requested digest'):
            dev.reconcile(self.args)
        self.assertTrue(self.review.exists())
        self.assertNotIn('release', dev.read(self.state))

    def test_wrong_release_or_busy_gate(self):
        for index, value in ((9,'wrong-release'), (11,self.op), (17,True), (15,3)):
            with self.subTest(index=index):
                original = self.row[index]
                self.row[index] = value
                with self.assertRaisesRegex(RuntimeError, 'journal, active release or gate'):
                    dev.reconcile(self.args)
                self.assertNotIn('release', dev.read(self.state))
                self.assertTrue(self.review.exists())
                self.row[index] = original

    def test_interrupted_review_cleanup(self):
        with patch.object(Path, 'unlink', side_effect=OSError('simulated interruption')):
            with self.assertRaisesRegex(OSError, 'interruption'):
                dev.reconcile(self.args)
        self.assert_recorded()
        self.assertTrue(self.review.exists())
        with patch.object(dev, 'save') as save:
            self.assertEqual(dev.reconcile(self.args), 0)
            save.assert_not_called()
        self.assertFalse(self.review.exists())
