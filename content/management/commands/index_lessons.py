from django.core.management.base import BaseCommand, CommandError
from content.services.lesson_sources import LessonSourceError, write_lesson_index


class Command(BaseCommand):
    help = "Обновляет только curriculum/INDEX.md — указатель файлов по классам и темам."

    def add_arguments(self, parser):
        parser.add_argument("--root")

    def handle(self, *args, **options):
        try:
            count = write_lesson_index(options["root"])
        except (LessonSourceError, OSError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(f"Указатель обновлён: {count} уроков."))
