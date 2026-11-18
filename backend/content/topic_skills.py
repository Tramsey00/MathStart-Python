"""Content's read and import services for approved topic-to-skill links."""
from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4

import sqlalchemy as sa

from backend.knowledge.models import skill
from backend.models.baseline import metadata

from .topic_skill_model import content_page, topic_skill


MAPPING_VERSION = 'pilot-v1'
APPROVED_PAIRS = {
    ('uproshhenie-vyrazhenij-raskrytie-skobok', 'expand_parentheses'),
    ('reshenie-linejnyh-uravnenij', 'linear_one_step'),
}
APPROVED_LOCATION = ('6-klass', 'matematika', 'preobrazovanie-bukvennyh-vyrazhenij')


class TopicSkillError(ValueError):
    pass


@dataclass(frozen=True)
class TopicSkillRead:
    skill_code: str
    skill_name: str
    role: str
    importance: Decimal
    position: int
    mapping_version: str


def read_topic_skills(database, content_page_id: int) -> tuple[TopicSkillRead, ...] | None:
    """None for an unavailable topic, an empty tuple for a public topic without active links."""
    page, link, node = content_page.c, topic_skill.c, skill.c
    active_links = topic_skill.join(skill, sa.and_(node.id == link.skill_id, node.active.is_(True)))
    rows = database.execute(sa.select(node.code, node.name, link.role, link.importance, link.position,
                                      link.mapping_version).select_from(
        content_page.outerjoin(active_links, page.id == link.content_page_id)
    ).where(page.id == content_page_id, page.page_type == 'topic', page.is_published.is_(True))
        .order_by(link.position, node.code)).all()
    if not rows:
        return None
    return tuple(TopicSkillRead(*row) for row in rows if row.code is not None)


def validate_pilot_mappings(package) -> tuple[tuple[str, str], ...]:
    try:
        if package['mapping_version'] != MAPPING_VERSION:
            raise TopicSkillError('Unexpected pilot mapping version')
        pairs = set()
        for row in package['mappings']:
            pair = (row['slug'], row['skill_code'])
            if pair in pairs:
                raise TopicSkillError('Duplicate pilot topic mapping')
            pairs.add(pair)
            location = (row['grade'], row['subject'], row['section'])
            if (location != APPROVED_LOCATION or row['role'] != 'PRIMARY'
                    or type(row['importance']) is not int or row['importance'] != 1
                    or type(row['position']) is not int or row['position'] != 0):
                raise TopicSkillError('Pilot mapping differs from the approved topic, role, weight or order')
        if pairs != APPROVED_PAIRS:
            raise TopicSkillError('Pilot topic/skill pairs differ from the approved mapping')
        return tuple(sorted(pairs))
    except (KeyError, TypeError) as error:
        raise TopicSkillError('Malformed pilot mapping package') from error


def resolve_pilot_topics(connection, pairs) -> dict[str, int]:
    """Resolve approved coordinates to retained ContentPage IDs and lock the source rows."""
    grades, subjects, sections = (metadata.tables[name] for name in
                                  ('content_grade', 'content_subject', 'content_section'))
    page, grade, subject, section = content_page.c, grades.c, subjects.c, sections.c
    location = content_page.join(grades, page.grade_id == grade.id).join(
        subjects, sa.and_(page.subject_id == subject.id, subject.grade_id == grade.id)
    ).join(sections, sa.and_(page.section_id == section.id, section.subject_id == subject.id))
    grade_slug, subject_slug, section_slug = APPROVED_LOCATION
    slugs = {slug for slug, _ in pairs}
    rows = connection.execute(sa.select(page.slug, page.id).select_from(location).where(
        page.slug.in_(slugs), page.page_type == 'topic', page.is_published.is_(True),
        grade.slug == grade_slug, subject.slug == subject_slug, section.slug == section_slug,
    ).order_by(page.id).with_for_update(read=True)).all()
    result = dict(rows)
    if result.keys() != slugs or len(rows) != len(slugs):
        raise TopicSkillError('Pilot topic is missing, unpublished, or has different catalogue coordinates')
    return result


def store_pilot_mappings(connection, pairs, pages, skills) -> int:
    link = topic_skill.c
    keys = {(pages[slug], skills[code]) for slug, code in pairs}
    rows = connection.execute(sa.select(link.content_page_id, link.skill_id, link.role, link.importance,
                                        link.position, link.mapping_version).where(sa.or_(
        link.mapping_version == MAPPING_VERSION, sa.tuple_(link.content_page_id, link.skill_id).in_(keys),
    ))).all()
    if rows:
        expected = {(*key, 'PRIMARY', Decimal(1), 0, MAPPING_VERSION) for key in keys}
        if set(rows) != expected:
            raise TopicSkillError('Installed pilot mappings differ from the approved package')
        return 0
    connection.execute(topic_skill.insert(), [
        dict(id=uuid4(), content_page_id=page_id, skill_id=skill_id, role='PRIMARY', importance=Decimal(1),
             position=0, mapping_version=MAPPING_VERSION)
        for page_id, skill_id in sorted(keys)
    ])
    return len(keys)
