"""Rehearse target API, PostgreSQL and edge with owned disposable containers.

Uses retained synthetic build inputs, not production data. Requires existing
locally built API and pinned PostgreSQL/edge images. Never pulls or deploys.
Actual HTTP/auth/proxy checks and cleanup determine the scoped result.
"""
import argparse,importlib.util,json,os,secrets,shutil,socket,subprocess,sys,time,uuid,ipaddress
from pathlib import Path
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.verify_public_block import source_snapshot,assert_source_unchanged
import sqlalchemy as sa
from sqlalchemy.engine import URL
import httpx
from backend.content.bootstrap import bootstrap_sources
from backend.content.releases import ReleaseStore,Descriptor
from backend.content.synthetic_setup import activate_initial
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.upgrade import fresh
from backend.models.baseline import ContentPage,User,StudentProfile,MediaAsset
from backend.users.bootstrap import seed_permissions
from backend.users.passwords import encode

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--disposable',action='store_true',required=True)
parser.add_argument('--runtime-root',type=Path,required=True)
parser.add_argument('--source-runtime',type=Path,required=True)
parser.add_argument('--artifact-root',type=Path,required=True)
parser.add_argument('--api-image',required=True)
parser.add_argument('--edge-image',required=True)
parser.add_argument('--docker',default=shutil.which('docker'))
parser.add_argument('--pg-port',type=int,default=55442)
args=parser.parse_args()
if not args.docker or importlib.util.find_spec('django') or importlib.util.find_spec('rest_framework'):
 parser.error('Docker CLI and separate no-Django target environment required')
docker=args.docker; directory=args.runtime_root.resolve()
source=args.source_runtime.resolve(); build=args.artifact_root.resolve()
if directory.exists() or not directory.is_relative_to(ROOT/'var'):
 parser.error('New owned runtime directory under checkout var/ required')
if any(not path.is_relative_to(ROOT/'var') or not path.is_dir() for path in (source,build)):
 parser.error('Retained synthetic source/runtime and build directories under var/ required')
if not 1024<=args.pg_port<=65535:parser.error('Unprivileged loopback PG port required')
manifest=json.loads((build/'output-manifest.json').read_text(encoding='utf-8'))
from urllib.parse import urlsplit
public=urlsplit(manifest['origin'])
if public.scheme!='http' or public.hostname!='127.0.0.1' or not public.port or public.username or public.password or public.path or public.query or public.fragment:
 parser.error('Synthetic build origin must be explicit loopback HTTP with port')
run_id=uuid.uuid4().hex[:12]
source_before=source_snapshot(ROOT)
directory.mkdir(parents=True)
prepared=json.loads((source/'prepare-result.json').read_text(encoding='utf-8'))
artifact=sha256((build/'output-manifest.json').read_bytes()).hexdigest()
release=ReleaseStore(source/'releases').load(Descriptor(uuid.UUID(int=0),prepared['release_id'],prepared['manifest_digest'],1))
origin=manifest['origin']; pgport=args.pg_port
for port in (public.port,pgport):
 with socket.socket() as listener:
  listener.bind(('127.0.0.1',port))
image=args.api_image
label='disposable-image-rehearsal'; names={kind:'mathstart-image-'+kind+'-'+run_id for kind in ('api','db','net','front','edge','public','copy','client')}
owned={}; engine=None; result={'status':'IN_PROGRESS','scope':'Containerized API/PG/read-only public volume + actual login/logout; retained synthetic inputs, not final QA','assertions':[]}
password=secrets.token_urlsafe(32); signing=secrets.token_urlsafe(48); account_password=secrets.token_urlsafe(28)
pg_env=directory/'private-postgres.env'; api_env=directory/'private-api.env'; client_env=directory/'private-client.env'
def command(args,timeout=120,log=None):
 r=subprocess.run([docker,*args],capture_output=True,timeout=timeout)
 if log: (directory/log).write_bytes(r.stdout+r.stderr)
 if r.returncode:
  diagnostic=(r.stdout+r.stderr).decode('utf-8',errors='replace')
  for secret in (password,signing,account_password):diagnostic=diagnostic.replace(secret,'[REDACTED]')
  (directory/'docker-failure.log').write_text(diagnostic,encoding='utf-8')
  raise RuntimeError('Owned Docker command failed')
 return r.stdout.decode('utf-8').strip()
def inspected(kind,identity):
 return json.loads(command([kind,'inspect',identity]))[0]
def check(condition,name):
 if not condition: raise AssertionError(name)
 result['assertions'].append(name)
try:
 result['source_before']=source_before
 result['images']={name:json.loads(command(['image','inspect',reference]))[0]['Id'] for name,reference in [('api',image),('postgres','postgres@sha256:efedf3595f1d6f415c08568ba171029bf54052e754cc9f030e3f2412b21f3d67'),('edge',args.edge_image)]}
 owned['net']=command(['network','create','--internal','--label','mathstart.purpose='+label,names['net']])
 owned['front']=command(['network','create','--label','mathstart.purpose='+label,names['front']])
 subnet=ipaddress.ip_network(inspected('network',owned['net'])['IPAM']['Config'][0]['Subnet'])
 assert subnet.version==4 and subnet.num_addresses>12
 edge_ip=str(subnet.network_address+10)
 if subprocess.run([docker,'volume','inspect',names['public']],capture_output=True,timeout=10).returncode==0: raise RuntimeError('Volume name already occupied')
 command(['volume','create','--label','mathstart.purpose='+label,names['public']]);owned['public']=names['public']
 database='test_ms7_mig_v01_image_'+run_id
 pg_env.write_text('POSTGRES_USER=image_test\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_DB='+database+'\n',encoding='utf-8')
 owned['db']=command(['run','--detach','--name',names['db'],'--label','mathstart.purpose='+label,'--network',names['front'],'--publish','127.0.0.1:'+str(pgport)+':5432','--tmpfs','/var/lib/postgresql/data','--env-file',str(pg_env),'postgres@sha256:efedf3595f1d6f415c08568ba171029bf54052e754cc9f030e3f2412b21f3d67'])
 command(['network','connect','--alias',names['db'],names['net'],owned['db']])
 url=URL.create('postgresql+psycopg',username='image_test',password=password,host='127.0.0.1',port=pgport,database=database)
 engine=sa.create_engine(url,hide_parameters=True,connect_args={'connect_timeout':3})
 for _ in range(40):
  try:
   with engine.connect() as c:c.execute(sa.text('SELECT 1'))
   break
  except sa.exc.OperationalError:time.sleep(1)
 else:raise RuntimeError('Owned image PG did not start')
 with engine.begin() as c:
  c.execute(sa.text('COMMENT ON DATABASE '+c.dialect.identifier_preparer.quote(database)+" IS 'MS7-MIG-V01 disposable synthetic test database'"));fresh(c)
 with UnitOfWork(engine) as uow:
  bootstrap_sources(uow.session,ROOT);seed_permissions(uow.session)
  rows=list(uow.session.scalars(sa.select(ContentPage)))
  check({row.id for row in rows}==set(release.pages),'fixture_exact_page_ids')
  from datetime import datetime
  for row in rows:
   page=release.pages[row.id]
   check(all(getattr(row,k)==page[k] for k in ('slug','title','body_html')),'fixture_page_'+str(row.id))
   uow.session.execute(sa.update(ContentPage.__table__).where(ContentPage.__table__.c.id==row.id).values(created_at=datetime.fromisoformat(page['created_at']),updated_at=datetime.fromisoformat(page['updated_at'])))
  user=User(username='image_fixture_'+run_id,password=encode(account_password),is_active=True,is_staff=True,is_superuser=True)
  uow.session.add(user);uow.session.flush();user_id=user.id
  uow.session.add(StudentProfile(user_id=user.id,onboarding_complete=False,onboarding_mode=None,selected_grade_id=None))
  page_ids={row.slug:row.id for row in rows}
  media=json.loads((ROOT/'site_content/media.json').read_text(encoding='utf-8'))['assets']
  for item in media:
   check(sha256((ROOT/'site_content/media'/item['file']).read_bytes()).hexdigest()==item['sha256'],'media_'+item['file'])
   uow.session.add(MediaAsset(title=item['title'],file=item['file'],alt_text=item['alt_text'],related_page_id=page_ids.get(item['related_page'])))
  uow.commit()
 result['phase']='activate_exact_fixture'
 activate_initial(engine,source/'releases',prepared['release_id'],prepared['receipt_digest'],build,artifact,origin)
 result['phase']='copy_verified_public_volume'
 copy_code="import os,shutil,sys; r=sys.argv[1]; shutil.copytree('/inputs/'+r,'/published/releases/'+r); shutil.copytree('/frontend','/published/frontend/'+r); [os.chown(os.path.join(p,n),10001,10001,follow_symlinks=False) for p,ds,fs in os.walk('/published') for n in ds+fs]; os.chown('/published',10001,10001)"
 owned['copy']=command(['run','--detach','--name',names['copy'],'--label','mathstart.purpose='+label,'--network','none','--no-healthcheck','--user','0','--mount','type=bind,source='+str(source/'releases')+',target=/inputs,readonly','--mount','type=bind,source='+str(build)+',target=/frontend,readonly','--mount','type=volume,source='+names['public']+',target=/published','--entrypoint','python',image,'-c',copy_code,prepared['release_id']])
 check(command(['wait',owned['copy']],timeout=180)=='0','public_copy_completed')
 command(['logs',owned['copy']],log='volume-copy.log');command(['rm',owned['copy']]);del owned['copy']
 api_url=url.set(host=names['db'],port=5432)
 env={'MATHSTART_DATABASE_URL':api_url.render_as_string(hide_password=False),'MATHSTART_DB_BACKEND':'postgresql','MATHSTART_HTTP_SIGNING_KEY':signing,'MATHSTART_PUBLIC_ORIGIN':origin,'MATHSTART_RELEASE_ROOT':'/runtime/releases','MATHSTART_PUBLIC_ARTIFACT_ROOT':'/runtime/frontend','MATHSTART_PUBLIC_ARTIFACT_DIGESTS':json.dumps({prepared['release_id']:artifact})}
 api_env.write_text(''.join(k+'='+v+'\n' for k,v in env.items()),encoding='utf-8')
 result['phase']='start_internal_api'
 owned['api']=command(['run','--detach','--name',names['api'],'--label','mathstart.purpose='+label,'--network',names['net'],'--network-alias','api','--read-only','--cap-drop','ALL','--tmpfs','/tmp:rw,nosuid,noexec,size=32m','--env-file',str(api_env),'--mount','type=volume,source='+names['public']+',target=/runtime,readonly',image,'python','-m','uvicorn','backend.content.public_runtime:application','--factory','--host','0.0.0.0','--port','8000','--workers','2','--no-access-log','--proxy-headers','--forwarded-allow-ips',edge_ip])
 result['phase']='start_nonroot_edge'
 edge_image=args.edge_image
 command(['image','inspect',edge_image],log='edge-image.json')
 owned['edge']=command(['create','--name',names['edge'],'--label','mathstart.purpose='+label,'--network',names['front'],'--read-only','--cap-drop','ALL','--user','101:101','--tmpfs','/tmp:rw,nosuid,noexec,size=16m,uid=101,gid=101','--publish','127.0.0.1:'+str(public.port)+':8080','--entrypoint','nginx',edge_image,'-g','daemon off;'])
 command(['network','connect','--ip',edge_ip,names['net'],owned['edge']])
 command(['start',owned['edge']])
 result['phase']='real_http_proxy_auth_checks'
 with httpx.Client(trust_env=False,follow_redirects=False,timeout=10) as client:
  deadline=time.monotonic()+90
  while time.monotonic()<deadline:
   if not inspected('container',owned['edge'])['State']['Running']:raise RuntimeError('Owned edge exited before readiness')
   if not inspected('container',owned['api'])['State']['Running']:raise RuntimeError('Owned API exited before readiness')
   try:
    home=client.get(origin+'/')
    if home.status_code==200:break
   except httpx.RequestError:pass
   time.sleep(.5)
  else:raise RuntimeError('Owned API image did not become ready')
  check(home.content==(build/'index.html').read_bytes(),'actual_container_public_html_matches_build')
  check(home.headers.get('cache-control')=='no-cache','public_revalidation')
  asset_url=next(iter(release.assets));asset=client.get(origin+asset_url)
  check(asset.status_code==200 and asset.content==release.assets[asset_url][1],'edge_source_asset_bytes')
  check(client.get(origin+asset_url,headers={'If-None-Match':asset.headers['etag']}).status_code==304,'edge_source_etag_304')
  check(client.get(origin+'/_private/shell.html').status_code==404,'edge_no_private_file_bypass')
  index=client.get(origin+'/_content/index.json');check(index.content==release.index_raw,'same_release_index')
  grades=client.get(origin+'/api/v1/grades/');check(grades.status_code==200 and len(grades.json()['data'])==6,'real_grade_api')
  csrf=client.get(origin+'/api/v1/auth/csrf/');check(csrf.status_code==200,'real_csrf_bootstrap')
  token=csrf.json()['data']['csrf_token']
  login=client.post(origin+'/api/v1/auth/login/',json={'username':'image_fixture_'+run_id,'password':account_password},headers={'Origin':origin,'X-CSRFToken':token,'X-Forwarded-For':'198.51.100.11','Forwarded':'for=198.51.100.11;proto=https'})
  check(login.status_code==200 and login.json()['data']['id']==user_id,'real_container_password_login')
  me=client.get(origin+'/api/v1/users/me/');check(me.status_code==200 and me.json()['data']['id']==user_id,'opaque_session_across_workers')
  token=client.get(origin+'/api/v1/auth/csrf/').json()['data']['csrf_token']
  rotated=client.post(origin+'/api/v1/auth/login/',json={'username':'image_fixture_'+run_id,'password':account_password},headers={'Origin':origin,'X-CSRFToken':token,'X-Forwarded-For':'198.51.100.12'})
  check(rotated.status_code==200,'second_real_worker_login')
  with engine.connect() as c:
   budgets=list(c.execute(sa.text('SELECT count FROM users_loginwindow')))
  check(len(budgets)==1 and budgets[0][0]==2,'spoofed_forwarded_ip_cannot_split_shared_login_budget')
  client_env.write_text('MATHSTART_TEST_USERNAME=image_fixture_'+run_id+'\nMATHSTART_TEST_PASSWORD='+account_password+'\n',encoding='utf-8')
  client_code="import os,sys,httpx; url='http://'+sys.argv[1]+':8080'; c=httpx.Client(trust_env=False,timeout=10,headers={'Host':sys.argv[2]}); r=c.get(url+'/api/v1/auth/csrf/'); assert r.status_code==200; token=r.json()['data']['csrf_token']; r=c.post(url+'/api/v1/auth/login/',json={'username':os.environ['MATHSTART_TEST_USERNAME'],'password':os.environ['MATHSTART_TEST_PASSWORD']},headers={'Origin':'http://'+sys.argv[2],'X-CSRFToken':token,'X-Forwarded-For':'198.51.100.11'}); assert r.status_code==200; c.close(); print('CLIENT_LOGIN_OK')"
  owned['client']=command(['run','--detach','--name',names['client'],'--label','mathstart.purpose='+label,'--network',names['front'],'--no-healthcheck','--read-only','--cap-drop','ALL','--env-file',str(client_env),'--entrypoint','python',image,'-c',client_code,names['edge'],public.netloc])
  check(command(['wait',owned['client']],timeout=60)=='0','independent_tcp_client_real_login')
  command(['logs',owned['client']],log='independent-client.log');command(['rm',owned['client']]);del owned['client']
  with engine.connect() as c:budgets=list(c.execute(sa.text('SELECT count FROM users_loginwindow')))
  check(sorted(row[0] for row in budgets)==[1,2],'legitimate_clients_get_distinct_shared_pg_budgets')
  private=client.get(origin+'/admin/auth/user/');check(private.status_code==200 and 'no-store' in private.headers.get('cache-control',''),'private_compiled_shell')
  token=client.get(origin+'/api/v1/auth/csrf/').json()['data']['csrf_token']
  denied=client.post(origin+'/api/v1/auth/logout/',json={},headers={'Origin':'https://untrusted.example','X-CSRFToken':token})
  check(denied.status_code==403 and client.get(origin+'/api/v1/users/me/').status_code==200,'untrusted_origin_denied_without_logout')
  logged_out=client.post(origin+'/api/v1/auth/logout/',json={},headers={'Origin':origin,'X-CSRFToken':token})
  check(logged_out.status_code==200 and client.get(origin+'/api/v1/users/me/').status_code==401,'real_logout_revokes_session')
 check(command(['exec',owned['api'],'python','-m','backend.health'])=='READY','actual_image_readiness')
 result.update(status='PASS',edge_image=edge_image,edge_allowlisted_ip=edge_ip,api_internal_network=True,pg_host_seed_loopback_port=pgport,pages=279,media=29,workers=2,output_manifest_digest=artifact,api_image=image)
except Exception as error:
 result.update(status='FAIL',failure_class=type(error).__name__)
 if isinstance(error,(AssertionError,RuntimeError)):result['failure_check']=str(error)
finally:
 if engine is not None:engine.dispose()
 errors=[]
 for key in ('client','edge','api','copy','db'):
  if key not in owned:continue
  try:
   state=inspected('container',owned[key]);assert state['Id']==owned[key] and state['Name']=='/'+names[key] and state['Config']['Labels']['mathstart.purpose']==label
   if key in ('api','edge'):command(['logs',owned[key]],log=key+'.log')
   command(['stop',owned[key]],timeout=30);command(['rm',owned[key]],timeout=30)
  except Exception as error:errors.append(type(error).__name__)
 for key,kind in (('public','volume'),('net','network'),('front','network')):
  if key not in owned:continue
  try:
   state=inspected(kind,owned[key]);assert state['Labels']['mathstart.purpose']==label
   command([kind,'rm',owned[key]],timeout=30)
  except Exception as error:errors.append(type(error).__name__)
 for private in (pg_env,api_env,client_env):
  if private.exists():private.unlink()
 try:result['source_after']=assert_source_unchanged(source_before,ROOT)
 except Exception as error:errors.append('SourceChanged')
 result['cleanup']='PASS' if not errors else 'FAIL';result['cleanup_errors']=errors
 if errors:result['status']='FAIL'
 result['assertions_count']=len(result['assertions'])
 (directory/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps({'status':result['status'],'failure_class':result.get('failure_class'),'assertions':result['assertions_count'],'cleanup':result['cleanup'],'result':str(directory.relative_to(ROOT)/'result.json')}))
raise SystemExit(0 if result['status']=='PASS' else 1)
