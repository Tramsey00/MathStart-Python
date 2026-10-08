"""R02 contract audit only: independent frozen/baseline oracles, no target runtime."""
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import unittest

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'specs/migration/r02-v1'
EVIDENCE = ROOT / 'docs/acceptance/MS7-MIG-R02'
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
os.environ.setdefault('DJANGO_DB_BACKEND','sqlite')
os.environ.setdefault('DJANGO_SECRET_KEY','synthetic-r02-contract-only-no-runtime')

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def graph_check(graph):
    visited, active = set(), set()
    def visit(node):
        if node in active:
            raise ValueError('dependency cycle')
        if node in visited:
            return
        if node not in graph:
            raise ValueError('missing dependency')
        active.add(node)
        for dep in graph[node]:
            visit(dep)
        active.remove(node)
        visited.add(node)
    for node in graph:
        visit(node)
    return visited

def exact_exchange(candidate, reference):
    """Typed JSON comparison with expectations outside the R02 package."""
    # bool must never compare equal to integer1 as Python equality would allow.
    def encode(value):
        return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
    if encode(candidate) != encode(reference):
        raise ValueError('old/new exchange semantics differ')

def new_validator(name):
    schema=load(PACKAGE/'delivery-v1.schema.json')
    return Draft202012Validator({'$defs':schema['$defs'],'$ref':'#/$defs/'+name},format_checker=FormatChecker())

class MigrationContractTests(unittest.TestCase):
    def test_all_input_blobs_preserved_without_pin_refresh(self):
        manifest=load(EVIDENCE/'input-tree-digests.json')
        self.assertEqual(manifest['input_sha'],'c133f920fc14ab18a463e039f8e480e064ced81c')
        # Batch cat-file keeps the audit practical for all source/history paths.
        names=list(manifest['files'])
        requests=''.join('HEAD:'+p+'\n' for p in names).encode()
        result=subprocess.run(['git','cat-file','--batch'],cwd=ROOT,input=requests,capture_output=True,check=True).stdout
        position=0
        for name in names:
            end=result.index(b'\n',position)
            header=result[position:end].decode().split()
            self.assertEqual(header[1],'blob',name)
            size=int(header[2]); data=result[end+1:end+1+size]
            self.assertEqual(hashlib.sha256(data).hexdigest(),manifest['files'][name],name)
            position=end+size+2

    def test_independent_historical_frozen_pins_and_official_oas(self):
        from scripts.r02a_contract_reference import validate_artifacts
        original=validate_artifacts()
        self.assertEqual(sum(1 for path in original['paths'].values() for method in path if method in {'get','post','patch','put','delete'}),37)
        pins=load(ROOT/'specs/api/candidate-manifest-v1.json')['artifacts']
        for path,digest in pins.items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)

    def test_new_schema_and_oas_with_offline_reference_resolution(self):
        schema=load(PACKAGE/'delivery-v1.schema.json')
        Draft202012Validator.check_schema(schema)
        oas=load(PACKAGE/'delivery-staff-v1.openapi.json')
        official=load(ROOT/'specs/api/schemas/openapi-3.1-2025-09-15.schema.json')
        Draft202012Validator(official,format_checker=FormatChecker()).validate(oas)
        def walk(value,file):
            if isinstance(value,dict):
                if '$ref' in value:
                    filename,_,pointer=value['$ref'].partition('#')
                    self.assertNotIn('://',filename)
                    target=(file.parent/filename).resolve() if filename else file
                    self.assertTrue(target.is_relative_to(ROOT))
                    current=load(target)
                    for field in pointer.split('/')[1:]:
                        current=current[field.replace('~1','/').replace('~0','~')]
                    Draft202012Validator.check_schema(current)
                for v in value.values():walk(v,file)
            elif isinstance(value,list):
                for v in value:walk(v,file)
        walk(schema,PACKAGE/'delivery-v1.schema.json')
        walk(oas,PACKAGE/'delivery-staff-v1.openapi.json')
        for definition in schema['$defs'].values():
            Draft202012Validator.check_schema(definition)

    def test_route_map_against_independent_code_and_policy(self):
        routes=load(PACKAGE/'implemented-routes-v1.json')
        self.assertEqual(routes['implemented_api_operation_count'],8)
        literal={'get_csrf','register','login','logout','get_me','update_me','complete_onboarding','list_grades'}
        ops=routes['operations']
        self.assertEqual(len(ops),37)
        self.assertEqual({v['operation_id'] for v in ops if v['baseline_state']=='IMPLEMENTED'},literal)
        for op in ops:
            self.assertEqual(op['target_state'],'NOT_IMPLEMENTED')
        self.assertEqual(routes['staff_baseline'],load(ROOT/'docs/acceptance/MS7-MIG-R01/admin-inventory.json'))
        users=(ROOT/'users/views.py').read_text(encoding='utf-8')
        self.assertIn('@endpoint({"GET", "PATCH"})',users)
        self.assertEqual(users.count('@endpoint('),6)
        self.assertIn('http_method_names = ["get"]',(ROOT/'content/api_views.py').read_text(encoding='utf-8'))

    def test_synthetic_old_new_against_independent_frozen_exchanges(self):
        old={v['operation_id']:v for v in load(ROOT/'specs/api/fixtures/http-exchanges-v1.json')}
        candidates=load(PACKAGE/'synthetic-exchanges-v1.json')
        for record in candidates:
            if record['case_id']=='logout_runtime':
                self.assertIs(record['candidate']['response']['data']['completed'],True)
                self.assertIn('{"completed": True}',(ROOT/'users/views.py').read_text(encoding='utf-8'))
                continue
            reference=old[record['reference_operation_id']]
            exact_exchange(record['candidate'],reference)
            with self.assertRaises(ValueError):
                changed=copy.deepcopy(record['candidate']);changed['status']=422
                exact_exchange(changed,reference)
            with self.assertRaises(ValueError):
                changed=copy.deepcopy(record['candidate']);changed['response']['meta']['version']='invented'
                exact_exchange(changed,reference)
        # Nested identity mismatches may validate a DTO but fail parity.
        first=copy.deepcopy(old['get_me']);first['response']['data']['id']=True
        with self.assertRaises(ValueError):exact_exchange(first,old['get_me'])

    def test_original_error_and_unsupported_exchanges_stay_safe(self):
        from scripts.r02a_contract_reference import validator
        errors=load(ROOT/'specs/api/fixtures/errors-v1.json')
        # The independent pre-migration suite owns exact example shape/coverage;
        # new package must preserve its bytes, never regenerate these fixtures.
        self.assertTrue(errors)
        policy=load(ROOT/'specs/api/http-policy-v1.json')
        self.assertEqual(policy['security']['foreign_owner_status'],404)
        self.assertEqual(policy['revision']['stale_status'],409)
        self.assertEqual(policy['lifecycle']['outcomes'],['CORRECT','WRONG','UNSUPPORTED','INDETERMINATE'])
        denied={'error':{'code':'NOT_FOUND','message':'Resource unavailable.','field_errors':{},'retryable':False,'request_id':'00000000-0000-4000-8000-000000000001'}}
        validator('NotFoundError').validate(denied)
        with self.assertRaises(ValidationError):validator('NotFoundError').validate({**denied,'private_owner':2})

    def test_failure_business_candidates_against_independent_originals(self):
        from scripts.r02a_contract_reference import validator
        candidates=load(PACKAGE/'synthetic-failure-business-v1.json')
        for group,file in [('errors','errors-v1.json'),('business_results','business-results-v1.json'),('invalid_shapes','invalid-v1.json')]:
            reference=load(ROOT/'specs/api/fixtures'/file)
            self.assertEqual(len(candidates[group]),len(reference))
            for example in candidates[group]:
                old=reference[example['reference_index']]
                exact_exchange(example['candidate'],old)
                if group=='invalid_shapes':
                    with self.assertRaises((ValidationError,ValueError)):validator(old['schema']).validate(old['value'])
                else:
                    validator(old['schema']).validate(old['response'])
                    changed=copy.deepcopy(example['candidate']);changed['status']=422
                    with self.assertRaises(ValueError):exact_exchange(changed,old)
        unsupported=[x['candidate'] for x in candidates['business_results'] if (x['candidate']['response'].get('data',{}).get('result') or {}).get('outcome')=='UNSUPPORTED']
        self.assertTrue(unsupported)
        for old in unsupported:
            changed=copy.deepcopy(old);changed['response']['data']['result']['outcome']='WRONG'
            with self.assertRaises(ValueError):exact_exchange(changed,old)

    def test_domain_and_migration_dependency_cycles_fail(self):
        policy=load(PACKAGE/'dependency-policy-v1.json')
        graph_check(policy['domains'])
        tasks=policy['migration_tasks']
        graph_check({t['id']:[dep['id'] for dep in t['dependencies']] for t in tasks})
        invalid=copy.deepcopy(policy['domains']);invalid['knowledge']=['content']
        with self.assertRaisesRegex(ValueError,'cycle'):graph_check(invalid)
        with self.assertRaises(ValueError):graph_check({'one':['missing']})

    def test_full_schema_mapping_against_external_R01_manifest(self):
        mapping=load(PACKAGE/'schema-mapping-v1.json')
        r01=load(ROOT/'docs/acceptance/MS7-MIG-R01/runtime-data-manifest.json')
        for key in ['columns','constraints','indexes','migrations','sequences']:
            self.assertEqual(mapping['physical_baseline'][key],r01[key])
        mapped={(c['source_table'],c['source_column']) for c in mapping['physical_baseline']['column_mapping']}
        self.assertEqual(mapped,{(c['table_name'],c['column_name']) for c in r01['columns']})
        model_columns={(m['table'],f['column']) for m in mapping['models'] for f in m['fields']}
        self.assertTrue(mapped<=model_columns)
        self.assertEqual(len(mapped),114)
        seq=mapping['fresh_disposable_sequence_evidence']
        self.assertGreater(len(seq['sequences']),0)
        self.assertTrue(all(c['identity_kind']=='d' for c in seq['identity_columns']))
        self.assertFalse(seq['working_DB_access'])

    def test_mapping_critical_defaults_and_on_delete_against_baseline_code(self):
        mapping=load(PACKAGE/'schema-mapping-v1.json')
        table={m['model']:{f['name']:f for f in m['fields']} for m in mapping['models']}
        for field in ['user','selected_grade']:
            self.assertEqual(table['users.StudentProfile'][field]['relationship']['on_delete_service'],'PROTECT')
        self.assertEqual(table['users.IdentityReceipt']['user']['relationship']['on_delete_service'],'PROTECT')
        self.assertEqual(table['content.Subject']['grade']['relationship']['on_delete_service'],'CASCADE')
        self.assertEqual(table['content.ContentPage']['grade']['relationship']['on_delete_service'],'SET_NULL')
        self.assertEqual(table['content.ContentPage']['is_published']['default']['value'],True)
        self.assertEqual(table['users.StudentProfile']['onboarding_complete']['default']['value'],False)
        self.assertEqual(table['users.StudentProfile']['id']['default']['value'],'uuid.uuid4')
        self.assertTrue(table['content.Grade']['created_at']['auto_now_add'])
        self.assertTrue(table['content.ContentPage']['updated_at']['auto_now'])
        self.assertFalse(table['content.ContentPage']['created_at']['auto_now'])

    def test_new_contract_digest_manifest_and_qa_not_frontend_inputs(self):
        for path,digest in load(EVIDENCE/'contract-digests.json')['files'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
        # The only existing UI pack remains isolated from full auth exchanges.
        ui=(ROOT/'specs/ui/fixtures/ui-states-v1.json').read_text(encoding='utf-8')
        self.assertNotIn('synthetic-exchanges-v1',ui)
        self.assertNotIn('synthetic-failure-business-v1',ui)

    def test_public_delivery_and_staff_secret_rejection(self):
        value={'delivery_version':'content-delivery-v1','id':70,'slug':'example','page_type':'topic','title':'Тема',
         'grade_id':30,'subject_id':None,'section_id':None,'order':0,'body_html':'<p>Trusted authored self-check</p>',
         'is_published':True,'seo':{'title':'Тема | MathStart','description':'Тема','canonical_path':'/example/'},
         'created_at':'2026-10-04T00:00:00Z','updated_at':'2026-10-04T00:00:00Z',
         'source':{'path':'curriculum/example','source_digest':'a'*64,'render_digest':'b'*64},'assets':[]}
        new_validator('ContentDelivery').validate(value)
        for mutation in [{'is_published':False},{'answer_key':'secret'},{'user_id':1},{'assets':[{'storage_key':'../private','url':'/media/a','kind':'media','sha256':'a'*64,'order':0,'lifecycle':'none'}]}]:
            with self.assertRaises(ValidationError):new_validator('ContentDelivery').validate({**value,**mutation})
        user={'id':1,'username':'synthetic','first_name':'','last_name':'','email':'','is_active':True,'is_staff':False,'is_superuser':False,
         'last_login':None,'date_joined':'2026-10-04T00:00:00Z','groups':[],'user_permissions':[],'has_usable_password':True}
        new_validator('StaffUserDTO').validate(user)
        for secret in ['password','encoded_password','session_key','request_digest']:
            with self.assertRaises(ValidationError):new_validator('StaffUserDTO').validate({**user,secret:'private'})

    def test_journal_recovery_shape_and_invalid_state(self):
        journal={'operation_id':'00000000-0000-4000-8000-000000000001','operation':'unpublish','stage':'RECOVERY_REQUIRED',
         'previous_release':'old','next_release':'new','manifest_digest':'a'*64,'plan_digest':'b'*64,'key_digest':'d'*64,
         'affected_paths':['/example/'],'updated_at':'2026-10-08T12:00:00Z','failure_code':'ACTIVATION_FAILED','resume_cursor':'activate','owner_id':'00000000-0000-4000-8000-000000000002',
         'fence_generation':1,'lease_until':'2026-10-08T12:01:00Z','db_committed':True,'activation_status':'UNKNOWN'}
        new_validator('PublicationJournal').validate(journal)
        with self.assertRaises(ValidationError):new_validator('PublicationJournal').validate({**journal,'stage':'FAKE_SUCCESS'})

    def test_finding_criteria_exact_copy_all_widths(self):
        accepted=load(ROOT/'docs/acceptance/MS7-MIG-R01/ilya-20261007/follow-up-F01-F04.json')['findings']
        rows=load(PACKAGE/'parity-matrix-v1.json')['rows']
        findings=[r for r in rows if r['area']=='baseline_exception']
        self.assertEqual(len(findings),4)
        for baseline,row in zip(accepted,findings):
            self.assertEqual(row['baseline_exception'],baseline)
            self.assertEqual(row['target_assertion'],baseline['expected_target_results'])
            self.assertEqual(row['widths'],[360,768,1440])
            self.assertEqual(row['implementation_owner'],'13baybars')

    def test_original_result_not_rewritten_and_evidence_paths_exist(self):
        old=load(ROOT/'docs/acceptance/MS7-MIG-R01/old-to-new-evidence.json')['records']
        lookup={r['original_result']['id']:r['original_result'] for r in old}
        new=load(EVIDENCE/'old-to-new-evidence.json')['records']
        self.assertEqual({r['original_result']['id'] for r in new},{'R02','R03','MS7-R02A','MS7-R03A','Grades PR24'})
        for row in new:
            original=row['original_result']
            if original['id'] in lookup:self.assertEqual(original,lookup[original['id']])
            for path in row['target_evidence']['paths']:self.assertTrue((ROOT/path).is_file())
            self.assertEqual(row['target_evidence']['implementation'],'NOT_IMPLEMENTED')

    def test_raw_input_digest_against_independent_baseline(self):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
        os.environ.setdefault('DJANGO_DB_BACKEND','sqlite')
        import django
        from django.apps import apps
        if not apps.ready:django.setup()
        from users.services import request_digest as baseline
        from scripts.r02a_contract_reference import request_digest as reference
        raw={'raw_text':'  x = −2\n','steps':[{'step_no':1,'raw_text':'é'},{'step_no':2,'raw_text':'e\u0301'}]}
        args=('1','submit_attempt','/api/v1/attempts/1/submit/',raw)
        self.assertEqual(baseline(*args),reference(*args))
        changed=copy.deepcopy(raw);changed['steps'].reverse()
        self.assertNotEqual(baseline(*args),reference('1',args[1],args[2],changed))
        self.assertNotEqual(baseline(*args),reference('2',args[1],args[2],raw))

    def test_password_baseline_against_independent_pbkdf2_vector(self):
        from django.contrib.auth.hashers import PBKDF2PasswordHasher
        # Standard published PBKDF2-HMAC-SHA256 vector, independent of our addenda.
        self.assertEqual(hashlib.pbkdf2_hmac('sha256',b'password',b'salt',1).hex(),
          '120fb6cffcf8b32c43e7225256c4f837a86548c92ccc35480805987cb70be17b')
        hasher=PBKDF2PasswordHasher()
        for password in ['synthetic-only','пароль-é']:
            salt='R02SyntheticFixedSalt'
            expected=base64.b64encode(hashlib.pbkdf2_hmac('sha256',password.encode(),salt.encode(),1000)).decode()
            encoded='pbkdf2_sha256$1000$'+salt+'$'+expected
            self.assertEqual(hasher.encode(password,salt,1000),encoded)
            self.assertTrue(hasher.verify(password,encoded))
            self.assertFalse(hasher.verify(password+'wrong',encoded))

    def test_legacy_cursor_signature_against_independent_hmac(self):
        import hmac
        from unittest.mock import patch
        from django.core import signing
        payload={'scope':'public:/api/v1/grades/','page_size':1,'created_at':'2026-10-04T00:00:00.000000+00:00','id':30}
        key='synthetic-r02-cursor-only';salt='content.grades.http-v1.cursor'
        def b64(value):return base64.urlsafe_b64encode(value).rstrip(b'=')
        alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';n=1760000000;stamp=''
        while n: n,remainder=divmod(n,62);stamp=alphabet[remainder]+stamp
        serialized=json.dumps(payload,separators=(',',':')).encode('latin-1')
        unsigned=b64(serialized).decode()+':'+stamp
        signing_key=hashlib.sha256((salt+'signer'+key).encode()).digest()
        expected=unsigned+':'+b64(hmac.new(signing_key,unsigned.encode(),hashlib.sha256).digest()).decode()
        with patch('django.core.signing.time.time',return_value=1760000000):
            actual=signing.dumps(payload,key=key,salt=salt)
        self.assertEqual(actual,expected)
        self.assertEqual(signing.loads(actual,key=key,salt=salt),payload)
        with self.assertRaises(signing.BadSignature):signing.loads(actual,key=key,salt='other')

    def test_staff_password_disable_and_own_change_against_django_forms(self):
        import django
        from django.apps import apps
        if not apps.ready: django.setup()
        from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
        from django.contrib.auth.models import User
        user=User(username='synthetic-staff',password='pbkdf2_sha256$1000$synthetic$unused',is_staff=True)
        self.assertIn('usable_password',AdminPasswordChangeForm(user).fields)
        self.assertEqual(set(PasswordChangeForm(user).fields),{'old_password','new_password1','new_password2'})
        validator=new_validator('PasswordChangeRequest')
        for value in [{'usable_password':False,'confirm_disable':True},
                      {'usable_password':True,'password1':'synthetic-only','password2':'synthetic-only'}]:
            validator.validate(value)
        for value in [{}, {'usable_password':False}, {'usable_password':False,'confirm_disable':False},
                      {'usable_password':True,'password1':'synthetic-only'},
                      {'usable_password':True,'password1':'x','password2':'x','confirm_disable':True},
                      {'usable_password':0,'confirm_disable':True}]:
            with self.assertRaises(ValidationError):validator.validate(value)
        new_validator('OwnPasswordChangeRequest').validate({'old_password':'synthetic-old','new_password1':'synthetic-new','new_password2':'synthetic-new'})
        oas=load(PACKAGE/'delivery-staff-v1.openapi.json')
        self.assertEqual(oas['paths']['/api/v1/staff/password_change/']['post']['x-required-permission'],'is_active && is_staff')
        props=load(PACKAGE/'delivery-v1.schema.json')['$defs']['StaffUserDTO']['properties']
        self.assertTrue({'password','password1','old_password','new_password1'}.isdisjoint(props))

    def test_strict_raw_parser_negative_cases_and_size_boundary(self):
        from types import SimpleNamespace
        from users.http import parse_request,APIError
        invalid=[(b'{bad',400,'INVALID_REQUEST'),(b'[]',400,'INVALID_REQUEST'),
          (b'{"username":"a","username":"b","password":"x"}',400,'INVALID_REQUEST'),
          (b'{"username":"a","password":NaN}',400,'INVALID_REQUEST'),
          (b'\xff',400,'INVALID_REQUEST'),(b'x'*65537,400,'LIMIT_EXCEEDED'),
          (b'{"username":"a","password":true}',400,'INVALID_REQUEST'),
          (b'{"username":"a","password":"x","owner":2}',400,'INVALID_REQUEST')]
        for raw,status,code in invalid:
            request=SimpleNamespace(content_type='application/json',encoding='utf-8',body=raw)
            with self.assertRaises(APIError) as error:parse_request(request,'LoginRequest')
            self.assertEqual((error.exception.status,error.exception.code),(status,code))
        body=b'{"username":"a","password":"x"}';raw=body+b' '*(65536-len(body))
        self.assertEqual(parse_request(SimpleNamespace(content_type='application/json',encoding='utf-8',body=raw),'LoginRequest'),{'username':'a','password':'x'})

if __name__=='__main__':unittest.main()
