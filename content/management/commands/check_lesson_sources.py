from django.core.management.base import BaseCommand, CommandError
from content.services.lesson_sources import LessonSourceError
from content.services.publishing import verify_lessons


class Command(BaseCommand):
    help = "Проверяет точное совпадение файлов уроков с базой, включая CSS/JS и метаданные."

    def add_arguments(self, parser):
        parser.add_argument("--root")
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--slug", nargs="+")
        group.add_argument("--all", dest="all_lessons", action="store_true")

    def handle(self, *args, **options):
        try:
            result = verify_lessons(options["root"], options["slug"], options["all_lessons"])
        except (LessonSourceError, OSError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(f"Полностью совпадают с базой: {result['verified']} уроков."))
