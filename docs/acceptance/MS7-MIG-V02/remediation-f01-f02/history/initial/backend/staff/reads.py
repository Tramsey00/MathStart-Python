"""Closed staff DTOs, Django ordering/search and signed SQL keysets."""
from datetime import datetime, timezone
import json
import re

import sqlalchemy as sa
from sqlalchemy.orm import aliased

from backend.models import baseline as models
from backend.infrastructure.http.contracts import document, validator, validate
from backend.infrastructure.http.transport import invalid, missing, singleton_query, page_size, identity
from backend.infrastructure.http.transport import timestamp as stamp

POLICY = document('specs/migration/r02-v1/staff-list-policy-v1.json')['resources']
OAS = document('specs/migration/r02-v1/delivery-staff-v1.openapi.json')['paths']
RESOURCES = {
    'grades': (models.Grade, 'StaffGradeDTO', 'content.grade'),
    'subjects': (models.Subject, 'StaffSubjectDTO', 'content.subject'),
    'sections': (models.Section, 'StaffSectionDTO', 'content.section'),
    'pages': (models.ContentPage, 'StaffPageDTO', 'content.contentpage'),
    'publications': (models.LessonPublication, 'StaffPublicationDTO', 'content.lessonpublication'),
    'media_assets': (models.MediaAsset, 'StaffMediaAssetDTO', 'content.mediaasset'),
    'redirects': (models.Redirect, 'StaffRedirectDTO', 'content.redirect'),
    'users': (models.User, 'StaffUserDTO', 'auth.user'),
    'groups': (models.Group, 'StaffGroupDTO', 'auth.group'),
}
SALT = 'content.staff.migration-r02-v1.cursor'
SEARCH_WORDS = re.compile(r'''((?:[^\s'"]*(?:(?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')[^\s'"]*)+)|\S+)''')


def search_terms(query):
    """Django smart_split semantics, including embedded quotes and escapes."""
    words = SEARCH_WORDS.findall(query)
    return [word[1:-1].replace('\\' + word[0], word[0]).replace('\\\\', '\\')
            if word[0] in {'"', "'"} and word[-1] == word[0] else word for word in words]
NATIVE_ORDER = {
    'grades': ['order', 'title'], 'subjects': ['grade__order', 'order', 'title'],
    'sections': ['subject__grade__order', 'subject__order', 'order', 'title'],
    'pages': ['page_type', 'grade__order', 'subject__order', 'section__order', 'order', 'title'],
    'publications': ['source_path'], 'media_assets': [], 'redirects': ['old_path'],
    'users': ['username'], 'groups': ['name'],
}


def view_permissions(resource):
    _, _, dotted = RESOURCES[resource]
    app, model = dotted.split('.')
    return f'{app}.view_{model}', f'{app}.change_{model}'


def dto(uow, resource, row):
    model, schema, _ = RESOURCES[resource]
    fields = validator(schema, True).schema['$defs'][schema]['required']
    data = {name: stamp(getattr(row, name)) if isinstance(getattr(row, name, None), datetime)
            else getattr(row, name, None) for name in fields}
    if resource == 'pages':
        publication = uow.session.scalar(sa.select(models.LessonPublication.source_path).where(models.LessonPublication.page_id == row.id))
        data['source_location'] = 'curriculum/' + publication if publication else f'site_content/pages/{row.slug}/'
    if resource in ('users', 'groups'):
        joins = [('groups', 'auth_user_groups', 'group_id', 'user_id'),
                 ('user_permissions', 'auth_user_user_permissions', 'permission_id', 'user_id')] if resource == 'users' else [
                 ('permissions', 'auth_group_permissions', 'permission_id', 'group_id')]
        for name, table, target, owner in joins:
            table = models.metadata.tables[table]
            data[name] = list(uow.session.scalars(sa.select(table.c[target]).where(table.c[owner] == row.id).order_by(table.c[target])))
        if resource == 'users':
            data['has_usable_password'] = not row.password.startswith('!')
    return validate(data, schema, True)


class Query:
    """Resolve only inventoried ORM field paths into explicit outer joins."""
    def __init__(self, model):
        self.model = model
        self.statement = sa.select(model)
        self.entities = {'': model}

    def field(self, path):
        parts = path.split('__')
        entity, prefix = self.model, ''
        for relation in parts[:-1]:
            prefix = prefix + '__' + relation if prefix else relation
            if prefix not in self.entities:
                target = aliased(getattr(entity, relation).property.mapper.class_)
                self.statement = self.statement.outerjoin(target, getattr(entity, relation))
                self.entities[prefix] = target
            entity = self.entities[prefix]
        field = parts[-1]
        return getattr(entity, 'id' if field == 'pk' else field)

    def expand(self, term):
        reverse = term.startswith('-')
        path = term.lstrip('-')
        if path in {'grade', 'subject', 'section', 'page', 'related_page'}:
            related = getattr(self.model, path).property.mapper.class_
            order = {models.Grade: ['order', 'title'],
                     models.Subject: ['grade__order', 'order', 'title'],
                     models.Section: ['subject__grade__order', 'subject__order', 'order', 'title'],
                     models.ContentPage: ['grade__order', 'subject__order', 'section__order', 'order', 'title']}[related]
            return [('-' if reverse ^ field.startswith('-') else '') + path + '__' + field.lstrip('-') for field in order]
        return [term]


def effective_order(resource, sort):
    policy = POLICY[resource]
    if sort in (None, 'default'):
        return list(policy['default_effective_order'])
    terms = sort.split(',')
    if (not re.fullmatch(policy['query_schema']['pattern'], sort)
            or len({t.lstrip('-') for t in terms}) != len(terms)):
        raise invalid()
    if len(terms) == 1:
        return policy['explicit_single_field_orders'][terms[0]]
    # Django explicit columns precede the native ModelAdmin queryset ordering.
    result = terms + NATIVE_ORDER[resource]
    unique = {'grades': {'slug'}, 'pages': {'slug'}, 'publications': {'page', 'source_path'},
              'redirects': {'old_path'}, 'users': {'username'}, 'groups': {'name'}, 'media_assets': {'id', 'file'}}
    if not {t.lstrip('-') for t in result} & unique.get(resource, set()):
        result.append('-pk')
    return result


def keyset(keys, values):
    branches, prefix = [], []
    for (field, descending), value in zip(keys, values):
        # PG ASC NULLS LAST, DESC NULLS FIRST, including mixed directions.
        if value is None:
            later = field.is_not(None) if descending else sa.false()
        else:
            comparable = sa.cast(field, sa.Integer) if field.type.python_type is bool else field
            comparable_value = int(value) if field.type.python_type is bool else value
            later = comparable < comparable_value if descending else sa.or_(comparable > comparable_value, field.is_(None))
        branches.append(sa.and_(*prefix, later))
        prefix.append(field.is_(None) if value is None else field == value)
    return sa.or_(*branches)


def cursor_scalar(field, raw):
    if not isinstance(raw, dict) or set(raw) != {'null', 'value'} or type(raw['null']) is not bool:
        raise invalid()
    value = raw['value']
    if raw['null']:
        if value is not None:
            raise invalid()
        return None
    expected = field.type.python_type
    if expected is datetime:
        if not isinstance(value, str):
            raise invalid()
        try:
            result = datetime.fromisoformat(value)
            if result.tzinfo is None or result.utcoffset() != timezone.utc.utcoffset(result):
                raise ValueError()
            return result
        except ValueError:
            raise invalid() from None
    if type(value) is not expected:
        raise invalid()
    return value


def list_records(uow, resource, params, signer, scope):
    operation = OAS[f'/api/v1/staff/{resource}/']['get']
    parameters = {p['name']: p for p in operation['parameters']}
    query = singleton_query(params, parameters)
    size = page_size(query.get('page_size', '20'))
    q = query.get('q', '')
    model, schema, _ = RESOURCES[resource]
    builder = Query(model)
    filters = {}
    for name, raw in query.items():
        if not name.startswith('filter__'):
            continue
        field = name[8:]
        shape = parameters[name]['schema']
        if shape.get('type') == 'boolean':
            if raw not in ('true', 'false'):
                raise invalid()
            value = raw == 'true'
        elif shape.get('type') == 'integer':
            value = identity(raw)
        elif raw in shape.get('enum', []):
            value = raw
        else:
            raise invalid()
        filters[field] = value
        if field == 'groups':
            membership = models.metadata.tables['auth_user_groups']
            predicate = model.id.in_(sa.select(membership.c.user_id).where(membership.c.group_id == value))
        else:
            if field in {'grade', 'subject'}:
                field += '_id'
            elif field == 'subject__grade':
                field += '_id'
            predicate = builder.field(field) == value
        builder.statement = builder.statement.where(predicate)
    # Each native search word ANDs an OR over inventoried fields.
    for word in search_terms(q):
        predicate = sa.or_(*(builder.field(f).icontains(word, autoescape=True) for f in operation['x-baseline-search-fields']))
        builder.statement = builder.statement.where(predicate)
    expanded = []
    for term in effective_order(resource, query.get('sort')):
        expanded.extend(builder.expand(term))
    # Repeated Django order terms have no ordering effect, but retain their binding.
    keys = [(builder.field(t.lstrip('-')), t.startswith('-')) for t in expanded]
    binding = {'actor_user_id': scope.user_id, 'authorization_scope_revision': scope.revision,
               'resource': resource, 'q': q, 'normalized_filters': filters,
               'effective_sort_keys_and_directions': expanded, 'page_size': size}
    if 'cursor' in query:
        value = signer.loads(query['cursor'], SALT, max_length=8192)
        if (not isinstance(value, dict) or set(value) != {'binding', 'last'}
                or json.dumps(value['binding'], sort_keys=True) != json.dumps(binding, sort_keys=True)
                or not isinstance(value['last'], list) or len(value['last']) != len(keys)):
            raise invalid()
        values = [cursor_scalar(field, raw) for (field, _), raw in zip(keys, value['last'])]
        builder.statement = builder.statement.where(keyset(keys, values))
    selected = [field.label('key_' + str(i)) for i, (field, _) in enumerate(keys)]
    statement = builder.statement.add_columns(*selected).order_by(*[
        field.desc().nulls_first() if desc else field.asc().nulls_last() for field, desc in keys]).limit(size + 1)
    rows = list(uow.session.execute(statement))
    more = len(rows) > size
    page = rows[:size]
    cursor = None
    if more:
        last = [{'null': v is None, 'value': stamp(v) if isinstance(v, datetime) else v} for v in page[-1][1:]]
        cursor = signer.dumps({'binding': binding, 'last': last}, SALT, compress=True)
    return [dto(uow, resource, row[0]) for row in page], {'next_cursor': cursor, 'page_size': size, 'has_more': more}


def detail(uow, resource, record_id):
    row = uow.repository(RESOURCES[resource][0]).get(record_id)
    if row is None:
        raise missing()
    return dto(uow, resource, row)


def history(uow, resource, record_id, params, signer, scope):
    # Authorization happens in the controller before both this object lookup and logs.
    if uow.repository(RESOURCES[resource][0]).get(record_id) is None:
        raise missing()
    query = singleton_query(params, {'page_size', 'cursor'})
    size = page_size(query.get('page_size', '20'))
    app, model = RESOURCES[resource][2].split('.')
    ct, log = models.ContentType, models.AdminLog
    statement = sa.select(log).join(ct, ct.id == log.content_type_id).where(
        ct.app_label == app, ct.model == model, log.object_id == str(record_id))
    binding = [scope.user_id, scope.revision, resource, record_id, size]
    if 'cursor' in query:
        value = signer.loads(query['cursor'], SALT, max_length=8192)
        if (not isinstance(value, dict) or set(value) != {'binding', 'last'}
                or json.dumps(value['binding']) != json.dumps(binding)
                or not isinstance(value['last'], list) or len(value['last']) != 2
                or type(value['last'][1]) is not int or value['last'][1] <= 0):
            raise invalid()
        try:
            last_time = datetime.fromisoformat(value['last'][0])
            if last_time.tzinfo is None:
                raise ValueError()
        except (TypeError, ValueError):
            raise invalid() from None
        statement = statement.where(sa.or_(log.action_time > last_time,
            sa.and_(log.action_time == last_time, log.id > value['last'][1])))
    rows = list(uow.session.scalars(statement.order_by(log.action_time, log.id).limit(size + 1)))
    more = len(rows) > size
    rows = rows[:size]
    # Log entries may historically contain arbitrary input; expose only known action.
    data = [{'id': r.id, 'actor_id': r.user_id, 'object_id': r.object_id,
             'action': {1: 'ADD', 2: 'CHANGE', 3: 'DELETE'}[r.action_flag],
             'occurred_at': stamp(r.action_time), 'summary': {1: 'Added.', 2: 'Changed.', 3: 'Deleted.'}[r.action_flag]}
            for r in rows]
    cursor = signer.dumps({'binding': binding, 'last': [stamp(rows[-1].action_time), rows[-1].id]}, SALT) if more else None
    return data, {'next_cursor': cursor, 'page_size': size, 'has_more': more}
