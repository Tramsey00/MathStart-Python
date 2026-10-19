"""Synthetic disposable fixtures only; no real session/auth bypass in runtime."""
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
from pathlib import Path
import uuid

import sqlalchemy as sa

from backend.models.baseline import metadata
from backend.models.protocol import journal, gate, active
from backend.infrastructure.http.signing import Signer
from backend.content.releases import Descriptor, ReleaseStore

STAMP = datetime(2026, 10, 4, tzinfo=timezone.utc)
KEY = 'synthetic-v02-only-not-production'


def seed(engine):
    with engine.begin() as c:
        c.execute(sa.insert(metadata.tables['content_grade']), [
            {'id': 70, 'title': '5 класс', 'slug': '5-klass', 'order': 99, 'created_at': STAMP},
            {'id': 30, 'title': '10 класс', 'slug': '10-klass', 'order': 1, 'created_at': STAMP},
            {'id': 50, 'title': '6 класс', 'slug': '6-klass', 'order': 0, 'created_at': STAMP + timedelta(seconds=1)}])
        c.execute(sa.insert(metadata.tables['content_subject']), [
            {'id': 101, 'title': 'Математика', 'slug': 'matematika', 'grade_id': 70, 'order': 0},
            {'id': 102, 'title': 'Алгебра', 'slug': 'algebra', 'grade_id': 50, 'order': 1}])
        c.execute(sa.insert(metadata.tables['content_section']).values(id=201, title='Числа', slug='chisla', subject_id=101))
        c.execute(sa.insert(metadata.tables['content_contentpage']), [
            {'id': 301, 'title': 'Главная', 'slug': 'glavnaya', 'page_type': 'home', 'is_published': True,
             'body_html': '<h1>Главная</h1>', 'grade_id': None, 'subject_id': None, 'section_id': None},
            {'id': 302, 'title': 'Сумма Straße', 'slug': 'topic', 'page_type': 'topic', 'is_published': True,
             'body_html': '<p>Теория</p>', 'grade_id': 70, 'subject_id': 101, 'section_id': 201},
            {'id': 303, 'title': 'Private draft', 'slug': 'draft', 'page_type': 'topic', 'is_published': False,
             'body_html': 'PRIVATE-DRAFT-SENTINEL', 'grade_id': None, 'subject_id': None, 'section_id': None},
            {'id': 304, 'title': 'Каталог', 'slug': 'karta-sajta', 'page_type': 'static', 'is_published': True,
             'body_html': '<p>Каталог</p>', 'grade_id': None, 'subject_id': None, 'section_id': None}])
        c.execute(sa.insert(metadata.tables['content_lessonpublication']), [
            {'id': 401, 'page_id': 302, 'source_path': 'topics/topic/lesson.json', 'published_digest': 'a' * 64, 'published_at': STAMP},
            {'id': 402, 'page_id': 303, 'source_path': 'topics/draft/lesson.json', 'published_digest': 'b' * 64, 'published_at': STAMP}])
        c.execute(sa.insert(metadata.tables['content_mediaasset']), [
            {'id': 501, 'title': 'Equal title', 'file': 'uploads/a.png', 'related_page_id': 302, 'alt_text': 'Synthetic'},
            {'id': 502, 'title': 'Equal title', 'file': 'uploads/b.png', 'related_page_id': 303, 'alt_text': 'Synthetic'},
            {'id': 503, 'title': 'Equal title', 'file': 'uploads/c.png', 'related_page_id': None, 'alt_text': 'Synthetic'}])
        c.execute(sa.insert(metadata.tables['content_redirect']), [
            {'id': 601, 'old_path': '/legacy1/', 'new_path': '/topic/', 'is_permanent': True, 'is_active': True},
            {'id': 602, 'old_path': '/legacy2/', 'new_path': '/topic/', 'is_permanent': False, 'is_active': False}])
        c.execute(sa.insert(metadata.tables['auth_user']), [
            {'id': 901, 'username': 'viewer', 'password': '!unusable', 'is_staff': True, 'is_active': True, 'is_superuser': False},
            {'id': 902, 'username': 'super', 'password': 'SECRET-ENCODED-PASSWORD', 'is_staff': True, 'is_active': True, 'is_superuser': True},
            {'id': 903, 'username': 'student', 'password': '!unusable', 'is_staff': False, 'is_active': True, 'is_superuser': False},
            {'id': 904, 'username': 'inactive', 'password': '!unusable', 'is_staff': True, 'is_active': False, 'is_superuser': False},
            {'id': 905, 'username': 'other', 'password': '!unusable', 'is_staff': True, 'is_active': True, 'is_superuser': False}])
        c.execute(sa.insert(metadata.tables['django_content_type']), [
            {'id': 41, 'app_label': 'content', 'model': 'contentpage'},
            {'id': 42, 'app_label': 'auth', 'model': 'user'}, {'id': 43, 'app_label': 'content', 'model': 'grade'}])
        c.execute(sa.insert(metadata.tables['auth_permission']), [
            {'id': 51, 'name': 'View page', 'codename': 'view_contentpage', 'content_type_id': 41},
            {'id': 52, 'name': 'Change user', 'codename': 'change_user', 'content_type_id': 42},
            {'id': 53, 'name': 'View grade', 'codename': 'view_grade', 'content_type_id': 43}])
        c.execute(sa.insert(metadata.tables['auth_group']).values(id=61, name='Editors'))
        c.execute(sa.insert(metadata.tables['auth_group_permissions']).values(id=71, group_id=61, permission_id=51))
        c.execute(sa.insert(metadata.tables['auth_user_groups']).values(id=72, user_id=901, group_id=61))
        c.execute(sa.insert(metadata.tables['auth_user_user_permissions']), [
            {'id': 73, 'user_id': 901, 'permission_id': 52}, {'id': 74, 'user_id': 901, 'permission_id': 53},
            {'id': 75, 'user_id': 905, 'permission_id': 51}])
        c.execute(sa.insert(metadata.tables['django_admin_log']).values(id=81, action_time=STAMP, object_id='302',
                 object_repr='private historical input', action_flag=2, change_message='PASSWORD-SENTINEL', content_type_id=41, user_id=901))


def release_files(root):
    release_id = 'synthetic-v02'
    base = Path(root) / release_id
    (base / 'pages').mkdir(parents=True, exist_ok=True)
    (base / 'assets').mkdir(exist_ok=True)
    asset_raw = b'body { color: black; }'
    (base / 'assets/theme.css').write_bytes(asset_raw)
    asset = {'storage_key': 'assets/theme.css', 'url': '/static/theme.css', 'kind': 'style',
             'sha256': sha256(asset_raw).hexdigest(), 'order': 0, 'lifecycle': 'none'}
    pages = []
    deliveries = {}
    for pk, slug, kind, title in [(301, 'glavnaya', 'home', 'Главная'), (302, 'topic', 'topic', 'Сумма Straße'),
                                   (304, 'karta-sajta', 'static', 'Каталог')]:
        path = '/' if kind == 'home' else f'/{slug}/'
        body = '<h1>Главная</h1>' if kind == 'home' else '<p>Теория</p>' if kind == 'topic' else '<p>Каталог</p>'
        stamp = STAMP.isoformat(timespec='microseconds')
        data = {'delivery_version': 'content-delivery-v1', 'id': pk, 'slug': slug, 'page_type': kind, 'title': title,
                'grade_id': 70 if kind == 'topic' else None, 'subject_id': 101 if kind == 'topic' else None,
                'section_id': 201 if kind == 'topic' else None, 'order': 0, 'body_html': body, 'is_published': True,
                'seo': {'title': title + ' | MathStart', 'description': 'Synthetic description', 'canonical_path': path},
                'created_at': stamp, 'updated_at': stamp,
                'source': {'path': f'site_content/pages/{slug}/page.json', 'source_digest': '1' * 64,
                           'render_digest': sha256(body.encode()).hexdigest()}, 'assets': [asset]}
        deliveries[pk] = data
        (base / f'pages/{pk}.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        pages.append({'id': pk, 'slug': slug, 'page_type': kind, 'url': path, 'canonical_path': path,
                      'delivery_path': f'pages/{pk}.json', 'updated_at': stamp,
                      'sitemap_changefreq': 'weekly' if kind == 'home' else 'monthly',
                      'sitemap_priority': 1.0 if kind == 'home' else 0.7 if kind == 'topic' else 0.5})
    topic = {k: deliveries[302][k] for k in ['id', 'title', 'slug', 'order', 'grade_id', 'subject_id', 'section_id']}
    topic['url'] = '/topic/'
    index = {'version': 'public-build-index-v1', 'release_id': release_id, 'pages': pages,
             'catalogue': {'grades': [{'id': 70, 'title': '5 класс', 'slug': '5-klass', 'order': 99}],
                           'subjects': [{'id': 101, 'title': 'Математика', 'slug': 'matematika', 'order': 0, 'grade_id': 70}],
                           'sections': [{'id': 201, 'title': 'Числа', 'slug': 'chisla', 'order': 0, 'subject_id': 101}], 'topics': [topic]},
             'aliases': [{'url': '/glavnaya/', 'page_id': 301, 'status': 200, 'canonical_path': '/'}],
             'redirects': [{'old_path': '/old.html', 'new_path': '/topic/', 'is_permanent': True},
                           {'old_path': '/старое.html', 'new_path': '/topic/', 'is_permanent': False},
                           {'old_path': '/topic/', 'new_path': '/', 'is_permanent': True}],
             'system_urls': ['/sitemap.xml', '/robots.txt']}
    raw = json.dumps(index, ensure_ascii=False).encode()
    (base / 'index.json').write_bytes(raw)
    descriptor = Descriptor(uuid.uuid4(), release_id, sha256(raw).hexdigest(), 1)
    return ReleaseStore(root), descriptor, index, deliveries


def activate_fixture(engine, descriptor):
    # This is disposable fixture construction, NOT V02 production publishing.
    with engine.begin() as c:
        c.execute(sa.insert(journal).values(id=descriptor.operation_id, namespace='public', key_digest='2' * 64,
            plan_digest='3' * 64, plan={}, release_id=descriptor.release_id, manifest_digest=descriptor.manifest_digest,
            owner_id=uuid.uuid4(), fence_generation=1, lease_until=STAMP, phase='COMPLETE', db_committed=True,
            activation_status='APPLIED', created_at=STAMP, updated_at=STAMP))
        c.execute(sa.insert(gate).values(namespace='public', fence_generation=1))
        c.execute(sa.insert(active).values(namespace='public', operation_id=descriptor.operation_id,
            release_id=descriptor.release_id, manifest_digest=descriptor.manifest_digest, fence_generation=1))
