"""Seed fresh target auth metadata without rewriting imported IDs/assignments."""
import sqlalchemy as sa
from backend.models.baseline import ContentType, Permission, SNAPSHOT


def seed_permissions(session):
    for model in SNAPSHOT['models']:
        dotted = model['model']
        app, name = dotted.split('.')
        if app == 'auto_created' or '_' in name or name == 'Migration':
            continue
        slug = name.lower()
        row = session.scalar(sa.select(ContentType).where(ContentType.app_label == app, ContentType.model == slug))
        if row is None:
            row = ContentType(app_label=app, model=slug)
            session.add(row)
            session.flush()
        for action in ['add', 'change', 'delete', 'view']:
            code = action + '_' + slug
            exists = session.scalar(sa.select(Permission.id).where(Permission.content_type_id == row.id, Permission.codename == code))
            if exists is None:
                session.add(Permission(content_type_id=row.id, codename=code,
                                       name='Can ' + action + ' ' + name.lower()))
    session.flush()
