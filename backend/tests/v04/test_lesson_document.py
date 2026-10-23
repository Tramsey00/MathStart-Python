"""Strict source boundary for versioned lesson documents and material routes."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from backend.content.build import load_material_routes, apply_material_redirects
from backend.content.sources import SourceError, lesson_document_is_rendered, load_sources, load_bundle, read_json, validate_lesson_document


class LessonDocumentTests(unittest.TestCase):
    def test_material_redirects_exist_only_for_published_canonical_pages(self):
        route = {'slug': 'pilot', 'path': '/materials/7-algebra-1', 'renderer_version': 'react-v1'}
        index = {'pages': [], 'redirects': []}
        apply_material_redirects(index, {'pilot': route})
        self.assertEqual(index['redirects'], [])
        index['pages'] = [{'slug': 'pilot', 'canonical_path': route['path']}]
        apply_material_redirects(index, {'pilot': route})
        self.assertEqual(index['redirects'], [{'old_path': '/pilot/', 'new_path': route['path'], 'is_permanent': True}])

    def test_http_quality_uses_pinned_canonical_path_and_rejects_mixed_inventory(self):
        from unittest.mock import MagicMock
        from backend.content.checks import inspect_public_quality
        page = SimpleNamespace(id=1, slug='old-slug', page_type='topic')
        session = MagicMock(); session.scalars.return_value = [page]
        release = SimpleNamespace(pages={1: {'slug': 'old-slug', 'seo': {'canonical_path': '/materials/7-algebra-1'}}})
        response = MagicMock(); response.status = 200; response.url = 'https://example.org/materials/7-algebra-1'
        response.read.return_value = b'<h1>Published lesson</h1>'
        opener = MagicMock(); opener.open.return_value.__enter__.return_value = response
        with patch('backend.content.checks.build_opener', return_value=opener):
            report, errors = inspect_public_quality(session, 'https://example.org', release=release)
        self.assertEqual(errors, 0); self.assertEqual(report['pages_checked'], 1)
        self.assertEqual(opener.open.call_args.args[0].full_url, response.url)
        with self.assertRaisesRegex(SourceError, 'inventory'):
            inspect_public_quality(session, 'https://example.org', release=SimpleNamespace(pages={}))

    def test_document_metadata_must_match_source_identity(self):
        from pathlib import Path
        from copy import deepcopy
        root = Path(__file__).resolve().parents[3]
        path = next(root.glob('curriculum/7-klass/algebra/02-linejnaya-funkciya-y-kx-b/03-*/lesson.json'))
        for key in ('grade', 'subject', 'section', 'title'):
            def changed_json(source):
                data = read_json(source)
                if source.name == 'content.json':
                    data = deepcopy(data); data[key] += '-different'
                return data
            with self.subTest(key=key), patch('backend.content.sources.read_json', side_effect=changed_json):
                with self.assertRaisesRegex(SourceError, 'metadata'):
                    load_bundle(root, path)

    def test_current_pilot_source_is_validated_and_versioned(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[3]
        bundles = load_sources(root)
        pilot = next(bundle for bundle in bundles if bundle.snapshot['slug'] == 'linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii')
        self.assertEqual(pilot.renderer_version, 'react-v1')
        self.assertEqual(len(pilot.lesson_document['sections']), 13)
        self.assertTrue(any(entry['path'].endswith('/content.json') for entry in pilot.files))
        from backend.infrastructure.http.contracts import validator
        self.assertTrue(validator('LessonDocument', True).is_valid(pilot.lesson_document))

    def setUp(self):
        self.document = {
            'version': 'lesson-document-v1', 'slug': 'pilot', 'title': 'Пилот',
            'subtitle': '', 'grade': '7 класс', 'subject': 'Алгебра', 'section': 'Функции',
            'sections': [{'id': 'intro', 'title': 'Введение', 'nodes': [
                {'kind': 'paragraph', 'tag': 'p', 'attrs': {}, 'children': [{'kind': 'text', 'text': 'Текст'}]},
                {'kind': 'interactive', 'name': 'linear', 'id': 'linear-graph'},
            ]}],
        }

    def test_valid_document_and_strict_negative_cases(self):
        validate_lesson_document(self.document, 'pilot')
        attacks = []
        from copy import deepcopy
        for attrs in (None, [], 'invalid', {'onclick': 'run()'}, {'id': {'invalid': True}}):
            invalid = deepcopy(self.document)
            invalid['sections'][0]['nodes'] = [{'kind': 'selfCheck', 'attrs': attrs, 'question': [], 'answer': [], 'disclosure': 'answer'}]
            attacks.append(invalid)
        script_tag = dict(self.document)
        script_tag['sections'] = [{'id': 'x', 'title': 'X', 'nodes': [
            {'kind': 'element', 'tag': 'script', 'attrs': {}, 'children': []}]}]
        attacks.append(script_tag)
        javascript_url = dict(self.document)
        javascript_url['sections'] = [{'id': 'x', 'title': 'X', 'nodes': [
            {'kind': 'element', 'tag': 'a', 'attrs': {'href': 'javascript:alert(1)'}, 'children': []}]}]
        attacks.append(javascript_url)
        event_attr = dict(self.document)
        event_attr['sections'] = [{'id': 'x', 'title': 'X', 'nodes': [
            {'kind': 'element', 'tag': 'p', 'attrs': {'onclick': 'run()'}, 'children': []}]}]
        attacks.append(event_attr)
        svg_event = dict(self.document)
        svg_event['sections'] = [{'id': 'x', 'title': 'X', 'nodes': [
            {'kind': 'element', 'tag': 'svg', 'attrs': {'viewBox': '0 0 1 1', 'onload': 'run()'}, 'children': []}]}]
        attacks.append(svg_event)
        inline_css = dict(self.document)
        inline_css['sections'] = [{'id': 'x', 'title': 'X', 'nodes': [
            {'kind': 'element', 'tag': 'p', 'attrs': {'style': 'background:url(javascript:run())'}, 'children': []}]}]
        attacks.append(inline_css)
        duplicate_sections = dict(self.document)
        duplicate_sections['sections'] = [self.document['sections'][0], self.document['sections'][0]]
        attacks.append(duplicate_sections)
        for attack in attacks:
            with self.subTest(attack=attack), self.assertRaises(SourceError):
                validate_lesson_document(attack, 'pilot')
        for missing in (None, {}, dict(self.document, slug='another')):
            with self.subTest(missing=missing), self.assertRaises(SourceError):
                validate_lesson_document(missing, 'pilot')

    def test_no_js_article_check_ignores_serialized_or_out_of_article_text(self):
        validate_lesson_document(self.document, 'pilot')
        complete = '<main class="lesson-article"><h1>Пилот</h1><section id="intro"><h2>Введение</h2><p>Текст</p></section></main>'
        self.assertTrue(lesson_document_is_rendered(self.document, complete))
        hidden = '<main class="lesson-article"><h1>Пилот</h1><section id="intro"><h2>Введение</h2></section></main><script>Текст</script>'
        self.assertFalse(lesson_document_is_rendered(self.document, hidden))

    def test_delivery_contract_requires_document_for_react_renderer(self):
        from backend.infrastructure.http.contracts import validator
        check = validator('ContentDelivery', True)
        delivery = {
            'delivery_version': 'content-delivery-v1', 'id': 1, 'slug': 'pilot', 'page_type': 'topic',
            'title': 'Пилот', 'grade_id': 1, 'subject_id': 2, 'section_id': 3, 'order': 1,
            'body_html': '<p>frozen snapshot</p>', 'is_published': True,
            'seo': {'title': 'Пилот', 'description': '', 'canonical_path': '/materials/7-algebra-1'},
            'created_at': '2026-10-24T00:00:00Z', 'updated_at': '2026-10-24T00:00:00Z',
            'source': {'path': 'curriculum/pilot/lesson.json', 'source_digest': 'a' * 64, 'render_digest': 'b' * 64, 'compatibility_assets_digest': 'c' * 64},
            'assets': [], 'renderer_version': 'react-v1', 'lesson_document': self.document,
        }
        self.assertTrue(check.is_valid(delivery))
        missing = dict(delivery); missing.pop('lesson_document')
        self.assertFalse(check.is_valid(missing))
        wrong = dict(delivery, renderer_version='legacy')
        self.assertFalse(check.is_valid(wrong))
        unknown = dict(delivery, renderer_version='react-v2')
        self.assertFalse(check.is_valid(unknown))

    def test_registry_rejects_duplicate_routes_and_renderer_mismatch(self):
        bundles = {'pilot': SimpleNamespace(snapshot={'grade': '7-klass', 'subject': 'algebra'}, renderer_version='react-v1')}
        good = {'version': 1, 'assignments': [
            {'slug': 'pilot', 'grade': 7, 'subject': 'algebra', 'number': 1, 'renderer_version': 'react-v1'}]}
        with patch('backend.content.build.read_json', return_value=good):
            self.assertEqual(load_material_routes('.', bundles)['pilot']['path'], '/materials/7-algebra-1')
        duplicate = {'version': 1, 'assignments': good['assignments'] * 2}
        with patch('backend.content.build.read_json', return_value=duplicate), self.assertRaises(SourceError):
            load_material_routes('.', bundles)
        mismatch = {'version': 1, 'assignments': [dict(good['assignments'][0], renderer_version='legacy')]}
        with patch('backend.content.build.read_json', return_value=mismatch), self.assertRaises(SourceError):
            load_material_routes('.', bundles)
        unknown = {'version': 1, 'assignments': [dict(good['assignments'][0], renderer_version='react-v2')]}
        with patch('backend.content.build.read_json', return_value=unknown), self.assertRaises(SourceError):
            load_material_routes('.', bundles)
        collision_bundles = dict(bundles, second=SimpleNamespace(
            snapshot={'grade': '7-klass', 'subject': 'algebra'}, renderer_version='legacy'))
        collision = {'version': 1, 'assignments': [
            good['assignments'][0],
            {'slug': 'second', 'grade': 7, 'subject': 'algebra', 'number': 1, 'renderer_version': 'legacy'}]}
        with patch('backend.content.build.read_json', return_value=collision), self.assertRaises(SourceError):
            load_material_routes('.', collision_bundles)

    def test_legacy_redirect_preserves_raw_query_string(self):
        from backend.infrastructure.http.app import public_redirect_or_missing
        release = SimpleNamespace(redirect=lambda path: {'new_path': '/materials/7-algebra-1', 'is_permanent': True})
        response = public_redirect_or_missing(release, '/old-lesson/', b'q=a%2Fb&keep=1')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers['location'], '/materials/7-algebra-1?q=a%2Fb&keep=1')


if __name__ == '__main__':
    unittest.main()
