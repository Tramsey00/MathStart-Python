import os
import re

import pymysql
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Проверяет подключение к исходной базе WordPress без изменения данных."

    def handle(self, *args, **options):
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

        posts_table = f"`{prefix}posts`"
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
                read_timeout=30,
                write_timeout=30,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Подключение успешно: {database}"
                )
            )

            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT post_type, COUNT(*) AS total
                    FROM {posts_table}
                    WHERE post_status = 'publish'
                      AND post_type IN ('post', 'page')
                    GROUP BY post_type
                    ORDER BY post_type;
                    """
                )
                type_counts = {
                    row["post_type"]: row["total"]
                    for row in cursor.fetchall()
                }

                post_count = type_counts.get("post", 0)
                page_count = type_counts.get("page", 0)
                published_total = post_count + page_count

                cursor.execute(
                    f"""
                    SELECT COUNT(*) AS total
                    FROM {posts_table}
                    WHERE post_type = 'attachment'
                      AND post_status = 'inherit';
                    """
                )
                attachment_count = cursor.fetchone()["total"]

                cursor.execute(
                    f"""
                    SELECT COUNT(*) AS total
                    FROM {taxonomy_table}
                    WHERE taxonomy = 'category';
                    """
                )
                category_count = cursor.fetchone()["total"]

                cursor.execute(
                    f"""
                    SELECT COUNT(*) AS total
                    FROM {posts_table}
                    WHERE post_status = 'publish'
                      AND post_type IN ('post', 'page')
                      AND TRIM(COALESCE(post_content, '')) = '';
                    """
                )
                empty_content_count = cursor.fetchone()["total"]

                cursor.execute(
                    f"""
                    SELECT post_name, COUNT(*) AS total
                    FROM {posts_table}
                    WHERE post_status = 'publish'
                      AND post_type IN ('post', 'page')
                      AND post_name <> ''
                    GROUP BY post_name
                    HAVING COUNT(*) > 1
                    ORDER BY total DESC, post_name
                    LIMIT 20;
                    """
                )
                duplicate_slugs = cursor.fetchall()

                cursor.execute(
                    f"""
                    SELECT COUNT(*) AS total
                    FROM {posts_table}
                    WHERE post_status = 'publish'
                      AND post_type IN ('post', 'page')
                      AND post_name = '';
                    """
                )
                empty_slug_count = cursor.fetchone()["total"]

            self.stdout.write("")
            self.stdout.write("Результаты аудита WordPress:")
            self.stdout.write(f"  Записи: {post_count}")
            self.stdout.write(f"  Страницы: {page_count}")
            self.stdout.write(
                f"  Всего опубликованных материалов: {published_total}"
            )
            self.stdout.write(f"  Вложения: {attachment_count}")
            self.stdout.write(f"  Рубрики: {category_count}")
            self.stdout.write(
                f"  Материалы с пустым содержимым: {empty_content_count}"
            )
            self.stdout.write(
                f"  Материалы с пустым slug: {empty_slug_count}"
            )
            self.stdout.write(
                f"  Повторяющиеся slug: {len(duplicate_slugs)}"
            )

            if duplicate_slugs:
                self.stdout.write("")
                self.stdout.write(
                    self.style.WARNING(
                        "Найдены повторяющиеся slug:"
                    )
                )

                for item in duplicate_slugs:
                    self.stdout.write(
                        f"  {item['post_name']}: {item['total']}"
                    )

            expected = {
                "post": 250,
                "page": 17,
                "published": 267,
            }

            counts_are_correct = (
                post_count == expected["post"]
                and page_count == expected["page"]
                and published_total == expected["published"]
            )

            self.stdout.write("")

            if counts_are_correct:
                self.stdout.write(
                    self.style.SUCCESS(
                        "Основные контрольные количества совпадают."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "Контрольные количества отличаются от ожидаемых."
                    )
                )

            if (
                empty_content_count == 0
                and empty_slug_count == 0
                and not duplicate_slugs
            ):
                self.stdout.write(
                    self.style.SUCCESS(
                        "Критических проблем опубликованного контента не найдено."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "Перед импортом необходимо проверить предупреждения."
                    )
                )

            self.stdout.write("")
            self.stdout.write(
                "База WordPress не изменялась: аудит выполнялся только на чтение."
            )

        except pymysql.MySQLError as error:
            raise CommandError(
                "Не удалось подключиться к WordPress-БД: "
                f"{error}"
            ) from error

        finally:
            if connection is not None:
                connection.close()