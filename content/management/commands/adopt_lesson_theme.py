from django.core.management.base import BaseCommand, CommandError
from content.services.lesson_sources import LessonSourceError
from content.services.theme_migration import adopt_theme


class Command(BaseCommand):
    help = "Подключает общий стиль степенных функций 2.0, сохраняя исходники и базу перед переносом."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        try:
            result = adopt_theme(options["dry_run"])
        except (LessonSourceError, OSError, ValueError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(str(result))
