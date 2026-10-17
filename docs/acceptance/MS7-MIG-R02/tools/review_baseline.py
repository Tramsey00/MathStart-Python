"""R02 review observations: existing Django only, guarded disposable PG read-only."""
import json, os, sys
from pathlib import Path
root=Path(sys.argv[1]).resolve(); sys.path.insert(0,str(root))
assert os.environ['DJANGO_DB_PORT']=='55439'
assert os.environ['DJANGO_DB_NAME']=='ms6_v01_smoke_ms7_mig_r02_20261008'
os.environ['DJANGO_SETTINGS_MODULE']='config.settings'
import django; django.setup()
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db import connection, transaction
from django.test import Client, RequestFactory, override_settings
from django.test.utils import CaptureQueriesContext
from django.middleware.csrf import _get_new_csrf_string
from content.models import ContentPage, Grade, Subject, Section, Redirect
from content.services.catalogue import catalogue_context
from content.sitemaps import ContentPageSitemap

def dump(name,value):
    path=root/'docs/acceptance/MS7-MIG-R02'/name
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

with transaction.atomic(), CaptureQueriesContext(connection) as queries:
    with connection.cursor() as cursor:cursor.execute('SET TRANSACTION READ ONLY')
    public=list(ContentPage.objects.filter(is_published=True).order_by('id'))
    topics=list(catalogue_context({})['catalogue_topics'])
    catalogue={
      'grades':list(Grade.objects.order_by('id').values('id','title','slug','order')),
      'subjects':list(Subject.objects.order_by('id').values('id','title','slug','order','grade_id')),
      'sections':list(Section.objects.order_by('id').values('id','title','slug','order','subject_id')),
      'topics':[{'id':p.id,'title':p.title,'slug':p.slug,'order':p.order,'grade_id':p.grade_id,'subject_id':p.subject_id,'section_id':p.section_id,'url':p.get_absolute_url()} for p in topics]}
    site=ContentPageSitemap()
    manifest={'version':'public-build-index-v1','release_id':'baseline-disposable-c133f920',
      'catalogue':catalogue,
      'pages':[{'id':p.id,'slug':p.slug,'page_type':p.page_type,'url':p.get_absolute_url(),'canonical_path':p.get_absolute_url(),
                 'delivery_path':'pages/'+str(p.id)+'.json','updated_at':p.updated_at.isoformat(),'sitemap_changefreq':site.changefreq(p),'sitemap_priority':site.priority(p)} for p in public],
      'aliases':[{'url':'/'+p.slug+'/','page_id':p.id,'status':200,'canonical_path':'/'} for p in public if p.page_type=='home'],
      'redirects':list(Redirect.objects.filter(is_active=True).order_by('id').values('old_path','new_path','is_permanent')),
      'system_urls':['/sitemap.xml','/robots.txt']}
    catalog_queries=[{}, {'q':'  ДРОБИ  '}, {'q':'no-match-synthetic'}, {'grade':'missing'}, {'subject':'missing'},
      {'grade':'5-klass'}, {'subject':'algebra'}, {'grade':'5-klass','subject':'algebra'}, {'q':'','subject':'matematika'},
      {'q':'ß'}, {'grade':'missing','subject':'algebra'}]
    cases=[]
    for params in catalog_queries:
        data=catalogue_context(params)
        cases.append({'params':params,'topic_ids':[p.id for p in data['catalogue_topics']],
          'grade_ids':[p.id for p in data['catalogue_grades']], 'subject_ids':[p.id for p in data['catalogue_subjects']],
          'selected_grade':data['catalogue_grade'],'selected_subject':data['catalogue_subject'],'query':data['catalogue_query'],'count':data['catalogue_count']})
    sorting={}
    for model,registered in admin.site._registry.items():
        if model._meta.label not in {'auth.User','auth.Group'} and model._meta.app_label!='content':continue
        cl=ChangeList.__new__(ChangeList);cl.model=model;cl.lookup_opts=model._meta;cl.model_admin=registered
        cl.list_display=list(registered.list_display);cl.params={}
        request=RequestFactory().get('/admin/');qs=model.objects.all()
        if registered.ordering:qs=qs.order_by(*registered.ordering)
        fields={str(name):cl.get_ordering_field(name) for name in cl.list_display}
        defaults=cl.get_ordering(request,qs)
        explicit={}
        for index,name in enumerate(cl.list_display):
            if fields[str(name)]:
                for prefix in ['','-']:
                    cl.params={'o':prefix+str(index)}
                    explicit[prefix+str(name)]=cl.get_ordering(request,qs)
        sorting[model._meta.label]={'list_display':cl.list_display,'sortable_fields':fields,'default_order':defaults,'explicit_orders':explicit}
    rows=[]
    unmatched=next(r['old_path'] for r in manifest['redirects'] if '/' in r['old_path'].strip('/') or '.' in r['old_path'])
    matched=next((r['old_path'] for r in manifest['redirects'] if r['old_path'].strip('/').replace('-','').replace('_','').isalnum()),None)
    paths=['/','/glavnaya/','/karta-sajta/','/sitemap.xml','/robots.txt','/account/','/missing-review/',unmatched,
           '/api/v1/auth/csrf/','/api/v1/grades/','/api/v1/auth/logout/']
    if matched:paths.append(matched)
    with override_settings(DEBUG=False,SECURE_SSL_REDIRECT=False,SESSION_COOKIE_SECURE=False,CSRF_COOKIE_SECURE=False,ALLOWED_HOSTS=['testserver']):
      for path in paths:
       for method in ['GET','HEAD','OPTIONS','TRACE','POST','PUT','PATCH','DELETE']:
        for csrf_state in (['none','valid','bad-origin'] if method in ['POST','PUT','PATCH','DELETE'] else ['none']):
            client=Client(enforce_csrf_checks=True);headers={}
            if csrf_state!='none':
                token=_get_new_csrf_string();client.cookies['csrftoken']=token;headers['HTTP_X_CSRFTOKEN']=token
                if csrf_state=='bad-origin':headers['HTTP_ORIGIN']='https://foreign.invalid'
            response=client.generic(method,path,data='{}',content_type='application/json',**headers)
            rows.append({'path':path,'method':method,'csrf':csrf_state,'status':response.status_code,'location':response.get('Location'),
                         'allow':response.get('Allow'),'body_length':len(response.content),
                         'error_code':response.json().get('error',{}).get('code') if response.get('Content-Type','').startswith('application/json') and method!='HEAD' else None})
    writes=[q['sql'] for q in queries.captured_queries if q['sql'].lstrip().upper().startswith(('INSERT','UPDATE','DELETE'))]
    assert not writes,'Unexpected domain write in read-only probe'
dump('review-baseline-public-index.json',manifest)
dump('review-baseline-observations.json',{'evidence_class':'REAL_DJANGO_DISPOSABLE_BASELINE_ONLY','input_sha':'c133f920fc14ab18a463e039f8e480e064ced81c',
  'postgres_port':55439,'domain_SQL_writes':0,'sorting':sorting,'catalogue_queries':cases,'http_method_csrf':rows})
print(json.dumps({'published_pages':len(public),'topics':len(topics),'aliases':len(manifest['aliases']),'redirects':len(manifest['redirects']),'http_cases':len(rows),'SQL_writes':0,'sorting':sorting},ensure_ascii=False,indent=2))
