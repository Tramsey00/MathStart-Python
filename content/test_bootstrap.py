"""Integration tests for rebuilding MathStart from source-controlled data."""

import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from content.models import (
    ContentPage,
    Grade,
    LessonPublication,
    MediaAsset,
    Redirect,
    Section,
    Subject,
)
from content.services.site_bootstrap import bootstrap_site, load_site_source, sha256_path


class SiteBootstrapTests(TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(
            prefix="mathstart-bootstrap-"
        )
        self.addCleanup(self.temporary.cleanup)

        temporary_root = Path(self.temporary.name)

        self.media_root = temporary_root / "media"
        self.static_root = temporary_root / "staticfiles"
        self.backup_root = temporary_root / "backups"

        # WhiteNoise/manifest storage is appropriate for production,
        # but integration tests do not run collectstatic.
        # Use ordinary static storage so templates can resolve
        # {% static %} URLs while rendering pages.
        self.static_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.settings_override = override_settings(
            MEDIA_ROOT=self.media_root,
            STATIC_ROOT=self.static_root,
            LESSON_BACKUP_ROOT=self.backup_root,
            STORAGES={
                "default": {
                    "BACKEND": (
                        "django.core.files.storage."
                        "FileSystemStorage"
                    ),
                },
                "staticfiles": {
                    "BACKEND": (
                        "django.contrib.staticfiles."
                        "storage.StaticFilesStorage"
                    ),
                },
            },
        )
        self.settings_override.enable()

        self.addCleanup(
            self.settings_override.disable
        )

    def assert_database_counts(self):
        self.assertEqual(
            Grade.objects.count(),
            6,
        )
        self.assertEqual(
            Subject.objects.count(),
            12,
        )
        self.assertEqual(
            Section.objects.count(),
            63,
        )
        self.assertEqual(
            ContentPage.objects.count(),
            279,
        )
        self.assertEqual(
            LessonPublication.objects.count(),
            263,
        )
        self.assertEqual(
            MediaAsset.objects.count(),
            29,
        )
        self.assertEqual(
            Redirect.objects.count(),
            282,
        )

    def assert_all_published_pages_render(self):
        pages = (
            ContentPage.objects
            .filter(is_published=True)
            .order_by("id")
        )

        for page in pages:
            with self.subTest(
                slug=page.slug,
                page_type=page.page_type,
            ):
                response = self.client.get(
                    page.get_absolute_url()
                )

                self.assertEqual(
                    response.status_code,
                    200,
                    msg=(
                        "Не удалось отрендерить "
                        f"страницу {page.slug!r}: "
                        f"HTTP {response.status_code}"
                    ),
                )

    def test_bootstrap_rebuilds_site_and_is_idempotent(
        self,
    ):
        self.assertEqual(
            ContentPage.objects.count(),
            0,
        )

        first = bootstrap_site()

        self.assertEqual(
            first["structure"][
                "grades_created"
            ],
            6,
        )
        self.assertEqual(
            first["structure"][
                "subjects_created"
            ],
            12,
        )
        self.assertEqual(
            first["structure"][
                "sections_created"
            ],
            63,
        )
        self.assertEqual(
            first["structure"][
                "pages_created"
            ],
            16,
        )
        self.assertEqual(
            first["structure"][
                "redirects_created"
            ],
            282,
        )

        self.assertEqual(
            first["publication"]["created"],
            263,
        )
        self.assertEqual(
            first["publication"]["registered"],
            263,
        )

        self.assertEqual(
            first["media_total"],
            29,
        )
        self.assertEqual(
            first["media_copied"],
            29,
        )
        self.assertEqual(
            first["media_created"],
            29,
        )

        self.assert_database_counts()

        # Counts alone must not hide missing/replaced sources or retired pages.
        source = load_site_source()
        self.assertSetEqual(
            set(ContentPage.objects.exclude(page_type="topic").values_list("slug", flat=True)),
            {record["page"]["slug"] for record in source["pages"]},
        )
        self.assertFalse(ContentPage.objects.filter(slug__in=("materialy", "pamyatki")).exists())
        self.assertSetEqual(
            set(LessonPublication.objects.values_list("page__slug", flat=True)),
            set(ContentPage.objects.filter(page_type="topic").values_list("slug", flat=True)),
        )

        # Bootstrap must produce pages that can actually pass
        # through URL resolution, views, model properties and
        # Django template rendering.
        self.assert_all_published_pages_render()

        runtime_files = [
            path
            for path in self.media_root.rglob("*")
            if path.is_file()
        ]

        self.assertEqual(
            len(runtime_files),
            29,
        )

        # Running bootstrap again must not create duplicate
        # database rows or copy the same media again.
        second = bootstrap_site()

        self.assertEqual(
            second["structure"][
                "grades_created"
            ],
            0,
        )
        self.assertEqual(
            second["structure"][
                "subjects_created"
            ],
            0,
        )
        self.assertEqual(
            second["structure"][
                "sections_created"
            ],
            0,
        )
        self.assertEqual(
            second["structure"][
                "pages_created"
            ],
            0,
        )
        self.assertEqual(
            second["structure"][
                "redirects_created"
            ],
            0,
        )

        self.assertEqual(
            second["publication"]["created"],
            0,
        )
        self.assertEqual(
            second["publication"]["changed"],
            0,
        )
        self.assertEqual(
            second["publication"]["registered"],
            0,
        )

        self.assertEqual(
            second["media_copied"],
            0,
        )
        self.assertEqual(
            second["media_created"],
            0,
        )

        self.assert_database_counts()

    def test_upgrade_retires_only_two_pages_and_preserves_data_on_repeat(self):
        bootstrap_site()
        lesson_slug = "bazovye-svojstva-stepenej-s-naturalnym-pokazatelem"
        pdf = "uploads/2026/07/pamyatka-stepeni.pdf"
        retired = []
        for slug in ("materialy", "pamyatki"):
            retired.append(ContentPage.objects.create(
                slug=slug, title=slug, page_type="static", body_html="<p>Historical content</p>",
            ))
            Redirect.objects.filter(old_path=f"/mathstart/{slug}/").update(new_path=f"/{slug}/")
            Redirect.objects.filter(old_path=f"/{slug}/").delete()
        MediaAsset.objects.filter(file=pdf).update(related_page=retired[1])
        extra = ContentPage.objects.create(slug="local-extra", title="Local page", page_type="static")
        draft = ContentPage.objects.create(slug="local-draft", title="Draft", page_type="static", is_published=False)
        user = get_user_model().objects.create_user(username="catalogue-sentinel")
        user_before = get_user_model().objects.filter(pk=user.pk).values().get()
        protected = (extra.pk, draft.pk)
        protected_before = list(ContentPage.objects.filter(pk__in=protected).order_by("pk").values())
        def snapshot():
            models = (Grade, Subject, Section, ContentPage, LessonPublication, MediaAsset, Redirect)
            return {model.__name__: list(model.objects.order_by("pk").values(*[
                f.attname for f in model._meta.concrete_fields
                if not getattr(f, "auto_now", False) and not getattr(f, "auto_now_add", False)
            ])) for model in models}

        # Dry-run rolls back retirement/redirects and does not modify media.
        before = snapshot()
        bootstrap_site(dry_run=True)
        self.assertEqual(snapshot(), before)
        result = bootstrap_site()
        self.assertEqual(result["structure"]["pages_unpublished"], 2)
        for page in retired:
            page.refresh_from_db()
            self.assertFalse(page.is_published)
            self.assertEqual(page.body_html, "<p>Historical content</p>")
        self.assertEqual(list(ContentPage.objects.filter(pk__in=protected).order_by("pk").values()), protected_before)
        self.assertEqual(get_user_model().objects.filter(pk=user.pk).values().get(), user_before)
        self.assertEqual(MediaAsset.objects.get(file=pdf).related_page.slug, lesson_slug)
        self.assertEqual(sha256_path(self.media_root / pdf), sha256_path(settings.BASE_DIR / "site_content/media" / pdf))
        # D066 temporarily hides the link, retaining the PDF and media identity.
        self.assertNotContains(self.client.get(f"/{lesson_slug}/"), f'href="/media/{pdf}"')
        for old, target in (("materialy", "karta-sajta"), ("pamyatki", lesson_slug)):
            for prefix in ("/", "/mathstart/"):
                self.assertRedirects(self.client.get(f"{prefix}{old}/"), f"/{target}/", status_code=301)
        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertNotContains(sitemap, "/materialy/")
        self.assertNotContains(sitemap, "/pamyatki/")
        self.assertContains(sitemap, f"/{lesson_slug}/")
        stable = snapshot()
        repeat = bootstrap_site()
        self.assertEqual(repeat["structure"]["pages_unpublished"], 0)
        self.assertEqual(snapshot(), stable)
        self.assertEqual(ContentPage.objects.count(), 283)
