from django.core.management.base import BaseCommand, CommandError

from content.services.lesson_assets import organize_assets
from content.services.lesson_sources import LessonSourceError


class Command(BaseCommand):
    help = "Выделяет общий CSS, переносит особенности и скрипты в необязательные page.css/page.js."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        try:
            result = organize_assets(dry_run=options["dry_run"])
        except (LessonSourceError, OSError, ValueError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(str(result))
