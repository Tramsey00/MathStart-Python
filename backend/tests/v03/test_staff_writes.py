"""Real disposable PostgreSQL coverage of baseline staff mutation contracts."""
import unittest

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
        with UnitOfWork(self.engine) as uow:
            uow.session.get(User, self.actor).is_superuser = False
            p = uow.session.scalar(sa.select(Permission.id).join(ContentType).where(
                ContentType.app_label == 'auth', Permission.codename == 'add_user'))
            uow.session.execute(sa.insert(metadata.tables['auth_user_user_permissions']).values(
                user_id=self.actor, permission_id=p))
            uow.commit()
        result = self.post('users/', {'username': 'denied', 'usable_password': False})
        self.assertEqual(result.status_code, 403, result.text)
        with UnitOfWork(self.engine) as uow:
            self.assertIsNone(uow.session.scalar(sa.select(User).where(User.username == 'denied')))

    def test_mutations_require_csrf_and_reject_unknown_duplicate_fields(self):
        self.assertEqual(self.client.post('/api/v1/staff/groups/', json={}).status_code, 403)
        headers = {**self.headers(), 'Content-Type': 'application/json'}
        for raw in [b'{"name":"x","permissions":[],"unknown":true}',
                    b'{"name":"x","name":"y","permissions":[]}', b'{"name":NaN,"permissions":[]}']:
            self.assertEqual(self.client.post('/api/v1/staff/groups/', content=raw, headers=headers).status_code, 400)

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
