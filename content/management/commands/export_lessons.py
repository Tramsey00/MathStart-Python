from django.core.management.base import BaseCommand, CommandError
from content.services.lesson_sources import LessonSourceError, export_lessons


class Command(BaseCommand):
    help = "Выгружает уроки в curriculum; не меняет базу и не перезаписывает исходники."

    def add_arguments(self, parser):
        parser.add_argument("--root", help="Каталог исходников; по умолчанию curriculum.")
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--slug", nargs="+")
        group.add_argument("--all", dest="all_lessons", action="store_true")

    def handle(self, *args, **options):
        try:
            result = export_lessons(options["root"], options["slug"], options["all_lessons"])
        except (LessonSourceError, OSError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(f"Выбрано: {result['selected']}; выгружено: {result['created']}; уже совпадают: {result['unchanged']}. База не изменена."))
