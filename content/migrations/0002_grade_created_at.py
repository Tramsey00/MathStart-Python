"""Add ordering facts without replacing catalogue identities or history."""
from datetime import datetime, timezone

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("content", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="grade",
            name="created_at",
            # Legacy rows predate timestamp tracking. One deterministic epoch
            # leaves their relative order to existing IDs, without inventing
            # separate historical creation times. New rows use auto_now_add.
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime(2026, 10, 4, tzinfo=timezone.utc),
                verbose_name="Создано в Django",
            ),
            preserve_default=False,
        ),
    ]
