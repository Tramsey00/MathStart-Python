"""React-produced document adapter for V02's pinned-release rendering seam.

All authored HTML arrives through ReleaseStore, never from user strings. Ordinary
links perform complete document navigation: browser document disposal owns every
legacy script/listener/timer/RAF, stylesheet and observer lifecycle.
"""
from html import escape
from itertools import groupby
from pathlib import Path
from urllib.parse import urlsplit


def esc(value):
    return escape(str(value), quote=True)


def catalogue_html(context):
    full = context['catalogue_full']
    relations = {name: {row['id']: row for row in full[name]} for name in ('grades', 'subjects', 'sections')}
    def label(kind, pk, fallback):
        return esc(relations[kind].get(pk, {}).get('title') or fallback)
    def options(kind, selected, default):
        return '<option value="">' + default + '</option>' + ''.join(
            f'<option value="{esc(row["slug"])}"' + (' selected' if row['slug'] == selected else '') + f'>{esc(row["title"])}</option>'
            for row in context['catalogue_' + kind])
    query = context['catalogue_query']
    parts = [f'''<form class="ms-catalogue-form" method="get" action="/karta-sajta/" role="search" aria-label="Поиск учебных тем">
<div class="ms-catalogue-search"><label for="catalogue-q">Название темы</label><input type="search" id="catalogue-q" name="q" value="{esc(query)}" placeholder="Например, дроби или уравнения"></div>
<div class="ms-catalogue-filters"><div><label for="catalogue-grade">Класс</label><select id="catalogue-grade" name="grade">{options('grades', context['catalogue_grade'], 'Все классы')}</select></div>
<div><label for="catalogue-subject">Предмет</label><select id="catalogue-subject" name="subject" aria-describedby="catalogue-filter-help">{options('subjects', context['catalogue_subject'], 'Все предметы')}</select></div>
<button type="submit">Показать темы</button><a class="ms-catalogue-reset" href="/karta-sajta/">Сбросить всё</a></div>
<p id="catalogue-filter-help" class="ms-catalogue-help">Выберите класс и нажмите «Показать темы», чтобы уточнить список предметов.</p></form>
<p class="ms-catalogue-count" role="status">Найдено тем: <strong>{context['catalogue_count']}</strong></p>''']
    topics = context['catalogue_topics']
    if not topics:
        parts.append('<section class="ms-catalogue-empty"><h2>Ничего не найдено</h2><p>Попробуйте другое название темы или сбросьте поиск и фильтры.</p></section>')
    elif query:
        parts.append('<section aria-label="Результаты поиска"><ul class="ms-catalogue-results">')
        for row in topics:
            parts.append(f'<li><a href="{esc(row["url"])}"><span class="ms-catalogue-topic-title">{esc(row["title"])}</span><span class="ms-catalogue-context">{label("grades",row["grade_id"],"Без класса")} · {label("subjects",row["subject_id"],"Математика")} · {label("sections",row["section_id"],"Темы")}</span></a></li>')
        parts.append('</ul></section>')
    else:
        for grade, grade_rows in groupby(topics, lambda row: row['grade_id']):
            grade_rows = list(grade_rows)
            parts.append(f'<section class="ms-catalogue-grade"><h2>{label("grades",grade,"Учебные темы")} <span>{len(grade_rows)} тем</span></h2>')
            for subject, subject_rows in groupby(grade_rows, lambda row: row['subject_id']):
                parts.append(f'<section class="ms-catalogue-subject"><h3>{label("subjects",subject,"Математика")}</h3>')
                for section, section_rows in groupby(subject_rows, lambda row: row['section_id']):
                    section_rows = list(section_rows)
                    opened = ' open' if context['catalogue_grade'] or context['catalogue_subject'] else ''
                    parts.append(f'<details class="ms-catalogue-section"{opened}><summary>{label("sections",section,"Темы")} <span>{len(section_rows)}</span></summary><ul>')
                    parts.extend(f'<li><a href="{esc(row["url"])}">{esc(row["title"])}</a></li>' for row in section_rows)
                    parts.append('</ul></details>')
                parts.append('</section>')
            parts.append('</section>')
    return ''.join(parts)


class PublicRenderer:
    """Serve one hash-verified React artifact and the same pinned catalogue.

    Artifact root may contain per-release subdirectories for retained releases.
    No Node process is involved in ordinary serving.
    """
    def __init__(self, artifact_root=None, artifact_digests=None):
        import os
        import json
        self.root = Path(artifact_root or os.environ['MATHSTART_PUBLIC_ARTIFACT_ROOT']).resolve()
        self.digests = artifact_digests if artifact_digests is not None else json.loads(os.environ.get('MATHSTART_PUBLIC_ARTIFACT_DIGESTS', '{}'))

    def __call__(self, page, context, canonical_url):
        from hashlib import sha256
        import json
        from backend.content.releases import inside
        pin = context.get('pinned_release')
        if not pin or set(pin) != {'release_id', 'manifest_digest'}:
            raise ValueError('Pinned release required')
        root = self.root
        if not (root / 'output-manifest.json').exists():
            root = inside(root, pin['release_id'])
        manifest_raw = (root / 'output-manifest.json').read_bytes()
        trusted_digest = self.digests(pin) if callable(self.digests) else self.digests.get(pin['release_id'])
        if sha256(manifest_raw).hexdigest() != trusted_digest:
            raise ValueError('Untrusted or corrupted artifact manifest')
        receipt = json.loads(manifest_raw)
        if receipt['release_id'] != pin['release_id'] or receipt['input_manifest_digest'] != pin['manifest_digest']:
            raise ValueError('Artifact/release mismatch')
        path = page['seo']['canonical_path']
        if canonical_url != receipt['origin'] + path:
            raise ValueError('Canonical origin/path mismatch')
        # The page supplied by the gateway must match the built immutable DTO.
        digest = sha256(json.dumps(page, ensure_ascii=False, separators=(',', ':'), sort_keys=True).encode()).hexdigest()
        if receipt['page_semantic_digests'][path] != digest:
            raise ValueError('Page/artifact mismatch')
        entry = next(row for row in receipt['files'] if row['url'] == path)
        raw = inside(root, entry['path']).read_bytes()
        if sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError('Artifact corruption')
        result = raw.decode('utf-8')
        if page['slug'] == 'karta-sajta':
            full_digest=sha256(json.dumps(context['catalogue_full'], ensure_ascii=False, separators=(',', ':'), sort_keys=True).encode()).hexdigest()
            if full_digest != receipt['catalogue_full_digest']:
                raise ValueError('Catalogue/artifact mismatch')
            start = '<section data-mathstart-catalogue="" class="ms-catalogue">'
            end = '</section><template data-mathstart-catalogue-end=""></template>'
            if result.count(start) != 1 or result.count(end) != 1:
                raise ValueError('Invalid catalogue boundary')
            before, rest = result.split(start, 1)
            _, after = rest.split(end, 1)
            result = before + start + catalogue_html(context) + end + after
        elif page.get('renderer_version', 'legacy') == 'react-v1':
            if set(context) != {'pinned_release', 'lesson_navigation', 'grade_links'}:
                raise ValueError('Unexpected React lesson context')
        elif set(context) != {'pinned_release'}:
            raise ValueError('Unexpected public context')
        if page.get('renderer_version', 'legacy') == 'react-v1':
            from backend.content.sources import lesson_document_is_rendered
            document = page.get('lesson_document')
            if (not isinstance(document, dict) or document.get('slug') != page['slug']
                    or not isinstance(document.get('sections'), list)
                    or not lesson_document_is_rendered(document, result)
                    or '<script type="module"' not in result):
                raise ValueError('Verified React lesson artifact is incomplete')
        elif page.get('renderer_version', 'legacy') != 'legacy':
            raise ValueError('Unsupported public renderer version')
        return result


def render_page(page, context, canonical_url):
    return PublicRenderer()(page, context, canonical_url)
