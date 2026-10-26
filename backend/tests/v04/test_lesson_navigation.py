"""Pinned catalogue presentation: section edges and the common grade footer."""
import unittest
import json
from hashlib import sha256
from pathlib import Path
import tempfile
from backend.content.lesson_context import lesson_context


class LessonNavigationTests(unittest.TestCase):
    def setUp(self):
        self.catalogue = {
            'grades': [{'id': 1, 'slug': '7-klass', 'title': 'Preserved title'}],
            'subjects': [{'id': 1, 'slug': 'algebra'}],
            'sections': [{'id': 1, 'slug': 'first', 'title': 'Первый раздел', 'order': 1},
                         {'id': 2, 'slug': 'second', 'title': 'Второй раздел', 'order': 2}],
            'topics': [dict(id=i, slug=f'topic-{i}', title=f'Topic {i}', grade_id=1,
                            subject_id=1, section_id=1 if i < 3 else 2, order=i,
                            url=f'/materials/7-algebra-{i}') for i in range(1, 5)],
        }

    def context(self, index):
        return lesson_context(self.catalogue, self.catalogue['topics'][index])

    def test_section_edges_cross_only_the_same_grade_and_subject(self):
        last = self.context(1)['lesson_navigation']
        self.assertEqual(last['next']['boundary'], 'section')
        self.assertEqual(last['next']['url'], '/materials/7-algebra-3')
        self.assertNotIn('boundary', last['previous'])
        first = self.context(2)['lesson_navigation']
        self.assertEqual(first['previous']['boundary'], 'section')
        self.assertNotIn('boundary', first['next'])
        self.catalogue['topics'].append(dict(self.catalogue['topics'][0], id=9, grade_id=2))
        self.assertIsNone(self.context(0)['lesson_navigation']['previous'])
        self.assertIsNone(self.context(3)['lesson_navigation']['next'])

    def test_section_link_and_six_display_labels_do_not_use_legacy_titles(self):
        context = self.context(0)
        self.assertEqual(context['lesson_section']['title'], 'Первый раздел')
        self.assertIn('section=first', context['lesson_section']['href'])
        self.assertEqual([g['title'] for g in context['grade_links']], [f'{i} класс' for i in range(5, 11)])
        self.assertTrue(all(g['href'].startswith('/materials?grade=') for g in context['grade_links']))

    def test_renderer_accepts_shared_context_but_refuses_missing_or_extra_fields(self):
        from frontend.rendering import PublicRenderer
        document = dict(slug='pilot', title='Пилот', subtitle='', sections=[dict(id='intro', title='Введение', nodes=[dict(kind='text', text='Текст')])])
        page = dict(slug='pilot', renderer_version='react-v1', lesson_document=document,
                    seo=dict(canonical_path='/materials/7-algebra-8'))
        raw = '<main class="lesson-article"><h1>Пилот</h1><section id="intro"><h2>Введение</h2>Текст</section></main><script type="module"></script>'.encode()
        path = page['seo']['canonical_path']
        manifest = dict(release_id='release', input_manifest_digest='a' * 64, origin='http://127.0.0.1:8131',
            page_semantic_digests={path: sha256(json.dumps(page, ensure_ascii=False, separators=(',', ':'), sort_keys=True).encode()).hexdigest()},
            files=[dict(url=path, path='lesson.html', sha256=sha256(raw).hexdigest())])
        manifest_raw = json.dumps(manifest).encode()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'output-manifest.json').write_bytes(manifest_raw)
            (root / 'lesson.html').write_bytes(raw)
            renderer = PublicRenderer(root, {'release': sha256(manifest_raw).hexdigest()})
            context = dict(self.context(0), pinned_release=dict(release_id='release', manifest_digest='a' * 64))
            self.assertIn('Текст', renderer(page, context, manifest['origin'] + path))
            missing = dict(context); del missing['lesson_section']
            for changed in (missing, dict(context, unexpected=True)):
                with self.assertRaisesRegex(ValueError, 'Unexpected React lesson context'):
                    renderer(page, changed, manifest['origin'] + path)
