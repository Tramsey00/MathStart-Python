from django.test import SimpleTestCase

from content.services.lesson_assets import extract_scripts
from content.services.lesson_sources import LessonSourceError


class ScriptExtractionTests(SimpleTestCase):
    def test_dom_and_svg_survive_and_script_order_is_preserved(self):
        before = '<main><svg viewBox="0 0 20 20"><path d="M 0 0 L 20 20"/></svg>'
        middle = '<button id="graph">Построить</button></main>'
        first = '\r\nwindow.graphValue = 2\r\n'
        second = 'document.getElementById("graph").textContent = window.graphValue;'
        body = before + '<script>' + first + '</script>' + middle + '<script>' + second + '</script>'
        html, js = extract_scripts(body, 'window.graphValue += 1;')
        self.assertEqual(html, before + middle)
        self.assertEqual(js, first + '\n;\n' + second + '\n;\nwindow.graphValue += 1;')
        self.assertEqual(extract_scripts(html, js), (html, js))

    def test_data_scripts_remain_html(self):
        body = '<script type="application/json">{"x": 1}</script><p>Текст</p>'
        self.assertEqual(extract_scripts(body), (body, ''))

    def test_special_execution_semantics_fail_closed(self):
        for script in (
            '<script src="/other.js"></script>',
            '<script type="module">export const x = 1;</script>',
            '<script>document.write("<p>Hi</p>")</script>',
            '<script>const source = document.currentScript;</script>',
        ):
            with self.subTest(script=script), self.assertRaises(LessonSourceError):
                extract_scripts(script)
