"""Add empty profiles for existing identities without changing User evidence."""
from django.conf import settings
from django.db import migrations


def backfill_profiles(apps, schema_editor):
    user_app, user_model = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(user_app, user_model)
    Profile = apps.get_model("users", "StudentProfile")
    alias = schema_editor.connection.alias
    missing = User.objects.using(alias).exclude(
        pk__in=Profile.objects.using(alias).values("user_id"),
    ).values_list("pk", flat=True)
    pending = []
    for user_id in missing.iterator(chunk_size=500):
        pending.append(Profile(user_id=user_id))
        if len(pending) == 500:
            Profile.objects.using(alias).bulk_create(pending)
            pending = []
    if pending:
        Profile.objects.using(alias).bulk_create(pending)


class Migration(migrations.Migration):
    dependencies = [("users", "0001_initial")]
    # Reverse intentionally preserves profiles/state: app rollback may keep the
    # additive tables. Dropping evidence-bearing tables is not a rollback recipe.
    operations = [migrations.RunPython(backfill_profiles, migrations.RunPython.noop)]
