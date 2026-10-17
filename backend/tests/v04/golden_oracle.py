"""Isolated legacy template oracle: run only in the separate Django environment."""
from hashlib import sha256
import json
from pathlib import Path

from django.conf import settings
settings.configure(TEMPLATES=[{'BACKEND': 'django.template.backends.django.DjangoTemplates',
                              'DIRS': [str(Path('templates').resolve())], 'APP_DIRS': False}],
                   INSTALLED_APPS=[])
import django
django.setup()
from content.services.lesson_components import render_component_lesson, render_themed_contents

result = {}
for path in sorted(Path('curriculum').rglob('lesson.json')):
    metadata = json.loads(path.read_bytes())
    raw = path.with_name('body.html').read_bytes().decode('utf-8')
    kind = metadata['format']
    body = render_component_lesson(raw) if kind == 'component_html' else render_themed_contents(raw) if kind == 'themed_html' else raw
    result[metadata['page']['slug']] = sha256(body.encode('utf-8')).hexdigest()
print(json.dumps(result, sort_keys=True))
