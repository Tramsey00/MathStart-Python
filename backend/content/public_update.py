"""Prepared equivalent of the installed site's scoped public-page update.

Only the four information pages, the installed power lesson, two retirement
flags, four redirects and one PDF metadata record are selected. Full immutable
build inputs still describe a consistent public edition.
"""
from hashlib import sha256

from backend.content.build import encoded
from backend.content.editions import decoded, normalized, project_updates
from backend.content.publication import PublicationConflict
from backend.content.sources import SourceError, file_inside, read_json
from backend.models.baseline import metadata

PUBLIC_PAGES = ('glavnaya', 'karta-sajta', 'o-proekte', 'kontakty')
RETIRED = ('materialy', 'pamyatki')
POWER_LESSON = 'bazovye-svojstva-stepenej-s-naturalnym-pokazatelem'
POWER_PDF = 'uploads/2026/07/pamyatka-stepeni.pdf'
RETIRED_PATHS = ('/materialy/', '/mathstart/materialy/', '/pamyatki/', '/mathstart/pamyatki/')
SELECTED = (*PUBLIC_PAGES, POWER_LESSON)


def public_update_changes(before, bundles, root, instant):
    from backend.content.preparation import source_changes
    sources = {bundle.snapshot['slug']: bundle for bundle in bundles}
    if any(slug not in sources for slug in SELECTED) or any(
            sources[slug].snapshot[key] is not None for slug in PUBLIC_PAGES for key in ('grade', 'subject', 'section')):
        raise SourceError('Incomplete or incompatible scoped public source')
    if not any(row['slug'] == POWER_LESSON and row['page_type'] == 'topic'
               for row in before['content_contentpage']):
        raise PublicationConflict('SOURCE_REGISTRATION_REQUIRED')
    # The lesson conflict guard runs before backups, media copies or handoffs.
    changes = source_changes(before, bundles, SELECTED, instant)
    state = project_updates(before, changes)
    for row in state['content_contentpage']:
        if row['slug'] in RETIRED and row['page_type'] == 'static' and row['is_published']:
            changes.append({'table': 'content_contentpage', 'before': row, 'after': {**row, 'is_published': False}})

    counters = {name: max([0, *[row['id'] for row in rows]]) for name, rows in before.items()}

    def upsert(name, matches, values):
        if len(matches) > 1:
            raise PublicationConflict('SOURCE_IDENTITY_CONFLICT')
        old = matches[0] if matches else None
        if old:
            after = {**old, **values}
        else:
            counters[name] += 1
            after = {'id': counters[name], **values}
            if name == 'content_mediaasset':
                after['created_at'] = instant
        after = normalized(decoded(metadata.tables[name], after))
        if old != after:
            changes.append({'table': name, 'before': old, 'after': after})

    media = read_json(root / 'site_content/media.json')
    if set(media) != {'schema_version', 'assets'} or media['schema_version'] != 1:
        raise SourceError('Invalid public media manifest')
    selected = [item for item in media['assets'] if item.get('file') == POWER_PDF]
    if len(selected) != 1 or set(selected[0]) != {'title', 'file', 'alt_text', 'related_page', 'sha256'}:
        raise SourceError('Exactly one reviewed public PDF required')
    item = selected[0]
    if sha256(file_inside(root, 'site_content/media/' + POWER_PDF).read_bytes()).hexdigest() != item['sha256']:
        raise SourceError('Public PDF hash mismatch')
    pages = {row['slug']: row['id'] for row in state['content_contentpage']}
    if item['related_page'] not in pages:
        raise SourceError('Public PDF page is absent')
    upsert('content_mediaasset', [row for row in before['content_mediaasset'] if row['file'] == POWER_PDF],
           {**{key: item[key] for key in ('title', 'file', 'alt_text')}, 'related_page_id': pages[item['related_page']]})
    manifest = read_json(root / 'site_content/redirects.json')
    if set(manifest) != {'schema_version', 'redirects'} or manifest['schema_version'] != 1:
        raise SourceError('Invalid public redirect manifest')
    redirects = [row for row in manifest['redirects'] if row.get('old_path') in RETIRED_PATHS]
    if len(redirects) != 4 or {row['old_path'] for row in redirects} != set(RETIRED_PATHS):
        raise SourceError('Exactly four reviewed public redirects required')
    for values in redirects:
        if set(values) != {'old_path', 'new_path', 'is_permanent', 'is_active'}:
            raise SourceError('Invalid public redirect')
        upsert('content_redirect', [row for row in before['content_redirect'] if row['old_path'] == values['old_path']], values)
    project_updates(before, changes)
    return changes


def backup_public_records(before, path, source_sha, before_digest):
    ids = {row['id'] for row in before['content_contentpage'] if row['slug'] == POWER_LESSON}
    selected = {
        'content_contentpage': [row for row in before['content_contentpage'] if row['slug'] in (*SELECTED, *RETIRED)],
        'content_lessonpublication': [row for row in before['content_lessonpublication'] if row['page_id'] in ids],
        'content_mediaasset': [row for row in before['content_mediaasset'] if row['file'] == POWER_PDF],
        'content_redirect': [row for row in before['content_redirect'] if row['old_path'] in RETIRED_PATHS],
    }
    with path.open('xb') as stream:
        stream.write(encoded({'version': 'public-records-before-update-v1', 'source_sha': source_sha,
                              'before_digest': before_digest, 'records': selected}))
