"""Real disposable PostgreSQL coverage of baseline staff mutation contracts."""
import unittest
from datetime import timedelta
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import sqlalchemy as sa

from backend.infrastructure.uow import UnitOfWork
from backend.models.baseline import User, Permission, ContentType, Group, AdminLog, metadata
from backend.users.bootstrap import seed_permissions
from backend.tests.v03 import test_identity as identity_fixture
PASSWORD = identity_fixture.PASSWORD


class StaffWriteTests(unittest.TestCase):
    setUpClass = classmethod(identity_fixture.PostgreSQLIdentityTests.setUpClass.__func__)
    tearDownClass = classmethod(identity_fixture.PostgreSQLIdentityTests.tearDownClass.__func__)
    tearDown = identity_fixture.PostgreSQLIdentityTests.tearDown
    headers = identity_fixture.PostgreSQLIdentityTests.headers
    register = identity_fixture.PostgreSQLIdentityTests.register

    def setUp(self):
        identity_fixture.PostgreSQLIdentityTests.setUp(self)
        with self.engine.begin() as connection:
            connection.execute(sa.text('TRUNCATE auth_group RESTART IDENTITY CASCADE'))
        result = self.register(username='syntheticOperator')
        self.assertEqual(result.status_code, 201)
        self.actor = result.json()['data']['id']
        with UnitOfWork(self.engine) as uow:
            seed_permissions(uow.session)
            actor = uow.session.get(User, self.actor)
            actor.is_staff, actor.is_superuser = True, True
            uow.commit()

    def post(self, path, body):
        return self.client.post('/api/v1/staff/' + path, json=body, headers=self.headers())

    def create_user(self, name='syntheticManaged'):
        result = self.post('users/', {'username': name, 'usable_password': True,
                                    'password1': PASSWORD, 'password2': PASSWORD})
        self.assertEqual(result.status_code, 201, result.text)
        self.assertNotIn('password', result.json()['data'])
        self.assertEqual(result.json()['meta']['version'], 'migration-r02-v1')
        return result.json()['data']

    def test_user_group_update_permissions_history_and_no_private_hash(self):
        user = self.create_user()
        group = self.post('groups/', {'name': 'synthetic group', 'permissions': []})
        self.assertEqual(group.status_code, 201, group.text)
        body = {k: v for k, v in user.items() if k not in {'id', 'has_usable_password'}}
        body.update(groups=[group.json()['data']['id']], first_name='Synthetic', is_staff=True)
        result = self.client.put(f"/api/v1/staff/users/{user['id']}/", json=body, headers=self.headers())
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(result.json()['data']['groups'], body['groups'])
        history = self.client.get(f"/api/v1/staff/users/{user['id']}/history/")
        self.assertEqual(history.status_code, 200, history.text)
        self.assertEqual(len(history.json()['data']), 2)
        self.assertNotIn('password', history.text)

    def test_combined_create_permissions_checked_on_server(self):
        permission_table = metadata.tables['auth_user_user_permissions']
        for selected in [('add_user',), ('change_user',), ()]:
            with self.subTest(permissions=selected):
                with UnitOfWork(self.engine) as uow:
                    uow.session.get(User, self.actor).is_superuser = False
                    uow.session.execute(sa.delete(permission_table).where(permission_table.c.user_id == self.actor))
                    ids = list(uow.session.scalars(sa.select(Permission.id).join(ContentType).where(
                        ContentType.app_label == 'auth', Permission.codename.in_(selected))))
                    for permission_id in ids:
                        uow.session.execute(sa.insert(permission_table).values(user_id=self.actor, permission_id=permission_id))
                    uow.commit()
                result = self.post('users/', {'username': 'denied', 'usable_password': False})
                self.assertEqual(result.status_code, 403, result.text)
                with UnitOfWork(self.engine) as uow:
                    self.assertIsNone(uow.session.scalar(sa.select(User).where(User.username == 'denied')))
        # Positive control: rejecting every request would not preserve this gate.
        with UnitOfWork(self.engine) as uow:
            ids = list(uow.session.scalars(sa.select(Permission.id).join(ContentType).where(
                ContentType.app_label == 'auth', Permission.codename.in_(['add_user', 'change_user']))))
            self.assertEqual(len(ids), 2)
            for permission_id in ids:
                uow.session.execute(sa.insert(permission_table).values(user_id=self.actor, permission_id=permission_id))
            uow.commit()
        allowed = self.post('users/', {'username': 'allowed_both', 'usable_password': False})
        self.assertEqual(allowed.status_code, 201, allowed.text)

    def test_password_change_revokes_detached_bridge_without_target_lineage(self):
        from backend.models.protocol import ReceiptBridge
        user = self.create_user()
        import uuid
        with self.engine.begin() as c:
            now = c.scalar(sa.select(sa.func.clock_timestamp()))
            c.execute(sa.insert(ReceiptBridge).values(id=uuid.uuid4(), original_scope='bootstrap:' + 'e' * 64,
                bootstrap_fingerprint='e' * 64, owner_user_id=user['id'], state='DETACHED', session_id=None,
                session_lineage_id=None, revocation_epoch=0, created_at=now,
                replay_until=now + timedelta(days=7), ticket_version=0,
                transfer_binding_digest='f' * 64))
        response = self.post(f"users/{user['id']}/password/", {'usable_password': True,
            'password1': 'Reviewed:new-pass!9237', 'password2': 'Reviewed:new-pass!9237'})
        self.assertEqual(response.status_code, 200, response.text)
        with self.engine.connect() as c:
            row = c.execute(sa.select(ReceiptBridge.state, ReceiptBridge.transfer_binding_digest).where(
                ReceiptBridge.owner_user_id == user['id'])).one()
            self.assertEqual(tuple(row), ('REVOKED', None))

    def test_deactivation_revokes_imported_bridge_before_possible_reactivation(self):
        from backend.models.protocol import ReceiptBridge
        import uuid
        user = self.create_user()
        with self.engine.begin() as c:
            now = c.scalar(sa.select(sa.func.clock_timestamp()))
            c.execute(sa.insert(ReceiptBridge).values(id=uuid.uuid4(), original_scope='bootstrap:' + 'd' * 64,
                bootstrap_fingerprint='d' * 64, owner_user_id=user['id'], state='DETACHED', session_id=None,
                session_lineage_id=None, revocation_epoch=0, created_at=now,
                replay_until=now + timedelta(days=7), ticket_version=0, transfer_binding_digest='f' * 64))
        body = {key: value for key, value in user.items() if key not in {'id', 'has_usable_password'}}
        for active in (False, True):
            response = self.client.put(f"/api/v1/staff/users/{user['id']}/", json={**body, 'is_active': active}, headers=self.headers())
            self.assertEqual(response.status_code, 200, response.text)
        with self.engine.connect() as c:
            row = c.execute(sa.select(ReceiptBridge.state, ReceiptBridge.transfer_binding_digest,
                ReceiptBridge.revocation_epoch).where(ReceiptBridge.owner_user_id == user['id'])).one()
            self.assertEqual(tuple(row), ('REVOKED', None, 1))

    def test_private_ui_capabilities_preserve_combined_gate_and_content_readonly(self):
        from backend.staff.presentation import capabilities
        from backend.staff.authorization import AuthenticatedIdentity
        with UnitOfWork(self.engine) as uow:
            scope = capabilities(uow, AuthenticatedIdentity(self.actor))
            self.assertTrue(scope['own_password'])
            self.assertTrue(scope['resources']['users']['add'])
            self.assertTrue(scope['resources']['groups']['delete'])
            for name in ['grades', 'subjects', 'sections', 'pages', 'publications', 'media_assets', 'redirects']:
                self.assertEqual(scope['resources'][name], {'view': True, 'add': False, 'change': False, 'delete': False})
            actor = uow.session.get(User, self.actor)
            actor.is_superuser = False
            p = uow.session.scalar(sa.select(Permission.id).join(ContentType).where(
                ContentType.app_label == 'auth', Permission.codename == 'add_user'))
            uow.session.execute(sa.insert(metadata.tables['auth_user_user_permissions']).values(user_id=self.actor, permission_id=p))
            uow.session.flush()
            self.assertFalse(capabilities(uow, AuthenticatedIdentity(self.actor))['resources']['users']['add'])
            p = uow.session.scalar(sa.select(Permission.id).join(ContentType).where(
                ContentType.app_label == 'auth', Permission.codename == 'change_user'))
            uow.session.execute(sa.insert(metadata.tables['auth_user_user_permissions']).values(user_id=self.actor, permission_id=p))
            self.assertTrue(capabilities(uow, AuthenticatedIdentity(self.actor))['resources']['users']['add'])
            actor.is_staff = False
            uow.session.flush()
            denied = capabilities(uow, AuthenticatedIdentity(self.actor))
            self.assertFalse(denied['own_password'])
            self.assertFalse(any(any(row.values()) for row in denied['resources'].values()))
            self.assertEqual(denied, capabilities(uow, None))

    def test_mutations_require_csrf_and_reject_unknown_duplicate_fields(self):
        self.assertEqual(self.client.post('/api/v1/staff/groups/', json={}).status_code, 403)
        headers = {**self.headers(), 'Content-Type': 'application/json'}
        for raw in [b'{"name":"x","permissions":[],"unknown":true}',
                    b'{"name":"x","name":"y","permissions":[]}', b'{"name":NaN,"permissions":[]}']:
            self.assertEqual(self.client.post('/api/v1/staff/groups/', content=raw, headers=headers).status_code, 400)

    def test_group_permission_revocation_serializes_with_another_actors_user_write(self):
        from backend.staff import writes
        from backend.infrastructure.http.signing import Signer
        from backend.infrastructure.http.transport import APIError
        from backend.models.protocol import TargetSession
        from backend.users.security import SessionIdentity
        managed = self.create_user('syntheticDelegatedStaff')
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            staff = s.get(User, managed['id'])
            staff.is_staff = True
            group = Group(name='Synthetic delegated authorization')
            s.add(group)
            s.flush()
            group_id = group.id
            permissions = list(s.scalars(sa.select(Permission.id).join(ContentType).where(
                ContentType.app_label == 'auth', Permission.codename.in_(['add_user', 'change_user']))))
            self.assertEqual(len(permissions), 2)
            s.execute(sa.insert(metadata.tables['auth_group_permissions']), [{'group_id': group_id, 'permission_id': p} for p in permissions])
            s.execute(sa.insert(metadata.tables['auth_user_groups']).values(user_id=staff.id, group_id=group_id))
            issued, _, _ = self.security.issue(s, staff, s.scalar(sa.select(sa.func.clock_timestamp())))
            actor = s.scalar(sa.select(TargetSession).where(TargetSession.user_id == self.actor, TargetSession.revoked_at.is_(None)))
            identity = lambda row: SessionIdentity(row.user_id, row.id, row.lineage_id, row.revocation_epoch)
            delegated, operator = identity(issued), identity(actor)
            uow.commit()
        service = writes.StaffWrites(self.service, Signer(identity_fixture.KEY))
        entered, proceed, revocation_started, revoked = Event(), Event(), Event(), Event()
        original = writes.permission
        def checked(scope, resource, action):
            original(scope, resource, action)
            if scope.user_id == managed['id'] and resource == 'users' and action == 'add':
                entered.set()
                if not proceed.wait(10):
                    raise RuntimeError('Concurrent authorization test coordination deadline')
        def revoke():
            revocation_started.set()
            result = service.mutate(operator, 'groups', 'update', {'name': 'Synthetic delegated authorization', 'permissions': []}, group_id)
            revoked.set()
            return result
        body = {'username': 'syntheticInFlightAllowed', 'usable_password': False}
        with patch.object(writes, 'permission', checked), ThreadPoolExecutor(max_workers=2) as executor:
            mutation = executor.submit(service.mutate, delegated, 'users', 'create', body)
            try:
                self.assertTrue(entered.wait(10))
                revocation = executor.submit(revoke)
                self.assertTrue(revocation_started.wait(10))
                self.assertFalse(revoked.wait(.25), 'Revocation overtook an authorized in-flight user mutation')
            finally:
                proceed.set()
            self.assertEqual(mutation.result(timeout=10)['username'], body['username'])
            self.assertEqual(revocation.result(timeout=10)['permissions'], [])
        with self.assertRaises(APIError) as denied:
            service.mutate(delegated, 'users', 'create', {**body, 'username': 'syntheticAfterRevocation'})
        self.assertEqual(denied.exception.status, 403)
        with UnitOfWork(self.engine) as uow:
            self.assertIsNone(uow.session.scalar(sa.select(User).where(User.username == 'syntheticAfterRevocation')))

    def test_password_change_revokes_other_sessions_and_returns_no_secret(self):
        user = self.create_user()
        result = self.post(f"users/{user['id']}/password/", {'usable_password': True,
                            'password1': 'Qm9!Vx2#Lr7@Zh4%', 'password2': 'Qm9!Vx2#Lr7@Zh4%'})
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(result.json()['data']['id'], user['id'])
        self.assertNotIn('password', result.json()['data'])

    def test_own_password_change_keeps_new_cookie_and_revokes_old(self):
        old_cookie = self.client.cookies.get('sessionid')
        result = self.post('password_change/', {'old_password': PASSWORD,
                           'new_password1': 'Changed:synthetic!9527', 'new_password2': 'Changed:synthetic!9527'})
        self.assertEqual(result.status_code, 200, result.text)
        self.assertNotEqual(self.client.cookies.get('sessionid'), old_cookie)
        self.assertEqual(self.client.get('/api/v1/users/me/').status_code, 200)

    def test_delete_preview_stale_confirmation_and_combined_bulk(self):
        users = [self.create_user('syntheticDeleteA'), self.create_user('syntheticDeleteB')]
        ids = [user['id'] for user in users]
        path = '/api/v1/staff/users/delete_selected/'
        preview = self.client.get(path, params=[('ids', str(pk)) for pk in ids])
        self.assertEqual(preview.status_code, 200, preview.text)
        self.assertFalse(preview.json()['data']['protected'])
        with UnitOfWork(self.engine) as uow:
            uow.session.get(User, ids[0]).first_name = 'changed after preview'
            uow.commit()
        body = {'ids': ids, 'confirmation_token': preview.json()['data']['confirmation_token']}
        self.assertEqual(self.client.post(path, json=body, headers=self.headers()).status_code, 409)
        preview = self.client.get(path, params=[('ids', str(pk)) for pk in ids])
        body['confirmation_token'] = preview.json()['data']['confirmation_token']
        result = self.client.post(path, json=body, headers=self.headers())
        self.assertEqual(result.status_code, 200, result.text)
        with UnitOfWork(self.engine) as uow:
            self.assertEqual(list(uow.session.scalars(sa.select(User.id).where(User.id.in_(ids)))), [])

    def test_protected_actor_cannot_be_bulk_deleted(self):
        user = self.create_user()
        ids = [self.actor, user['id']]
        preview = self.client.get('/api/v1/staff/users/delete_selected/', params=[('ids', str(pk)) for pk in ids])
        self.assertEqual(preview.status_code, 200, preview.text)
        self.assertTrue(preview.json()['data']['protected'])
        result = self.post('users/delete_selected/', {'ids': ids, 'confirmation_token': preview.json()['data']['confirmation_token']})
        self.assertEqual(result.status_code, 409, result.text)
        with UnitOfWork(self.engine) as uow:
            self.assertEqual(len(list(uow.session.scalars(sa.select(User.id).where(User.id.in_(ids))))), 2)


if __name__ == '__main__':
    unittest.main()
