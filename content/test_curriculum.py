"""Tests for curriculum sources and conflict-safe publishing."""

import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib import admin
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import RequestFactory, TestCase, override_settings

from content.admin import ContentPageAdmin
from content.models import (
    ContentPage,
    Grade,
    LessonPublication,
    Section,
    Subject,
)
from content.services.lesson_sources import (
    PAGE_FIELDS,
    page_snapshot,
)
from content.services.publishing import (
    publish_lessons,
)

class CurriculumPublishingTests(TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(
            prefix="mathstart-curriculum-"
        )
        self.addCleanup(self.temporary.cleanup)

        self.root = (
            Path(self.temporary.name)
            / "curriculum"
        )

        self.settings_override = override_settings(
            LESSON_SOURCE_ROOT=self.root,
            LESSON_BACKUP_ROOT=(
                Path(self.temporary.name)
                / "backups"
            ),
            ALLOWED_HOSTS=[
                "testserver",
                "localhost",
            ],
        )

        self.settings_override.enable()
        self.addCleanup(
            self.settings_override.disable
        )

        self.grade = Grade.objects.create(
            title="8 класс",
            slug="8-klass",
            order=8,
        )

        self.subject = Subject.objects.create(
            title="Алгебра",
            slug="algebra",
            grade=self.grade,
            order=1,
        )

        self.section = Section.objects.create(
            title="Квадратичная функция",
            slug="quadratic-function",
            subject=self.subject,
            order=6,
        )

    def page(
        self,
        slug="quadratic-function",
        **overrides,
    ):
        fields = {
            "title": (
                "Квадратичная функция "
                "y = ax² + bx + c"
            ),
            "slug": slug,
            "page_type": (
                ContentPage.PageType.TOPIC
            ),
            "grade": self.grade,
            "subject": self.subject,
            "section": self.section,
            "order": 6,
            "body_html": (
                "<h1>Квадратичная функция</h1>"
                "<p>y = x² − 2x + 1</p>"
            ),
            "page_css": "",
            "page_js": "",
            "seo_title": "",
            "seo_description": "",
            "is_published": True,
        }

        fields.update(overrides)

        return ContentPage.objects.create(
            **fields
        )

    def write_source(self, page):
        snapshot = page_snapshot(page)

        directory = self.root / page.slug
        directory.mkdir(
            parents=True,
            exist_ok=False,
        )

        metadata = {
            "schema_version": 2,
            "format": "html",
            "page": {
                field: snapshot[field]
                for field in PAGE_FIELDS
            },
        }

        (
            directory / "lesson.json"
        ).write_text(
            json.dumps(
                metadata,
                ensure_ascii=False,
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )

        (
            directory / "body.html"
        ).write_bytes(
            snapshot["body_html"].encode(
                "utf-8"
            )
        )

        if snapshot["page_css"]:
            (
                directory / "page.css"
            ).write_bytes(
                snapshot["page_css"].encode(
                    "utf-8"
                )
            )

        if snapshot["page_js"]:
            (
                directory / "page.js"
            ).write_bytes(
                snapshot["page_js"].encode(
                    "utf-8"
                )
            )

        return directory

    def command(
        self,
        name,
        pages=None,
        **options,
    ):
        options.setdefault(
            "root",
            str(self.root),
        )

        if pages is not None:
            options["slug"] = [
                page.slug
                for page in pages
            ]

        options.setdefault(
            "stdout",
            io.StringIO(),
        )

        return call_command(
            name,
            **options,
        )

    def edit_body(self, page, body):
        path = (
            self.root
            / page.slug
            / "body.html"
        )

        path.write_bytes(
            body.encode("utf-8")
        )

    def test_first_publication_registers_source(self):
        page = self.page()
        self.write_source(page)

        self.assertFalse(
            LessonPublication.objects.exists()
        )

        self.command(
            "publish_lessons",
            [page],
        )

        publication = (
            LessonPublication.objects.get(
                page=page
            )
        )

        self.assertTrue(
            publication.source_path.endswith(
                "lesson.json"
            )
        )

    def test_changed_source_updates_page(self):
        page = self.page()
        self.write_source(page)

        self.command(
            "publish_lessons",
            [page],
        )

        body = (
            "<h1>Обновлённый урок</h1>"
            "<p>2 + 2 = 4.</p>"
        )

        self.edit_body(page, body)

        self.command(
            "publish_lessons",
            [page],
        )

        page.refresh_from_db()

        self.assertEqual(
            page.body_html,
            body,
        )

    def test_database_edit_creates_conflict(self):
        page = self.page()
        self.write_source(page)

        self.command(
            "publish_lessons",
            [page],
        )

        ContentPage.objects.filter(
            pk=page.pk
        ).update(
            body_html=(
                "<p>Правка напрямую "
                "в базе.</p>"
            )
        )

        self.edit_body(
            page,
            "<h1>Новая версия</h1>",
        )

        with self.assertRaises(
            CommandError
        ):
            self.command(
                "publish_lessons",
                [page],
            )

    def test_dry_run_changes_nothing(self):
        page = self.page()
        self.write_source(page)

        # Сначала регистрируем исходник.
        self.command(
            "publish_lessons",
            [page],
        )

        publication = LessonPublication.objects.get(
            page=page
        )
        published_digest_before = (
            publication.published_digest
        )

        self.edit_body(
            page,
            "<h1>Новая версия</h1>",
        )

        before = (
            ContentPage.objects.get(
                pk=page.pk
            ).body_html
        )

        self.command(
            "publish_lessons",
            [page],
            dry_run=True,
        )

        page.refresh_from_db()
        publication.refresh_from_db()

        # dry-run не должен менять страницу.
        self.assertEqual(
            page.body_html,
            before,
        )

        # И не должен обновлять состояние публикации.
        self.assertEqual(
            publication.published_digest,
            published_digest_before,
        )
    def test_missing_page_is_created_from_source(
        self,
    ):
        page = self.page()
        expected = page_snapshot(page)

        self.write_source(page)

        slug = page.slug
        page.delete()

        self.assertFalse(
            ContentPage.objects.filter(
                slug=slug
            ).exists()
        )

        result = publish_lessons(
            root=self.root,
            slugs=[slug],
        )

        self.assertEqual(
            result["created"],
            1,
        )
        self.assertEqual(
            result["changed"],
            1,
        )
        self.assertEqual(
            result["registered"],
            1,
        )

        recreated = (
            ContentPage.objects
            .select_related(
                "grade",
                "subject",
                "section",
            )
            .get(slug=slug)
        )

        self.assertEqual(
            page_snapshot(recreated),
            expected,
        )

        publication = (
            LessonPublication.objects.get(
                page=recreated
            )
        )

        self.assertTrue(
            publication.source_path.endswith(
                "lesson.json"
            )
        )

    def test_missing_page_dry_run_creates_nothing(
        self,
    ):
        page = self.page()
        self.write_source(page)

        slug = page.slug
        page.delete()

        result = publish_lessons(
            root=self.root,
            slugs=[slug],
            dry_run=True,
        )

        self.assertEqual(
            result["created"],
            1,
        )
        self.assertEqual(
            result["changed"],
            1,
        )
        self.assertEqual(
            result["registered"],
            1,
        )

        self.assertFalse(
            ContentPage.objects.filter(
                slug=slug
            ).exists()
        )

        self.assertFalse(
            LessonPublication.objects.exists()
        )

    def test_missing_catalog_prevents_creation(
        self,
    ):
        page = self.page()
        self.write_source(page)

        slug = page.slug
        page.delete()

        self.section.delete()

        with self.assertRaises(
            CommandError
        ):
            self.command(
                "publish_lessons",
                [page],
            )

        self.assertFalse(
            ContentPage.objects.filter(
                slug=slug
            ).exists()
        )

        self.assertFalse(
            LessonPublication.objects.exists()
        )

    def test_repeated_publication_is_idempotent(
        self,
    ):
        page = self.page()
        self.write_source(page)

        slug = page.slug
        page.delete()

        first = publish_lessons(
            root=self.root,
            slugs=[slug],
        )

        self.assertEqual(
            first["created"],
            1,
        )

        with patch(
            "content.services.publishing."
            "backup_database"
        ) as backup:
            second = publish_lessons(
                root=self.root,
                slugs=[slug],
            )

        backup.assert_not_called()

        self.assertEqual(
            second["created"],
            0,
        )
        self.assertEqual(
            second["changed"],
            0,
        )
        self.assertEqual(
            second["registered"],
            0,
        )
        self.assertIsNone(
            second["backup"]
        )

        self.assertEqual(
            ContentPage.objects.filter(
                slug=slug
            ).count(),
            1,
        )

        self.assertEqual(
            LessonPublication.objects.count(),
            1,
        )

    def test_verification_detects_changed_source(self):
        page = self.page()
        self.write_source(page)

        self.command(
            "publish_lessons",
            [page],
        )

        self.command(
            "check_lesson_sources",
            all_lessons=True,
        )

        self.edit_body(
            page,
            "<h1>Несовпадающая версия</h1>",
        )

        with self.assertRaises(
            CommandError
        ):
            self.command(
                "check_lesson_sources",
                all_lessons=True,
            )

    def test_managed_lesson_is_read_only_in_admin(
        self,
    ):
        page = self.page()
        self.write_source(page)

        self.command(
            "publish_lessons",
            [page],
        )

        page_admin = ContentPageAdmin(
            ContentPage,
            admin.site,
        )

        request = RequestFactory().get("/")

        readonly = (
            page_admin.get_readonly_fields(
                request,
                page,
            )
        )

        for field in (
            "body_html",
            "page_css",
            "page_js",
            "title",
            "slug",
            "order",
        ):
            self.assertIn(
                field,
                readonly,
            )

        self.assertFalse(
            page_admin.has_change_permission(
                request,
                page,
            )
        )