"""Baseline User/Group mutations with server permissions, audit and protection."""
from datetime import datetime
import hashlib
import json
import secrets

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from backend.infrastructure.uow import UnitOfWork
from backend.infrastructure.locks import OrderedLocks
from backend.infrastructure.collector import plan_deletion, delete_collected, ProtectedDeletion, RestrictedDeletion
from backend.infrastructure.http import transport as wire
from backend.models.baseline import User, Group, Permission, ContentType, AdminLog, metadata
from backend.models.protocol import TargetSession, ReceiptBridge
from backend.staff.authorization import authorize, AuthenticatedIdentity
from backend.staff import reads
from backend.users import passwords
from backend.users.service import conflict, validate_current
from backend.users.security import revoke_lineage


def permission(scope, resource, action):
    model = 'user' if resource == 'users' else 'group'
    required = [f'auth.{action}_{model}']
    if resource == 'users' and action == 'add':
        required.append('auth.change_user')
    if not scope.superuser and not all(p in scope.permissions for p in required):
        raise wire.forbidden()


def audit(session, actor, resource, row, action):
    model = 'user' if resource == 'users' else 'group'
    ct = session.scalar(sa.select(ContentType).where(ContentType.app_label == 'auth', ContentType.model == model))
    if ct is None:
        raise wire.unavailable()
    session.add(AdminLog(user_id=actor, content_type_id=ct.id, object_id=str(row.id),
                        object_repr=(row.username if resource == 'users' else row.name)[:200],
                        action_flag={'created': 1, 'changed': 2, 'deleted': 3}[action],
                        change_message='Target staff ' + action + ' ' + model + '.'))


def joins(session, table_name, owner_column, owner_id, target_column, ids, target_model):
    existing = set(session.scalars(sa.select(target_model.id).where(target_model.id.in_(ids))))
    if existing != set(ids):
        raise wire.invalid()
    table = metadata.tables[table_name]
    session.execute(sa.delete(table).where(table.c[owner_column] == owner_id))
    for identity in sorted(ids):
        session.execute(sa.insert(table).values({owner_column: owner_id, target_column: identity}))


def password_value(body, user, *, creating=False):
    if body['usable_password']:
        value = body.get('password1', '')
        if value != body.get('password2') or not passwords.validate_password(value, user):
            raise wire.invalid()
        return passwords.encode(value)
    if not creating and (body.get('confirm_disable') is not True or user.password.startswith('!')):
        raise conflict()
    return '!' + secrets.token_urlsafe(30)


class StaffWrites:
    def __init__(self, identity_service, signer):
        self.identity_service, self.security = identity_service, identity_service.security
        self.engine, self.signer = self.security.engine, signer

    def _scope(self, uow, identity, resource, action, ids=()):
        locks = OrderedLocks(uow.session)
        locks.namespace('identity', 'lineage:' + str(identity.lineage_id))
        locks.namespace('staff', resource)
        user_ids = sorted(set([identity.user_id, *ids] if resource == 'users' else [identity.user_id]))
        list(uow.session.scalars(sa.select(User).where(User.id.in_(user_ids)).order_by(User.id).with_for_update()))
        scope = authorize(uow, AuthenticatedIdentity(identity.user_id))
        if action:
            permission(scope, resource, action)
        actor = uow.session.get(User, identity.user_id)
        validate_current(uow.session, identity, actor, self.security.keys, lock=False)
        return scope

    def mutate(self, identity, resource, action, body, record_id=None):
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            self._scope(uow, identity, resource, 'add' if action == 'create' else 'change', [record_id] if record_id else [])
            model = User if resource == 'users' else Group
            row = s.scalar(sa.select(model).where(model.id == record_id).with_for_update()) if record_id else model()
            if row is None:
                raise wire.missing()
            if resource == 'users':
                if not passwords.valid_username(body['username']):
                    raise wire.invalid()
                row.username = body['username']
                if action == 'create':
                    row.password = password_value(body, row, creating=True)
                else:
                    if not passwords.valid_email(body['email']) or any(len(body[k]) > 150 for k in ['first_name', 'last_name']):
                        raise wire.invalid()
                    for field in ['first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser']:
                        setattr(row, field, body[field])
                    for field in ['last_login', 'date_joined']:
                        setattr(row, field, datetime.fromisoformat(body[field].replace('Z', '+00:00')) if body[field] else None)
            else:
                row.name = body['name']
            try:
                with s.begin_nested():
                    s.add(row)
                    s.flush()
            except IntegrityError:
                raise wire.invalid() from None
            if resource == 'users' and action != 'create':
                joins(s, 'auth_user_groups', 'user_id', row.id, 'group_id', body['groups'], Group)
                joins(s, 'auth_user_user_permissions', 'user_id', row.id, 'permission_id', body['user_permissions'], Permission)
                if not row.is_active:
                    now = s.scalar(sa.select(sa.func.clock_timestamp()))
                    for lineage in s.scalars(sa.select(TargetSession.lineage_id).where(TargetSession.user_id == row.id).distinct()):
                        revoke_lineage(s, lineage, now)
            if resource == 'groups':
                joins(s, 'auth_group_permissions', 'group_id', row.id, 'permission_id', body['permissions'], Permission)
            audit(s, identity.user_id, resource, row, 'created' if action == 'create' else 'changed')
            s.flush()
            result = reads.dto(uow, resource, row)
            uow.commit()
            return result

    def change_password(self, identity, record_id, body, *, own=False):
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            self._scope(uow, identity, 'users', None if own else 'change', [record_id])
            row = s.get(User, record_id)
            if row is None:
                raise wire.missing()
            if own:
                if not passwords.verify(body['old_password'], row.password):
                    raise wire.invalid()
                body = {'usable_password': True, 'password1': body['new_password1'], 'password2': body['new_password2']}
            value = password_value(body, row)
            now = s.scalar(sa.select(sa.func.clock_timestamp()))
            lineages = sorted(set(s.scalars(sa.select(TargetSession.lineage_id).where(TargetSession.user_id == row.id))), key=str)
            for lineage in lineages:
                revoke_lineage(s, lineage, now)
            row.password = value
            cookies = None
            if row.id == identity.user_id:
                _, token, csrf = self.security.issue(s, row, now)
                cookies = (token, csrf)
            audit(s, identity.user_id, 'users', row, 'changed')
            s.flush()
            result = reads.dto(uow, 'users', row)
            uow.commit()
            return result, cookies

    def _revision(self, uow, resource, rows):
        data = []
        for row in rows:
            values = reads.dto(uow, resource, row)
            if resource == 'users':
                values = {**values, 'password_revision': hashlib.sha256(row.password.encode()).hexdigest()}
            data.append(values)
        return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    def delete(self, identity, resource, ids, *, token=None):
        ids = sorted(ids)
        if not ids or len(ids) != len(set(ids)):
            raise wire.invalid()
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            scope = self._scope(uow, identity, resource, 'delete', ids)
            model = User if resource == 'users' else Group
            rows = list(s.scalars(sa.select(model).where(model.id.in_(ids)).order_by(model.id).with_for_update()))
            if len(rows) != len(ids):
                raise wire.missing()
            revision = self._revision(uow, resource, rows)
            now = s.scalar(sa.select(sa.func.clock_timestamp()))
            payload = {'actor': identity.user_id, 'resource': resource, 'ids': ids, 'revision': revision,
                       'permission_revision': scope.revision}
            table = 'auth_user' if resource == 'users' else 'auth_group'
            protected = False
            try:
                plan_deletion(s, table, ids)
            except (ProtectedDeletion, RestrictedDeletion):
                protected = True
            if token is None:
                payload['expires'] = int(now.timestamp()) + 300
                return {'ids': ids, 'confirmation_token': self.signer.dumps(payload, 'staff.delete-confirmation'),
                        'protected': protected, 'summary': 'Protected related records prevent deletion.' if protected else f'Delete {len(ids)} records.'}
            try:
                supplied = self.signer.loads(token, 'staff.delete-confirmation', max_length=16384)
            except wire.APIError:
                raise conflict() from None
            if (not isinstance(supplied, dict) or set(supplied) != set(payload) | {'expires'}
                    or type(supplied['expires']) is not int or supplied['expires'] <= int(now.timestamp())
                    or any(supplied[k] != value for k, value in payload.items()) or protected):
                raise conflict()
            for row in rows:
                audit(s, identity.user_id, resource, row, 'deleted')
            result = [reads.dto(uow, resource, row) for row in rows]
            s.flush()
            if resource == 'users':
                # Legacy-compatible auth cleanup after the combined PROTECT preflight.
                s.execute(sa.delete(TargetSession).where(TargetSession.user_id.in_(ids)))
            delete_collected(s, table, ids)
            uow.commit()
            return result
