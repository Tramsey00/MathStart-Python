"""Upgrade drill on Django's isolated test database; never the runtime DB."""
from importlib import import_module

from django.contrib.auth.hashers import make_password
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class IdentityUpgradeTests(TransactionTestCase):
    def test_upgrade_preserves_existing_users_content_and_profile_state(self):
        executor = MigrationExecutor(connection)
        # Only disposable Django test storage is rolled back to the pre-V02
        # schema for this upgrade test. No production rollback command is supplied.
        executor.migrate([("users", None)])
        try:
            executor = MigrationExecutor(connection)
            old = executor.loader.project_state([
                ("auth", "0012_alter_user_first_name_max_length"),
            ] + executor.loader.graph.leaf_nodes("content")).apps
            User, Grade = old.get_model("auth", "User"), old.get_model("content", "Grade")
            user = User.objects.create(username="upgrade-synthetic", password=make_password("Synthetic-Upgrade-Only-47!"),
                                       email="upgrade@example.invalid", is_staff=True)
            inactive = User.objects.create(username="upgrade-inactive", is_active=False)
            grade = Grade.objects.create(title="Preserved content", slug="upgrade-grade")
            before_users = list(User.objects.order_by("pk").values())
            before_grades = list(Grade.objects.order_by("pk").values())
            executor.migrate([("users", "0002_backfill_profiles")])
            current = executor.loader.project_state([
                ("users", "0002_backfill_profiles"),
            ] + executor.loader.graph.leaf_nodes("content")).apps
            Profile = current.get_model("users", "StudentProfile")
            self.assertEqual(list(current.get_model("auth", "User").objects.order_by("pk").values()), before_users)
            self.assertEqual(list(current.get_model("content", "Grade").objects.order_by("pk").values()), before_grades)
            self.assertEqual(Profile.objects.filter(user_id__in=[user.pk, inactive.pk]).count(), 2)
            self.assertEqual(Profile.objects.get(user_id=user.pk).onboarding_complete, False)
            # Backfill is safe to rerun and must not overwrite an existing profile.
            Profile.objects.filter(user_id=user.pk).update(selected_grade_id=grade.pk,
                onboarding_mode="SELF_REPORT", onboarding_complete=True)
            before_profiles = list(Profile.objects.order_by("pk").values())
            with connection.schema_editor() as editor:
                import_module("users.migrations.0002_backfill_profiles").backfill_profiles(current, editor)
            self.assertEqual(list(Profile.objects.order_by("pk").values()), before_profiles)
        finally:
            executor = MigrationExecutor(connection)
            executor.migrate(executor.loader.graph.leaf_nodes())
