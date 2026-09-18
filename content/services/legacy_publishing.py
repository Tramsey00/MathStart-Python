"""Prevent historical generators from replacing filesystem-managed lessons."""
from django.core.management.base import CommandError
from content.models import LessonPublication


def require_unmanaged_database():
    if LessonPublication.objects.exists():
        raise CommandError(
            "Уроки этой базы уже переведены в curriculum/. Исторический генератор "
            "отключён, чтобы не заменить редактируемые исходники. Используйте "
            "manage.py publish_lessons --slug АДРЕС. См. docs/editing-lessons.md."
        )
