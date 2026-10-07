"""Publish only the reviewed public pages and support-page retirement."""

from django.core.management.base import BaseCommand, CommandError

from content.services.lesson_sources import LessonSourceError
from content.services.public_pages import update_public_pages
from content.services.site_bootstrap import SiteBootstrapError


class Command(BaseCommand):
    help = "Точечно обновляет главную, каталог, О проекте, Контакты и завершает снятие двух старых страниц."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Проверить в откатываемой транзакции без изменения файлов.")

    def handle(self, *args, **options):
        try:
            result = update_public_pages(dry_run=options["dry_run"])
        except (SiteBootstrapError, LessonSourceError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write("Проверка без сохранения." if result["dry_run"] else "Публичные страницы обновлены.")
        self.stdout.write(
            f"Страниц: {result['pages_selected']}; редиректов: {result['redirects_selected']}; "
            f"снято с публикации: {result['structure']['pages_unpublished']}; "
            f"изменено уроков: {result['publication']['changed']}; PDF скопировано: {result['media_copied']}."
        )
        if result["backup"]:
            self.stdout.write(f"Снимок записей: {result['backup']}")
