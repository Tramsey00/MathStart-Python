"""Source preparation on explicitly disposable target databases.

This slice seeds empty catalogues without replacing runtime edits. Publication
activation is deliberately separate and requires the durable publisher gate.
"""
from datetime import datetime, timezone
import sqlalchemy as sa

from backend.models.baseline import Grade, Subject, Section, ContentPage, LessonPublication, Redirect, GRADE_EPOCH
from backend.content.sources import SourceError, digest, load_sources, read_json


def bootstrap_sources(session, root):
    bundles = load_sources(root)
    catalog = read_json(root / 'site_content/catalog.json')
    if set(catalog) != {'schema_version', 'grades', 'subjects', 'sections'} or catalog['schema_version'] != 1:
        raise SourceError('Invalid catalogue')
    grades, subjects, sections = {}, {}, {}
    for name, model, target, identity in [('grades', Grade, grades, ['slug']),
            ('subjects', Subject, subjects, ['grade', 'slug']),
            ('sections', Section, sections, ['grade', 'subject', 'slug'])]:
        for item in catalog[name]:
            key = tuple(item[k] for k in identity)
            if key in target:
                raise SourceError('Duplicate catalogue identity')
            values = {k: v for k, v in item.items() if k not in {'grade', 'subject'}}
            if model is Subject:
                values['grade_id'] = grades[(item['grade'],)].id
            if model is Section:
                values['subject_id'] = subjects[(item['grade'], item['subject'])].id
            where = [model.slug == item['slug']]
            if model is Subject:
                where.append(model.grade_id == values['grade_id'])
            if model is Section:
                where.append(model.subject_id == values['subject_id'])
            row = session.scalar(sa.select(model).where(*where))
            if row is None:
                if model is Grade:
                    values['created_at'] = GRADE_EPOCH
                row = model(**values)
                session.add(row)
                session.flush()
            elif any(getattr(row, k) != value for k, value in values.items()):
                raise SourceError('Catalogue conflict: runtime edit retained')
            target[key] = row
    for bundle in bundles:
        data = bundle.snapshot
        values = {k: v for k, v in data.items() if k not in {'grade', 'subject', 'section'}}
        values['grade_id'] = grades[(data['grade'],)].id if data['grade'] else None
        values['subject_id'] = subjects[(data['grade'], data['subject'])].id if data['subject'] else None
        values['section_id'] = sections[(data['grade'], data['subject'], data['section'])].id if data['section'] else None
        row = session.scalar(sa.select(ContentPage).where(ContentPage.slug == data['slug']))
        if row is None:
            row = ContentPage(**values)
            session.add(row)
            session.flush()
        elif any(getattr(row, k) != value for k, value in values.items()):
            raise SourceError('Page conflict: runtime edit retained')
        if data['page_type'] == 'topic':
            source = bundle.path.removeprefix('curriculum/')
            publication = session.scalar(sa.select(LessonPublication).where(LessonPublication.page_id == row.id))
            if publication is None:
                session.add(LessonPublication(page_id=row.id, source_path=source, published_digest=digest(data), published_at=datetime.now(timezone.utc)))
            elif publication.source_path != source or publication.published_digest != digest(data):
                raise SourceError('Publication conflict')
    redirects = read_json(root / 'site_content/redirects.json')
    for values in redirects['redirects']:
        row = session.scalar(sa.select(Redirect).where(Redirect.old_path == values['old_path']))
        if row is None:
            session.add(Redirect(**values))
        elif any(getattr(row, k) != value for k, value in values.items()):
            raise SourceError('Redirect conflict')
    session.flush()
    return bundles
