"""Shared theme adoption must preserve authored mathematics and widget code."""
import copy
import tempfile
from pathlib import Path

from bs4 import BeautifulSoup
from django.conf import settings
from django.template.loader import render_to_string
from django.test import SimpleTestCase, override_settings

from content.lessons.v2.layout import render as historical_render
from content.lessons.v2.natural import PAGE as NATURAL
from content.lessons.v2.power import PAGE as POWER
from content.lessons.v2.rational import PAGE as RATIONAL
from content.models import ContentPage
from content.services.lesson_components import SourceTree, component, render_component_lesson, render_legacy_contents
from content.services.lesson_sources import LessonBundle, LessonSourceError, digest, json_bytes
from content.services.lesson_theme import MARKER, theme_context
from content.services.theme_migration import prepare_lesson


def visible_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.select("script, style"):
        node.decompose()
    return " ".join(soup.get_text(" ", strip=True).split())


def raw_elements(html, tag):
    tree = SourceTree(html)
    return [html[node.start:node.end] for node in tree.elements if node.tag == tag]


class LessonThemeMigrationTests(SimpleTestCase):
    svg = ('<svg id="original-diagram" viewBox="0 0 120 80" aria-label="График">'
           '\n  <defs><clipPath id="plotClip"><rect width="120" height="80"/></clipPath></defs>'
           '\n  <path clip-path="url(#plotClip)" d="M 0,80 Q 60,0 120,80"/>\n</svg>')
    script = ('<script>\nconst label = "x < 4 & y > 0";\n'
              'document.querySelector("#original-diagram").dataset.ready = "true";\n</script>')
    css = ('.ms-post .ms-title { color: #102a56; }\r\n'
           '@media (max-width: 900px) { .ms-post .ms-title { font-size: 23px; } }\r\n')

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def bundle(self, body, slug="old-lesson"):
        directory = self.root / slug
        directory.mkdir()
        page = {
            "slug": slug, "page_type": "topic", "grade": "10-klass",
            "subject": "algebra", "section": "real-numbers", "title": "Урок",
            "order": 1, "seo_title": "", "seo_description": "", "is_published": True,
        }
        snapshot = {**page, "body_html": body, "page_css": "", "page_js": ""}
        metadata = {"schema_version": 1, "format": "legacy_html", "page": page,
                    "origin": {}, "baseline_digest": digest(snapshot)}
        path = directory / "lesson.json"
        path.write_bytes(json_bytes(metadata))
        (directory / "body.html").write_bytes(body.encode("utf-8"))
        (directory / "page.css").write_bytes(b"")
        (directory / "page.js").write_bytes(b"")
        return LessonBundle(path, path.relative_to(self.root).as_posix(), metadata, snapshot)

    def legacy_body(self):
        return (
            '<style media="screen">' + self.css + '</style>\n'
            '<main class="ms-post"><section class="ms-hero"><h1 class="ms-title">Числа</h1>'
            '<span id="lesson-section-1">Начало</span></section>'
            '<section class="ms-section"><h2>1. Числа и формулы</h2>'
            '<p>Формула: <span class="ms-frac"><span>1</span><span>2</span></span>.</p>'
            + self.svg + '</section><section id="practice" class="ms-section-soft">'
            '<h2>2. Самопроверка</h2><p>Сравните числа.</p>'
            '<details class="ms-answer"><summary>Решение</summary><p>2 &gt; 1.</p></details>'
            '</section></main>' + self.script
        )

    def test_legacy_migration_preserves_exact_svg_scripts_and_responsive_css(self):
        bundle = self.bundle(self.legacy_body())
        files_before = {path.name: path.read_bytes() for path in bundle.path.parent.iterdir()}
        metadata_before = copy.deepcopy(bundle.metadata)
        snapshot_before = copy.deepcopy(bundle.snapshot)

        plan = prepare_lesson(bundle)

        self.assertFalse(plan["modern"])
        self.assertEqual(plan["metadata"]["format"], "themed_html")
        self.assertIn(MARKER, plan["body"])
        self.assertIn('data-lesson-layout="legacy"', plan["body"])
        self.assertIn(self.svg, plan["body"])
        self.assertEqual(raw_elements(plan["body"], "script"), [self.script])
        self.assertEqual(list(plan["assets"].values()), [self.css.encode("utf-8")])
        soup = BeautifulSoup(plan["body"], "html.parser")
        link = soup.select_one("link[data-lesson-legacy-style]")
        self.assertEqual(link["href"], settings.STATIC_URL + next(iter(plan["assets"])))
        self.assertEqual(link["media"], "screen")
        self.assertFalse(soup.select_one(".ms-desktop-toc").has_attr("style"))
        self.assertEqual(metadata_before, bundle.metadata)
        self.assertEqual(snapshot_before, bundle.snapshot)
        self.assertEqual(files_before, {path.name: path.read_bytes() for path in bundle.path.parent.iterdir()})

    def test_generated_contents_keep_existing_ids_and_avoid_collisions(self):
        bundle = self.bundle(self.legacy_body())
        first, repeated = prepare_lesson(bundle), prepare_lesson(bundle)
        self.assertEqual(first["body"], repeated["body"])
        soup = BeautifulSoup(first["body"], "html.parser")
        ids = [node["id"] for node in soup.select("[id]")]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual([a["href"] for a in soup.select(".ms-toc-link")],
                         ["#lesson-section-2", "#practice"])
        self.assertEqual([a.strong.get_text() for a in soup.select(".ms-toc-link")],
                         ["Числа и формулы", "Самопроверка"])
        self.assertIn("1", soup.select_one(".ms-toc-practice small").get_text())

    def test_marked_source_is_skipped_without_changing_it(self):
        bundle = self.bundle(self.legacy_body())
        plan = prepare_lesson(bundle)
        body_path = bundle.path.parent / "body.html"
        body_path.write_bytes(plan["body"].encode("utf-8"))
        before = body_path.read_bytes()
        self.assertIsNone(prepare_lesson(bundle))
        self.assertEqual(body_path.read_bytes(), before)

    def test_legacy_contents_follow_headings_without_manual_link_edits(self):
        plan = prepare_lesson(self.bundle(self.legacy_body()))
        changed = plan["body"].replace("<h2>1. Числа и формулы</h2>", "<h2>1. Новое название раздела</h2>")
        output = render_legacy_contents(changed)
        soup = BeautifulSoup(output, "html.parser")
        self.assertEqual(soup.select_one('.ms-toc-link strong').get_text(), "Новое название раздела")
        self.assertEqual(render_legacy_contents(output), output)

    def test_solutions_inside_theory_are_not_labelled_self_check(self):
        raw = self.legacy_body().replace(self.svg, self.svg + '<div class="ms-task"><details class="ms-answer"><summary>Разбор примера</summary><div>2 + 2 = 4.</div></details></div>')
        output = prepare_lesson(self.bundle(raw))["body"]
        soup = BeautifulSoup(output, "html.parser")
        self.assertEqual(len(soup.select('.ms-toc-practice')), 1)
        self.assertEqual(soup.select_one('.ms-toc-practice')['href'], '#practice')

    def test_legacy_relative_css_resources_require_review(self):
        body = self.legacy_body().replace(self.css, '.ms-hero{background:url(../image.svg)}')
        bundle = self.bundle(body)
        with self.assertRaisesMessage(LessonSourceError, "относительные ресурсы"):
            prepare_lesson(bundle)
        self.assertEqual((bundle.path.parent / "body.html").read_bytes(), body.encode("utf-8"))

    def test_all_three_reference_lessons_keep_text_ids_svg_and_twelve_solutions(self):
        for lesson in (POWER, NATURAL, RATIONAL):
            with self.subTest(slug=lesson["slug"]):
                original = historical_render(lesson)
                bundle = self.bundle(original, lesson["slug"])
                files_before = {path.name: path.read_bytes() for path in bundle.path.parent.iterdir()}
                plan = prepare_lesson(bundle)
                self.assertTrue(plan["modern"])
                self.assertEqual(plan["metadata"]["format"], "component_html")
                self.assertEqual(plan["assets"], {})
                self.assertEqual(raw_elements(plan["body"], "style"), [])
                self.assertEqual(raw_elements(plan["body"], "script"), [])
                rendered = render_component_lesson(plan["body"])
                self.assertEqual(visible_text(rendered), visible_text(original))
                self.assertEqual(raw_elements(rendered, "svg"), raw_elements(original, "svg"))
                old_soup = BeautifulSoup(original, "html.parser")
                new_soup = BeautifulSoup(rendered, "html.parser")
                self.assertEqual([node["id"] for node in new_soup.select("[id]")],
                                 [node["id"] for node in old_soup.select("[id]")])
                old_answers = [visible_text(str(node)) for node in old_soup.select(".ms-answer > div")]
                new_answers = [visible_text(str(node)) for node in new_soup.select(".ms-answer > div")]
                self.assertEqual(len(new_answers), 12)
                self.assertEqual(new_answers, old_answers)
                self.assertEqual(render_component_lesson(rendered), rendered)
                self.assertEqual(files_before, {path.name: path.read_bytes() for path in bundle.path.parent.iterdir()})

    def test_modified_reference_assets_cannot_be_discarded(self):
        original = historical_render(POWER).replace("<style>", "<style>/* authored change */", 1)
        bundle = self.bundle(original, POWER["slug"])
        with self.assertRaisesMessage(LessonSourceError, "ресурсы отличаются"):
            prepare_lesson(bundle)
        self.assertEqual((bundle.path.parent / "body.html").read_bytes(), original.encode("utf-8"))

    def test_component_rendering_requires_an_explicit_theme(self):
        with self.assertRaisesMessage(ValueError, "power-v2"):
            render_component_lesson(self.legacy_body())

    def test_component_titles_escape_while_authored_formulas_remain_html(self):
        rendered = component("section", {"id": "definition", "title": "<b>Определение</b>",
                                         "body_html": '<p>x<sup>2</sup> &gt; 0</p>'})
        self.assertIn("&lt;b&gt;Определение&lt;/b&gt;", rendered)
        self.assertIn('<p>x<sup>2</sup> &gt; 0</p>', rendered)
        toc = component("contents", {"entries": [{"id": "definition", "title": "<b>Тема</b>",
                                                   "note": '<img src="x">'}]})
        self.assertNotIn("<img", toc)
        self.assertNotIn("<b>", toc)
        self.assertIn('href="#definition"', toc)


@override_settings(STORAGES={"staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}})
class LessonThemeAssetTests(SimpleTestCase):
    def page(self, layout="legacy", widget=False):
        body = f'<main class="ms-post ms-lesson-page" {MARKER} data-lesson-layout="{layout}"'
        if widget:
            body += ' data-lesson-widget="power-functions"'
        return ContentPage(page_type="topic", slug="lesson", title="Урок", body_html=body + "></main>")

    def test_unmarked_pages_are_unchanged_and_marked_site_pages_share_the_theme(self):
        page = self.page()
        page.body_html = '<main class="ms-post">Старый урок</main>'
        self.assertEqual(theme_context(page), {})
        page = self.page()
        page.page_type = "static"
        self.assertIn('mathstart/css/lesson.css', theme_context(page)['theme_before'])
        self.assertIn('mathstart/css/site-pages.css', theme_context(page)['theme_before'])

    def test_every_lesson_format_uses_the_same_reference_styles(self):
        for layout in ("legacy", "components"):
            with self.subTest(layout=layout):
                page = self.page(layout)
                context = theme_context(page)
                html = render_to_string("page_detail.html", {"page": page, **context})
                soup = BeautifulSoup(html, "html.parser")
                links = soup.select('link[rel="stylesheet"]')
                self.assertTrue(links)
                self.assertTrue(all(not link.get("media") for link in links))
                self.assertEqual([link['href'].split('/')[-1] for link in links],
                                 ['site.css', 'lesson.css', 'lesson-math.css', 'lesson-components.css', 'lesson-diagrams.css', 'lesson-contents.css'])
                self.assertEqual(len(soup.select('script[src$="lesson-navigation.js"]')), 1)
                for asset in context["theme_before"] + context["theme_scripts"]:
                    self.assertTrue((settings.BASE_DIR / "static" / asset).is_file(), asset)

    def test_power_widget_assets_are_loaded_once_and_only_for_its_lesson(self):
        common = theme_context(self.page("components"))
        powered = theme_context(self.page("components", widget=True))
        self.assertEqual(len(powered["theme_scripts"]), len(set(powered["theme_scripts"])))
        self.assertEqual(powered["theme_scripts"][-2:],
                         ["mathstart/js/math.js", "mathstart/js/widgets/power-functions.js"])
        self.assertNotIn("mathstart/js/math.js", common["theme_scripts"])
        self.assertIn("mathstart/css/widgets/power-functions.css", powered["theme_before"])
        for asset in powered["theme_before"] + powered["theme_scripts"]:
            self.assertTrue((settings.BASE_DIR / "static" / asset).is_file(), asset)

    def test_local_resources_follow_base_and_execute_after_lesson_markup(self):
        page = self.page()
        page.body_html = page.body_html.replace('<main ', '<main data-lesson-base="classic" ')
        page.page_css = '.specific-figure { width: 300px; }'
        page.page_js = 'window.specificFigureReady = true;'
        html = render_to_string("page_detail.html", {"page": page, **theme_context(page)})
        self.assertLess(html.index('lesson.css'), html.index(page.page_css))
        self.assertLess(html.index(page.page_css), html.index('<main '))
        self.assertNotIn('lesson-base.css', html)
        self.assertNotIn('lesson-legacy.css', html)
        self.assertLess(html.index('</main>'), html.index(page.page_js))
        self.assertEqual(html.count(page.page_css), 1)
        self.assertEqual(html.count(page.page_js), 1)
