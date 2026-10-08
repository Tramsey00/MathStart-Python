"""R02 B01-B07/N01: baseline oracles + proposed handoff negatives; no target runtime."""
import copy, json, os, re, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from jsonschema import Draft202012Validator, FormatChecker, ValidationError
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'specs/migration/r02-v1';E=ROOT/'docs/acceptance/MS7-MIG-R02'
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
os.environ.setdefault('DJANGO_DB_BACKEND','sqlite')
os.environ.setdefault('DJANGO_SECRET_KEY','synthetic-r02-review-only')
import django
from django.apps import apps
if not apps.ready:django.setup()

def load(path):return json.loads(path.read_text(encoding='utf-8'))
def validator(name):
 s=load(P/'delivery-v1.schema.json')
 return Draft202012Validator({'$defs':s['$defs'],'$ref':'#/$defs/'+name},format_checker=FormatChecker())
def request(permissions):
 from django.test import RequestFactory
 r=RequestFactory().get('/admin/auth/user/add/')
 r.user=SimpleNamespace(has_perm=lambda p:p in permissions,is_active=True,is_staff=True,is_superuser=False)
 return r
def project_catalogue(index,query):
 """Test-only frontend projection from exported data; baseline function is the oracle."""
 data=index['catalogue']; lookup={kind:{r['id']:r for r in rows} for kind,rows in data.items() if kind!='topics'}
 topics=data['topics']; grade_rows=list({t['grade_id']:lookup['grades'][t['grade_id']] for t in topics if t['grade_id']}.values())
 grade=query.get('grade','');grade=grade if grade in {g['slug'] for g in grade_rows} else ''
 selected=[t for t in topics if not grade or lookup['grades'].get(t['grade_id'],{}).get('slug')==grade]
 subjects={}
 for t in selected:
  if t['subject_id']:
   s=lookup['subjects'][t['subject_id']];subjects.setdefault(s['slug'],s)
 subject=query.get('subject','');subject=subject if subject in subjects else ''
 q=query.get('q','').strip()
 matches=[t for t in selected if (not subject or lookup['subjects'].get(t['subject_id'],{}).get('slug')==subject) and q.casefold() in t['title'].casefold()]
 return {'topic_ids':[t['id'] for t in matches],'grade_ids':[g['id'] for g in grade_rows],
  'subject_ids':[s['id'] for s in subjects.values()],'selected_grade':grade,'selected_subject':subject,'query':q,'count':len(matches)}
def validate_index_semantics(index):
 validator('PublicBuildIndex').validate(index)
 pages=index['pages'];ids=[p['id'] for p in pages];urls=[p['url'] for p in pages]
 if len(set(ids))!=len(ids) or len(set(urls))!=len(urls):raise ValueError('duplicate page')
 lookup={p['id']:p for p in pages};c=index['catalogue']
 for rows in [c['grades'],c['subjects'],c['sections'],c['topics']]:
  if len({r['id'] for r in rows})!=len(rows):raise ValueError('duplicate entity')
 grades={g['id'] for g in c['grades']};subjects={s['id'] for s in c['subjects']};sections={s['id'] for s in c['sections']}
 if any(s['grade_id'] not in grades for s in c['subjects']):raise ValueError('foreign grade')
 if any(s['subject_id'] not in subjects for s in c['sections']):raise ValueError('foreign subject')
 topic_ids=set()
 for t in c['topics']:
  if t['id'] not in lookup or lookup[t['id']]['page_type']!='topic' or t['url']!=lookup[t['id']]['url']:raise ValueError('missing topic page')
  if t['grade_id'] is not None and t['grade_id'] not in grades:raise ValueError('foreign topic grade')
  if t['subject_id'] is not None and t['subject_id'] not in subjects:raise ValueError('foreign topic subject')
  if t['section_id'] is not None and t['section_id'] not in sections:raise ValueError('foreign topic section')
  topic_ids.add(t['id'])
 if topic_ids!={p['id'] for p in pages if p['page_type']=='topic'}:raise ValueError('missing catalogue topic')
def parse_sort(value,rule):
 Draft202012Validator(rule['query_schema']).validate(value)
 if value=='default':return []
 terms=value.split(',');fields=[s.lstrip('-') for s in terms]
 if len(set(fields))!=len(fields):raise ValueError('duplicate sort field')
 return terms
def observable_semantics(value):
 validator('PublicationObservableState').validate(value)
 if value['state']=='IN_SYNC' and value['active']!=value['db_edition']:raise ValueError('false synchronized state')
 pending=value['pending']
 if pending and pending['db_committed'] and (pending['next_release']!=value['db_edition']['release_id'] or pending['manifest_digest']!=value['db_edition']['manifest_digest']):raise ValueError('committed release mismatch')

class ReviewContractTests(unittest.TestCase):
 def test_B01_actual_useradmin_requires_add_and_change(self):
  from django.contrib import admin
  from django.contrib.auth.models import User
  from django.contrib.admin.options import ModelAdmin
  from django.core.exceptions import PermissionDenied
  registered=admin.site._registry[User]
  with patch.object(ModelAdmin,'add_view',return_value='parent-add-gate'):
   with self.assertRaises(PermissionDenied):registered._add_view(request({'auth.add_user'}))
   self.assertEqual(registered._add_view(request({'auth.add_user','auth.change_user'})),'parent-add-gate')
  for perms in [set(),{'auth.change_user'}]:
   with self.assertRaises(PermissionDenied):registered._changeform_view(request(perms),None,'',None)
  for active,staff in [(False,True),(True,False),(False,False)]:
   r=request({'auth.add_user','auth.change_user'});r.user.is_active=active;r.user.is_staff=staff
   self.assertFalse(admin.site.has_permission(r))
  op=load(P/'delivery-staff-v1.openapi.json')['paths']['/api/v1/staff/users/']['post']
  self.assertEqual(op['x-required-permission'],'is_active && is_staff && auth.add_user && auth.change_user')

 def test_B02_full_published_manifest_against_unchanged_file_sources(self):
  index=load(E/'review-baseline-public-index.json');validate_index_semantics(index)
  source={}
  for file in [*(ROOT/'curriculum').rglob('lesson.json'),*(ROOT/'site_content/pages').rglob('page.json')]:
   page=load(file)['page']
   if page['is_published']:source[page['slug']]=page
  self.assertEqual({p['slug'] for p in index['pages']},set(source))
  self.assertEqual(len(index['catalogue']['topics']),sum(p['page_type']=='topic' for p in source.values()))
  for p in index['pages']:
   page=source[p['slug']];self.assertEqual(p['page_type'],page['page_type'])
   self.assertEqual(p['canonical_path'],'/' if page['page_type']=='home' else '/'+page['slug']+'/')
   self.assertEqual(p['delivery_path'],'pages/'+str(p['id'])+'.json')
  self.assertEqual(index['aliases'],[{'url':'/glavnaya/','page_id':next(p['id'] for p in index['pages'] if p['slug']=='glavnaya'),'status':200,'canonical_path':'/'}])
  for mutate in [lambda x:x['pages'].append(x['pages'][0]),lambda x:x['catalogue']['topics'].pop(),lambda x:x['catalogue']['topics'][0].update(subject_id=999999)]:
   bad=copy.deepcopy(index);mutate(bad)
   with self.assertRaises((ValidationError,ValueError)):validate_index_semantics(bad)
  for bad in [{**index,'users':[]},{**index,'session_key':'secret'}]:
   with self.assertRaises(ValidationError):validator('PublicBuildIndex').validate(bad)

 def test_B02_catalogue_projection_against_real_baseline_queries(self):
  index=load(E/'review-baseline-public-index.json')
  for case in load(E/'review-baseline-observations.json')['catalogue_queries']:
   self.assertEqual(project_catalogue(index,case['params']),{k:v for k,v in case.items() if k!='params'})
  self.assertEqual(project_catalogue(index,{'grade':'unknown','subject':'unknown','ignored':'x'}),project_catalogue(index,{}))

 def test_B02_unicode_and_repeated_query_using_original_catalogue_function(self):
  from django.http import QueryDict
  from content.services.catalogue import catalogue_context
  from content.models import ContentPage
  grade=SimpleNamespace(id=1,slug='g',title='G');subject=SimpleNamespace(id=2,slug='s',title='S')
  topic=SimpleNamespace(id=3,title='Straße É e\u0301',grade=grade,subject=subject)
  with patch.object(ContentPage.objects,'filter') as manager:
   manager.return_value.select_related.return_value.only.return_value.order_by.return_value=[topic]
   result=catalogue_context(QueryDict('q=wrong&q=STRASSE&grade=invalid&grade=g&subject=s&unknown=x'))
   self.assertEqual(result['catalogue_topics'],[topic]);self.assertEqual(result['catalogue_query'],'STRASSE')
   self.assertEqual(catalogue_context({'q':'é'})['catalogue_count'],1)
   self.assertEqual(catalogue_context({'q':'e\u0301'})['catalogue_count'],1)
   self.assertEqual(catalogue_context({'q':'  STRASSE  '})['catalogue_count'],1)
   self.assertEqual(catalogue_context({'q':'strase'})['catalogue_count'],0)

 def test_B03_strict_boolean_wire_and_native_redirect_filter(self):
  from django.contrib.admin.filters import BooleanFieldListFilter
  from django.contrib import admin
  from content.models import Redirect
  op=load(P/'delivery-staff-v1.openapi.json')['paths']['/api/v1/staff/redirects/']['get']
  param=next(p for p in op['parameters'] if p['name']=='filter__is_permanent')
  self.assertEqual(param['x-wire-literals'],['true','false'])
  for wire,value,native in [('true',True,'1'),('false',False,'0')]:
   Draft202012Validator(param['schema']).validate(value)
   f=BooleanFieldListFilter(Redirect._meta.get_field('is_permanent'),request(set()),{'is_permanent__exact':[native]},Redirect,admin.site._registry[Redirect],'is_permanent')
   qs=f.queryset(request(set()),Redirect.objects.all())
   self.assertIn(value,[v for v in qs.query.where.children[0].rhs] if isinstance(qs.query.where.children[0].rhs,list) else [qs.query.where.children[0].rhs])
  for bad in [0,1,'true','false',None,'True']:
   with self.assertRaises(ValidationError):Draft202012Validator(param['schema']).validate(bad)
  def decode_wire(values):
   if len(values)!=1 or type(values[0]) is not str or values[0] not in {'true','false'}:raise ValueError('invalid boolean wire')
   return values[0]=='true'
  self.assertIs(decode_wire(['true']),True);self.assertIs(decode_wire(['false']),False)
  for bad in [[],['true','false'],['0'],['1'],['True'],['FALSE'],[''],[True],[False]]:
   with self.assertRaises(ValueError):decode_wire(bad)

 def test_B04_all_resource_sort_contracts_against_actual_changelist(self):
  from django.contrib import admin
  from django.contrib.admin.views.main import ChangeList
  policy=load(P/'staff-list-policy-v1.json');oas=load(P/'delivery-staff-v1.openapi.json')
  for resource,rule in policy['resources'].items():
   model=apps.get_model(rule['model']);registered=admin.site._registry[model]
   cl=ChangeList.__new__(ChangeList);cl.model=model;cl.lookup_opts=model._meta;cl.model_admin=registered;cl.list_display=list(registered.list_display);cl.params={}
   allowed=[cl.get_ordering_field(f) for f in cl.list_display if cl.get_ordering_field(f)]
   self.assertEqual(rule['allowed_fields'],allowed)
   qs=model.objects.all()
   if registered.ordering:qs=qs.order_by(*registered.ordering)
   self.assertEqual(rule['default_effective_order'],cl.get_ordering(request(set()),qs))
   op=oas['paths']['/api/v1/staff/'+resource+'/']['get']
   self.assertEqual(next(p for p in op['parameters'] if p['name']=='sort')['schema'],rule['query_schema'])
   for field in allowed:
    for sign in ['','-']:
     value=sign+field;self.assertEqual(parse_sort(value,rule),[value])
     cl.params={'o':sign+str(cl.list_display.index(field))}
     self.assertEqual(rule['explicit_single_field_orders'][value],cl.get_ordering(request(set()),qs))
   for bad in ['+title','title,',' title','password','grade__password','id;DROP',',','']:
    with self.assertRaises((ValidationError,ValueError)):parse_sort(bad,rule)
   if allowed:
    with self.assertRaises(ValueError):parse_sort(allowed[0]+',-'+allowed[0],rule)
  self.assertEqual(policy['resources']['groups']['allowed_fields'],[])

 def test_B04_multisort_directions_and_cursor_binding(self):
  from django.contrib import admin
  from django.contrib.admin.views.main import ChangeList
  from content.models import ContentPage
  policy=load(P/'staff-list-policy-v1.json');rule=policy['resources']['pages']
  terms=parse_sort('-grade,title,-updated_at',rule)
  cl=ChangeList.__new__(ChangeList);cl.model=ContentPage;cl.lookup_opts=ContentPage._meta;cl.model_admin=admin.site._registry[ContentPage];cl.list_display=list(cl.model_admin.list_display)
  cl.params={'o':'.'.join(('-' if t.startswith('-') else '')+str(cl.list_display.index(t.lstrip('-'))) for t in terms)}
  qs=ContentPage.objects.all().order_by(*cl.model_admin.ordering)
  self.assertEqual(cl.get_ordering(request(set()),qs),terms+list(cl.model_admin.ordering)+['-pk'])
  required={'actor_user_id','authorization_scope_revision','resource','q','normalized_filters','effective_sort_keys_and_directions','page_size'}
  self.assertEqual(set(policy['cursor_binding']),required)
  original={'actor_user_id':1,'authorization_scope_revision':'r1','resource':'pages','q':'x','normalized_filters':{'is_published':True},'effective_sort_keys_and_directions':terms,'page_size':20}
  # A signed token is checked against the complete binding, not only its sort.
  def compare(a,b):
   if json.dumps(a,sort_keys=True)!=json.dumps(b,sort_keys=True):raise ValueError('cursor binding changed')
  compare(original,copy.deepcopy(original))
  for key in required:
   changed=copy.deepcopy(original);changed[key]=None
   with self.assertRaises(ValueError):compare(original,changed)
  # Native FK sorting expands model Meta ordering, not __str__ or FK numeric ID.
  compiler=qs.order_by('-grade','title','-updated_at').query.get_compiler('default')
  expressions=[str(item[0].expression) for item in compiler.get_order_by()]
  self.assertIn('order',expressions[0]);self.assertIn('title',expressions[1])
  self.assertTrue(compiler.get_order_by()[0][0].descending)
  self.assertTrue(compiler.get_order_by()[1][0].descending)

 def test_B05_group_form_queryset_does_not_require_group_admin_permission(self):
  from django.contrib import admin
  from django.contrib.auth.models import User,Group
  actor=request({'auth.change_user'});registered=admin.site._registry[User]
  field=registered.formfield_for_manytomany(User._meta.get_field('groups'),actor)
  self.assertEqual(field.queryset.model,Group);self.assertEqual(field.queryset.query.order_by,('name',))
  groups=admin.site._registry[Group]
  self.assertFalse(groups.has_view_permission(actor));self.assertFalse(groups.has_change_permission(actor));self.assertFalse(groups.has_add_permission(actor));self.assertFalse(groups.has_delete_permission(actor))
  self.assertNotIn('groups',str(registered.add_fieldsets))
  op=load(P/'delivery-staff-v1.openapi.json')['paths']['/api/v1/staff/users/{id}/group_choices/']['get']
  self.assertEqual(op['x-required-permission'],'is_active && is_staff && auth.change_user')
  validator('StaffGroupChoice').validate({'id':1,'name':'synthetic'})
  with self.assertRaises(ValidationError):validator('StaffGroupChoice').validate({'id':1,'name':'synthetic','permissions':[1]})

 def test_B06_observable_publication_states_and_recovery_negatives(self):
  samples=load(P/'synthetic-review-exchanges-v1.json')['publication_states']
  for s in samples:observable_semantics(s)
  self.assertEqual({v['state'] for v in samples},{'IN_SYNC','PENDING','RECOVERY_REQUIRED','UNAVAILABLE'})
  synced=copy.deepcopy(next(s for s in samples if s['state']=='IN_SYNC'));synced['db_edition']['release_id']='different'
  with self.assertRaises(ValueError):observable_semantics(synced)
  recovery=copy.deepcopy(next(s for s in samples if s['state']=='RECOVERY_REQUIRED'));recovery['pending']['failure_code']=None
  with self.assertRaises(ValidationError):observable_semantics(recovery)
  recovery=copy.deepcopy(next(s for s in samples if s['state']=='RECOVERY_REQUIRED'));recovery['pending']['next_release']='different'
  with self.assertRaises(ValueError):observable_semantics(recovery)
  recovery=copy.deepcopy(next(s for s in samples if s['state']=='RECOVERY_REQUIRED'));recovery['pending']['manifest_digest']='c'*64
  with self.assertRaises(ValueError):observable_semantics(recovery)
  for secret in ['idempotency_key','resume_cursor','raw_plan','password']:
   with self.assertRaises(ValidationError):validator('PublicationObservableState').validate({**samples[0],secret:'private'})
  path=load(P/'delivery-staff-v1.openapi.json')['paths']['/api/v1/staff/pages/{id}/publication_state/']
  self.assertEqual(set(path),{'get'});self.assertIn('content.view_contentpage OR content.change_contentpage',path['get']['x-required-permission'])

 def test_B07_methods_csrf_precedence_and_fallback_from_real_observations(self):
  observations=load(E/'review-baseline-observations.json');self.assertEqual(observations['domain_SQL_writes'],0)
  rows=observations['http_method_csrf'];lookup={(r['path'],r['method'],r['csrf']):r for r in rows}
  for path in ['/sitemap.xml','/robots.txt','/','/glavnaya/']:
   for method in ['GET','HEAD','OPTIONS','TRACE']:self.assertEqual(lookup[path,method,'none']['status'],200)
   for method in ['POST','PUT','PATCH','DELETE']:
    self.assertEqual(lookup[path,method,'none']['status'],403);self.assertEqual(lookup[path,method,'bad-origin']['status'],403);self.assertEqual(lookup[path,method,'valid']['status'],200)
  for csrf,status in [('none',403),('bad-origin',403),('valid',404)]:self.assertEqual(lookup['/missing-review/','POST',csrf]['status'],status)
  for row in rows:
   if row['path']=='/api/v1/auth/logout/':self.assertEqual(row['status'],401)
   if row['path']=='/api/v1/grades/' and row['method']!='GET':self.assertEqual(row['status'],400)
  from django.urls import resolve,Resolver404
  def unresolved_path(path):
   try:resolve(path);return False
   except Resolver404:return True
  unresolved=[r for r in rows if unresolved_path(r['path'])]
  self.assertTrue(unresolved)
  self.assertTrue(all(r['status'] in [301,302] for r in unresolved))
  for row in load(P/'implemented-routes-v1.json')['pages']:
   if row['path'] in ['/sitemap.xml','/robots.txt','404 redirect fallback']:self.assertIn('ALL methods',row['target_methods'])

 def test_N01_real_account_controller_and_review_coverage(self):
  matrix=load(P/'parity-matrix-v1.json')['rows']
  row=next(r for r in matrix if r['id']=='UI-01')
  self.assertIn('static/mathstart/js/ui/account.js',row['baseline_reference']);self.assertNotIn('identity-controller.js',row['baseline_reference'])
  source=(ROOT/'static/mathstart/js/ui/account.js').read_text(encoding='utf-8')
  self.assertIn('clearCredentials',source);self.assertIn('stateReloadNeeded',source)
  self.assertEqual({r['id'] for r in matrix if r['id'].startswith('REVIEW-')},{'REVIEW-'+v for v in ['B01','B02','B03','B04','B05','B06','B07','N01']})

if __name__=='__main__':unittest.main()
