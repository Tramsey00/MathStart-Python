import hashlib

from django.core.management.base import BaseCommand
from django.db import transaction

from content.models import ContentPage


OLD_SITE_BASES = (
    "http://localhost/mathstart",
    "https://localhost/mathstart",
    "http://127.0.0.1/mathstart",
    "https://127.0.0.1/mathstart",
    "https://cy874851.tw1.ru",
    "http://cy874851.tw1.ru",
    "//cy874851.tw1.ru",
)

OLD_MARKERS = (
    "localhost/mathstart",
    "127.0.0.1/mathstart",
    "cy874851.tw1.ru",
    "wp-content/uploads",
)


def replace_counted(value, old, new):
    """
    Заменяет строку и возвращает:
    новое значение и количество замен.
    """
    occurrences = value.count(old)

    if occurrences:
        value = value.replace(old, new)

    return value, occurrences


def rewrite_text(value):
    """
    Заменяет старые адреса WordPress на Django-пути.

    Обрабатывает:
    - обычные HTML-ссылки;
    - src и srcset;
    - CSS url(...);
    - URL внутри JavaScript;
    - экранированные URL вида https:\\/\\/...
    """
    if not value:
        return value, 0

    result = value
    replacement_count = 0

    # Сначала убираем старые домены.
    # base + "/" заменяем на "/", чтобы не получить "//slug/".
    for old_base in OLD_SITE_BASES:
        result, count = replace_counted(
            result,
            f"{old_base}/",
            "/",
        )
        replacement_count += count

        result, count = replace_counted(
            result,
            old_base,
            "/",
        )
        replacement_count += count

    # Те же адреса, но экранированные внутри JavaScript.
    for old_base in OLD_SITE_BASES:
        escaped_base = old_base.replace("/", r"\/")

        result, count = replace_counted(
            result,
            f"{escaped_base}\\/",
            r"\/",
        )
        replacement_count += count

        result, count = replace_counted(
            result,
            escaped_base,
            r"\/",
        )
        replacement_count += count

    # Медиа WordPress.
    plain_media_replacements = (
        (
            "/mathstart/wp-content/uploads/",
            "/media/uploads/",
        ),
        (
            "/wp-content/uploads/",
            "/media/uploads/",
        ),
    )

    for old_value, new_value in plain_media_replacements:
        result, count = replace_counted(
            result,
            old_value,
            new_value,
        )
        replacement_count += count

    # Экранированные пути к медиа.
    escaped_media_replacements = (
        (
            r"\/mathstart\/wp-content\/uploads\/",
            r"\/media\/uploads\/",
        ),
        (
            r"\/wp-content\/uploads\/",
            r"\/media\/uploads\/",
        ),
    )

    for old_value, new_value in escaped_media_replacements:
        result, count = replace_counted(
            result,
            old_value,
            new_value,
        )
        replacement_count += count

    # Относительные WordPress-ссылки.
    result, count = replace_counted(
        result,
        "/mathstart/",
        "/",
    )
    replacement_count += count

    result, count = replace_counted(
        result,
        r"\/mathstart\/",
        r"\/",
    )
    replacement_count += count

    return result, replacement_count


class Command(BaseCommand):
    help = (
        "Заменяет старые URL WordPress в HTML, CSS и JavaScript "
        "на локальные пути Django."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Проверить замену ссылок без сохранения "
                "изменений в базе Django."
            ),
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        pages = list(
            ContentPage.objects.all().order_by("id")
        )

        changed_pages = 0
        unchanged_pages = 0
        total_replacements = 0

        self.stdout.write(
            f"Проверка ссылок в {len(pages)} материалах..."
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Режим dry-run: изменения не будут сохранены."
                )
            )

        with transaction.atomic():
            for page in pages:
                body_html, body_replacements = rewrite_text(
                    page.body_html
                )
                page_css, css_replacements = rewrite_text(
                    page.page_css
                )
                page_js, js_replacements = rewrite_text(
                    page.page_js
                )

                page_replacements = (
                    body_replacements
                    + css_replacements
                    + js_replacements
                )

                if page_replacements == 0:
                    unchanged_pages += 1
                    continue

                page.body_html = body_html
                page.page_css = page_css
                page.page_js = page_js
                page.content_checksum = hashlib.sha256(
                    body_html.encode("utf-8")
                ).hexdigest()

                page.save(
                    update_fields=(
                        "body_html",
                        "page_css",
                        "page_js",
                        "content_checksum",
                        "updated_at",
                    )
                )

                changed_pages += 1
                total_replacements += page_replacements

            if dry_run:
                transaction.set_rollback(True)

        remaining_occurrences = 0
        remaining_pages = set()

        # При dry-run база откатилась, поэтому считаем остатки
        # по преобразованным данным повторно в памяти.
        for page in pages:
            body_html, _ = rewrite_text(page.body_html)
            page_css, _ = rewrite_text(page.page_css)
            page_js, _ = rewrite_text(page.page_js)

            combined_content = (
                body_html
                + "\n"
                + page_css
                + "\n"
                + page_js
            ).lower()

            for marker in OLD_MARKERS:
                marker_count = combined_content.count(
                    marker.lower()
                )

                if marker_count:
                    remaining_occurrences += marker_count
                    remaining_pages.add(page.id)

        self.stdout.write("")
        self.stdout.write("Результат:")
        self.stdout.write(
            f"  Изменено материалов: {changed_pages}"
        )
        self.stdout.write(
            f"  Без изменений: {unchanged_pages}"
        )
        self.stdout.write(
            f"  Выполнено замен: {total_replacements}"
        )
        self.stdout.write(
            "  Осталось старых адресов после преобразования: "
            f"{remaining_occurrences}"
        )
        self.stdout.write(
            "  Материалов с оставшимися старыми адресами: "
            f"{len(remaining_pages)}"
        )

        self.stdout.write("")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Dry-run завершён. Изменения "
                    "в базе Django отменены."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Ссылки WordPress успешно преобразованы."
                )
            )