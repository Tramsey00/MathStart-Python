from django.test import SimpleTestCase

from .services.css_cleanup import (
    choose_base, conflicting, Declaration, local_rules, parse_rules, relevant,
    serialize_rules,
)


def page(css, html='<div class="ms-post"><button class="a b">A</button></div>'):
    import re
    return {"rules": list(parse_rules(css)), "source": html, "words": set(re.findall(r"[a-zA-Z_][\w-]*", html))}


class CssCleanupTests(SimpleTestCase):
    def test_common_base_preserves_overlapping_component_order(self):
        css = '.a { color: blue; } .b { color: white; }'
        self.assertEqual(local_rules(page(css), list(parse_rules(css))), [])

    def test_local_override_before_common_declaration_is_not_lost(self):
        original = page('.a { color: red; } .b { color: white; }')
        result = serialize_rules(local_rules(original, list(parse_rules('.b { color: white; }'))))
        self.assertIn('.b {', result)
        self.assertIn('color: white;', result)

    def test_reversed_shared_order_keeps_local_cascade(self):
        original = page('.a { color: blue; } .b { color: white; }')
        result = serialize_rules(local_rules(original, list(parse_rules('.b { color: white; } .a { color: blue; }'))))
        self.assertIn('.b {', result)
        self.assertIn('color: white;', result)

    def test_shorthand_overrides_are_retained(self):
        original = page('.a { margin-left: 9px; } .b { margin: 0; }')
        result = serialize_rules(local_rules(original, list(parse_rules('.b { margin: 0; }'))))
        self.assertIn('margin: 0;', result)

    def test_independent_longhands_and_border_radius_can_move(self):
        self.assertFalse(conflicting(Declaration('font-size', '20px'), Declaration('font-weight', '700')))
        self.assertFalse(conflicting(Declaration('border-radius', '20px'), Declaration('border', '1px solid blue')))
        self.assertTrue(conflicting(Declaration('font', 'inherit'), Declaration('line-height', '1.5')))
        self.assertTrue(conflicting(Declaration('border', 'none'), Declaration('border-top-color', 'blue')))

    def test_importance_does_not_promote_a_page_without_important(self):
        pages = [page('.a { color: blue !important; }'), page('.a { color: red; }')]
        base = choose_base(pages, minimum_uses=1)
        self.assertTrue(base)
        self.assertFalse(base[0].declarations[0].important)
        result = serialize_rules(local_rules(pages[0], base))
        self.assertIn('color: blue !important;', result)

    def test_baseline_cannot_add_properties_missing_on_another_page(self):
        pages = [page('.a { color: blue; padding: 20px; }'), page('.a { color: red; }')]
        base = choose_base(pages, minimum_uses=1)
        self.assertNotIn('padding', serialize_rules(base))

    def test_baseline_cannot_add_a_missing_matching_selector(self):
        pages = [page('.a { color: blue; }'), page('.b { color: red; }')]
        self.assertEqual(choose_base(pages, minimum_uses=1), [])

    def test_dynamic_ready_and_hover_states_are_conservative(self):
        original = page('.a:hover { color: red; } .b:hover { color: white; }')
        result = serialize_rules(local_rules(original, list(parse_rules('.b:hover { color: white; }'))))
        self.assertIn('.b:hover', result)
        original = page('.a[data-ready="true"] { color: red; } .b[data-ready="true"] { color: white; }')
        result = serialize_rules(local_rules(original, list(parse_rules('.b[data-ready="true"] { color: white; }'))))
        self.assertIn('.b[data-ready="true"]', result)

    def test_negative_selector_is_not_removed_for_an_absent_class(self):
        self.assertTrue(relevant('.a:not(.missing)', {'a'}))
        self.assertFalse(relevant('.a .missing', {'a'}))

    def test_parser_preserves_strings_and_width_conditions(self):
        css = '@media(max-width:720px) {.a, .b {content: "a;b"; color: blue !important;}}'
        parsed = list(parse_rules(css))
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0].media, ('@media (max-width: 720px)',))
        self.assertEqual(parsed[0].declarations[0].value, '"a;b"')
        rendered = serialize_rules(parsed)
        self.assertEqual(list(parse_rules(rendered)), parsed)
        self.assertNotIn('\n\n', rendered)
