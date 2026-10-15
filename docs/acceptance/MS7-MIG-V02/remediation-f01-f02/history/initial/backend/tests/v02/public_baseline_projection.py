"""Full 279-page source-profile projection comparison; no activation or writes."""
import json
import os
import subprocess
import sys
from pathlib import Path
from hashlib import sha256

import sqlalchemy as sa
from sqlalchemy.engine import URL

from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.infrastructure.uow import UnitOfWork
from backend.models.baseline import ContentPage, LessonPublication
from backend.content.projection import ReviewedSource, delivery_candidate, build_index_candidate


def main():
    name = os.environ['DJANGO_DB_NAME']
    if not name.startswith('ms6_v01_smoke_v02_') or os.environ.get('DJANGO_DB_PORT') != '15441':
        raise RuntimeError('Only V02 disposable baseline profile is allowed')
    oracle = subprocess.run([sys.executable, '-m', 'backend.tests.v02.legacy_comparator'],
                            input=b'[{"resource":"__content"}]', capture_output=True, timeout=60)
    if oracle.returncode:
        raise RuntimeError('Independent Django content comparator failed')
    original = json.loads(oracle.stdout)[0]
    engine = create_engine(DatabaseConfig(URL.create('postgresql+psycopg', username='postgres', host='127.0.0.1', port=15441, database=name)))
    statements = []
    def record(connection, cursor, statement, parameters, context, many):
        statements.append(statement)
    sa.event.listen(engine, 'before_cursor_execute', record)
    with UnitOfWork(engine) as uow:
        uow.session.execute(sa.text('SET TRANSACTION READ ONLY'))
        pages = list(uow.session.scalars(sa.select(ContentPage).where(ContentPage.is_published.is_(True)).order_by(ContentPage.id)))
        deliveries = {}
        for page in pages:
            path = uow.session.scalar(sa.select(LessonPublication.source_path).where(LessonPublication.page_id == page.id))
            path = 'curriculum/' + path if path else f'site_content/pages/{page.slug}/page.json'
            # This test covers complete metadata/source identities. Asset-family
            # trust and renderer lifecycle are separately delegated to V04/I02/I03.
            root = Path(__file__).resolve().parents[3]
            source_file = (root / path).resolve()
            if not source_file.is_relative_to(root):
                raise AssertionError('Source identity escaped repository')
            if source_file.is_dir():
                source_file = source_file / 'lesson.json'
                path += '/lesson.json'
            source = ReviewedSource(path, sha256(source_file.read_bytes()).hexdigest(), ())
            deliveries[page.id] = delivery_candidate(uow, page.slug, source)
        index = build_index_candidate(uow, 'v02-readonly-candidate', deliveries)
        if [t['id'] for t in index['catalogue']['topics']] != original['ids']:
            raise AssertionError('Target topic catalogue differs from Django')
        if {str(pk): data['seo'] for pk, data in deliveries.items()} != original['seo']:
            raise AssertionError('Target SEO differs from Django')
    if not all(s.lstrip().upper().startswith(('SELECT', 'SET TRANSACTION READ ONLY')) for s in statements):
        raise AssertionError('Read projection performed a write')
    print(json.dumps({'pages': len(index['pages']), 'topics': len(index['catalogue']['topics']),
                     'source_identity_mapping': 'PASS', 'seo_vs_django': 'PASS', 'catalogue_order_vs_django': 'PASS',
                     'read_only_sql': 'PASS', 'candidate_activation': 'NOT_PERFORMED',
                     'full_asset_family_and_browser_render': 'NOT_VERIFIED_BY_THIS_CHECK'}))
    engine.dispose()


if __name__ == '__main__':
    main()
