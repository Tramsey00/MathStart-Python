"""Prepare existing source updates without changing DB rows or sequences.

The result is an immutable build handoff and explicit full before/after patches.
It is not a publication or a claim. Source registration/new IDs and bootstrap
remain separate operations and are refused rather than allocated in a dry-run.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import uuid

import sqlalchemy as sa

from backend.content.build import encoded, assets_for, verify_source_checkout, install_build_inputs
from backend.content.editions import decoded, snapshot, normalized, project_updates
from backend.content.projection import (ReviewedSource, delivery_for_page, catalogue_from_snapshot, index_for_pages)
from backend.content.publication import PublicationConflict
from backend.content.releases import Descriptor
from backend.content.sources import load_sources, digest, SourceError
from backend.infrastructure.uow import UnitOfWork
from backend.models.baseline import metadata

EDITABLE = ('title', 'order', 'seo_title', 'seo_description', 'body_html', 'page_css', 'page_js', 'is_published')


def related(state):
    result = {}
    for key in ('grade', 'subject', 'section'):
        result[key] = {row['id']: SimpleNamespace(**row) for row in state['content_' + key]}
    return result


def source_snapshot(row, relations):
    subject = relations['subject'].get(row['subject_id'])
    section = relations['section'].get(row['section_id'])
    if (subject is not None and subject.grade_id != row['grade_id']
            or section is not None and section.subject_id != row['subject_id']):
        raise PublicationConflict('SOURCE_IDENTITY_CONFLICT')
    data = {key: row[key] for key in (*EDITABLE, 'slug', 'page_type')}
    for key in ('grade', 'subject', 'section'):
        data[key] = relations[key][row[key + '_id']].slug if row[key + '_id'] is not None else None
    return data


def source_changes(before, bundles, selected, instant, *, unpublish=False):
    """No ID allocation, timestamp rewrite, source rebind or runtime overwrite."""
    if not selected or len(selected) != len(set(selected)):
        raise SourceError('Explicit nonempty unique selection required')
    by_slug = {row['slug']: row for row in before['content_contentpage']}
    sources = {bundle.snapshot['slug']: bundle for bundle in bundles}
    relations = related(before)
    publications = {row['page_id']: row for row in before['content_lessonpublication']}
    changes = []
    removed = set()
    for slug in selected:
        row, bundle = by_slug.get(slug), sources.get(slug)
        if row is None or bundle is None:
            raise PublicationConflict('SOURCE_REGISTRATION_REQUIRED')
        current = source_snapshot(row, relations)
        desired = bundle.snapshot
        if any(current[key] != desired[key] for key in ('slug', 'page_type', 'grade', 'subject', 'section')):
            raise PublicationConflict('SOURCE_IDENTITY_CONFLICT')
        publication = publications.get(row['id'])
        if row['page_type'] == 'topic':
            if publication is None:
                raise PublicationConflict('SOURCE_REGISTRATION_REQUIRED')
            if publication['source_path'] != bundle.path.removeprefix('curriculum/'):
                raise PublicationConflict('SOURCE_IDENTITY_CONFLICT')
            if digest(current) != publication['published_digest']:
                raise PublicationConflict('SOURCE_CONFLICT')
        after = {**row, **({key: desired[key] for key in EDITABLE} if not unpublish else {'is_published': False})}
        if after != row:
            from content.quality import inspect_html
            if not unpublish and inspect_html(after['body_html'])['issues']:
                raise PublicationConflict('CONTENT_QUALITY_FAILED')
            after['updated_at'] = instant
            changes.append({'table': 'content_contentpage', 'before': row, 'after': after})
            if row['is_published'] and not after['is_published']:
                removed.add('/' if row['page_type'] == 'home' else '/' + row['slug'] + '/')
                if row['page_type'] == 'home':
                    removed.add('/' + row['slug'] + '/')
        if publication is not None:
            desired_digest = digest(source_snapshot(after, relations))
            if publication['published_digest'] != desired_digest:
                changes.append({'table': 'content_lessonpublication', 'before': publication,
                    'after': {**publication, 'published_digest': desired_digest, 'published_at': instant}})
    # Retain redirect rows/history, but do not publish chains ending at a newly
    # removed document. A still-published page keeps precedence over a redirect.
    active_paths = {'/' if row['page_type'] == 'home' else '/' + row['slug'] + '/'
                    for row in before['content_contentpage'] if row['is_published']} - removed
    active_paths |= {'/' + row['slug'] + '/' for row in before['content_contentpage']
                     if row['is_published'] and row['page_type'] == 'home'} - removed
    redirects = list(before['content_redirect'])
    while True:
        retired = [row for row in redirects if row['is_active'] and row['new_path'] in removed]
        if not retired:
            break
        for row in retired:
            changes.append({'table': 'content_redirect', 'before': row, 'after': {**row, 'is_active': False}})
            if row['old_path'] not in active_paths:
                removed.add(row['old_path'])
            redirects.remove(row)
    return changes


def prepare_sources(engine, source_root, output_root, release_id, source_sha, *, slugs=None, all_lessons=False,
                    unpublish=False, dry_run=False):
    import re
    if (not re.fullmatch('[A-Za-z0-9_-]{1,120}', release_id or '')
            or not re.fullmatch('[a-f0-9]{40}', source_sha or '') or bool(slugs) == bool(all_lessons)):
        raise SourceError('Reviewed identity and exactly one nonempty selection required')
    source_root = Path(source_root).resolve()
    verify_source_checkout(source_root, source_sha)
    bundles = load_sources(source_root)
    selected = [b.snapshot['slug'] for b in bundles if b.snapshot['page_type'] == 'topic'] if all_lessons else slugs
    with UnitOfWork(engine) as uow:
        uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
        before = snapshot(uow.session)
        instant = normalized({'at': uow.session.scalar(sa.select(sa.func.clock_timestamp()))})['at']
    changes = source_changes(before, bundles, selected, instant, unpublish=unpublish)
    after = project_updates(before, changes)
    if dry_run:
        return {'selected': len(selected), 'changes': len(changes), 'effects': 'NONE', 'activation': 'NOT_PERFORMED'}
    relations, sources, files, deliveries, pages = related(after), {b.snapshot['slug']: b for b in bundles}, {}, {}, []
    for values in after['content_contentpage']:
        if not values['is_published']:
            continue
        bundle = sources.get(values['slug'])
        if bundle is None or source_snapshot(values, relations) != bundle.snapshot:
            raise PublicationConflict('SOURCE_CONFLICT')
        page = SimpleNamespace(**decoded(metadata.tables['content_contentpage'], values))
        for key in ('grade', 'subject', 'section'):
            setattr(page, key, relations[key].get(values[key + '_id']))
        assets = assets_for(source_root, bundle)
        for asset, raw in assets:
            if files.setdefault(asset['storage_key'], raw) != raw:
                raise PublicationConflict('ARTIFACT_CONFLICT')
        reviewed = ReviewedSource(bundle.path, bundle.source_digest, tuple(a for a, _ in assets))
        deliveries[page.id] = delivery_for_page(page, reviewed)
        pages.append(page)
    # The VALUES projections query only captured rows using the database's real
    # collation and exact baseline ordering; they never observe a newer edition.
    with UnitOfWork(engine) as uow:
        uow.session.execute(sa.text('SET TRANSACTION READ ONLY'))
        catalogue = catalogue_from_snapshot(uow.session, after)
        redirects = after['content_redirect']
        if redirects:
            columns = [sa.column(key, metadata.tables['content_redirect'].c[key].type) for key in
                       ('old_path', 'new_path', 'is_permanent', 'is_active')]
            values = sa.values(*columns).data([tuple(row[c.name] for c in columns) for row in redirects]).cte('prepared_redirects')
            redirects = [SimpleNamespace(**row) for row in uow.session.execute(
                sa.select(values).where(values.c.is_active.is_(True)).order_by(values.c.old_path)).mappings()]
    index = index_for_pages(sorted(pages, key=lambda p: p.id), release_id, deliveries, catalogue, redirects)
    files.update({f'pages/{pk}.json': encoded(page) for pk, page in deliveries.items()})
    files['index.json'] = encoded(index)
    manifest_digest = sha256(files['index.json']).hexdigest()
    receipt = {'version': 'build-input-receipt-v1', 'source_sha': source_sha, 'release_id': release_id,
               'manifest_digest': manifest_digest, 'pages': len(deliveries), 'topics': len(catalogue['topics']),
               'assets': len(files) - len(deliveries) - 1, 'activation': 'NOT_PERFORMED',
               'files': [{'path': key, 'sha256': sha256(raw).hexdigest(), 'size': len(raw)} for key, raw in sorted(files.items())],
               'source_files': [entry for bundle in bundles for entry in bundle.files]}
    descriptor = Descriptor(uuid.UUID(int=0), release_id, manifest_digest, 1)
    install_build_inputs(output_root, release_id, descriptor, receipt, files)
    return {'selected': len(selected), 'changes': changes, 'before_digest': digest(before), 'after_digest': digest(after),
            'release_id': release_id, 'manifest_digest': manifest_digest,
            'input_receipt_digest': sha256(encoded(receipt)).hexdigest(), 'activation': 'NOT_PERFORMED',
            'effects': 'immutable build handoff only; no DB rows or sequences changed'}
