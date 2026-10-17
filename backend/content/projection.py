"""Read-only V01 -> closed delivery/build projections for V04/I02 consumers.

Candidates are not active releases. The reviewed source/asset provider remains
server-side; no HTTP client may supply a trust attestation or asset pathname.
"""
from dataclasses import dataclass
from hashlib import sha256

import sqlalchemy as sa

from backend.models.baseline import ContentPage, Grade, Subject, Section, metadata
from backend.infrastructure.http.contracts import validate
from backend.infrastructure.http.transport import missing
from backend.infrastructure.http.transport import timestamp as stamp
from backend.models.baseline import Redirect
from backend.infrastructure.http.transport import unavailable
from backend.content.releases import safe_public_path


@dataclass(frozen=True)
class ReviewedSource:
    path: str
    source_digest: str
    assets: tuple


def seo(page):
    title = (page.seo_title or '').strip()
    if not title:
        title = 'MathStart — математика для 5–10 классов' if page.page_type == 'home' else f'{page.title} | MathStart'
    description = (page.seo_description or '').strip()
    if not description:
        if page.page_type == 'grade':
            name = page.grade.title if page.grade else page.title
            description = f'Математика для {name}: теория, примеры, памятки и задания для самопроверки на сайте MathStart.'
        elif page.page_type == 'subject':
            grade = page.grade.title if page.grade else ''
            subject = page.subject.title if page.subject else page.title
            description = f'{subject}, {grade}: учебные темы, теория, подробные примеры и задания для самопроверки на сайте MathStart.'
        elif page.page_type == 'topic':
            description = f'Тема «{page.title}»: теория, примеры, пошаговые разборы и задания для самопроверки на образовательном сайте MathStart.'
        else:
            description = f'{page.title} — информация на образовательном сайте MathStart.'
    return {'title': title, 'description': description,
            'canonical_path': '/' if page.page_type == 'home' else f'/{page.slug}/'}


def delivery_candidate(uow, slug, reviewed_source):
    if type(reviewed_source) is not ReviewedSource:
        raise TypeError('Reviewed server source artifact required')
    page = uow.session.scalar(sa.select(ContentPage).where(ContentPage.slug == slug, ContentPage.is_published.is_(True)))
    if page is None:
        raise missing()
    return delivery_for_page(page, reviewed_source)


def delivery_for_page(page, reviewed_source):
    if type(reviewed_source) is not ReviewedSource or not page.is_published:
        raise TypeError('Reviewed published page required')
    data = {field: getattr(page, field) for field in ['id', 'slug', 'page_type', 'title', 'grade_id',
            'subject_id', 'section_id', 'order', 'body_html', 'is_published']}
    data.update(delivery_version='content-delivery-v1', seo=seo(page), created_at=stamp(page.created_at),
        updated_at=stamp(page.updated_at), source={'path': reviewed_source.path,
        'source_digest': reviewed_source.source_digest, 'render_digest': sha256(page.body_html.encode('utf-8')).hexdigest()},
        assets=list(reviewed_source.assets))
    return validate(data, 'ContentDelivery', True)


def catalogue_candidate(uow):
    """Execute baseline PG ordering here; frontend never reproduces DB collation."""
    return catalogue_query(uow.session, *(metadata.tables[name] for name in
                           ('content_contentpage', 'content_grade', 'content_subject', 'content_section')))


def catalogue_query(session, pages, grades, subjects, sections):
    p, g, s, c = pages.c, grades.c, subjects.c, sections.c
    fields = ['id', 'title', 'slug', 'order', 'grade_id', 'subject_id', 'section_id']
    statement = sa.select(*(p[f] for f in fields)).select_from(pages.outerjoin(
        grades, p.grade_id == g.id).outerjoin(subjects, p.subject_id == s.id).outerjoin(
        sections, p.section_id == c.id)).where(p.is_published.is_(True), p.page_type == 'topic').order_by(
        g.order.asc().nulls_last(), p.grade_id.asc().nulls_last(),
        s.order.asc().nulls_last(), p.subject_id.asc().nulls_last(),
        c.order.asc().nulls_last(), p.section_id.asc().nulls_last(), p.order, p.title, p.id)
    topics = []
    for row in session.execute(statement):
        item = dict(row._mapping)
        item['url'] = f'/{item["slug"]}/'
        topics.append(item)
    data = {'topics': topics}
    for name, table, columns, ordering, source in [
        ('grades', grades, ['id', 'title', 'slug', 'order'], [g.order, g.title, g.id], grades),
        ('subjects', subjects, ['id', 'title', 'slug', 'order', 'grade_id'], [g.order, s.order, s.title, s.id], subjects.join(grades, s.grade_id == g.id)),
        ('sections', sections, ['id', 'title', 'slug', 'order', 'subject_id'], [g.order, s.order, c.order, c.title, c.id],
         sections.join(subjects, c.subject_id == s.id).join(grades, s.grade_id == g.id))]:
        statement = sa.select(*(table.c[f] for f in columns)).select_from(source)
        data[name] = [dict(row._mapping) for row in session.execute(statement.order_by(*ordering))]
    return validate(data, 'PublicCatalogue', True)


def catalogue_from_snapshot(session, state):
    """Order a prepared edition using the real PostgreSQL collation, no writes."""
    tables = []
    for name, fields in [
        ('content_contentpage', ['id', 'title', 'slug', 'order', 'grade_id', 'subject_id', 'section_id', 'is_published', 'page_type']),
        ('content_grade', ['id', 'title', 'slug', 'order']),
        ('content_subject', ['id', 'title', 'slug', 'order', 'grade_id']),
        ('content_section', ['id', 'title', 'slug', 'order', 'subject_id'])]:
        physical = metadata.tables[name]
        columns = [sa.column(key, physical.c[key].type) for key in fields]
        rows = [tuple(row[key] for key in fields) for row in state[name]]
        if rows:
            table = sa.values(*columns).data(rows).cte('prepared_' + name)
        else:
            table = sa.select(*(sa.cast(sa.null(), col.type).label(col.name) for col in columns)).where(sa.false()).cte('prepared_' + name)
        tables.append(table)
    return catalogue_query(session, *tables)


def build_index_candidate(uow, release_id, deliveries):
    """Complete read-only candidate; V04 validates/stages/activates it separately."""
    published = list(uow.session.scalars(sa.select(ContentPage).where(ContentPage.is_published.is_(True)).order_by(ContentPage.id)))
    redirects = list(uow.session.scalars(sa.select(Redirect).where(Redirect.is_active.is_(True)).order_by(Redirect.old_path)))
    return index_for_pages(published, release_id, deliveries, catalogue_candidate(uow), redirects)


def index_for_pages(published, release_id, deliveries, catalogue, redirect_rows):
    if set(deliveries) != {p.id for p in published}:
        raise unavailable()
    pages, aliases = [], []
    for page in published:
        data = validate(deliveries[page.id], 'ContentDelivery', True)
        if (data['id'] != page.id or data['slug'] != page.slug or data['page_type'] != page.page_type
                or data['seo'] != seo(page) or data['body_html'] != page.body_html):
            raise unavailable()
        canonical = data['seo']['canonical_path']
        pages.append({'id': page.id, 'slug': page.slug, 'page_type': page.page_type, 'url': canonical,
            'canonical_path': canonical, 'delivery_path': f'pages/{page.id}.json', 'updated_at': stamp(page.updated_at),
            'sitemap_changefreq': 'weekly' if page.page_type in {'home', 'grade', 'subject'} else 'monthly',
            'sitemap_priority': 1.0 if page.page_type == 'home' else 0.8 if page.page_type in {'grade', 'subject'} else 0.7 if page.page_type == 'topic' else 0.5})
        if page.page_type == 'home':
            aliases.append({'url': f'/{page.slug}/', 'page_id': page.id, 'status': 200, 'canonical_path': '/'})
    redirects = []
    for row in redirect_rows:
        if not safe_public_path(row.old_path) or not safe_public_path(row.new_path) or row.old_path == row.new_path:
            raise unavailable()
        redirects.append({'old_path': row.old_path, 'new_path': row.new_path, 'is_permanent': row.is_permanent})
    index = {'version': 'public-build-index-v1', 'release_id': release_id, 'pages': pages,
             'catalogue': catalogue, 'aliases': aliases, 'redirects': redirects,
             'system_urls': ['/sitemap.xml', '/robots.txt']}
    return validate(index, 'PublicBuildIndex', True)
