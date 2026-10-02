"""No-database Django tests of the read-only UI foundation and legacy shell."""
import importlib.util
import json
import re
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from django.http import Http404
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import Resolver404, resolve

from . import views
from .ui_foundation import load_fixture_pack

STATIC_STORAGE = {"staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}}


@override_settings(STORAGES=STATIC_STORAGE)
class UIFoundationTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def isolated_urls(self, debug):
        # Evaluate actual URL module independently under each setting; no cached reload illusion.
        with override_settings(DEBUG=debug):
            spec = importlib.util.spec_from_file_location("content._i02_test_urls", Path(__file__).with_name("urls.py"))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        return module

    def test_gallery_route_is_absent_when_debug_disabled_and_view_has_defence(self):
        yes, no = self.isolated_urls(True), self.isolated_urls(False)
        self.assertEqual(resolve("/__ui__/foundation/", urlconf=yes).func, views.ui_foundation)
        with self.assertRaises(Resolver404):
            resolve("/__ui__/foundation/", urlconf=no)
        with override_settings(DEBUG=False), self.assertRaises(Http404):
            views.ui_foundation(self.factory.get("/__ui__/foundation/"))

    @override_settings(DEBUG=True)
    def test_gallery_get_performs_no_db_queries_no_cache_and_rejects_mutations(self):
        response = views.ui_foundation(self.factory.get("/__ui__/foundation/", {"fixture": "../../private"}))
        self.assertEqual(response.status_code, 200)  # SimpleTestCase forbids all database access.
        self.assertIn("no-store", response["Cache-Control"])
        for method in ["post", "put", "patch", "delete", "head"]:
            reply = views.ui_foundation(getattr(self.factory, method)("/__ui__/foundation/"))
            self.assertEqual(reply.status_code, 405)
            self.assertEqual(reply["Allow"], "GET")

    @override_settings(DEBUG=True)
    def test_state_markup_keyboard_relationships_and_only_safe_json_are_delivered(self):
        html = views.ui_foundation(self.factory.get("/__ui__/foundation/")).content.decode()
        for state in ["ordinary", "loading", "error", "empty"]:
            self.assertIn(f'data-state="{state}"', html)
        for markup in ['FIXTURE ONLY', 'for="demo-input"', 'aria-describedby="demo-input-help demo-input-error"',
                       'role="alert"', 'role="status"', 'aria-busy="true"', 'href="#foundation-main"',
                       'noindex, nofollow', 'type="button"']:
            self.assertIn(markup, html)
        self.assertNotIn("<form", html)
        payload = json.loads(re.search(r'<script id="ui-fixtures" type="application/json">(.*?)</script>', html, re.S)[1])
        self.assertEqual(payload, load_fixture_pack())
        for secret in ['"answer"', '"checker"', '"validation_spec"', '"canonical_solution"', '"revealed_content"']:
            self.assertNotIn(secret, html)
        self.assertNotIn("http-exchanges", html)

    @override_settings(DEBUG=True)
    def test_untrusted_strings_are_escaped_in_html_and_json_script(self):
        pack = load_fixture_pack()
        sentinel = '</script><img src=x onerror="alert(1)">'
        pack["exercises"][0]["statement"] = sentinel
        with patch("content.views.load_fixture_pack", return_value=pack):
            html = views.ui_foundation(self.factory.get("/__ui__/foundation/")).content.decode()
        self.assertNotIn(sentinel, html)
        self.assertIn("&lt;/script&gt;&lt;img", html)
        self.assertIn("\\u003C/script\\u003E", html)
        field = render_to_string("ui/components/field.html", {"field_id": "x", "label": sentinel, "value": sentinel})
        self.assertNotIn(sentinel, field)

    def test_legacy_content_retains_metadata_authored_html_assets_and_catalogue(self):
        page = SimpleNamespace(meta_title="Legacy title", meta_description="Legacy description", page_type="topic",
                               page_css=".legacy {color:red}", page_js="window.legacy=true;", slug="karta-sajta",
                               body_html='<main class="legacy">Trusted authored HTML</main>')
        html = render_to_string("page_detail.html", {"page": page, "canonical_url": "https://example.invalid/legacy/",
                               "theme_before": ["mathstart/css/lesson.css"], "theme_scripts": ["mathstart/js/lesson-navigation.js"],
                               "catalogue_pages": [], "catalogue_topics": []})
        for value in ["<title>Legacy title</title>", 'name="description"', 'property="og:type"', 'content="article"',
                      'rel="canonical"', 'href="https://example.invalid/legacy/"', 'content="index, follow"',
                      'name="twitter:card"', page.body_html, page.page_css, page.page_js, 'data-lesson-page-css',
                      'mathstart/css/lesson.css', 'mathstart/js/lesson-navigation.js', 'lesson-diagrams.js', 'ms-site-footer', 'ms-catalogue']:
            self.assertIn(value, html)
        self.assertEqual(html.count('mathstart/css/site.css'), 1)
        self.assertNotIn("ui-fixtures", html)
        self.assertNotIn("schema-dispatch.js", html)
        self.assertNotIn("foundation.css", html)
