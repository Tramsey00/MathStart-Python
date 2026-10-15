"""Read-only V01 -> closed delivery/build projections for V04/I02 consumers.

Candidates are not active releases. The reviewed source/asset provider remains
server-side; no HTTP client may supply a trust attestation or asset pathname.
"""
from dataclasses import dataclass
from hashlib import sha256

import sqlalchemy as sa

from backend.models.baseline import ContentPage, Grade, Subject, Section
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
    data = {field: getattr(page, field) for field in ['id', 'slug', 'page_type', 'title', 'grade_id',
            'subject_id', 'section_id', 'order', 'body_html', 'is_published']}
    data.update(delivery_version='content-delivery-v1', seo=seo(page), created_at=stamp(page.created_at),
        updated_at=stamp(page.updated_at), source={'path': reviewed_source.path,
        'source_digest': reviewed_source.source_digest, 'render_digest': sha256(page.body_html.encode('utf-8')).hexdigest()},
        assets=list(reviewed_source.assets))
    return validate(data, 'ContentDelivery', True)


def catalogue_candidate(uow):
    """Execute baseline PG ordering here; frontend never reproduces DB collation."""
    fields = ['id', 'title', 'slug', 'order', 'grade_id', 'subject_id', 'section_id']
    statement = sa.select(*(getattr(ContentPage, f) for f in fields)).outerjoin(
        Grade, ContentPage.grade_id == Grade.id).outerjoin(Subject, ContentPage.subject_id == Subject.id).outerjoin(
        Section, ContentPage.section_id == Section.id).where(ContentPage.is_published.is_(True), ContentPage.page_type == 'topic').order_by(
        Grade.order.asc().nulls_last(), ContentPage.grade_id.asc().nulls_last(),
        Subject.order.asc().nulls_last(), ContentPage.subject_id.asc().nulls_last(),
        Section.order.asc().nulls_last(), ContentPage.section_id.asc().nulls_last(),
        ContentPage.order, ContentPage.title, ContentPage.id)
    topics = []
    for row in uow.session.execute(statement):
        item = dict(row._mapping)
        item['url'] = f'/{item["slug"]}/'
        topics.append(item)
    data = {'topics': topics}
    for name, model, columns, ordering in [
        ('grades', Grade, ['id', 'title', 'slug', 'order'], [Grade.order, Grade.title, Grade.id]),
        ('subjects', Subject, ['id', 'title', 'slug', 'order', 'grade_id'], [Grade.order, Subject.order, Subject.title, Subject.id]),
        ('sections', Section, ['id', 'title', 'slug', 'order', 'subject_id'], [Grade.order, Subject.order, Section.order, Section.title, Section.id])]:
        statement = sa.select(*(getattr(model, f) for f in columns))
        if model is Subject:
            statement = statement.join(Grade, Subject.grade_id == Grade.id)
        elif model is Section:
            statement = statement.join(Subject, Section.subject_id == Subject.id).join(Grade, Subject.grade_id == Grade.id)
        data[name] = [dict(row._mapping) for row in uow.session.execute(statement.order_by(*ordering))]
    return validate(data, 'PublicCatalogue', True)


def build_index_candidate(uow, release_id, deliveries):
    """Complete read-only candidate; V04 validates/stages/activates it separately."""
    published = list(uow.session.scalars(sa.select(ContentPage).where(ContentPage.is_published.is_(True)).order_by(ContentPage.id)))
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
    for row in uow.session.scalars(sa.select(Redirect).where(Redirect.is_active.is_(True)).order_by(Redirect.old_path)):
        if not safe_public_path(row.old_path) or not safe_public_path(row.new_path) or row.old_path == row.new_path:
            raise unavailable()
        redirects.append({'old_path': row.old_path, 'new_path': row.new_path, 'is_permanent': row.is_permanent})
    index = {'version': 'public-build-index-v1', 'release_id': release_id, 'pages': pages,
             'catalogue': catalogue_candidate(uow), 'aliases': aliases, 'redirects': redirects,
             'system_urls': ['/sitemap.xml', '/robots.txt']}
    return validate(index, 'PublicBuildIndex', True)
