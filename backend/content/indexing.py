"""The existing lesson INDEX command: read-only DB, explicit generated file."""
import os
from pathlib import Path
import uuid

import sqlalchemy as sa

from backend.content.sources import load_sources, SourceError
from backend.models.baseline import ContentPage, Grade, Subject, Section


def index_bytes(session, source_root):
    bundles = {bundle.snapshot['slug']: bundle for bundle in load_sources(source_root)
               if bundle.snapshot['page_type'] == 'topic'}
    query = sa.select(ContentPage.slug, ContentPage.grade_id, ContentPage.subject_id, ContentPage.section_id,
        Grade.title.label('grade_title'), Subject.title.label('subject_title'),
        Section.title.label('section_title'), Section.order.label('section_order')).select_from(ContentPage)
    query = query.outerjoin(Grade, Grade.id == ContentPage.grade_id).outerjoin(Subject,
        Subject.id == ContentPage.subject_id).outerjoin(Section, Section.id == ContentPage.section_id)
    query = query.where(ContentPage.page_type == 'topic').order_by(Grade.order, Subject.order,
        ContentPage.subject_id, Section.order, ContentPage.section_id, ContentPage.order, ContentPage.slug)
    lines = ['# Уроки MathStart', '', 'Исходники сгруппированы по классу, предмету и разделу. Ссылка открывает HTML урока; рядом находится `lesson.json` с его метаданными.', '']
    previous, count = (None, None, None), 0
    for page in session.execute(query).mappings():
        bundle = bundles.get(page['slug'])
        if bundle is None:
            continue  # Same baseline policy for retired rows without sources.
        if any(page[key] is None for key in ('grade_title', 'subject_title', 'section_title', 'section_order')):
            raise SourceError('Lesson catalogue identity is incomplete')
        identity = tuple(page[key] for key in ('grade_id', 'subject_id', 'section_id'))
        if identity != previous:
            lines.append('')
        if identity[0] != previous[0]:
            lines += ['## ' + page['grade_title'], '']
        if identity[1] != previous[1]:
            lines += ['### ' + page['subject_title'], '']
        if identity[2] != previous[2]:
            lines += [f"**{page['section_order']}. {page['section_title']}**", '']
        relative = Path(bundle.path.removeprefix('curriculum/')).parent.as_posix()
        title = bundle.snapshot['title'].replace('[', r'\[').replace(']', r'\]')
        lines.append(f"- {page['section_order']}.{bundle.snapshot['order']} [{title}]({relative}/body.html)")
        previous, count = identity, count + 1
    if count == 0:
        raise SourceError('No indexed lessons')
    lines += ['', f'Всего исходников в указателе: {count}.', '']
    return '\n'.join(lines).encode('utf-8'), count


def write_index(output_root, payload, *, dry_run=False):
    root = Path(output_root).resolve()
    destination = root / 'INDEX.md'
    if destination.is_symlink():
        raise SourceError('Generated index cannot replace a symlink')
    if dry_run:
        return 'NONE'
    root.mkdir(parents=True, exist_ok=True)
    if destination.is_file() and destination.read_bytes() == payload:
        return 'UNCHANGED'
    temporary = root / ('.INDEX-' + uuid.uuid4().hex + '.tmp')
    try:
        with temporary.open('xb') as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, destination)
        if os.name != 'nt':
            descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        return 'INDEX_WRITTEN'
    finally:
        if temporary.exists():
            temporary.unlink()
