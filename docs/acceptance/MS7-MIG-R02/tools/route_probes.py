import json
import os
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root))
assert os.environ['DJANGO_DB_PORT']=='55439'
os.environ['DJANGO_SETTINGS_MODULE']='config.settings'
import django;django.setup()
from django.test import Client,override_settings
from django.test.utils import CaptureQueriesContext
from django.db import connection
rows=[]
with override_settings(SECURE_SSL_REDIRECT=False,SESSION_COOKIE_SECURE=False,CSRF_COOKIE_SECURE=False,ALLOWED_HOSTS=['testserver']):
    client=Client(enforce_csrf_checks=True)
    csrf=client.get('/api/v1/auth/csrf/').json()['data']['csrf_token']
    for method,path,body in [('GET','/api/v1/auth/csrf',None),('POST','/api/v1/auth/login','{}'),
      ('HEAD','/api/v1/auth/csrf/',None),('OPTIONS','/api/v1/auth/csrf/',None),('HEAD','/api/v1/grades/',None),
      ('GET','/api/v1/grades/','{bad'),('HEAD','/account/',None),('OPTIONS','/account/',None),
      ('POST','/','{}'),('HEAD','/',None),('OPTIONS','/',None),('GET','/glavnaya/',None),
      ('GET','/__ui__/foundation/',None),('GET','/api/v1/users/missing/',None)]:
        with CaptureQueriesContext(connection) as queries:
            response=client.generic(method,path,data=body or '',content_type='application/json',HTTP_X_CSRFTOKEN=csrf)
        writes=[q['sql'] for q in queries.captured_queries if q['sql'].lstrip().upper().startswith(('INSERT','UPDATE','DELETE'))]
        assert not writes,(method,path,'unexpected domain SQL write')
        rows.append({'method':method,'path':path,'synthetic_body':body,'status':response.status_code,
          'location':response.get('Location'),'allow':response.get('Allow'),'cache_control':response.get('Cache-Control'),
          'content_type':response.get('Content-Type'),'domain_SQL_writes':0,
          'error_code':response.json().get('error',{}).get('code') if response.get('Content-Type','').startswith('application/json') and method!='HEAD' else None})
out=root/'docs/acceptance/MS7-MIG-R02/baseline-route-probes.json'
out.write_text(json.dumps({'evidence_class':'REAL_DJANGO_DISPOSABLE_BASELINE_ONLY','port':55439,'DEBUG':False,
  'csrf':'verified synthetic client token, not exported','rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(rows,ensure_ascii=False,indent=2))
