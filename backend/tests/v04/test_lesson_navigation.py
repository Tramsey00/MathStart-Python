"""Pinned catalogue presentation: section edges and the common grade footer."""
import unittest
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
        self.assertTrue(all(g['href'].startswith('/karta-sajta/?grade=') for g in context['grade_links']))
