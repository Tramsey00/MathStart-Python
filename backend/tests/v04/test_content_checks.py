"""Existing CLI semantics on real PG data and an owned HTTP listener."""
import ast
from contextlib import contextmanager
import json
import os
import subprocess
import sys
from pathlib import Path
import tempfile
from threading import Thread
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace
import unittest

import sqlalchemy as sa

from backend.content import checks
from backend.content.sources import SourceError
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.upgrade import require_disposable
from backend.models.baseline import ContentPage

ROOT = Path(__file__).resolve().parents[3]


@contextmanager
def public_server(status=200, body=b'<html><body><h1>Published mathematics</h1></body></html>'):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(status)
            if status == 302:
                self.send_header('Location', 'http://invalid.example/never-follow')
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield 'http://127.0.0.1:' + str(server.server_port)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        if thread.is_alive():
            raise RuntimeError('Owned HTTP server did not stop')


class InspectionHelperTests(unittest.TestCase):
    def test_reference_extraction_and_normalization_match_original_command(self):
        from scripts.legacy_oracle import oracle_root
        tree = ast.parse((oracle_root() / 'content/management/commands/check_site_integrity.py').read_text(encoding='utf-8'))
        names = {'normalize_internal_path', 'normalize_page_path', 'extract_css_urls', 'extract_page_references'}
        nodes = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
                 and not (isinstance(node, ast.ImportFrom) and node.module.startswith(('django', 'content')))
                 or isinstance(node, ast.FunctionDef) and node.name in names
                 or isinstance(node, ast.Assign)]
        original = {}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), 'preserved-integrity-helpers', 'exec'), original)
        for url in ['', '#anchor', ' /lesson/?q=2#part ', '//localhost/a%20b', 'https://external.example/a',
                    'https://127.0.0.1/static/a.css', 'mailto:a@example.test', 'data:abc', 'a\\b', '/a//b']:
            self.assertEqual(checks.normalize_internal_path(url), original['normalize_internal_path'](url), url)
        page = SimpleNamespace(body_html='<a href="/lesson/">A</a><img srcset="/media/a.png 1x, /media/b.png 2x"><style>a{background:url(/static/a.svg)}</style><video poster="/media/p.png"></video>', page_css='a{background:url("/static/b.svg")}')
        self.assertEqual(checks.references(page), original['extract_page_references'](page))

    def test_files_cannot_escape_configured_storage_roots(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'inside').mkdir()
            (root / 'outside.txt').write_text('outside')
            self.assertFalse(checks.confined_file(root / 'inside', '../outside.txt'))
            self.assertTrue(checks.confined_file(root, 'outside.txt'))


class PostgreSQLInspectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = sa.create_engine(os.environ['MATHSTART_V04_DATABASE_URL'], hide_parameters=True)
        with cls.engine.begin() as c:
            require_disposable(c)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def test_all_263_lessons_match_including_css_js_and_metadata(self):
        with UnitOfWork(self.engine) as uow:
            uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
            self.assertEqual(checks.verify_lesson_sources(uow.session, ROOT, all_lessons=True), {'verified': 263})

    def test_unreviewed_css_and_unknown_selections_fail_without_overwrite(self):
        with UnitOfWork(self.engine) as uow:
            page = uow.session.scalar(sa.select(ContentPage).where(ContentPage.page_type == 'topic').order_by(ContentPage.id))
            original = page.page_css
            page.page_css += '\n/* unreviewed change */'
            with self.assertRaises(SourceError):
                checks.verify_lesson_sources(uow.session, ROOT, slugs=[page.slug])
            self.assertNotEqual(page.page_css, original)
            for options in [{}, {'all_lessons': True, 'slugs': [page.slug]}, {'slugs': ['absent']}, {'slugs': [page.slug, page.slug]}]:
                with self.assertRaises(SourceError):
                    checks.verify_lesson_sources(uow.session, ROOT, **options)

    def test_integrity_reports_existing_inventory_and_real_negative_references(self):
        with UnitOfWork(self.engine) as uow:
            report, errors = checks.inspect_site(uow.session, static_roots=[ROOT / 'static'], media_root=ROOT / 'site_content/media')
            self.assertEqual(report['summary']['pages_total'], 279)
            self.assertEqual(report['summary']['topics_total'], 263)
            self.assertGreater(report['summary']['checked_references'], 0)
            self.assertEqual(errors, 0, json.dumps(report['summary']))
            page = uow.session.scalar(sa.select(ContentPage).where(ContentPage.page_type == 'topic').order_by(ContentPage.id))
            page.body_html += '<img src="/media/absent-negative.png"><a href="/absent-negative/">Missing</a><link href="/static/absent-negative.css">'
            report, errors = checks.inspect_site(uow.session, static_roots=[ROOT / 'static'], media_root=ROOT / 'site_content/media')
            self.assertEqual(errors, 3)
            for kind in ['broken_internal_links', 'broken_static_references', 'broken_media_references']:
                self.assertEqual(report[kind][0]['page'], page.slug)

    def test_quality_inspects_real_http_and_preserves_issues_status_and_redirect_failure(self):
        # A private transaction narrows the HTTP workload to one existing page;
        # it is rolled back and never changes the prepared release/database.
        with UnitOfWork(self.engine) as uow:
            page = uow.session.scalar(sa.select(ContentPage).where(ContentPage.is_published.is_(True)).order_by(ContentPage.id))
            uow.session.execute(sa.update(ContentPage).where(ContentPage.id != page.id).values(is_published=False))
            for status, body, expected in [(200, b'<h1>Math</h1>', 0), (200, b'<p>TODO</p>', 1), (404, b'Absent', 1), (302, b'Redirect', 1)]:
                with self.subTest(status=status, body=body), public_server(status, body) as origin:
                    report, errors = checks.inspect_public_quality(uow.session, origin)
                    self.assertEqual(report['pages_checked'], 1)
                    self.assertEqual(errors, expected)
                    if status != 200:
                        self.assertEqual(report['issues'][0]['detail'], status)

    def test_actual_cli_reports_nonzero_failures_no_django_and_no_database_mutations(self):
        from backend.tests.test_postgres import data_digest
        environment = {**os.environ, 'MATHSTART_DB_BACKEND': 'postgresql',
                       'MATHSTART_DATABASE_URL': self.engine.url.render_as_string(hide_password=False)}
        code = ('import importlib.util,sys; assert importlib.util.find_spec("django") is None; '
                'from backend.cli import main; result=main(sys.argv[1:]); '
                'assert not any(m=="django" or m.startswith("django.") for m in sys.modules); raise SystemExit(result)')
        with self.engine.connect() as connection:
            before = data_digest(connection)
        with tempfile.TemporaryDirectory() as directory:
            report_root = Path(directory) / 'reports'
            source = subprocess.run([sys.executable, '-c', code, 'check-lesson-sources', '--all'], cwd=ROOT,
                                    env=environment, capture_output=True, timeout=90)
            self.assertEqual(source.returncode, 0, source.stderr.decode(errors='replace'))
            self.assertEqual(json.loads(source.stdout), {'verified': 263})
            base = [sys.executable, '-c', code, 'check-site-integrity', '--report-root', str(report_root),
                    '--static-root', str(ROOT / 'static'), '--media-root', str(ROOT / 'site_content/media')]
            positive = subprocess.run(base, cwd=ROOT, env=environment, capture_output=True, timeout=90)
            self.assertEqual(positive.returncode, 0, positive.stdout.decode(errors='replace'))
            self.assertEqual(json.loads((report_root / 'site_integrity_report.json').read_text(encoding='utf-8'))['summary']['pages_total'], 279)
            with public_server() as origin:
                quality = subprocess.run([sys.executable, '-c', code, 'check-content-quality', '--origin', origin,
                                          '--report-root', str(report_root)], cwd=ROOT, env=environment,
                                         capture_output=True, timeout=90)
                self.assertEqual(quality.returncode, 0, quality.stderr.decode(errors='replace'))
                self.assertEqual(json.loads(quality.stdout)['pages_checked'], 279)
                self.assertEqual(json.loads((report_root / 'content_quality_report.json').read_text(encoding='utf-8'))['issues'], [])
            # Missing storage must produce both a durable report and nonzero exit.
            negative = subprocess.run([*base[:-1], str(Path(directory) / 'absent-media')], cwd=ROOT,
                                      env=environment, capture_output=True, timeout=90)
            self.assertEqual(negative.returncode, 1)
            self.assertGreater(json.loads(negative.stdout)['errors'], 0)
            dry = subprocess.run([*base, '--dry-run'], cwd=ROOT, env=environment, capture_output=True, timeout=90)
            self.assertEqual(dry.returncode, 2)
        with self.engine.connect() as connection:
            self.assertEqual(data_digest(connection), before)


if __name__ == '__main__':
    unittest.main()
