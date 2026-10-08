"""Capture code metadata and disposable schema, never configured working DB."""
import json
import os
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(root))
assert os.environ.get('DJANGO_DB_PORT')=='55439'
assert os.environ.get('DJANGO_DB_NAME')=='ms6_v01_smoke_ms7_mig_r02_20261008'
os.environ['DJANGO_SETTINGS_MODULE']='config.settings'
import django
django.setup()
from django.apps import apps
from django.db import connection
from django.db.models import NOT_PROVIDED
from django.db.migrations.recorder import MigrationRecorder

def default(value):
    if value is NOT_PROVIDED:return {'kind':'not_provided'}
    if callable(value):return {'kind':'application_callable','value':value.__module__+'.'+value.__qualname__}
    return {'kind':'application_value','value':value}

models=[]
for model in [*apps.get_models(include_auto_created=True),MigrationRecorder.Migration]:
    fields=[]
    for f in model._meta.local_fields:
        item={'name':f.name,'column':f.column,'target_table':model._meta.db_table,'target_column':f.column,
          'operation':'PRESERVE_SAME_COLUMN_AND_VALUES','type':f.get_internal_type(),
          'db_type':f.db_type(connection),'null':f.null,'blank':f.blank,'unique':f.unique,
          'primary_key':f.primary_key,'max_length':f.max_length,'db_index':f.db_index,
          'default':default(f.default),'db_default':default(f.db_default),
          'auto_now':getattr(f,'auto_now',False),'auto_now_add':getattr(f,'auto_now_add',False),
          'choices':list(f.choices) if f.choices else [],
          'validators':[v.__class__.__module__+'.'+v.__class__.__name__ for v in f.validators]}
        if f.remote_field:
            item['relationship']={'to_table':f.remote_field.model._meta.db_table,
              'to_column':f.target_field.column,'on_delete_service':f.remote_field.on_delete.__name__,
              'physical_action':'Compare R01 SQL FK definition; no implicit SQL cascade',
              'target_behavior':'Collector-equivalent service including PROTECT before bulk/single mutation'}
        fields.append(item)
    models.append({'model':model._meta.label,'table':model._meta.db_table,
      'target_table':model._meta.db_table,'operation':'PRESERVE','auto_created':bool(model._meta.auto_created),
      'fields':fields,'unique_together':[list(v) for v in model._meta.unique_together],
      'constraints':[{'name':c.name,'definition':str(c.deconstruct())} for c in model._meta.constraints],
      'm2m':[{'name':f.name,'through':f.remote_field.through._meta.db_table,'target':f.remote_field.model._meta.db_table} for f in model._meta.local_many_to_many]})

with connection.cursor() as c:
    c.execute('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY')
    c.execute('''SELECT schemaname, sequencename, data_type, start_value,
                       min_value, max_value, increment_by, cycle, cache_size, last_value
                FROM pg_sequences WHERE schemaname='public' ORDER BY sequencename''')
    names=[d[0] for d in c.description]
    seq=[dict(zip(names,r)) for r in c.fetchall()]
    c.execute('''SELECT t.relname table_name,a.attname column_name,a.attidentity identity_kind,
                       pg_get_serial_sequence('public.'||t.relname,a.attname) owned_sequence
                FROM pg_class t JOIN pg_namespace n ON n.oid=t.relnamespace
                JOIN pg_attribute a ON a.attrelid=t.oid
                WHERE n.nspname='public' AND t.relkind='r' AND a.attnum>0
                  AND NOT a.attisdropped AND (a.attidentity<>'' OR
                       pg_get_serial_sequence('public.'||t.relname,a.attname) IS NOT NULL)
                ORDER BY t.relname,a.attname''')
    names=[d[0] for d in c.description]
    ids=[dict(zip(names,r)) for r in c.fetchall()]
    c.execute('ROLLBACK')
old=json.loads((root/'docs/acceptance/MS7-MIG-R01/runtime-data-manifest.json').read_text(encoding='utf-8'))
physical={key:old[key] for key in ['columns','constraints','indexes','migrations','sequences']}
physical['column_mapping']=[{'source_table':v['table_name'],'source_column':v['column_name'],
  'target_table':v['table_name'],'target_column':v['column_name'],'operation':'PRESERVE_TYPES_NULLABILITY_VALUES_DEFAULTS'} for v in old['columns']]
data={'version':'migration-r02-v1','source':'R01 read-only physical manifest + exact baseline Django model metadata',
 'input_sha':'c133f920fc14ab18a463e039f8e480e064ced81c','physical_baseline':physical,
 'models':models,'fresh_disposable_sequence_evidence':{'database_profile':'fresh_baseline_Django_only',
 'server_port':55439,'working_DB_access':False,'read_transaction':'REPEATABLE READ READ ONLY / ROLLBACK',
 'sequences':seq,'identity_columns':ids,'limitations':'Sequence last_value belongs to disposable fresh bootstrap, never the working DB. V01 must inventory deployed copy and preserve higher sequence values.'}}
out=root/'specs/migration/r02-v1/schema-mapping-v1.json'
out.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf-8',newline='\n')
print(f'Mapped {len(models)} tables, {len(old["columns"])} physical columns, {len(seq)} sequences')
