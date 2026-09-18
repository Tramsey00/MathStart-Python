"""Repository checks preventing old per-lesson themes from returning."""
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from content.services.css_cleanup import parse_rules, selector_words
from content.services.lesson_components import SourceTree


class SharedStyleContractTests(SimpleTestCase):
    def test_local_styles_only_target_lesson_features(self):
        common = {'ms-post', 'ms-lesson-page', 'ms-legacy-lesson'}
        for path in (settings.BASE_DIR / 'static/mathstart/css').glob('lesson*.css'):
            for rule in parse_rules(path.read_text(encoding='utf-8')):
                common.update(selector_words(rule.selector))
        for path in (settings.BASE_DIR / 'curriculum').rglob('page.css'):
            with self.subTest(path=path.relative_to(settings.BASE_DIR)):
                rules = list(parse_rules(path.read_text(encoding='utf-8')))
                self.assertTrue(rules, 'An empty page.css must be removed.')
                for rule in rules:
                    feature_context = bool(re.search(r'#[\w-]+|\[data-ms-', rule.selector))
                    self.assertTrue(feature_context or selector_words(rule.selector) - common,
                                    f'Common component override: {rule.selector}')

    def test_lesson_markup_has_no_embedded_or_retired_styles(self):
        for path in (settings.BASE_DIR / 'curriculum').rglob('body.html'):
            with self.subTest(path=path.relative_to(settings.BASE_DIR)):
                source = path.read_text(encoding='utf-8')
                tree = SourceTree(source)
                self.assertFalse(any(node.tag in ('style', 'link') for node in tree.elements))
                self.assertNotIn('data-lesson-base=', source)
                self.assertTrue(any(node.has_class('ms-lesson-page') for node in tree.elements))
