from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("content", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="LessonPublication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_path", models.CharField(max_length=500, unique=True)),
                ("published_digest", models.CharField(max_length=64)),
                ("published_at", models.DateTimeField(auto_now=True)),
                ("page", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="lesson_publication", to="content.contentpage")),
            ],
            options={
                "verbose_name": "Публикация урока из файлов",
                "verbose_name_plural": "Публикации уроков из файлов",
            },
        ),
    ]
