"""Integration tests for rebuilding MathStart from source-controlled data."""

import tempfile
from pathlib import Path

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
from content.services.site_bootstrap import bootstrap_site


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
            281,
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
            280,
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
            18,
        )
        self.assertEqual(
            first["structure"][
                "redirects_created"
            ],
            280,
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