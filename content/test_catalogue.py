"""GET catalogue behavior on the configured database (including Cyrillic)."""

from bs4 import BeautifulSoup
from django.test import TestCase, override_settings

from content.models import ContentPage, Grade, Section, Subject
from content.services.catalogue import catalogue_context


@override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})
class CatalogueTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        ContentPage.objects.create(slug="karta-sajta", title="Все темы",
                                   page_type="static", body_html="<header><h1>Все темы</h1></header>")
        for number in (5, 7, 8):
            grade = Grade.objects.create(title=f"{number} класс", slug=f"{number}-klass", order=number)
            for name, slug in (("Алгебра", "algebra"), ("Геометрия", "geometry")):
                subject = Subject.objects.create(title=name, slug=slug, grade=grade)
                section = Section.objects.create(title=f"Раздел {name}", slug="section", subject=subject)
                ContentPage.objects.create(
                    title="Линейные уравнения" if slug == "algebra" else "Углы и треугольники",
                    slug=f"topic-{number}-{slug}", grade=grade, subject=subject,
                    section=section, page_type="topic", is_published=number != 8,
                )
        empty = Grade.objects.create(title="Пустой класс", slug="empty")
        Subject.objects.create(title="Пустой предмет", slug="empty", grade=empty)
        ContentPage.objects.create(title="Информация", slug="info", page_type="static")

    def get_catalogue(self, **params):
        response = self.client.get("/karta-sajta/", params)
        self.assertEqual(response.status_code, 200)
        return response, BeautifulSoup(response.content, "html.parser")

    def test_browse_hierarchy_published_only_and_real_links(self):
        response, soup = self.get_catalogue()
        self.assertEqual(response.context["catalogue_count"], 4)
        self.assertEqual(len(soup.select("main.ms-catalogue h1")), 1)
        self.assertEqual(len(soup.select(".ms-catalogue-grade")), 2)
        self.assertEqual(len(soup.select(".ms-catalogue-subject")), 4)
        self.assertEqual(len(soup.select("details summary")), 4)
        for a in soup.select(".ms-catalogue-section li a"):
            self.assertEqual(self.client.get(a["href"]).status_code, 200)
        for forbidden in ('href="/info/"', 'href="/materialy/"', 'href="/pamyatki/"',
                          'value="8-klass"', 'value="empty"', 'schema-dispatch.js'):
            self.assertNotContains(response, forbidden)
        with self.assertNumQueries(1):
            context = catalogue_context({})
            self.assertEqual(len(context["catalogue_topics"]), 4)

    def test_cyrillic_search_trim_case_context_and_filter_intersection(self):
        for query in ("  УРАВНЕНИЯ  ", "уРаВнЕнИя"):
            with self.subTest(query=query):
                response, soup = self.get_catalogue(q=query, grade="7-klass", subject="algebra")
                self.assertEqual(response.context["catalogue_count"], 1)
                self.assertEqual(soup.select_one('[name="q"]')["value"], query.strip())
                self.assertEqual(soup.select_one('[name="grade"] option[selected]')["value"], "7-klass")
                self.assertEqual(soup.select_one('[name="subject"] option[selected]')["value"], "algebra")
                self.assertFalse(soup.select("details"))
                self.assertEqual(soup.select_one(".ms-catalogue-results a")["href"], "/topic-7-algebra/")
                self.assertIn("7 класс · Алгебра · Раздел Алгебра", soup.select_one(".ms-catalogue-context").text)

    def test_grade_and_subject_options_follow_published_topics(self):
        ContentPage.objects.filter(slug="topic-5-geometry").update(is_published=False)
        response, soup = self.get_catalogue(grade="5-klass", subject="geometry")
        self.assertEqual(response.context["catalogue_subject"], "")
        self.assertEqual(response.context["catalogue_count"], 1)
        self.assertEqual([o.get("value") for o in soup.select('[name="subject"] option')], ["", "algebra"])
        response, _ = self.get_catalogue(subject="algebra")
        self.assertEqual(response.context["catalogue_count"], 2)

    def test_empty_and_invalid_parameters_are_safe(self):
        response, soup = self.get_catalogue(q="нет такой темы", grade="7-klass")
        self.assertContains(response, "Ничего не найдено")
        self.assertEqual(response.context["catalogue_count"], 0)
        self.assertEqual(len(soup.select('[name="subject"] option')), 3)
        for params in ({"grade": "-1", "subject": "999999999999999999999999"},
                       {"grade": "8-klass", "subject": "empty", "q": "   "},
                       {"grade": "' OR 1=1", "subject": "<script>"}):
            response, _ = self.get_catalogue(**params)
            self.assertEqual(response.context["catalogue_count"], 4)
        response, _ = self.get_catalogue(q='<script>alert("x")</script>')
        self.assertNotContains(response, '<script>alert("x")</script>')
        ContentPage.objects.filter(page_type="topic").update(is_published=False)
        response, soup = self.get_catalogue()
        self.assertContains(response, "Ничего не найдено")
        self.assertFalse(soup.select(".ms-catalogue-grade"))

    def test_get_form_reset_and_refresh_do_not_require_javascript(self):
        response, soup = self.get_catalogue(q="уравнения", grade="7-klass")
        form = soup.select_one("form")
        self.assertEqual(form["method"], "get")
        self.assertEqual(form["action"], "/karta-sajta/")
        for control in soup.select("input, select"):
            self.assertIsNotNone(soup.select_one(f'label[for="{control["id"]}"]'))
        self.assertEqual(soup.select_one(".ms-catalogue-reset")["href"], "/karta-sajta/")
        self.assertEqual(response.content, self.client.get(response.wsgi_request.get_full_path()).content)
        lesson = self.client.get("/topic-7-algebra/")
        self.assertNotContains(lesson, "catalogue.css")
        self.assertNotContains(lesson, "ui/tokens.css")
