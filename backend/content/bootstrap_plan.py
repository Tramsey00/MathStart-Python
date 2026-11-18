"""Pure full-site bootstrap edition; preserve runtime edits and all old rows."""
from hashlib import sha256
from pathlib import Path
from urllib.parse import unquote

from backend.content.editions import decoded, normalized, project_updates
from backend.content.sources import SourceError, file_inside, read_json
from backend.content.publication import PublicationConflict
from backend.models.baseline import GRADE_EPOCH, metadata


def reviewed_previous_page(current, bundle, prior_files):
    """Allow presentation changes only from the verified published source bytes."""
    location = Path(bundle.path)
    previous = {Path(item['path']).name: item['sha256']
                for item in (prior_files or {}).get(location.parent.as_posix(), ())}
    fields = {'body_html': 'body.html', 'page_css': 'page.css', 'page_js': 'page.js'}
    return (location.name in previous
            and all(current[key] == bundle.snapshot[key] for key in current.keys() - fields.keys())
            and all(sha256(current[key].encode()).hexdigest() == previous[name] if name in previous
                    else current[key] == '' for key, name in fields.items()))


def retire_redirects(rows, retirement, changes):
    """Deactivate known public paths and chains to them without losing rows."""
    from backend.content.build import retired_public_path
    pending = [row for row in rows if row['is_active']]
    removed = set(retirement.paths)
    while pending:
        matches = [row for row in pending if any(retired_public_path(row[key], removed)
                                                for key in ('old_path', 'new_path'))]
        if not matches:
            return
        for row in matches:
            changes.append({'table': 'content_redirect', 'before': row, 'after': {**row, 'is_active': False}})
            path = unquote(row['old_path'])
            if path not in retirement.canonical:
                removed.add(path)
            pending.remove(row)


def bootstrap_changes(before, bundles, root, instant, *, retirement=None, previous_sources=None):
    from backend.content.preparation import source_changes, related, source_snapshot
    catalogue = read_json(root / 'site_content/catalog.json')
    if set(catalogue) != {'schema_version', 'grades', 'subjects', 'sections'} or catalogue['schema_version'] != 1:
        raise SourceError('Invalid bootstrap catalogue')
    changes, grades, subjects, sections = [], {}, {}, {}
    counters = {name: max([0, *[row['id'] for row in rows]]) for name, rows in before.items()}
    def identifier(name):
        counters[name] += 1
        if counters[name] >= 2**63:
            raise PublicationConflict('INVALID_EDITION')
        return counters[name]
    def insert(name, values):
        new = normalized(decoded(metadata.tables[name], normalized({'id': identifier(name), **values})))
        changes.append({'table': name, 'before': None, 'after': new})
        return new
    for key, name, mapping in [('grades', 'content_grade', grades), ('subjects', 'content_subject', subjects),
                               ('sections', 'content_section', sections)]:
        for item in catalogue[key]:
            values = {field: value for field, value in item.items() if field not in {'grade', 'subject'}}
            identity = (item['slug'],)
            if key == 'subjects':
                values['grade_id'] = grades[(item['grade'],)]['id']
                identity = (item['grade'], item['slug'])
            elif key == 'sections':
                values['subject_id'] = subjects[(item['grade'], item['subject'])]['id']
                identity = (item['grade'], item['subject'], item['slug'])
            if identity in mapping:
                raise SourceError('Duplicate bootstrap catalogue identity')
            matches = [row for row in before[name] if row['slug'] == item['slug'] and all(
                row[field] == values[field] for field in ('grade_id', 'subject_id') if field in values)]
            if len(matches) > 1:
                raise PublicationConflict('SOURCE_IDENTITY_CONFLICT')
            if matches:
                row = matches[0]
                if any(row.get(field) != value for field, value in values.items()):
                    raise PublicationConflict('SOURCE_CONFLICT')
            else:
                if key == 'grades':
                    values['created_at'] = GRADE_EPOCH
                row = insert(name, values)
            mapping[identity] = row
    state = project_updates(before, changes)
    sources = {bundle.snapshot['slug']: bundle for bundle in bundles}
    relations = related(state)
    # No last-published digest exists for public static/catalogue documents.
    # Bootstrap refuses a runtime edit instead of treating it as an update.
    for page in state['content_contentpage']:
        bundle = sources.get(page['slug'])
        if bundle is None or page['page_type'] == 'topic':
            continue
        current = source_snapshot(page, relations)
        if current != bundle.snapshot and not (
                previous_sources is not None and reviewed_previous_page(current, bundle, previous_sources.files)):
            raise PublicationConflict('SOURCE_CONFLICT')
    pages = source_changes(state, bundles, list(sources), instant, previous_sources=previous_sources)
    changes.extend(pages)
    state = project_updates(state, pages)
    # Retire presentation with the same PKs, content and references. An
    # absent source on its own is never permission to retire a database row.
    retired_pages = retirement.pages if retirement is not None else {'materialy', 'pamyatki'}
    for page in state['content_contentpage']:
        if page['slug'] not in retired_pages or not page['is_published']:
            continue
        if page['page_type'] not in {'grade', 'subject', 'static'} or page['slug'] in sources:
            raise PublicationConflict('SOURCE_IDENTITY_CONFLICT')
        changes.append({'table': 'content_contentpage', 'before': page, 'after': {**page, 'is_published': False}})
    if retirement is not None:
        retire_redirects(before['content_redirect'], retirement, changes)
    page_ids = {page['slug']: page['id'] for page in state['content_contentpage']}
    media = read_json(root / 'site_content/media.json')
    if set(media) != {'schema_version', 'assets'} or media['schema_version'] != 1:
        raise SourceError('Invalid bootstrap media manifest')
    media_files = set()
    for item in media['assets']:
        if set(item) != {'title', 'file', 'alt_text', 'related_page', 'sha256'} or item['file'] in media_files:
            raise SourceError('Invalid/duplicate bootstrap media identity')
        media_files.add(item['file'])
        raw = file_inside(root, 'site_content/media/' + item['file']).read_bytes()
        if sha256(raw).hexdigest() != item['sha256']:
            raise SourceError('Bootstrap seed media hash mismatch')
        if item['related_page'] and item['related_page'] not in page_ids:
            raise SourceError('Bootstrap media page is absent')
        values = {key: item[key] for key in ('title', 'file', 'alt_text')}
        values['related_page_id'] = page_ids.get(item['related_page'])
        matches = [row for row in before['content_mediaasset'] if row['file'] == item['file']]
        if len(matches) > 1:
            raise PublicationConflict('SOURCE_IDENTITY_CONFLICT')
        if matches:
            if any(matches[0][key] != value for key, value in values.items()):
                raise PublicationConflict('SOURCE_CONFLICT')
        else:
            insert('content_mediaasset', {**values, 'created_at': instant})
    redirects = read_json(root / 'site_content/redirects.json')
    if set(redirects) != {'schema_version', 'redirects'} or redirects['schema_version'] != 1:
        raise SourceError('Invalid bootstrap redirects')
    # Explicit material aliases belong to the prepared DB edition too. An alias
    # existing only in the input index cannot pass the publisher's independent
    # reconstruction from DB rows and immutable page deliveries.
    from backend.content.build import load_material_routes
    routes = load_material_routes(root, sources)
    material_aliases = [] if retirement is not None else [{'old_path': alias, 'new_path': route['path'],
                         'is_permanent': True, 'is_active': True}
                        for route in routes.values() if route['renderer_version'] == 'react-v1'
                        for alias in route.get('aliases', [])]
    paths = set()
    for values in [*redirects['redirects'], *material_aliases]:
        if set(values) != {'old_path', 'new_path', 'is_permanent', 'is_active'} or values['old_path'] in paths:
            raise SourceError('Invalid/duplicate bootstrap redirect identity')
        paths.add(values['old_path'])
        matches = [row for row in before['content_redirect'] if row['old_path'] == values['old_path']]
        if len(matches) > 1:
            raise PublicationConflict('SOURCE_IDENTITY_CONFLICT')
        if matches:
            if any(matches[0][key] != value for key, value in values.items()):
                raise PublicationConflict('SOURCE_CONFLICT')
        else:
            insert('content_redirect', values)
    # Reject malformed fields before any build/filesystem or SQL effects.
    project_updates(before, changes)
    return changes
