"""Additive Grade upgrade with preserved references, in disposable test DB."""
from datetime import datetime, timezone

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class GradeUpgradeTests(TransactionTestCase):
    def test_upgrade_preserves_legacy_catalogue_and_onboarding(self):
        executor = MigrationExecutor(connection)
        executor.migrate([("content", "0001_initial")])
        try:
            executor = MigrationExecutor(connection)
            old = executor.loader.project_state([
                ("content", "0001_initial"), ("users", "0002_backfill_profiles"),
            ]).apps
            Grade, Subject = old.get_model("content", "Grade"), old.get_model("content", "Subject")
            User, Profile = old.get_model("auth", "User"), old.get_model("users", "StudentProfile")
            grade = Grade.objects.create(id=77, slug="5-klass", title="Preserved grade", order=5,
                                         description="Preserved description")
            subject = Subject.objects.create(grade=grade, slug="math", title="Preserved subject")
            user = User.objects.create(username="grade-upgrade", is_active=True)
            Profile.objects.create(user=user, selected_grade=grade, onboarding_mode="SELF_REPORT",
                                   onboarding_complete=True)
            before = {name: list(model.objects.order_by("pk").values())
                      for name, model in [("Grade", Grade), ("Subject", Subject),
                                          ("User", User), ("Profile", Profile)]}
            executor.migrate([("content", "0002_grade_created_at")])
            current = executor.loader.project_state([
                ("content", "0002_grade_created_at"), ("users", "0002_backfill_profiles"),
            ]).apps
            new_grade = current.get_model("content", "Grade")
            self.assertEqual(list(new_grade.objects.values(*before["Grade"][0])), before["Grade"])
            self.assertEqual(new_grade.objects.get(pk=77).created_at,
                             datetime(2026, 10, 4, tzinfo=timezone.utc))
            for app, name in [("content", "Subject"), ("auth", "User"), ("users", "Profile")]:
                model = current.get_model(app, "StudentProfile" if name == "Profile" else name)
                self.assertEqual(list(model.objects.order_by("pk").values()), before[name])
            self.assertEqual(current.get_model("content", "Subject").objects.get(pk=subject.pk).grade_id, 77)
        finally:
            executor = MigrationExecutor(connection)
            executor.migrate(executor.loader.graph.leaf_nodes())
