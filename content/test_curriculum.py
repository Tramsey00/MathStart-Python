"""Regression checks for lossless lesson extraction and conflict-safe publishing."""

import hashlib
import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from content.models import ContentPage, Grade, LessonPublication, Section, Subject


class CurriculumPublishingTests(TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="mathstart-curriculum-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "curriculum"
        self.settings_override = override_settings(
            LESSON_SOURCE_ROOT=self.root,
            LESSON_BACKUP_ROOT=Path(self.temporary.name) / "backups",
            ALLOWED_HOSTS=["testserver", "localhost"],
        )
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.grade = Grade.objects.create(title="8 класс", slug="8-klass", order=8)
        self.subject = Subject.objects.create(
            title="Алгебра", slug="algebra", grade=self.grade, order=1
        )
        self.section = Section.objects.create(
            title="Квадратичная функция", slug="quadratic-function",
            subject=self.subject, order=6,
        )

    def page(self, slug="quadratic-function", **overrides):
        fields = {
            "title": "Квадратичная функция y = ax² + bx + c",
            "slug": slug,
            "page_type": ContentPage.PageType.TOPIC,
            "grade": self.grade,
            "subject": self.subject,
            "section": self.section,
            "order": 6,
            "body_html": (
                '<style>.formula { color: #2563eb; }</style>\r\n'
                '<h1>Квадратичная функция</h1>\r\n'
                '<p class="formula">y = x² − 2x + 1</p>\r\n'
                '<input id="coefficient" type="range" min="-3" max="3">\r\n'
                '<svg viewBox="0 0 100 100"><path d="M 0 90 Q 50 -50 100 90"/></svg>\r\n'
                '<script>document.getElementById("coefficient").dataset.ready="true";</script>\r\n'
            ),
            "page_css": ".formula::before { content: 'Степень: '; }\r\n",
            "page_js": 'window.lessonLabel = "Функция";\r\n',
            "seo_title": "Квадратичная функция — теория",
            "seo_description": "Свойства параболы, формулы и примеры.",
            "is_published": True,
            "wordpress_id": None,
            "legacy_url": "https://old.example.invalid/quadratic/",
            "source_file": "wordpress:mysql:wp_posts:993",
            # Historical checksums are provenance, not the publication registry.
            "content_checksum": "legacy-checksum",
        }
        fields.update(overrides)
        return ContentPage.objects.create(**fields)

    def command(self, name, pages=None, **options):
        options.setdefault("root", str(self.root))
        if pages is not None:
            options["slug"] = [page.slug for page in pages]
        options.setdefault("stdout", io.StringIO())
        return call_command(name, **options)

    def document(self, page):
        for path in self.root.rglob("lesson.json"):
            data = json.loads(path.read_bytes().decode("utf-8"))
            if data["page"]["slug"] == page.slug:
                return path, data
        self.fail(f"No exported lesson.json for {page.slug}")

    def edit_metadata(self, page, **fields):
        path, data = self.document(page)
        data["page"].update(fields)
        path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    def edit_body(self, page, body="<h1>Обновлённый урок</h1><p>Проверенный пример: 2 + 2 = 4.</p>"):
        path, _ = self.document(page)
        (path.parent / "body.html").write_bytes(body.encode("utf-8"))
        return body

    def snapshot(self):
        return list(ContentPage.objects.order_by("pk").values())

    def exported_bytes(self):
        return {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in self.root.rglob("*") if path.is_file()
        }

    def register(self, page):
        self.command("export_lessons", [page])
        self.command("publish_lessons", [page])

    def test_export_and_initial_publication_preserve_fields_and_http_bytes(self):
        pilots = [
            self.page("text-lesson", title="Множества", body_html="<h1>Множества</h1>\r\n<p>Множество состоит из элементов.</p>\r\n"),
            self.page("fraction-lesson", title="Дроби", body_html='<h1>Дроби</h1>\r\n<p><span class="fraction"><span>2</span><span>3</span></span></p>\r\n'),
            self.page(),
        ]
        before = self.snapshot()
        http_before = {}
        for page in pilots:
            response = self.client.get(page.get_absolute_url())
            self.assertEqual(response.status_code, 200)
            http_before[page.slug] = response.content

        self.command("export_lessons", all_lessons=True)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(LessonPublication.objects.count(), 0)
        for page in pilots:
            manifest, data = self.document(page)
            self.assertEqual(data["schema_version"], 1)
            self.assertEqual(data["format"], "legacy_html")
            self.assertEqual(data["page"]["grade"], self.grade.slug)
            self.assertEqual(data["origin"]["source_file"], page.source_file)
            for filename, field in [("body.html", "body_html"), ("page.css", "page_css"), ("page.js", "page_js")]:
                self.assertEqual((manifest.parent / filename).read_bytes(), getattr(page, field).encode("utf-8"))

        self.command("publish_lessons", all_lessons=True)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(LessonPublication.objects.count(), len(pilots))
        for page in pilots:
            self.assertEqual(self.client.get(page.get_absolute_url()).content, http_before[page.slug])

    def test_repeated_export_and_publication_are_true_no_ops(self):
        page = self.page()
        self.register(page)
        pages_before = self.snapshot()
        registrations_before = list(LessonPublication.objects.values())
        files_before = self.exported_bytes()
        self.command("export_lessons", [page])
        self.command("publish_lessons", [page])
        self.assertEqual(self.snapshot(), pages_before)
        self.assertEqual(list(LessonPublication.objects.values()), registrations_before)
        self.assertEqual(self.exported_bytes(), files_before)

    def test_empty_resources_are_not_exported_and_are_optional_on_publish(self):
        page = self.page(page_css="", page_js="")
        self.register(page)
        manifest, _ = self.document(page)
        self.assertEqual({p.name for p in manifest.parent.iterdir()}, {"lesson.json", "body.html"})
        self.edit_body(page)
        self.command("publish_lessons", [page])
        page.refresh_from_db()
        self.assertEqual((page.page_css, page.page_js), ("", ""))
        self.command("check_lesson_sources", all_lessons=True)
        self.command("export_lessons", [page])
        self.assertFalse((manifest.parent / "page.css").exists())
        self.assertFalse((manifest.parent / "page.js").exists())

    def test_removing_optional_resources_clears_the_published_resources(self):
        page = self.page()
        self.register(page)
        manifest, _ = self.document(page)
        for name in ("page.css", "page.js"):
            (manifest.parent / name).unlink()
        self.command("publish_lessons", [page], dry_run=True)
        page.refresh_from_db()
        self.assertTrue(page.page_css)
        self.command("publish_lessons", [page])
        page.refresh_from_db()
        self.assertEqual((page.page_css, page.page_js), ("", ""))
        response = self.client.get(page.get_absolute_url()).content.decode()
        self.assertNotIn("window.lessonLabel", response)
        self.assertNotIn(".formula::before", response)

    def test_edited_sources_publish_selected_fields_and_keep_other_pages(self):
        page = self.page()
        other = self.page("untouched-lesson", order=7)
        self.register(page)
        other_before = ContentPage.objects.filter(pk=other.pk).values().get()
        origin_before = {field: getattr(page, field) for field in [
            "id", "slug", "grade_id", "subject_id", "section_id", "page_type",
            "source_file", "legacy_url", "wordpress_id", "created_at",
            "original_created_at", "original_updated_at",
        ]}
        body = self.edit_body(page)
        self.edit_metadata(page, title="Уточнённое название", order=9,
                           seo_title="Новый SEO-заголовок", seo_description="Новое описание.")
        manifest, _ = self.document(page)
        css = ".formula { color: #183153; }\r\n"
        js = 'window.lessonLabel = "Новая версия";\r\n'
        (manifest.parent / "page.css").write_bytes(css.encode("utf-8"))
        (manifest.parent / "page.js").write_bytes(js.encode("utf-8"))
        self.command("publish_lessons", [page])
        page.refresh_from_db()
        self.assertEqual(page.body_html, body)
        self.assertEqual(page.page_css, css)
        self.assertEqual(page.page_js, js)
        self.assertEqual(page.title, "Уточнённое название")
        self.assertEqual(page.order, 9)
        self.assertEqual(page.seo_title, "Новый SEO-заголовок")
        self.assertEqual(page.seo_description, "Новое описание.")
        self.assertEqual(page.content_checksum, hashlib.sha256(body.encode("utf-8")).hexdigest())
        for field, value in origin_before.items():
            self.assertEqual(getattr(page, field), value, field)
        self.assertEqual(ContentPage.objects.filter(pk=other.pk).values().get(), other_before)
        # The original export baseline remains valid through the registry.
        self.command("export_lessons", [page])
        self.edit_body(page, "<h1>Следующая редакция</h1><p>3 + 3 = 6.</p>")
        self.command("publish_lessons", [page])
        page.refresh_from_db()
        self.assertIn("Следующая редакция", page.body_html)

    def test_dry_run_never_changes_pages_registrations_or_sources(self):
        page = self.page()
        self.command("export_lessons", [page])
        before = self.snapshot()
        self.command("publish_lessons", [page], dry_run=True)
        self.assertEqual(LessonPublication.objects.count(), 0)
        self.assertEqual(self.snapshot(), before)
        self.command("publish_lessons", [page])
        self.edit_body(page)
        registrations = list(LessonPublication.objects.values())
        files_before = self.exported_bytes()
        self.command("publish_lessons", [page], dry_run=True)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(list(LessonPublication.objects.values()), registrations)
        self.assertEqual(self.exported_bytes(), files_before)

    def test_reexport_does_not_overwrite_edited_source_or_add_partial_files(self):
        page = self.page()
        self.command("export_lessons", [page])
        self.edit_body(page)
        before = self.exported_bytes()
        with self.assertRaises(CommandError):
            self.command("export_lessons", [page])
        self.assertEqual(self.exported_bytes(), before)

    def test_database_edits_to_metadata_html_css_or_js_are_conflicts(self):
        for field, changed in [
            ("title", "Исправлено в админке"),
            ("body_html", "<p>Независимая правка материала.</p>"),
            ("page_css", ".other { color: red; }"),
            ("page_js", "window.changedElsewhere = true;"),
        ]:
            with self.subTest(field=field):
                page = self.page(f"conflict-{field.replace('_', '-')}")
                self.register(page)
                ContentPage.objects.filter(pk=page.pk).update(**{field: changed})
                before = self.snapshot()
                registrations = list(LessonPublication.objects.values())
                self.edit_body(page)
                with self.assertRaises(CommandError):
                    self.command("publish_lessons", [page])
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(list(LessonPublication.objects.values()), registrations)

    def test_database_drift_before_first_publication_is_protected(self):
        page = self.page()
        self.command("export_lessons", [page])
        ContentPage.objects.filter(pk=page.pk).update(page_css=".later { opacity: .9; }")
        before = self.snapshot()
        with self.assertRaises(CommandError):
            self.command("publish_lessons", [page])
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(LessonPublication.objects.exists())

    def test_batch_conflict_prevents_every_page_update(self):
        first = self.page("a-first")
        second = self.page("z-second")
        self.command("export_lessons", all_lessons=True)
        self.command("publish_lessons", all_lessons=True)
        self.edit_body(first)
        self.edit_body(second)
        ContentPage.objects.filter(pk=second.pk).update(title="Правка вне исходников")
        before = self.snapshot()
        registrations = list(LessonPublication.objects.order_by("pk").values())
        with self.assertRaises(CommandError):
            self.command("publish_lessons", all_lessons=True)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(list(LessonPublication.objects.order_by("pk").values()), registrations)

    def test_missing_payload_and_changed_identity_cannot_publish(self):
        page = self.page()
        self.register(page)
        manifest, _ = self.document(page)
        body_path = manifest.parent / "body.html"
        body_before = body_path.read_bytes()
        body_path.unlink()
        before = self.snapshot()
        with self.assertRaises(CommandError):
            self.command("publish_lessons", [page])
        self.assertEqual(self.snapshot(), before)
        body_path.write_bytes(body_before)
        for field, value in [("slug", "replacement-url"), ("grade", "9-klass"),
                             ("subject", "geometry"), ("section", "other-section"),
                             ("page_type", "static")]:
            with self.subTest(field=field):
                original = manifest.read_bytes()
                self.edit_metadata(page, **{field: value})
                with self.assertRaises(CommandError):
                    self.command("publish_lessons", all_lessons=True)
                self.assertEqual(self.snapshot(), before)
                manifest.write_bytes(original)

    def test_invalid_html_in_one_lesson_cancels_batch(self):
        first = self.page("a-first")
        second = self.page("z-second")
        self.command("export_lessons", all_lessons=True)
        self.command("publish_lessons", all_lessons=True)
        self.edit_body(first)
        self.edit_body(second, '<h1>Урок</h1><a href="#missing">Пример</a>')
        before = self.snapshot()
        with self.assertRaises(CommandError):
            self.command("publish_lessons", all_lessons=True)
        self.assertEqual(self.snapshot(), before)

    def test_explicit_selection_and_unknown_slugs_are_checked(self):
        self.page()
        for name in ["export_lessons", "publish_lessons"]:
            with self.subTest(command=name):
                with self.assertRaises(CommandError):
                    self.command(name)
                with self.assertRaises(CommandError):
                    self.command(name, slug=["missing-lesson"])
        self.assertFalse(LessonPublication.objects.exists())

    def test_failure_during_write_rolls_back_already_saved_pages(self):
        first = self.page("a-first")
        second = self.page("z-second")
        self.command("export_lessons", all_lessons=True)
        self.command("publish_lessons", all_lessons=True)
        self.edit_body(first)
        self.edit_body(second)
        before = self.snapshot()
        registrations = list(LessonPublication.objects.order_by("pk").values())
        save = ContentPage.save

        def fail_second(instance, *args, **kwargs):
            if instance.pk == second.pk:
                raise RuntimeError("Simulated write failure")
            return save(instance, *args, **kwargs)

        with patch.object(ContentPage, "save", fail_second):
            with self.assertRaises(RuntimeError):
                self.command("publish_lessons", all_lessons=True)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(list(LessonPublication.objects.order_by("pk").values()), registrations)

    def test_managed_lesson_admin_and_historical_publishers_cannot_overwrite_files(self):
        from django.contrib import admin
        from django.test import RequestFactory
        from content.admin import ContentPageAdmin

        page = self.page()
        self.register(page)
        page_admin = ContentPageAdmin(ContentPage, admin.site)
        request = RequestFactory().get("/")
        readonly = page_admin.get_readonly_fields(request, page)
        for field in ("body_html", "page_css", "page_js", "title", "slug", "order"):
            self.assertIn(field, readonly)
        self.assertEqual(page_admin.get_prepopulated_fields(request, page), {})
        self.assertFalse(page_admin.has_change_permission(request, page))
        self.assertIn("curriculum/", page_admin.lesson_source(page))
        standalone = self.page("standalone", page_type="static")
        self.assertNotIn("body_html", page_admin.get_readonly_fields(request, standalone))
        before = self.snapshot()
        for command in ("add_grade10_algebra", "add_grade10_v2", "add_natural_v2",
                        "add_rational_v2", "refresh_power_lesson", "apply_content_repairs"):
            with self.subTest(command=command), self.assertRaises(CommandError):
                call_command(command, stdout=io.StringIO())
        self.assertEqual(self.snapshot(), before)

    def test_verification_detects_missing_and_changed_sources(self):
        page = self.page()
        self.command("export_lessons", all_lessons=True)
        self.command("check_lesson_sources", all_lessons=True)
        self.edit_body(page)
        with self.assertRaises(CommandError):
            self.command("check_lesson_sources", all_lessons=True)
