"""PostgreSQL publication regression; never interpret SQLite skips as proof."""
from concurrent.futures import ThreadPoolExecutor

from django.db import DatabaseError, connections, transaction
from django.test import TransactionTestCase, skipUnlessDBFeature

from content.models import ContentPage, LessonPublication
from content.services.lesson_sources import load_bundles
from content.services.publishing import publication_plan, publish_lessons
from content import test_curriculum


@skipUnlessDBFeature("has_select_for_update")
class PostgreSQLPublicationTests(TransactionTestCase):
    # Reuse fixture construction without inheriting/rerunning the TestCase suite.
    setUp = test_curriculum.CurriculumPublishingTests.setUp
    page = test_curriculum.CurriculumPublishingTests.page
    write_source = test_curriculum.CurriculumPublishingTests.write_source
    edit_body = test_curriculum.CurriculumPublishingTests.edit_body

    def test_nullable_catalog_join_can_publish_and_update(self):
        page = self.page()
        self.write_source(page)
        slug = page.slug
        # Fresh bootstrap reaches the locking query even when no page exists.
        # Nullable FK schema still produces outer joins for populated relations.
        page.delete()
        first = publish_lessons(root=self.root, slugs=[slug])
        self.assertEqual(first["created"], 1)
        page = ContentPage.objects.get(slug=slug)
        self.edit_body(page, "<h1>Updated PostgreSQL lesson</h1>")
        publish_lessons(root=self.root, slugs=[page.slug])
        page.refresh_from_db()
        self.assertEqual(page.body_html, "<h1>Updated PostgreSQL lesson</h1>")
        repeated = publish_lessons(root=self.root, slugs=[slug])
        self.assertEqual(repeated["changed"], 0)
        self.assertEqual(ContentPage.objects.filter(slug=slug).count(), 1)
        self.assertEqual(LessonPublication.objects.filter(page=page).count(), 1)

    def test_publication_plan_holds_page_lock_on_separate_connection(self):
        page = self.page()
        self.write_source(page)
        publish_lessons(root=self.root, slugs=[page.slug])
        publication = LessonPublication.objects.get(page=page)
        bundles = load_bundles(self.root, slugs=[page.slug])

        def contender(model, pk):
            try:
                with transaction.atomic():
                    model.objects.order_by("pk").select_for_update(nowait=True).get(pk=pk)
                return "unlocked"
            except DatabaseError as exc:
                return getattr(exc.__cause__, "sqlstate", None)
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=1) as executor:
            with transaction.atomic():
                publication_plan(bundles, lock=True)
                for model, pk in ((ContentPage, page.pk), (LessonPublication, publication.pk)):
                    with self.subTest(model=model.__name__):
                        self.assertEqual(executor.submit(contender, model, pk).result(timeout=10), "55P03")
            # Both locks must release when the publishing transaction ends.
            for model, pk in ((ContentPage, page.pk), (LessonPublication, publication.pk)):
                self.assertEqual(executor.submit(contender, model, pk).result(timeout=10), "unlocked")
