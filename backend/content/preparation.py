"""Prepare source publication, including new identities, without DB effects.

The result is an immutable build handoff and explicit full before/after patches.
It is not a publication or a claim. Proposed new PKs are checked against the
captured edition and installed only by the fenced participant's SQL commit.
Preparation and dry-run never consume sequences or register rows.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import uuid

import sqlalchemy as sa

from backend.content.build import (encoded, assets_for, verify_source_checkout, install_build_inputs,
                                   load_material_routes, source_file_record, apply_material_redirects)
from backend.content.editions import decoded, snapshot, normalized, project_updates
from backend.content.projection import (ReviewedSource, delivery_for_page, catalogue_from_snapshot, index_for_pages)
from backend.content.publication import PublicationConflict
from backend.content.releases import Descriptor
from backend.content.sources import load_sources, digest, publication_digest, SourceError
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
    """Pure proposed identities; no sequences, source rebind or runtime overwrite."""
    if not selected or len(selected) != len(set(selected)):
        raise SourceError('Explicit nonempty unique selection required')
    by_slug = {row['slug']: row for row in before['content_contentpage']}
    sources = {bundle.snapshot['slug']: bundle for bundle in bundles}
    relations = related(before)
    publications = {row['page_id']: row for row in before['content_lessonpublication']}
    source_owners = {row['source_path']: row['page_id'] for row in before['content_lessonpublication']}
    next_ids = {name: max([0, *[row['id'] for row in before[name]]]) for name in
                ('content_contentpage', 'content_lessonpublication')}
    def identifier(name):
        next_ids[name] += 1
        if next_ids[name] >= 2**63:
            raise PublicationConflict('INVALID_EDITION')
        return next_ids[name]

    def catalogue_identity(desired):
        result = {}
        for key in ('grade', 'subject', 'section'):
            slug = desired[key]
            options = [row for row in relations[key].values() if row.slug == slug] if slug is not None else []
            if key == 'subject':
                options = [row for row in options if row.grade_id == result['grade_id']]
            if key == 'section':
                options = [row for row in options if row.subject_id == result['subject_id']]
            if slug is not None and len(options) != 1:
                raise PublicationConflict('SOURCE_IDENTITY_CONFLICT')
            result[key + '_id'] = options[0].id if options else None
        return result
    changes = []
    removed = set()
    for slug in sorted(selected, key=lambda value: sources[value].path if value in sources else value):
        row, bundle = by_slug.get(slug), sources.get(slug)
        if bundle is None or row is None and unpublish:
            raise PublicationConflict('SOURCE_REGISTRATION_REQUIRED')
        desired = bundle.snapshot
        original = row
        if row is None:
            row = {'id': identifier('content_contentpage'), **{key: desired[key] for key in ('slug', 'page_type', *EDITABLE)},
                   **catalogue_identity(desired), 'created_at': instant, 'updated_at': instant}
        current = source_snapshot(row, relations)
        if any(current[key] != desired[key] for key in ('slug', 'page_type', 'grade', 'subject', 'section')):
            raise PublicationConflict('SOURCE_IDENTITY_CONFLICT')
        publication = publications.get(row['id'])
        if row['page_type'] == 'topic':
            source_path = bundle.path.removeprefix('curriculum/')
            if any(row[key + '_id'] is None for key in ('grade', 'subject', 'section')):
                raise PublicationConflict('SOURCE_IDENTITY_CONFLICT')
            if source_path in source_owners and source_owners[source_path] != row['id']:
                raise PublicationConflict('SOURCE_IDENTITY_CONFLICT')
            if publication is not None and publication['source_path'] != source_path:
                raise PublicationConflict('SOURCE_IDENTITY_CONFLICT')
            if publication is None and unpublish:
                raise PublicationConflict('SOURCE_REGISTRATION_REQUIRED')
            accepted = (publication['published_digest'], digest(desired), publication_digest(bundle, desired)) if publication else (digest(desired), publication_digest(bundle, desired))
            if digest(current) not in accepted:
                raise PublicationConflict('SOURCE_CONFLICT')
        after = {**row, **({key: desired[key] for key in EDITABLE} if not unpublish else {'is_published': False})}
        if original is None or after != row:
            from backend.content.quality import inspect_html
            if not unpublish and inspect_html(after['body_html'])['issues']:
                raise PublicationConflict('CONTENT_QUALITY_FAILED')
            after['updated_at'] = instant
            changes.append({'table': 'content_contentpage', 'before': original, 'after': after})
            if original is not None and row['is_published'] and not after['is_published']:
                removed.add('/' if row['page_type'] == 'home' else '/' + row['slug'] + '/')
                if row['page_type'] == 'home':
                    removed.add('/' + row['slug'] + '/')
        if row['page_type'] == 'topic' and publication is None:
            new = {'id': identifier('content_lessonpublication'), 'page_id': after['id'],
                   'source_path': bundle.path.removeprefix('curriculum/'),
                   'published_digest': publication_digest(bundle, source_snapshot(after, relations)), 'published_at': instant}
            changes.append({'table': 'content_lessonpublication', 'before': None, 'after': new})
            source_owners[new['source_path']] = new['page_id']
        elif publication is not None:
            desired_digest = publication_digest(bundle, source_snapshot(after, relations))
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
                    unpublish=False, dry_run=False, bootstrap=False, public_update=False, public_backup_path=None):
    import re
    if (not re.fullmatch('[A-Za-z0-9_-]{1,120}', release_id or '')
            or not re.fullmatch('[a-f0-9]{40}', source_sha or '')
            or bootstrap and public_update
            or (bool(slugs) == bool(all_lessons) if not (bootstrap or public_update) else bool(slugs) or all_lessons or unpublish)
            or public_update and not dry_run and public_backup_path is None):
        raise SourceError('Reviewed identity and exactly one nonempty selection required')
    source_root = Path(source_root).resolve()
    verify_source_checkout(source_root, source_sha)
    bundles = load_sources(source_root)
    bundle_by_slug = {b.snapshot['slug']: b for b in bundles}
    routes = load_material_routes(source_root, bundle_by_slug)
    from backend.content.public_update import SELECTED
    selected = (list(SELECTED) if public_update else [b.snapshot['slug'] for b in bundles] if bootstrap else
                [b.snapshot['slug'] for b in bundles if b.snapshot['page_type'] == 'topic'] if all_lessons else slugs)
    with UnitOfWork(engine) as uow:
        uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
        before = snapshot(uow.session)
        instant = normalized({'at': uow.session.scalar(sa.select(sa.func.clock_timestamp()))})['at']
    if public_update:
        from backend.content.public_update import public_update_changes
        changes = public_update_changes(before, bundles, source_root, instant)
    elif bootstrap:
        from backend.content.bootstrap_plan import bootstrap_changes
        changes = bootstrap_changes(before, bundles, source_root, instant)
    else:
        changes = source_changes(before, bundles, selected, instant, unpublish=unpublish)
    after = project_updates(before, changes)
    if dry_run:
        return {'selected': len(selected), 'changes': len(changes), 'effects': 'NONE', 'activation': 'NOT_PERFORMED'}
    relations, sources, files, deliveries, pages = related(after), {b.snapshot['slug']: b for b in bundles}, {}, {}, []
    publications = {row['page_id']: row for row in after['content_lessonpublication']}
    for values in after['content_contentpage']:
        if not values['is_published']:
            continue
        bundle = sources.get(values['slug'])
        if bundle is None or source_snapshot(values, relations) != bundle.snapshot:
            raise PublicationConflict('SOURCE_CONFLICT')
        if bundle.renderer_version == 'react-v1':
            publication = publications.get(values['id'])
            if (publication is None or publication['source_path'] != bundle.path.removeprefix('curriculum/')
                    or publication['published_digest'] != publication_digest(bundle, bundle.snapshot)):
                raise PublicationConflict('SOURCE_CONFLICT')
        page = SimpleNamespace(**decoded(metadata.tables['content_contentpage'], values))
        for key in ('grade', 'subject', 'section'):
            setattr(page, key, relations[key].get(values[key + '_id']))
        assets = assets_for(source_root, bundle)
        for asset, raw in assets:
            if files.setdefault(asset['storage_key'], raw) != raw:
                raise PublicationConflict('ARTIFACT_CONFLICT')
        route = routes.get(values['slug'])
        reviewed = ReviewedSource(bundle.path, bundle.source_digest, tuple(a for a, _ in assets),
            bundle.renderer_version, bundle.lesson_document,
            route['path'] if route and route['renderer_version'] == 'react-v1' else None)
        deliveries[page.id] = delivery_for_page(page, reviewed)
        pages.append(page)
    # The VALUES projections query only captured rows using the database's real
    # collation and exact baseline ordering; they never observe a newer edition.
    with UnitOfWork(engine) as uow:
        uow.session.execute(sa.text('SET TRANSACTION READ ONLY'))
        catalogue = catalogue_from_snapshot(uow.session, after)
        page_by_slug = {item['slug']: item for item in deliveries.values()}
        for topic in catalogue['topics']:
            delivery = page_by_slug.get(topic['slug'])
            if delivery is None:
                raise PublicationConflict('SOURCE_CONFLICT')
            topic['url'] = delivery['seo']['canonical_path']
        redirects = after['content_redirect']
        if redirects:
            columns = [sa.column(key, metadata.tables['content_redirect'].c[key].type) for key in
                       ('old_path', 'new_path', 'is_permanent', 'is_active')]
            values = sa.values(*columns).data([tuple(row[c.name] for c in columns) for row in redirects]).cte('prepared_redirects')
            redirects = [SimpleNamespace(**row) for row in uow.session.execute(
                sa.select(values).where(values.c.is_active.is_(True)).order_by(values.c.old_path)).mappings()]
    index = index_for_pages(sorted(pages, key=lambda p: p.id), release_id, deliveries, catalogue, redirects)
    try:
        apply_material_redirects(index, routes)
    except SourceError as exc:
        raise PublicationConflict('ARTIFACT_CONFLICT') from exc
    from backend.infrastructure.http.contracts import validate
    index = validate(index, 'PublicBuildIndex', True)
    files.update({f'pages/{pk}.json': encoded(page) for pk, page in deliveries.items()})
    files['index.json'] = encoded(index)
    manifest_digest = sha256(files['index.json']).hexdigest()
    receipt = {'version': 'build-input-receipt-v1', 'source_sha': source_sha, 'release_id': release_id,
               'manifest_digest': manifest_digest, 'pages': len(deliveries), 'topics': len(catalogue['topics']),
               'assets': len(files) - len(deliveries) - 1, 'activation': 'NOT_PERFORMED',
               'files': [{'path': key, 'sha256': sha256(raw).hexdigest(), 'size': len(raw)} for key, raw in sorted(files.items())],
               'source_files': [entry for bundle in bundles for entry in bundle.files]
                               + [source_file_record(source_root, 'site_content/material-routes.json')]}
    descriptor = Descriptor(uuid.UUID(int=0), release_id, manifest_digest, 1)
    if public_update:
        from backend.content.public_update import backup_public_records
        backup_public_records(before, Path(public_backup_path), source_sha, digest(before))
    install_build_inputs(output_root, release_id, descriptor, receipt, files)
    return {'selected': len(selected), 'changes': changes, 'before_digest': digest(before), 'after_digest': digest(after),
            'release_id': release_id, 'manifest_digest': manifest_digest,
            'input_receipt_digest': sha256(encoded(receipt)).hexdigest(), 'activation': 'NOT_PERFORMED',
            'effects': 'immutable build handoff and selected public backup only; no DB rows or sequences changed' if public_update else 'immutable build handoff only; no DB rows or sequences changed',
            **({'backup': str(public_backup_path)} if public_update else {})}
