from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from content.services.lesson_sources import (
    LessonSourceError,
)
from content.services.site_bootstrap import (
    SiteBootstrapError,
    bootstrap_site,
)


class Command(BaseCommand):
    help = (
        "Восстанавливает структуру MathStart, "
        "уроки и media из version-controlled "
        "источников."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--root",
            default=None,
            help=(
                "Путь к site_content. "
                "По умолчанию BASE_DIR/site_content."
            ),
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Проверить bootstrap "
                "без сохранения изменений."
            ),
        )

    def handle(self, *args, **options):
        try:
            result = bootstrap_site(
                root=options["root"],
                dry_run=options["dry_run"],
            )
        except (
            SiteBootstrapError,
            LessonSourceError,
        ) as exc:
            raise CommandError(
                str(exc)
            ) from exc

        structure = result["structure"]
        publication = result["publication"]

        prefix = (
            "Проверка bootstrap без записи."
            if result["dry_run"]
            else "Bootstrap MathStart завершён."
        )

        self.stdout.write(prefix)

        self.stdout.write(
            "Каталог: "
            f"новых классов "
            f"{structure['grades_created']}; "
            f"предметов "
            f"{structure['subjects_created']}; "
            f"разделов "
            f"{structure['sections_created']}."
        )

        self.stdout.write(
            "Страницы сайта: "
            f"новых "
            f"{structure['pages_created']}."
        )

        self.stdout.write(
            "Redirect: "
            f"новых "
            f"{structure['redirects_created']}."
        )

        self.stdout.write(
            "Уроки: "
            f"выбрано "
            f"{publication['selected']}; "
            f"создано "
            f"{publication['created']}; "
            f"изменено "
            f"{publication['changed']}; "
            f"зарегистрировано "
            f"{publication['registered']}."
        )

        self.stdout.write(
            "Media: "
            f"в источнике "
            f"{result['media_total']}; "
            f"скопировано "
            f"{result['media_copied']}; "
            f"создано записей "
            f"{result['media_created']}."
        )
