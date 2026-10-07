"""Actual localhost HTTP smoke against isolated candidate Django runtime."""
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[4]
qa = root.parent / 'qa'
env = os.environ.copy()
env.update(DJANGO_SECRET_KEY='r01-disposable-django-key', DJANGO_DEBUG='False',
           DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost,testserver',
           DJANGO_DB_BACKEND='postgresql', DJANGO_DB_HOST='127.0.0.1',
           DJANGO_DB_PORT='55437', DJANGO_DB_NAME='ms6_v01_smoke_ms7_mig_r01_20261007',
           DJANGO_DB_USER='r01_disposable', DJANGO_DB_PASSWORD='r01-disposable-only',
           DJANGO_DB_TEST_NAME='test_ms7_mig_r01_20261007',
           DJANGO_RUNTIME_ROOT=str(qa / 'runtime'), PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
os.environ.update(env)
sys.path.insert(0, str(root))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()
from content.models import ContentPage, Redirect
from django.utils.encoding import iri_to_uri
paths = list(ContentPage.objects.filter(is_published=True).order_by('slug'))
urls = {x.get_absolute_url() for x in paths}
# page_detail also serves the published home slug /glavnaya/; middleware
# consults Redirect only after 404. Preserve that explicit source behavior.
active_route_urls = urls | {f'/{x.slug}/' for x in paths}
redirects = list(Redirect.objects.filter(is_active=True).values('old_path','new_path','is_permanent'))
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
opener = urllib.request.build_opener(NoRedirect)
def get(path):
    try:
        response = opener.open('http://127.0.0.1:8017' + iri_to_uri(path), timeout=15)
    except urllib.error.HTTPError as exc:
        response = exc
    data = response.read()
    return {'path':path,'status':response.code,'location':response.headers.get('Location'),
            'content_type':response.headers.get('Content-Type'), 'cache_control':response.headers.get('Cache-Control'),
            'body_size':len(data),'http_rendered_sha256':hashlib.sha256(data).hexdigest()}
log = (qa / 'route-server.log').open('w', encoding='utf-8')
proc = subprocess.Popen([sys.executable,'manage.py','runserver','127.0.0.1:8017','--noreload'],
                        cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT,
                        creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
results = []
try:
    for i in range(60):
        if proc.poll() is not None:
            raise RuntimeError('candidate server exited')
        try:
            if get('/')['status']==200:
                break
        except (OSError, urllib.error.URLError):
            time.sleep(.5)
    else:
        raise RuntimeError('candidate HTTP startup timeout')
    for path in sorted(urls):
        row = get(path)
        row['expected_status'] = 200
        results.append(row)
    for row in redirects:
        r = get(row['old_path'])
        r['expected_status'] = 200 if row['old_path'] in active_route_urls else 301 if row['is_permanent'] else 302
        r['expected_location'] = None if row['old_path'] in active_route_urls else iri_to_uri(row['new_path'])
        results.append(r)
    for path, status in [('/account/',200),('/sitemap.xml',200),('/robots.txt',200),
                         ('/api/v1/grades/',200),('/api/v1/auth/csrf/',200),
                         ('/api/v1/users/me/',401),('/__ui__/foundation/',404),
                         ('/api/v1/health/',404),('/r01-unknown-no-page/',404),
                         ('/static/mathstart/css/site.css',200),('/admin/',302)]:
        row = get(path)
        row['expected_status'] = status
        results.append(row)
    failures = [x for x in results if x['status'] != x['expected_status'] or x.get('expected_location') and x['location'] != x['expected_location']]
    assert get('/account/')['cache_control']=='private, no-store'
    data = {'source_commit':'8c11edadc8debc81432d1db1145feac504f09061', 'port':8017,
            'database':'ms6_v01_smoke_ms7_mig_r01_20261007','public_urls':len(urls),
            'active_route_aliases':sorted(active_route_urls - urls),'redirect_rules':len(redirects),'requests':len(results),'failures':failures,
            'semantics':'actual localhost HTTP Django candidate on disposable PG; response digests may include CSRF randomness and are not source/persistent content digests', 'results':results}
    (root / 'docs/acceptance/MS7-MIG-R01/route-smoke.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:data[k] for k in ['public_urls','redirect_rules','requests','failures']}))
    raise SystemExit(1 if failures else 0)
finally:
    proc.terminate()
    proc.wait(timeout=15)
    log.close()
