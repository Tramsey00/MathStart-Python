"""Sanitized R01 schema/aggregate facts in one verified read-only snapshot.

No credentials, hashes, sessions, receipt payloads or identity rows are exported.
Always rolls back; never runs migrate/bootstrap/publish/stamp.
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--original', type=Path, required=True)
    args = p.parse_args()
    root = Path(__file__).resolve().parents[4]
    out = root / 'docs/acceptance/MS7-MIG-R01'
    sys.path.insert(0, str(root))
    from dotenv import load_dotenv
    load_dotenv(args.original / '.env', override=False)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()
    from django.db import connection
    from django.contrib import admin
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Permission
    from django.test import RequestFactory
    from content.models import ContentPage, LessonPublication
    from content.services.lesson_sources import load_bundles, source_root, digest, page_snapshot
    assert connection.vendor == 'postgresql', 'R01 working DB requires PostgreSQL'
    manifest = {'source_commit': '8c11edadc8debc81432d1db1145feac504f09061', 'privacy': 'schema and aggregate facts only; no identity values or secrets', 'transaction': {}}
    def query(cursor, sql, params=None):
        cursor.execute(sql, params)
        names = [x.name for x in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]
    with connection.cursor() as cursor:
        cursor.execute('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY')
        try:
            cursor.execute('SHOW transaction_read_only')
            readonly = cursor.fetchone()[0]
            cursor.execute('SHOW transaction_isolation')
            isolation = cursor.fetchone()[0]
            assert readonly == 'on' and isolation == 'repeatable read'
            manifest['transaction'].update(begin='BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY', transaction_read_only=readonly, transaction_isolation=isolation)
            manifest['version'] = query(cursor, 'SELECT version() AS version, current_setting(\'server_version_num\') AS server_version_num')
            manifest['columns'] = query(cursor, "SELECT table_name,column_name,data_type,udt_name,is_nullable,column_default,character_maximum_length,datetime_precision FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,ordinal_position")
            manifest['constraints'] = query(cursor, "SELECT c.relname AS table_name,k.conname AS name,k.contype AS type,pg_get_constraintdef(k.oid) AS definition FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' ORDER BY c.relname,k.conname")
            manifest['indexes'] = query(cursor, "SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname='public' ORDER BY tablename,indexname")
            manifest['sequences'] = query(cursor, "SELECT sequence_name,data_type,start_value,minimum_value,maximum_value,increment,cycle_option FROM information_schema.sequences WHERE sequence_schema='public' ORDER BY sequence_name")
            manifest['migrations'] = query(cursor, 'SELECT app,name FROM django_migrations ORDER BY app,name')
            tables = query(cursor, "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name")
            manifest['table_counts'] = {}
            for row in tables:
                cursor.execute('SELECT count(*) FROM ' + connection.ops.quote_name(row['table_name']))
                manifest['table_counts'][row['table_name']] = cursor.fetchone()[0]
            manifest['page_aggregates'] = query(cursor, 'SELECT page_type,is_published,count(*) AS count FROM content_contentpage GROUP BY page_type,is_published ORDER BY page_type,is_published')
            manifest['grade_timestamp_aggregates'] = query(cursor, 'SELECT min(created_at) AS minimum,max(created_at) AS maximum,count(*) AS count FROM content_grade')
            manifest['password_algorithms_only'] = query(cursor, "SELECT CASE WHEN password LIKE '!%' THEN 'unusable' ELSE split_part(password,'$',1) END AS algorithm,count(*) AS count FROM auth_user GROUP BY 1 ORDER BY 1")
            manifest['role_aggregates'] = query(cursor, 'SELECT is_active,is_staff,is_superuser,count(*) AS count FROM auth_user GROUP BY is_active,is_staff,is_superuser ORDER BY 1,2,3')
            manifest['permission_catalogue'] = query(cursor, 'SELECT ct.app_label,ct.model,p.codename FROM auth_permission p JOIN django_content_type ct ON ct.id=p.content_type_id ORDER BY ct.app_label,ct.model,p.codename')
            bundles = {b.slug: b for b in load_bundles(source_root(), all_lessons=True)}
            from content.services.site_bootstrap import load_site_source
            site_rows = {x['page']['slug']: x for x in load_site_source()['pages']}
            original_site_rows = {x['page']['slug']: x for x in load_site_source(args.original / 'site_content')['pages']}
            state = dict(LessonPublication.objects.values_list('page_id', 'published_digest'))
            rendered = []
            for page in ContentPage.objects.select_related('grade', 'subject', 'section').order_by('slug'):
                row = {'slug': page.slug, 'url': page.get_absolute_url(), 'page_type': page.page_type, 'published': page.is_published, 'runtime_snapshot_digest': digest(page_snapshot(page)), 'publication_digest': state.get(page.pk), 'runtime_payload_sha256': {f: hashlib.sha256(getattr(page, f).encode('utf-8')).hexdigest() for f in ['body_html','page_css','page_js']}}
                b = bundles.get(page.slug)
                if b:
                    row.update(source_path='curriculum/' + b.relative_path, renderer_format=b.metadata['format'], desired_rendered_snapshot_digest=digest(b.snapshot), runtime_matches_rendered_source=digest(page_snapshot(page)) == digest(b.snapshot), publication_matches_source=state.get(page.pk) == digest(b.snapshot))
                elif page.slug in site_rows:
                    source = site_rows[page.slug]
                    desired = {**source['page'], **{f: source[f] for f in ['body_html', 'page_css', 'page_js']}}
                    row.update(source_path='site_content/pages/' + page.slug + '/page.json', desired_rendered_snapshot_digest=digest(desired), runtime_matches_rendered_source=digest(page_snapshot(page)) == digest(desired))
                    current = page_snapshot(page)
                    row['mismatch_fields'] = [f for f in current if current[f] != desired[f]]
                    normalize = lambda value: value.replace('\r\n', '\n') if isinstance(value, str) else value
                    row['runtime_matches_after_lf_normalization'] = all(normalize(current[f]) == normalize(desired[f]) for f in current)
                    old = original_site_rows[page.slug]
                    row['runtime_matches_original_checkout_source'] = digest(current) == digest({**old['page'], **{f: old[f] for f in ['body_html', 'page_css', 'page_js']}})
                rendered.append(row)
            manifest['content_source_consistency'] = {'topic_rows': sum(x['page_type']=='topic' for x in rendered), 'mapped_sources': sum('source_path' in x for x in rendered), 'runtime_mismatches': [x['slug'] for x in rendered if x.get('runtime_matches_rendered_source') is False], 'publication_mismatches': [x['slug'] for x in rendered if x.get('publication_matches_source') is False]}
            manifest['retained_unpublished_content'] = [{'slug': x['slug'], 'type': x['page_type']} for x in rendered if not x['published']]
        finally:
            cursor.execute('ROLLBACK')
            manifest['transaction']['end'] = 'ROLLBACK'
    connection.close()
    (out / 'runtime-data-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2, default=str) + '\n', encoding='utf-8')
    (out / 'rendered-runtime-digests.json').write_text(json.dumps({'semantics': 'Django renderer snapshot digests; separate from exact authored Git blob hashes; read-only working DB comparison', 'source_commit': manifest['source_commit'], 'pages': rendered}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # Registered admin behavior is inspected with an unsaved synthetic superuser.
    # No staff mutation or actual identity is used for the audit.
    req = RequestFactory().get('/admin/')
    req.user = get_user_model()(is_staff=True, is_active=True, is_superuser=True)
    registry = []
    for model, ma in sorted(admin.site._registry.items(), key=lambda x: x[0]._meta.label):
        row = {'model': model._meta.label, 'admin_class': type(ma).__module__ + '.' + type(ma).__name__, 'permissions': {k: getattr(ma, 'has_' + k + '_permission')(req) for k in ['view','add','change','delete']}, 'actions': list(ma.get_actions(req)), 'list_display': list(ma.get_list_display(req)), 'list_filter': list(ma.get_list_filter(req)), 'search_fields': list(ma.get_search_fields(req)), 'readonly_fields': list(ma.get_readonly_fields(req)), 'add_fieldsets': ma.get_fieldsets(req), 'change_fieldsets': ma.get_fieldsets(req, model()), 'admin_urls': [str(x.pattern) for x in ma.get_urls()], 'required_permission_codenames': [f'{model._meta.app_label}.{x}_{model._meta.model_name}' for x in ['view','add','change','delete']]}
        registry.append(row)
    (out / 'admin-inventory.json').write_text(json.dumps({'registered': registry, 'permission_model_registered': Permission in admin.site._registry, 'inspection': 'unsaved synthetic superuser; metadata only, no DB mutation; actual server permissions also require is_active/is_staff; content changes disabled even for superuser'}, ensure_ascii=False, indent=2, default=str) + '\n', encoding='utf-8')
    print(json.dumps({'readonly': manifest['transaction'], 'counts': manifest['table_counts'], 'consistency': manifest['content_source_consistency'], 'registered_admin_models': [x['model'] for x in registry]}, ensure_ascii=False))

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('R01 read-only audit failed: ' + type(exc).__name__ + ' (raw details suppressed)')
        raise SystemExit(1) from None
