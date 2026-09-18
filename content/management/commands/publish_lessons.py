from django.core.management.base import BaseCommand, CommandError
from content.services.lesson_sources import LessonSourceError
from content.services.publishing import publish_lessons


class Command(BaseCommand):
    help = "Публикует существующие уроки из curriculum с проверкой конфликтов и резервной копией."

    def add_arguments(self, parser):
        parser.add_argument("--root", help="Каталог исходников; по умолчанию curriculum.")
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--slug", nargs="+")
        group.add_argument("--all", dest="all_lessons", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        try:
            result = publish_lessons(options["root"], options["slug"], options["all_lessons"], options["dry_run"])
        except (LessonSourceError, OSError) as exc:
            raise CommandError(str(exc)) from exc
        prefix = "Проверка без записи" if options["dry_run"] else "Публикация завершена"
        self.stdout.write(self.style.SUCCESS(f"{prefix}. Уроков: {result['selected']}; изменений содержимого/метаданных: {result['changed']}; новых связей с файлами: {result['registered']}."))
        if result["backup"]:
            self.stdout.write("Резервная копия: " + result["backup"])
