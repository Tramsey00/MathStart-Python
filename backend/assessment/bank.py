"""Atomic operator workflows. Assessment owns the bank; Content and Knowledge are read only."""
from uuid import uuid4

import sqlalchemy as sa

from backend.content.topic_skill_model import content_page
from backend.knowledge.graph import PILOT_VERSION
from backend.knowledge.models import skill
from backend.models.baseline import metadata, utc_now

from .models import exercise, exercise_skill, validation, version
from .package import BankError, TOPICS, digest, validate_rows, validation_data
from .templates import TEMPLATES


def lock_bank(connection):
    connection.execute(sa.text("SELECT pg_advisory_xact_lock(hashtextextended('mathstart.assessment.bank', 0))"))


def references(connection, rows):
    grade, subject, section = (metadata.tables[name] for name in
                              ('content_grade', 'content_subject', 'content_section'))
    page = content_page.c
    catalogue = (content_page.join(grade, page.grade_id == grade.c.id)
                 .join(subject, sa.and_(page.subject_id == subject.c.id, subject.c.grade_id == grade.c.id))
                 .join(section, sa.and_(page.section_id == section.c.id, section.c.subject_id == subject.c.id)))
    topics = connection.execute(sa.select(page.slug, page.id, section.c.slug.label('section'))
        .select_from(catalogue).where(page.slug.in_(TOPICS), page.page_type == 'topic',
            page.is_published.is_(True), grade.c.slug == '6-klass', subject.c.slug == 'matematika')
        .order_by(page.id).with_for_update(read=True)).all()
    if len(topics) != len(TOPICS) or {row.slug: row.section for row in topics} != TOPICS:
        raise BankError('Bank topic is missing, unpublished, or in a different catalogue location')
    codes = {code for row in rows for code in (row['primary'], *row['secondary'])}
    skills = dict(connection.execute(sa.select(skill.c.code, skill.c.id).where(
        skill.c.code.in_(codes), skill.c.active.is_(True), skill.c.graph_version == PILOT_VERSION
    ).order_by(skill.c.id).with_for_update(read=True)).all())
    if skills.keys() != codes:
        raise BankError('Bank requires the installed, active Knowledge pilot skills')
    return {row.slug: row.id for row in topics}, skills


def candidate(row, skill_ids):
    template = TEMPLATES[row['schema']]
    private = validation_data(row)
    version_data = {'version': row['version'], 'mode': template.mode, 'difficulty': row['difficulty'],
                    'statement': row['statement'], 'schema_code': row['schema'],
                    'public_schema': template.public_contract(), 'provenance': row['provenance'],
                    'digest': digest({'exercise': row, 'public': template.public_contract(),
                                      'validation': private})}
    links = {skill_ids[row['primary']]: 'PRIMARY'}
    links.update({skill_ids[code]: 'SECONDARY' for code in row['secondary']})
    return version_data, {**private, 'digest': digest(private)}, links


def store_candidate(connection, row, topic_ids, skill_ids, action):
    topic_id = topic_ids[row['topic']]
    entity = connection.execute(sa.select(exercise).where(exercise.c.code == row['code'])).mappings().one_or_none()
    if entity is None:
        if action != 'import':
            raise BankError('Import the reviewed bank before publishing')
        exercise_id = uuid4()
        connection.execute(exercise.insert().values(id=exercise_id, code=row['code'], topic_id=topic_id,
                                                    created_at=utc_now()))
    else:
        exercise_id = entity['id']
        if entity['topic_id'] != topic_id:
            raise BankError('Exercise identity already belongs to a different topic')

    public, private, links = candidate(row, skill_ids)
    versions = connection.execute(sa.select(version).where(version.c.exercise_id == exercise_id)
                                 .order_by(version.c.version.desc())).mappings().all()
    existing = next((item for item in versions if item['version'] == row['version']), None)
    if existing is None:
        if action != 'import':
            raise BankError('Import the reviewed version before publishing')
        if row['version'] != (versions[0]['version'] if versions else 0) + 1:
            raise BankError('New exercise versions must be consecutively numbered')
        version_id = uuid4()
        connection.execute(version.insert().values(id=version_id, exercise_id=exercise_id, status='DRAFT', **public))
        connection.execute(validation.insert().values(version_id=version_id, **private))
        connection.execute(exercise_skill.insert(), [dict(version_id=version_id, skill_id=skill_id, role=role)
                                                     for skill_id, role in links.items()])
        return 1
    version_id = existing['id']
    installed_private = connection.execute(sa.select(validation).where(
        validation.c.version_id == version_id)).mappings().one_or_none()
    installed_links = dict(connection.execute(sa.select(exercise_skill.c.skill_id, exercise_skill.c.role)
                            .where(exercise_skill.c.version_id == version_id)).all())
    if (any(existing[key] != value for key, value in public.items()) or installed_private is None
            or any(installed_private[key] != value for key, value in private.items()) or installed_links != links):
        raise BankError('Version already exists with different data; create a new version')
    if action == 'import' or existing['status'] == 'PUBLISHED':
        return 0
    if existing['status'] != 'DRAFT' or any(
            item['version'] > row['version'] and item['status'] != 'DRAFT' for item in versions):
        raise BankError('Archived or superseded versions cannot be published')
    connection.execute(version.update().where(version.c.exercise_id == exercise_id, version.c.status == 'PUBLISHED')
                       .values(status='ARCHIVED'))
    connection.execute(version.update().where(version.c.id == version_id).values(status='PUBLISHED'))
    return 1


def apply_bank(engine, rows, action):
    if action not in {'import', 'publish'}:
        raise BankError('Unknown bank action')
    validate_rows(rows)
    with engine.connect().execution_options(isolation_level='READ COMMITTED') as connection, connection.begin():
        lock_bank(connection)
        if action == 'publish':
            active = set(connection.scalars(sa.select(exercise.c.code).join(
                version, version.c.exercise_id == exercise.c.id).where(version.c.status == 'PUBLISHED')))
            if active - {row['code'] for row in rows}:
                raise BankError('Archive previously published exercises omitted by the reviewed package first')
        topics, skills = references(connection, rows)
        return sum(store_candidate(connection, row, topics, skills, action) for row in rows)


def archive(engine, code, number):
    with engine.connect().execution_options(isolation_level='READ COMMITTED') as connection, connection.begin():
        lock_bank(connection)
        row = connection.execute(sa.select(version.c.id, version.c.status).join(
            exercise, version.c.exercise_id == exercise.c.id
        ).where(exercise.c.code == code, version.c.version == number)).one_or_none()
        if row is None or row.status == 'DRAFT':
            raise BankError('Published version to archive was not found')
        if row.status == 'ARCHIVED':
            return 0
        return connection.execute(version.update().where(version.c.id == row.id)
                                  .values(status='ARCHIVED')).rowcount
