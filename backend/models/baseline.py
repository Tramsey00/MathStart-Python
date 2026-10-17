"""Django-independent SQLAlchemy mapping of the immutable R02 physical snapshot.

Python defaults are separate from SQL defaults. Relationships are view-only:
deletion is owned by the collector service, never ORM cascades.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import registry, relationship

SNAPSHOT = json.loads((Path(__file__).with_name('baseline-v1.json')).read_text(encoding='utf-8'))
COMPATIBILITY = json.loads(Path(__file__).with_name('compatibility-v1.json').read_text(encoding='utf-8'))
DDL_OVERRIDES = {(item['table'], item['column']): item for item in COMPATIBILITY['ddl_overrides']}
metadata = sa.MetaData()
mapper_registry = registry(metadata=metadata)
GRADE_EPOCH = datetime(2026, 10, 4, tzinfo=timezone.utc)
ONBOARDING_CHECK = (
    '(NOT onboarding_complete AND onboarding_mode IS NULL) OR '
    "(onboarding_complete AND onboarding_mode IN ('START_ZERO','DIAGNOSTIC','SELF_REPORT') "
    'AND onboarding_mode IS NOT NULL AND selected_grade_id IS NOT NULL)'
)


def utc_now():
    return datetime.now(timezone.utc)


def sql_type(field, table_name):
    kind = field['db_type']
    override = DDL_OVERRIDES.get((table_name, field['column']))
    if override:
        physical = next(column for column in SNAPSHOT['physical_baseline']['columns']
                        if (column['table_name'], column['column_name']) == (table_name, field['column']))
        if (not field['primary_key'] or kind != override['model_db_type']
                or physical['data_type'] != override['physical_db_type']):
            raise ValueError('Compatibility override no longer matches the reviewed input')
        kind = override['physical_db_type']
    if kind.startswith('varchar('):
        return sa.String(field['max_length'])
    return {
        'integer': sa.Integer(), 'bigint': sa.BigInteger().with_variant(sa.Integer(), 'sqlite'),
        'smallint': sa.SmallInteger(), 'boolean': sa.Boolean(), 'text': sa.Text(),
        'uuid': sa.Uuid(), 'jsonb': sa.JSON(none_as_null=True).with_variant(JSONB(none_as_null=True), 'postgresql'),
        'timestamp with time zone': sa.DateTime(timezone=True).with_variant(TIMESTAMP(timezone=True, precision=6), 'postgresql'),
    }[kind]


def application_default(field):
    value = field['default']
    if field['auto_now_add'] or field['auto_now']:
        return utc_now
    if value['kind'] == 'application_value':
        return value['value']
    if value['kind'] == 'application_callable':
        return {'uuid.uuid4': uuid.uuid4, 'django.utils.timezone.now': utc_now}[value['value']]
    if not field['null'] and field['type'] in {'CharField', 'SlugField', 'TextField', 'FileField'}:
        return ''
    return None


def identifier_list(raw):
    return [part.strip().strip('"') for part in raw.split(',')]


def build_metadata():
    identities = {x['table_name']: x for x in SNAPSHOT['fresh_disposable_sequence_evidence']['identity_columns']}
    constraints = SNAPSHOT['physical_baseline']['constraints']
    for model in SNAPSHOT['models']:
        columns = []
        for field in model['fields']:
            args = []
            if field['primary_key'] and model['table'] in identities:
                args.append(sa.Identity(always=False, start=1, increment=1, minvalue=1, cycle=False, cache=1))
            columns.append(sa.Column(field['column'], sql_type(field, model['table']), *args,
                primary_key=field['primary_key'], nullable=field['null'],
                default=application_default(field), info={'baseline_field': field}))
        table = sa.Table(model['table'], metadata, *columns)
        for item in (x for x in constraints if x['table_name'] == table.name):
            definition = item['definition']
            if item['type'] == 'p':
                table.primary_key.name = item['name']
            elif item['type'] == 'u':
                table.append_constraint(sa.UniqueConstraint(*identifier_list(definition[8:-1]), name=item['name']))
            elif item['type'] == 'f':
                match = re.fullmatch(r'FOREIGN KEY \((.+)\) REFERENCES (\w+)\((.+)\) DEFERRABLE INITIALLY DEFERRED', definition)
                if not match:
                    raise ValueError('Unreviewed baseline FK format')
                local, target, remote = match.groups()
                table.append_constraint(sa.ForeignKeyConstraint(identifier_list(local),
                    [target + '.' + c for c in identifier_list(remote)], name=item['name'],
                    deferrable=True, initially='DEFERRED'))
            elif item['type'] == 'c':
                # Reparse the original Django IN expression, not PostgreSQL's
                # deparsed varchar[] -> text[] cast. The latter reparses into
                # per-element casts and changes pg_get_constraintdef output.
                # The original IN expression produces the exact frozen catalog
                # definition; schema.py deliberately retains strict equality.
                expression = ONBOARDING_CHECK if item['name'] == 'users_consistent_onboarding' else definition[7:-1]
                table.append_constraint(sa.CheckConstraint(expression, name=item['name']))
            else:
                raise ValueError('Unreviewed baseline constraint type')
    owned_indexes = {c['name'] for c in constraints if c['type'] in {'p', 'u'}}
    for item in SNAPSHOT['physical_baseline']['indexes']:
        if item['indexname'] in owned_indexes:
            continue
        match = re.fullmatch(r'CREATE INDEX \w+ ON public\.\w+ USING btree \((.+)\)', item['indexdef'])
        if not match:
            raise ValueError('Unreviewed baseline index format')
        table = metadata.tables[item['tablename']]
        names, ops = [], {}
        for part in match.group(1).split(','):
            parts = part.strip().split()
            name = parts[0].strip('"')
            names.append(name)
            if len(parts) == 2:
                ops[name] = parts[1]
        sa.Index(item['indexname'], *(table.c[name] for name in names), postgresql_ops=ops)


build_metadata()


class Grade: pass
class Subject: pass
class Section: pass
class ContentPage: pass
class LessonPublication: pass
class MediaAsset: pass
class Redirect: pass
class User: pass
class Group: pass
class Permission: pass
class UserGroup: pass
class UserPermission: pass
class GroupPermission: pass
class StudentProfile: pass
class IdentityReceipt: pass
class LoginWindow: pass
class ContentType: pass
class AdminLog: pass
class LegacySession: pass
class DjangoMigration: pass


MODEL_TYPES = dict(zip([
    'content_grade', 'content_subject', 'content_section', 'content_contentpage',
    'content_lessonpublication', 'content_mediaasset', 'content_redirect', 'auth_user',
    'auth_group', 'auth_permission', 'auth_user_groups', 'auth_user_user_permissions',
    'auth_group_permissions', 'users_studentprofile', 'users_identityreceipt',
    'users_loginwindow', 'django_content_type', 'django_admin_log', 'django_session', 'django_migrations',
], [Grade, Subject, Section, ContentPage, LessonPublication, MediaAsset, Redirect,
    User, Group, Permission, UserGroup, UserPermission, GroupPermission, StudentProfile,
    IdentityReceipt, LoginWindow, ContentType, AdminLog, LegacySession, DjangoMigration]))


def ordinary_insert_timestamps(mapper, connection, entity):
    # Django Field.pre_save(add=True) replaces even explicit caller values.
    # Mapper events cover Repository.add/save and ordinary Session inserts.
    # Historical migration/import uses explicit Core DML, never this ORM path.
    for column in mapper.columns:
        field = column.info.get('baseline_field', {})
        if field.get('auto_now_add') or field.get('auto_now'):
            setattr(entity, column.name, utc_now())


def ordinary_update_timestamps(mapper, connection, entity):
    # Full ORM saves include auto_now, while auto_now_add is insert-only.
    # Restricted save/update_fields and bulk operations use controlled Core DML.
    for column in mapper.columns:
        if column.info.get('baseline_field', {}).get('auto_now'):
            setattr(entity, column.name, utc_now())


for model in SNAPSHOT['models']:
    table = metadata.tables[model['table']]
    properties = {}
    for field in model['fields']:
        if 'relationship' in field:
            target = MODEL_TYPES[field['relationship']['to_table']]
            properties[field['name']] = relationship(target, foreign_keys=[table.c[field['column']]], viewonly=True)
    mapper = mapper_registry.map_imperatively(MODEL_TYPES[model['table']], table, properties=properties)
    sa.event.listen(mapper, 'before_insert', ordinary_insert_timestamps)
    sa.event.listen(mapper, 'before_update', ordinary_update_timestamps)
