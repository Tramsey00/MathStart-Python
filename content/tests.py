from django.test import SimpleTestCase

from .quality import inspect_html


class ContentQualityTests(SimpleTestCase):
    def test_detects_visible_authoring_instructions(self):
        result = inspect_html(
            "<p>Далее здесь можно изменить html-код</p>"
        )

        self.assertTrue(result["issues"])

    def test_detects_shortcodes(self):
        result = inspect_html(
            '<p>[contact-form-7 id="x"]</p>'
        )

        self.assertTrue(result["issues"])

    def test_ignores_comments_and_script_contents(self):
        result = inspect_html(
            "<!-- edit HTML -->"
            "<script>// TODO</script>"
            "<p>Найдите x.</p>"
        )

        self.assertFalse(result["issues"])

    def test_detects_duplicate_ids_and_missing_svg_references(self):
        result = inspect_html(
            '<svg viewBox="0 0 10 10">'
            '<path id="a" fill="url(#missing)"/>'
            '<path id="a"/>'
            "</svg>"
        )

        issue_kinds = {
            issue["kind"]
            for issue in result["issues"]
        }

        self.assertEqual(
            issue_kinds,
            {
                "duplicate_id",
                "missing_svg_reference",
            },
        )