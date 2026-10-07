import hashlib
import json
import os
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[4]
out = root / 'docs/acceptance/MS7-MIG-R01'
original = root.parents[2]
sys.path.insert(0, str(root))
os.environ.update(DJANGO_SETTINGS_MODULE='config.settings', DJANGO_SECRET_KEY='r01-metadata-only',
                  DJANGO_DB_BACKEND='postgresql', DJANGO_DB_NAME='ms6_v01_smoke_ms7_mig_r01_20261007',
                  DJANGO_DB_USER='r01_disposable', DJANGO_DB_PASSWORD='r01-disposable-only',
                  DJANGO_DB_HOST='127.0.0.1', DJANGO_DB_PORT='55437', DJANGO_DEBUG='False')
import django
django.setup()
from django.core.management import get_commands
from django.apps import apps
from django.urls import get_resolver, URLResolver

def save(name, data):
    (out / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + '\n', encoding='utf-8')

manifest = json.loads((out / 'source-manifest.json').read_text(encoding='utf-8'))
counts = {}
for x in manifest['files']:
    a, b = original / x['path'], root / x['path']
    aa, bb = a.read_bytes(), b.read_bytes()
    label = 'identical' if aa == bb else 'CRLF_LF_only' if aa.replace(b'\r\n',b'\n') == bb.replace(b'\r\n',b'\n') else 'substantive'
    x['original_candidate_relation'] = label
    counts[label] = counts.get(label, 0) + 1
    # .gitattributes is now a deliberately scoped R01 change.
    if label == 'substantive':
        assert x['path'] in {'.gitattributes', 'AGENTS.md', 'README.md'}, x['path']
manifest['comparison_at_preparation'] = counts
manifest['note'] = 'Original/candidate hashes were captured before R01 additions. Current R01 root documents and .gitattributes have scoped recorded changes; input source hashes remain pinned independently.'
save('source-manifest.json', manifest)
file_inventory = json.loads((out / 'file-inventory.json').read_text(encoding='utf-8'))
file_inventory['installed_command_registry'] = get_commands()
save('file-inventory.json', file_inventory)
models = []
for m in apps.get_models():
    models.append({'model': m._meta.label, 'table': m._meta.db_table,
                   'fields': [{'name': f.name, 'column': f.column, 'type': type(f).__name__,
                               'primary_key': f.primary_key, 'null': f.null, 'blank': f.blank,
                               'unique': f.unique, 'db_index': f.db_index,
                               'auto_now': getattr(f,'auto_now',False), 'auto_now_add': getattr(f,'auto_now_add',False),
                               'default': str(f.default), 'db_default': str(f.db_default),
                               'relation': f.related_model._meta.label if f.is_relation else None,
                               'on_delete': getattr(getattr(f.remote_field,'on_delete',None),'__name__',None)}
                              for f in m._meta.concrete_fields],
                   'constraints': [str(c) for c in m._meta.constraints]})
save('model-inventory.json', models)
routes = []
def walk(patterns, prefix=''):
    for r in patterns:
        path = prefix + str(r.pattern)
        if isinstance(r, URLResolver):
            walk(r.url_patterns, path)
        else:
            routes.append({'pattern':path,'name':r.name,'callback':r.lookup_str})
walk(get_resolver().url_patterns)
save('route-inventory.json', {'debug':False,'routes':routes,'note':'DEBUG foundation/media patterns documented separately; public content URLs enumerated in rendered-runtime-digests.json. Resolver existence is not HTTP acceptance.'})
print(json.dumps({'comparison':counts,'commands':len(get_commands()),'models':len(models),'route_patterns':len(routes)}))
