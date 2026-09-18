import hashlib
import os
import re
from collections import Counter
from datetime import datetime, timezone as datetime_timezone

import pymysql
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from dotenv import load_dotenv

from content.models import ContentPage, Grade, Subject
from content.wordpress_map import WORDPRESS_CATEGORY_TO_SUBJECT


EXPECTED_POST_COUNT = 250
EXPECTED_PAGE_COUNT = 17
EXPECTED_TOTAL_COUNT = 267


def normalize_wordpress_datetime(value):
    """
    Преобразует дату WordPress в timezone-aware datetime.
    WordPress GMT-даты считаются временем UTC.
    """
    if not value:
        return None

    if isinstance(value, str):
        value = value.strip()

        if not value or value.startswith("0000-00-00"):
            return None

        try:
            value = datetime.strptime(
                value,
                "%Y-%m-%d %H:%M:%S",
            )
        except ValueError:
            return None

    if not isinstance(value, datetime):
        return None

    if timezone.is_naive(value):
        return timezone.make_aware(
            value,
            datetime_timezone.utc,
        )

    return value


class Command(BaseCommand):
    help = (
        "Импортирует опубликованные страницы и записи WordPress "
        "в модель ContentPage."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Проверить импорт без сохранения изменений "
                "в базе Django."
            ),
        )

        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help=(
                "Ограничить количество импортируемых материалов. "
                "Используется только для тестирования."
            ),
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]

        load_dotenv(settings.BASE_DIR / ".env")

        host = os.getenv("WP_DB_HOST", "127.0.0.1")
        port_raw = os.getenv("WP_DB_PORT", "3306")
        database = os.getenv("WP_DB_NAME", "")
        user = os.getenv("WP_DB_USER", "")
        password = os.getenv("WP_DB_PASSWORD", "")
        prefix = os.getenv("WP_TABLE_PREFIX", "wp_")

        try:
            port = int(port_raw)
        except ValueError as error:
            raise CommandError(
                "WP_DB_PORT должен быть целым числом."
            ) from error

        if not database:
            raise CommandError(
                "В файле .env не указано WP_DB_NAME."
            )

        if not user:
            raise CommandError(
                "В файле .env не указано WP_DB_USER."
            )

        if not re.fullmatch(r"[A-Za-z0-9_]+", prefix):
            raise CommandError(
                "WP_TABLE_PREFIX содержит недопустимые символы."
            )

        if limit is not None and limit <= 0:
            raise CommandError(
                "Параметр --limit должен быть больше нуля."
            )

        posts_table = f"`{prefix}posts`"
        options_table = f"`{prefix}options`"
        relationships_table = f"`{prefix}term_relationships`"
        taxonomy_table = f"`{prefix}term_taxonomy`"

        connection = None

        try:
            connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
                connect_timeout=10,
                read_timeout=60,
                write_timeout=30,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Подключение к WordPress-БД успешно: {database}"
                )
            )

            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT option_name, option_value
                    FROM {options_table}
                    WHERE option_name IN ('home', 'siteurl');
                    """
                )

                wordpress_options = {
                    row["option_name"]: row["option_value"]
                    for row in cursor.fetchall()
                }

                wordpress_base_url = (
                    wordpress_options.get("home")
                    or wordpress_options.get("siteurl")
                    or "http://localhost/mathstart"
                ).rstrip("/")

                limit_sql = ""

                if limit is not None:
                    limit_sql = f" LIMIT {limit:d}"

                cursor.execute(
                    f"""
                    SELECT
                        p.ID,
                        p.post_type,
                        p.post_title,
                        p.post_name,
                        p.post_content,
                        p.post_date_gmt,
                        p.post_modified_gmt,
                        p.menu_order,
                        GROUP_CONCAT(
                            DISTINCT CASE
                                WHEN tt.taxonomy = 'category'
                                THEN tt.term_id
                                ELSE NULL
                            END
                            ORDER BY tt.term_id
                            SEPARATOR ','
                        ) AS category_ids
                    FROM {posts_table} AS p
                    LEFT JOIN {relationships_table} AS tr
                        ON tr.object_id = p.ID
                    LEFT JOIN {taxonomy_table} AS tt
                        ON tt.term_taxonomy_id = tr.term_taxonomy_id
                    WHERE p.post_status = 'publish'
                      AND p.post_type IN ('post', 'page')
                    GROUP BY
                        p.ID,
                        p.post_type,
                        p.post_title,
                        p.post_name,
                        p.post_content,
                        p.post_date_gmt,
                        p.post_modified_gmt,
                        p.menu_order
                    ORDER BY
                        CASE
                            WHEN p.post_type = 'page' THEN 0
                            ELSE 1
                        END,
                        p.ID
                    {limit_sql};
                    """
                )

                wordpress_rows = cursor.fetchall()

        except pymysql.MySQLError as error:
            raise CommandError(
                "Не удалось прочитать WordPress-БД: "
                f"{error}"
            ) from error

        finally:
            if connection is not None:
                connection.close()

        if limit is None and len(wordpress_rows) != EXPECTED_TOTAL_COUNT:
            raise CommandError(
                "Получено неожиданное количество материалов: "
                f"{len(wordpress_rows)} вместо "
                f"{EXPECTED_TOTAL_COUNT}."
            )

        grades = {
            grade.slug: grade
            for grade in Grade.objects.all()
        }

        subjects = {
            (subject.grade.slug, subject.slug): subject
            for subject in Subject.objects.select_related("grade")
        }

        expected_grade_slugs = {
            "5-klass",
            "6-klass",
            "7-klass",
            "8-klass",
            "9-klass",
        }

        missing_grades = expected_grade_slugs - grades.keys()

        if missing_grades:
            raise CommandError(
                "В Django отсутствуют классы: "
                + ", ".join(sorted(missing_grades))
                + ". Сначала выполните "
                "import_wordpress_structure."
            )

        prepared_materials = []
        validation_errors = []
        type_counter = Counter()

        for row in wordpress_rows:
            wordpress_id = int(row["ID"])
            wordpress_post_type = row["post_type"]
            title = (row["post_title"] or "").strip()
            slug = (row["post_name"] or "").strip()
            body_html = row["post_content"] or ""

            if not title:
                validation_errors.append(
                    f"WordPress ID {wordpress_id}: пустой заголовок."
                )

            if not slug:
                validation_errors.append(
                    f"WordPress ID {wordpress_id}: пустой slug."
                )
                continue

            grade = None
            subject = None
            page_type = ContentPage.PageType.STATIC
            order = int(row["menu_order"] or 0)

            if wordpress_post_type == "post":
                page_type = ContentPage.PageType.TOPIC
                order = 0

                raw_category_ids = row["category_ids"] or ""

                category_ids = [
                    int(category_id)
                    for category_id in raw_category_ids.split(",")
                    if category_id.strip()
                ]

                if len(category_ids) != 1:
                    validation_errors.append(
                        f"Запись ID {wordpress_id}, slug={slug}: "
                        "ожидалась ровно одна учебная рубрика, "
                        f"получено {category_ids}."
                    )
                    continue

                category_id = category_ids[0]

                subject_mapping = (
                    WORDPRESS_CATEGORY_TO_SUBJECT.get(category_id)
                )

                if subject_mapping is None:
                    validation_errors.append(
                        f"Запись ID {wordpress_id}, slug={slug}: "
                        "нет соответствия для WordPress-рубрики "
                        f"term_id={category_id}."
                    )
                    continue

                grade_slug, subject_slug = subject_mapping

                grade = grades.get(grade_slug)
                subject = subjects.get(
                    (grade_slug, subject_slug)
                )

                if grade is None or subject is None:
                    validation_errors.append(
                        f"Запись ID {wordpress_id}, slug={slug}: "
                        "не найден класс или предмет "
                        f"{grade_slug} → {subject_slug}."
                    )
                    continue

            elif wordpress_post_type == "page":
                if slug == "glavnaya":
                    page_type = ContentPage.PageType.HOME

                elif slug in {"5-klass", "6-klass"}:
                    page_type = ContentPage.PageType.GRADE
                    grade = grades.get(slug)

                    if grade is None:
                        validation_errors.append(
                            f"Страница {slug}: класс не найден."
                        )
                        continue

                else:
                    subject_page_match = re.fullmatch(
                        r"(7|8|9)-klass-"
                        r"(algebra|geometriya|"
                        r"veroyatnost-i-statistika)",
                        slug,
                    )

                    if subject_page_match:
                        class_number = subject_page_match.group(1)
                        subject_slug = subject_page_match.group(2)
                        grade_slug = f"{class_number}-klass"

                        grade = grades.get(grade_slug)
                        subject = subjects.get(
                            (grade_slug, subject_slug)
                        )
                        page_type = ContentPage.PageType.SUBJECT

                        if grade is None or subject is None:
                            validation_errors.append(
                                f"Страница {slug}: не найден "
                                "соответствующий класс или предмет."
                            )
                            continue

                    else:
                        page_type = ContentPage.PageType.STATIC

            if page_type == ContentPage.PageType.HOME:
                legacy_url = f"{wordpress_base_url}/"
            else:
                legacy_url = (
                    f"{wordpress_base_url}/{slug}/"
                )

            checksum = hashlib.sha256(
                body_html.encode("utf-8")
            ).hexdigest()

            prepared_materials.append(
                {
                    "wordpress_id": wordpress_id,
                    "title": title,
                    "slug": slug,
                    "page_type": page_type,
                    "grade": grade,
                    "subject": subject,
                    "section": None,
                    "order": order,
                    "body_html": body_html,
                    "page_css": "",
                    "page_js": "",
                    "seo_title": "",
                    "seo_description": "",
                    "is_published": True,
                    "legacy_url": legacy_url,
                    "source_file": (
                        f"wordpress:mysql:"
                        f"{prefix}posts:{wordpress_id}"
                    ),
                    "content_checksum": checksum,
                    "original_created_at": (
                        normalize_wordpress_datetime(
                            row["post_date_gmt"]
                        )
                    ),
                    "original_updated_at": (
                        normalize_wordpress_datetime(
                            row["post_modified_gmt"]
                        )
                    ),
                }
            )

            type_counter[page_type] += 1

        if validation_errors:
            error_preview = "\n".join(
                f"  - {message}"
                for message in validation_errors[:30]
            )

            if len(validation_errors) > 30:
                error_preview += (
                    "\n  - ... и ещё "
                    f"{len(validation_errors) - 30} ошибок."
                )

            raise CommandError(
                "Импорт остановлен из-за ошибок проверки:\n"
                f"{error_preview}"
            )

        if limit is None:
            post_count = type_counter[
                ContentPage.PageType.TOPIC
            ]

            page_count = (
                type_counter[ContentPage.PageType.HOME]
                + type_counter[ContentPage.PageType.GRADE]
                + type_counter[ContentPage.PageType.SUBJECT]
                + type_counter[ContentPage.PageType.STATIC]
                + type_counter[ContentPage.PageType.OGE]
            )

            if post_count != EXPECTED_POST_COUNT:
                raise CommandError(
                    "Получено неожиданное количество тем: "
                    f"{post_count} вместо {EXPECTED_POST_COUNT}."
                )

            if page_count != EXPECTED_PAGE_COUNT:
                raise CommandError(
                    "Получено неожиданное количество страниц: "
                    f"{page_count} вместо {EXPECTED_PAGE_COUNT}."
                )

        created_count = 0
        updated_count = 0

        self.stdout.write("")
        self.stdout.write("Предварительная структура импорта:")

        for page_type, label in ContentPage.PageType.choices:
            self.stdout.write(
                f"  {label}: {type_counter[page_type]}"
            )

        self.stdout.write(
            f"  Всего: {len(prepared_materials)}"
        )

        if dry_run:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "Режим dry-run: изменения не будут сохранены."
                )
            )

        with transaction.atomic():
            for material in prepared_materials:
                wordpress_id = material.pop("wordpress_id")

                page, was_created = (
                    ContentPage.objects.update_or_create(
                        wordpress_id=wordpress_id,
                        defaults=material,
                    )
                )

                if was_created:
                    created_count += 1
                else:
                    updated_count += 1

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write("")
        self.stdout.write("Результат:")
        self.stdout.write(
            f"  Создано: {created_count}"
        )
        self.stdout.write(
            f"  Обновлено: {updated_count}"
        )
        self.stdout.write(
            f"  Обработано: {len(prepared_materials)}"
        )

        self.stdout.write("")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Dry-run завершён. "
                    "Изменения в базе Django отменены."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Страницы и записи WordPress "
                    "успешно импортированы."
                )
            )

        self.stdout.write("")
        self.stdout.write(
            "HTML сохранён без изменений в поле body_html."
        )
        self.stdout.write(
            "Учебные темы пока не распределены "
            "по 60 разделам."
        )