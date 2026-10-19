"""Full legacy byte parity and actual target INDEX CLI with no domain writes."""
import base64
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import sqlalchemy as sa

from backend.content.indexing import index_bytes
from backend.content.sources import SourceError
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.upgrade import require_disposable
from backend.models.baseline import ContentPage
from backend.tests.legacy_tools import legacy_python, oracle_root, oracle_environment
from backend.tests.test_postgres import data_digest

ROOT = Path(__file__).resolve().parents[3]


class IndexingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = sa.create_engine(os.environ['MATHSTART_V04_DATABASE_URL'], hide_parameters=True)
        with cls.engine.connect() as c:
            require_disposable(c)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def test_full_263_lesson_index_exact_bytes_match_actual_legacy_command(self):
        url = self.engine.url
        env = {**os.environ, 'DJANGO_DB_BACKEND': 'postgresql', 'DJANGO_DB_HOST': url.host,
               'DJANGO_DB_PORT': str(url.port), 'DJANGO_DB_NAME': url.database, 'DJANGO_DB_USER': url.username,
               'DJANGO_DB_PASSWORD': url.password or '', 'DJANGO_SECRET_KEY': 'synthetic-index-oracle',
               'DJANGO_DEBUG': '0', 'PYTHONIOENCODING': 'utf-8'}
        process = subprocess.run([legacy_python(), '-m', 'backend.tests.v04.index_oracle'], env=oracle_environment(env),
                                 cwd=oracle_root(), capture_output=True, timeout=60)
        self.assertEqual(process.returncode, 0, 'Independent legacy index oracle failed')
        oracle = json.loads(process.stdout)
        with UnitOfWork(self.engine) as uow:
            payload, count = index_bytes(uow.session, ROOT)
        self.assertEqual(count, 263)
        self.assertEqual(oracle['indexed'], count)
        self.assertEqual(payload, base64.b64decode(oracle['payload']))

    def test_actual_cli_dry_run_repeat_and_domain_sequences_preserved(self):
        from backend.cli import main
        with self.engine.connect() as c:
            before = data_digest(c)
            sequences = list(c.execute(sa.text('SELECT sequencename,last_value FROM pg_sequences WHERE schemaname=current_schema() ORDER BY sequencename')))
        env = {'MATHSTART_DATABASE_URL': self.engine.url.render_as_string(hide_password=False), 'MATHSTART_DB_BACKEND': 'postgresql'}
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, env):
            output = Path(directory) / 'generated'
            args = ['index-lessons', '--source-root', str(ROOT), '--output-root', str(output)]
            with redirect_stdout(io.StringIO()) as text:
                self.assertEqual(main([*args, '--dry-run']), 0)
            self.assertEqual(json.loads(text.getvalue()), {'indexed': 263, 'effects': 'NONE'})
            self.assertFalse(output.exists())
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(args), 0)
            path = output / 'INDEX.md'
            raw, stamp = path.read_bytes(), path.stat().st_mtime_ns
            with redirect_stdout(io.StringIO()) as text:
                self.assertEqual(main(args), 0)
            self.assertEqual(json.loads(text.getvalue())['effects'], 'UNCHANGED')
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(path.stat().st_mtime_ns, stamp)
        with self.engine.connect() as c:
            self.assertEqual(data_digest(c), before)
            self.assertEqual(list(c.execute(sa.text('SELECT sequencename,last_value FROM pg_sequences WHERE schemaname=current_schema() ORDER BY sequencename'))), sequences)

    def test_missing_catalogue_identity_refuses_without_writing(self):
        with UnitOfWork(self.engine) as uow:
            page = uow.session.scalar(sa.select(ContentPage).where(ContentPage.page_type == 'topic').order_by(ContentPage.id))
            uow.session.execute(sa.update(ContentPage).where(ContentPage.id == page.id).values(grade_id=None))
            with self.assertRaises(SourceError):
                index_bytes(uow.session, ROOT)


if __name__ == '__main__':
    unittest.main()
