"""Public-site markup, scoped publication and production-static regressions."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase, override_settings

from content.models import ContentPage, Grade, LessonPublication, MediaAsset, Redirect, Section, Subject
from content.services.lesson_sources import LessonSourceError, digest, page_snapshot
from content.services.public_pages import POWER_LESSON, POWER_PDF, PUBLIC_PAGE_SLUGS, update_public_pages
from content.services.site_bootstrap import SiteBootstrapError, bootstrap_site, sha256_path


class PublicPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="mathstart-public-pages-")
        cls.runtime = Path(cls.temporary.name)
        (cls.runtime / "staticfiles").mkdir()
        cls.override = override_settings(
            MEDIA_ROOT=cls.runtime / "media", STATIC_ROOT=cls.runtime / "staticfiles",
            LESSON_BACKUP_ROOT=cls.runtime / "backups",
            STORAGES={
                "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
                "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
            },
        )
        cls.override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.override.disable()
        cls.temporary.cleanup()

    @classmethod
    def setUpTestData(cls):
        bootstrap_site()

    def setUp(self):
        self.backup_root = self.runtime / self._testMethodName / "backups"
        self.enterContext(override_settings(LESSON_BACKUP_ROOT=self.backup_root))

    def snapshot(self):
        return {model.__name__: list(model.objects.order_by("pk").values(*[
            f.attname for f in model._meta.concrete_fields
            if not getattr(f, "auto_now", False) and not getattr(f, "auto_now_add", False)
        ])) for model in (Grade, Subject, Section, ContentPage, LessonPublication, MediaAsset, Redirect)}

    def stage_old_site(self):
        for slug in PUBLIC_PAGE_SLUGS:
            ContentPage.objects.filter(slug=slug).update(body_html="<h1>Old public page</h1>")
        for slug in ("materialy", "pamyatki"):
            ContentPage.objects.create(slug=slug, title=slug, page_type="static", body_html="<p>Archived content</p>")
            Redirect.objects.filter(old_path=f"/{slug}/").delete()
            Redirect.objects.filter(old_path=f"/mathstart/{slug}/").update(new_path=f"/{slug}/")
        MediaAsset.objects.filter(file=POWER_PDF).update(related_page=ContentPage.objects.get(slug="pamyatki"))
        lesson = ContentPage.objects.get(slug=POWER_LESSON)
        soup = BeautifulSoup(lesson.body_html, "html.parser")
        pdf_link = soup.find("a", href=f"/media/{POWER_PDF}")
        if pdf_link is not None:
            lesson.body_html = lesson.body_html.replace(str(pdf_link.parent), "")
        else:
            # D066 temporarily removes this link from the current source.
            # Stage the former link so scoped publication must remove it while
            # preserving the PDF asset, file and its lesson association.
            lesson.body_html += f'<p><a href="/media/{POWER_PDF}">Legacy PDF link</a></p>'
        lesson.save(update_fields=["body_html"])
        # The old content was accepted; publication must use its usual digest.
        LessonPublication.objects.filter(page=lesson).update(published_digest=digest(page_snapshot(lesson)))

    def test_scoped_upgrade_dry_run_repeat_and_preservation(self):
        self.stage_old_site()
        extra = ContentPage.objects.create(slug="local-extra", title="Local extra", page_type="static", is_published=False)
        ordinary = ContentPage.objects.exclude(slug__in=(*PUBLIC_PAGE_SLUGS, "materialy", "pamyatki", POWER_LESSON)).first()
        ContentPage.objects.filter(pk=ordinary.pk).update(seo_description="Preserve local unrelated edit")
        user = get_user_model().objects.create_user(username="public-pages-sentinel")
        user_before = get_user_model().objects.filter(pk=user.pk).values().get()
        before = self.snapshot()
        update_public_pages(dry_run=True)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(self.backup_root.exists())
        result = update_public_pages()
        self.assertEqual(result["structure"]["pages_unpublished"], 2)
        self.assertEqual(result["publication"]["selected"], 1)
        self.assertEqual(result["publication"]["changed"], 1)
        backup = json.loads(Path(result["backup"]).read_text(encoding="utf-8"))
        self.assertTrue(all(row["model"].startswith("content.") for row in backup))
        self.assertTrue(any(row["fields"].get("body_html") == "<h1>Old public page</h1>" for row in backup))
        allowed_ids = set(ContentPage.objects.filter(slug__in=(*PUBLIC_PAGE_SLUGS, "materialy", "pamyatki", POWER_LESSON)).values_list("pk", flat=True))
        after = self.snapshot()
        for model in ("Grade", "Subject", "Section"):
            self.assertEqual(after[model], before[model])
        self.assertEqual([row for row in after["ContentPage"] if row["id"] not in allowed_ids],
                         [row for row in before["ContentPage"] if row["id"] not in allowed_ids])
        self.assertEqual(get_user_model().objects.filter(pk=user.pk).values().get(), user_before)
        extra.refresh_from_db()
        self.assertFalse(extra.is_published)
        for slug in ("materialy", "pamyatki"):
            archived = ContentPage.objects.get(slug=slug)
            self.assertFalse(archived.is_published)
            self.assertEqual(archived.body_html, "<p>Archived content</p>")
        self.assertEqual(MediaAsset.objects.get(file=POWER_PDF).related_page.slug, POWER_LESSON)
        self.assertEqual(sha256_path(self.runtime / "media" / POWER_PDF), sha256_path(settings.BASE_DIR / "site_content/media" / POWER_PDF))
        # D066 changes visible content; the asset/file checks above still apply.
        self.assertNotContains(self.client.get(f"/{POWER_LESSON}/"), f'href="/media/{POWER_PDF}"')
        for old, target in (("materialy", "karta-sajta"), ("pamyatki", POWER_LESSON)):
            for prefix in ("/", "/mathstart/"):
                self.assertRedirects(self.client.get(f"{prefix}{old}/"), f"/{target}/", status_code=301)
        self.assertNotContains(self.client.get("/sitemap.xml"), "/pamyatki/")
        self.assertNotContains(self.client.get("/sitemap.xml"), "/materialy/")
        repeat = update_public_pages()
        self.assertEqual(repeat["publication"]["changed"], 0)
        self.assertEqual(repeat["structure"]["pages_unpublished"], 0)
        self.assertEqual(self.snapshot(), after)

    def test_lesson_conflict_prevents_public_page_update(self):
        self.stage_old_site()
        ContentPage.objects.filter(slug=POWER_LESSON).update(body_html="<p>Independent lesson edit</p>")
        before = self.snapshot()
        with self.assertRaises(LessonSourceError):
            update_public_pages()
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(self.backup_root.exists())

    def test_late_error_rolls_back_lesson_static_pages_and_redirects(self):
        self.stage_old_site()
        before = self.snapshot()
        with patch("content.services.public_pages.sync_media_rows", side_effect=SiteBootstrapError("Injected media failure")):
            with self.assertRaises(SiteBootstrapError):
                update_public_pages()
        self.assertEqual(self.snapshot(), before)

    def test_actual_source_markup_metadata_and_shared_links(self):
        expected = (("/", "MathStart"), ("/karta-sajta/", "Все темы"), ("/o-proekte/", "О проекте"), ("/kontakty/", "Контакты"))
        for route, heading in expected:
            response = self.client.get(route)
            soup = BeautifulSoup(response.content, "html.parser")
            self.assertEqual([h.get_text(strip=True) for h in soup.select("h1")], [heading])
            brand = soup.select_one(".ms-site-header .ms-site-brand")
            self.assertEqual(brand["href"], "/")
            self.assertEqual(brand.get_text(strip=True), "MathStart")
            self.assertEqual(brand.svg["aria-hidden"], "true")
            self.assertEqual([a["href"] for a in soup.select(".ms-footer-links a")], ["/karta-sajta/", "/o-proekte/", "/kontakty/"])
            self.assertFalse(soup.select('a[href="/pamyatki/"], a[href="/materialy/"]'))
        catalogue = self.client.get("/karta-sajta/", {"q": "ДРОБ", "grade": "5-klass"})
        self.assertContains(catalogue, "<title>Все темы — MathStart</title>", html=True)
        self.assertGreater(catalogue.context["catalogue_count"], 0)
        self.assertNotContains(catalogue, "Навигация по сайту")
        about = self.client.get("/o-proekte/")
        self.assertContains(about, "О проекте — MathStart")
        self.assertContains(about, "это не полный курс")
        self.assertNotContains(about, "Примеры учебных материалов")
        self.assertNotContains(about, "ms-about-gallery")
        self.assertEqual(MediaAsset.objects.filter(related_page__slug="o-proekte").count(), 3)
        contacts = self.client.get("/kontakty/")
        self.assertContains(contacts, 'href="mailto:rr06@mail.ru"')
        self.assertContains(contacts, "Контакты — MathStart")
        home = BeautifulSoup(self.client.get("/").content, "html.parser")
        self.assertTrue(home.select_one('.ms-hero a[href="#classes"]'))
        self.assertEqual(len(home.select("#classes details")), 4)
        self.assertEqual(len(home.select(".ms-benefits-list > div")), 3)
        self.assertEqual(len(home.select(".ms-lesson-sequence > li")), 3)
        self.assertFalse(home.select(".ms-home-benefits .ms-card-icon, .ms-home-lesson .ms-card-icon"))
        self.assertNotIn("Выберите нужный класс, затем откройте предмет", home.get_text(" ", strip=True))

    def test_pages_render_with_production_manifest_and_served_css(self):
        storage = {**settings.STORAGES, "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}}
        with override_settings(DEBUG=False, STORAGES=storage):
            call_command("collectstatic", interactive=False, verbosity=0)
            client = Client()
            for route in ("/", "/karta-sajta/", "/o-proekte/", "/kontakty/", "/5-klass/", f"/{POWER_LESSON}/"):
                response = client.get(route)
                self.assertEqual(response.status_code, 200)
                soup = BeautifulSoup(response.content, "html.parser")
                for link in soup.select('link[rel="stylesheet"]'):
                    url = link["href"]
                    self.assertRegex(url, r"\.[0-9a-f]{12}\.css$")
                    self.assertEqual(client.get(url).status_code, 200, url)
