"""MS-T009 only: real PG, synthetic users, injected fake mail, no live send."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import os
import unittest
import sqlalchemy as sa
from starlette.testclient import TestClient
from backend.infrastructure.http.app import create_app
from backend.infrastructure.http.signing import Signer
from backend.migrations.upgrade import require_disposable
from backend.models.baseline import User, metadata
from backend.models.identity import account, token, window
from backend.users.service import IdentityService
from backend.users.security import Security
from backend.users.mail import FakeMail, UnconfiguredMail
from backend.users import passwords

ORIGIN='https://mathstart.example'
PASSWORD='A long mathematical phrase! 5972'
NEW='Another mathematical phrase! 6429'
class AccountSecurityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.engine=sa.create_engine(os.environ['MATHSTART_V03_DATABASE_URL'],hide_parameters=True)
  with cls.engine.begin() as c: require_disposable(c)
 @classmethod
 def tearDownClass(cls):cls.engine.dispose()
 def setUp(self):
  with self.engine.begin() as c:
   c.execute(sa.text('TRUNCATE identity_request_window,identity_security_event,auth_user RESTART IDENTITY CASCADE'))
  self.mail=FakeMail();self.security=Security(self.engine,'synthetic-key-for-account-tests',ORIGIN)
  self.service=IdentityService(self.security,self.mail)
  self.app=create_app(self.engine,Signer(self.security.key),identity_service=self.service,public_origin=ORIGIN)
  self.client=self.client_for()
 def tearDown(self):self.client.close()
 def client_for(self):return TestClient(self.app,base_url=ORIGIN)
 def headers(self,client=None):
  client=client or self.client
  return {'Origin':ORIGIN,'X-CSRFToken':client.get('/api/v1/auth/csrf/').json()['data']['csrf_token']}
 def register(self,name='student',client=None):
  client=client or self.client
  return client.post('/api/v1/auth/register/',json={'username':name,'password':PASSWORD},headers={**self.headers(client),'Idempotency-Key':'register-'+name})
 def post(self,action,body,client=None):
  client=client or self.client
  return client.post('/api/v1/account/'+action+'/',json=body,headers=self.headers(client))
 def add_email(self,address='study@example.test'):
  r=self.post('email',{'current_password':PASSWORD,'email':address});self.assertEqual(r.status_code,200,r.text)
  return self.mail.messages[-1][2].split('#token=')[1]
 def test_confirm_recover_reset_revokes_sessions_single_use(self):
  self.assertEqual(self.register().status_code,201)
  raw=self.add_email()
  self.assertFalse(self.client.get('/api/v1/account/state/').json()['data']['email_verified'])
  self.assertEqual(self.post('recover',{'username':'student'}).status_code,200)
  self.assertEqual(len(self.mail.messages),1) # unverified does not recover
  self.assertEqual(self.post('verify',{'token':raw}).status_code,200)
  self.assertEqual(self.post('verify',{'token':raw}).status_code,400)
  self.assertEqual(self.post('recover',{'username':'student'}).status_code,200)
  reset=self.mail.messages[-1][2].split('#token=')[1]
  self.assertEqual(self.post('reset',{'token':reset,'new_password':NEW}).status_code,200)
  self.assertEqual(self.client.get('/api/v1/users/me/').status_code,401)
  self.assertEqual(self.post('reset',{'token':reset,'new_password':PASSWORD}).status_code,400)
  r=self.client.post('/api/v1/auth/login/',json={'username':'student','password':NEW},headers=self.headers())
  self.assertEqual(r.status_code,200,r.text)
 def test_owner_csrf_and_closed_dto(self):
  self.register();raw=self.add_email()
  with self.client_for() as other:
   self.register('anotherStudent',other)
   self.assertEqual(self.post('verify',{'token':raw},other).status_code,403)
  r=self.client.post('/api/v1/account/email/',json={'email':'other@example.test','current_password':PASSWORD})
  self.assertEqual(r.status_code,403)
  self.assertEqual(self.post('email',{'email':'other@example.test','current_password':PASSWORD,'user_id':'2'}).status_code,400)
  self.assertEqual(self.post('email',{'email':'other@example.test','current_password':'bad'}).status_code,401)
 def test_expiry_change_delete_revoke_tokens_and_no_get_consumption(self):
  self.register();raw=self.add_email()
  self.assertEqual(self.client.get('/api/v1/account/verify/').status_code,405)
  with self.engine.begin() as c:c.execute(token.update().values(expires_at=sa.func.clock_timestamp()-timedelta(seconds=1)))
  self.assertEqual(self.post('verify',{'token':raw}).status_code,400)
  raw=self.add_email('new@example.test')
  self.assertEqual(self.post('email',{'email':'','current_password':PASSWORD}).status_code,200)
  self.assertEqual(self.post('verify',{'token':raw}).status_code,400)
 def test_password_and_logout_all_reauthentication_revocation(self):
  self.register()
  with self.client_for() as other:
   self.assertEqual(other.post('/api/v1/auth/login/',json={'username':'student','password':PASSWORD},headers=self.headers(other)).status_code,200)
   self.assertEqual(self.post('password',{'current_password':PASSWORD,'new_password':NEW}).status_code,200)
   self.assertEqual(other.get('/api/v1/users/me/').status_code,401)
  self.assertEqual(self.client.get('/api/v1/users/me/').status_code,401)
  self.client.post('/api/v1/auth/login/',json={'username':'student','password':NEW},headers=self.headers())
  self.assertEqual(self.post('sessions',{'current_password':NEW}).status_code,200)
  self.assertEqual(self.client.get('/api/v1/users/me/').status_code,401)
 def test_new_policy_legacy_login_and_maximum(self):
  self.assertEqual(self.client.post('/api/v1/auth/register/',json={'username':'new','password':'old pass'},headers={**self.headers(),'Idempotency-Key':'short'}).status_code,400)
  with self.engine.begin() as c:
   c.execute(metadata.tables['auth_user'].insert().values(username='OldCase.'+'x'*40,password=passwords.encode('old pass'),email='same@example.test',first_name='',last_name='',is_active=True,is_staff=False,is_superuser=False))
  self.assertEqual(self.client.post('/api/v1/auth/login/',json={'username':'OldCase.'+'x'*40,'password':'old pass'},headers=self.headers()).status_code,200)
  self.assertFalse(passwords.verify('x'*4097,passwords.encode('old pass')))
 def test_atomic_budget_shared_workers_and_restart(self):
  def attempt(_):
   service=IdentityService(self.security,self.mail)
   try:service.account.budget('login','synthetic-school','target');return 200
   except Exception as e:return getattr(e,'status',500)
  with ThreadPoolExecutor(max_workers=12) as pool:results=list(pool.map(attempt,range(16)))
  self.assertEqual(results.count(200),10,results);self.assertEqual(results.count(429),6,results)
  # Separate students behind one school IP have independent pair budgets.
  self.service.account.budget('login','synthetic-school','another')
 def test_concurrent_token_only_one_winner(self):
  self.register();raw=self.add_email();self.post('verify',{'token':raw});self.post('recover',{'username':'student'})
  raw=self.mail.messages[-1][2].split('#token=')[1]
  def consume(_):
   try:self.service.account.consume('reset',{'token':raw,'new_password':NEW},None);return 200
   except Exception as e:return getattr(e,'status',500)
  with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(consume,range(2)))
  self.assertEqual(sorted(results),[200,400])
 def test_verified_uniqueness_and_old_email_not_trusted(self):
  self.register();raw=self.add_email();self.assertEqual(self.post('verify',{'token':raw}).status_code,200)
  with self.client_for() as other:
   self.register('secondStudent',other)
   self.assertEqual(self.post('email',{'current_password':PASSWORD,'email':'STUDY@example.test'},other).status_code,200)
   raw=self.mail.messages[-1][2].split('#token=')[1]
   self.assertEqual(self.post('verify',{'token':raw},other).status_code,409)
 def test_unconfigured_delivery_generic_response_privacy_headers(self):
  self.service.account.mail=UnconfiguredMail()
  for username in ['unknown','student']:
   r=self.post('recover',{'username':username});self.assertEqual(r.status_code,503)
   self.assertIn('no-store',r.headers['cache-control']);self.assertEqual(r.headers['referrer-policy'],'no-referrer')

 def test_forwarded_ip_requires_exact_trusted_peer(self):
  from starlette.requests import Request
  request=Request({'type':'http','headers':[(b'x-forwarded-for',b'203.0.113.7')],'client':('127.0.0.1',9000)})
  self.assertEqual(self.security.remote(request),'127.0.0.1')
  trusted=Security(self.engine,self.security.key,ORIGIN,trusted_proxies=['127.0.0.1/32'])
  self.assertEqual(trusted.remote(request),'203.0.113.7')
 def test_delivery_failure_does_not_enumerate_recovery_accounts(self):
  self.register();raw=self.add_email();self.post('verify',{'token':raw})
  def failure(*args):raise RuntimeError('synthetic provider failure')
  self.mail.send=failure
  for username in ['student','unknown']:
   self.assertEqual(self.post('recover',{'username':username}).status_code,200)
 def test_rate_retry_cleanup_and_cross_ip_login_budget(self):
  for i in range(100):self.service.account.budget('login','distributed-'+str(i),'victim')
  with self.assertRaises(Exception) as raised:self.service.account.budget('login','another-ip','victim')
  self.assertEqual(raised.exception.status,429);self.assertGreater(raised.exception.retry_after,0)
  self.service.account.budget('login','another-ip','differentStudent')
  for i in range(5):self.service.account.budget('recover','remote','someone')
  with self.assertRaises(Exception) as raised:self.service.account.budget('recover','other-remote','someone')
  self.assertEqual(raised.exception.status,429)
  with self.engine.begin() as c:c.execute(window.update().values(started_at=sa.func.clock_timestamp()-timedelta(days=3)))
  self.service.account.budget('recover','remote','someone')
 def test_concurrent_failed_logins_audit_without_nested_connections(self):
  def failed(i):
   try:self.service.login({'username':'missing-'+str(i),'password':PASSWORD},'synthetic-ip',None);return 200
   except Exception as e:return getattr(e,'status',500)
  with ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(failed,range(8)))
  self.assertEqual(results,[401]*8)
  with self.engine.begin() as c:
   self.assertEqual(c.scalar(sa.text("SELECT count(*) FROM identity_security_event WHERE kind='login_failed'")),8)

if __name__=='__main__':unittest.main()
