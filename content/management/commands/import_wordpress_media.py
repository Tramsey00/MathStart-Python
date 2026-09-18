import os
import re
import shutil
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

import pymysql
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from dotenv import load_dotenv

from content.models import ContentPage, MediaAsset


EXPECTED_ATTACHMENT_COUNT = 38

IGNORED_UPLOAD_FILES = {
    ".htaccess",
    ".ds_store",
    "thumbs.db",
}


def normalize_relative_path(value):
    """
    Преобразует путь WordPress в безопасный относительный путь.
    Например: 2026/07/image.png
    """
    if not value:
        return ""

    value = unquote(str(value))
    value = value.replace("\\", "/").strip("/")
    path = PurePosixPath(value)

    if (
        path.is_absolute()
        or ".." in path.parts
        or not path.parts
    ):
        return ""

    return "/".join(path.parts)


def get_relative_upload_path(attached_file, guid):
    """
    Сначала использует _wp_attached_file.
    Если метаполе пустое, извлекает путь из guid.
    """
    relative_path = normalize_relative_path(attached_file)

    if relative_path:
        return relative_path

    if not guid:
        return ""

    parsed_url = urlparse(guid)
    url_path = unquote(parsed_url.path or "")
    marker = "/wp-content/uploads/"

    marker_position = url_path.lower().find(marker)

    if marker_position == -1:
        return ""

    relative_path = url_path[
        marker_position + len(marker):
    ]

    return normalize_relative_path(relative_path)


def find_archive_upload_members(archive):
    """
    Находит все файлы wp-content/uploads внутри ZIP,
    даже если сайт лежит во вложенной корневой папке.
    """
    marker = "wp-content/uploads/"
    members = {}

    for archive_info in archive.infolist():
        if archive_info.is_dir():
            continue

        archive_name = archive_info.filename.replace(
            "\\",
            "/",
        )

        marker_position = archive_name.lower().find(marker)

        if marker_position == -1:
            continue

        relative_path = archive_name[
            marker_position + len(marker):
        ]

        relative_path = normalize_relative_path(
            relative_path
        )

        if not relative_path:
            continue

        filename = PurePosixPath(relative_path).name.lower()

        if filename in IGNORED_UPLOAD_FILES:
            continue

        members[relative_path.lower()] = {
            "relative_path": relative_path,
            "archive_info": archive_info,
        }

    return members


class Command(BaseCommand):
    help = (
        "Извлекает wp-content/uploads из архива WordPress "
        "и импортирует вложения в MediaAsset."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Проверить архив и WordPress-БД "
                "без сохранения файлов и записей."
            ),
        )

        parser.add_argument(
            "--archive",
            default=str(
                settings.BASE_DIR
                / "source"
                / "mathstart-site.zip.zip"
            ),
            help="Путь к полному ZIP-архиву WordPress.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        archive_path = Path(options["archive"]).resolve()

        if not archive_path.is_file():
            raise CommandError(
                f"Архив WordPress не найден: {archive_path}"
            )

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
                "WP_TABLE_PREFIX содержит "
                "недопустимые символы."
            )

        posts_table = f"`{prefix}posts`"
        postmeta_table = f"`{prefix}postmeta`"

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

            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        p.ID,
                        p.post_title,
                        p.post_parent,
                        p.guid,
                        MAX(
                            CASE
                                WHEN pm.meta_key = '_wp_attached_file'
                                THEN pm.meta_value
                                ELSE NULL
                            END
                        ) AS attached_file,
                        MAX(
                            CASE
                                WHEN pm.meta_key = '_wp_attachment_image_alt'
                                THEN pm.meta_value
                                ELSE NULL
                            END
                        ) AS alt_text
                    FROM {posts_table} AS p
                    LEFT JOIN {postmeta_table} AS pm
                        ON pm.post_id = p.ID
                    WHERE p.post_type = 'attachment'
                      AND p.post_status = 'inherit'
                    GROUP BY
                        p.ID,
                        p.post_title,
                        p.post_parent,
                        p.guid
                    ORDER BY p.ID;
                    """
                )

                attachments = cursor.fetchall()

        except pymysql.MySQLError as error:
            raise CommandError(
                "Не удалось прочитать вложения "
                f"WordPress: {error}"
            ) from error

        finally:
            if connection is not None:
                connection.close()

        if len(attachments) != EXPECTED_ATTACHMENT_COUNT:
            raise CommandError(
                "Получено неожиданное количество вложений: "
                f"{len(attachments)} вместо "
                f"{EXPECTED_ATTACHMENT_COUNT}."
            )

        try:
            archive = zipfile.ZipFile(archive_path)
        except zipfile.BadZipFile as error:
            raise CommandError(
                f"Файл не является исправным ZIP: {archive_path}"
            ) from error

        with archive:
            archive_members = find_archive_upload_members(
                archive
            )

            prepared_attachments = []
            missing_files = []

            for attachment in attachments:
                relative_path = get_relative_upload_path(
                    attachment["attached_file"],
                    attachment["guid"],
                )

                if not relative_path:
                    missing_files.append(
                        "WordPress ID "
                        f"{attachment['ID']}: "
                        "не удалось определить путь."
                    )
                    continue

                archive_member = archive_members.get(
                    relative_path.lower()
                )

                if archive_member is None:
                    missing_files.append(
                        "WordPress ID "
                        f"{attachment['ID']}: "
                        f"{relative_path} отсутствует в архиве."
                    )
                    continue

                parent_wordpress_id = int(
                    attachment["post_parent"] or 0
                )

                related_page = None

                if parent_wordpress_id:
                    related_page = (
                        ContentPage.objects.filter(
                            wordpress_id=parent_wordpress_id
                        ).first()
                    )

                prepared_attachments.append(
                    {
                        "wordpress_id": int(
                            attachment["ID"]
                        ),
                        "title": (
                            attachment["post_title"] or ""
                        ).strip(),
                        "relative_path": relative_path,
                        "old_url": (
                            attachment["guid"] or ""
                        ).strip(),
                        "alt_text": (
                            attachment["alt_text"] or ""
                        ).strip(),
                        "related_page": related_page,
                        "archive_info": archive_member[
                            "archive_info"
                        ],
                    }
                )

            if missing_files:
                error_text = "\n".join(
                    f"  - {message}"
                    for message in missing_files
                )

                raise CommandError(
                    "Не все вложения найдены в архиве:\n"
                    f"{error_text}"
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Архив найден: {archive_path.name}"
                )
            )
            self.stdout.write(
                f"Файлов в wp-content/uploads: "
                f"{len(archive_members)}"
            )
            self.stdout.write(
                f"Вложений WordPress: {len(attachments)}"
            )
            self.stdout.write(
                "Вложений, сопоставленных с файлами: "
                f"{len(prepared_attachments)}"
            )
            self.stdout.write(
                f"Отсутствующих файлов: {len(missing_files)}"
            )

            if dry_run:
                self.stdout.write("")
                self.stdout.write(
                    self.style.WARNING(
                        "Dry-run завершён. Файлы и записи "
                        "MediaAsset не создавались."
                    )
                )
                return

            uploads_root = (
                Path(settings.MEDIA_ROOT) / "uploads"
            )
            uploads_root.mkdir(
                parents=True,
                exist_ok=True,
            )

            extracted_count = 0

            # Извлекаем все файлы uploads, а не только
            # зарегистрированные вложения. Это сохраняет
            # миниатюры и другие версии изображений.
            for archive_member in archive_members.values():
                relative_path = archive_member[
                    "relative_path"
                ]
                archive_info = archive_member[
                    "archive_info"
                ]

                destination = (
                    uploads_root
                    / Path(
                        *PurePosixPath(
                            relative_path
                        ).parts
                    )
                )

                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                with archive.open(
                    archive_info,
                    "r",
                ) as source_file:
                    with destination.open(
                        "wb",
                    ) as destination_file:
                        shutil.copyfileobj(
                            source_file,
                            destination_file,
                        )

                extracted_count += 1

            created_count = 0
            updated_count = 0

            with transaction.atomic():
                for attachment in prepared_attachments:
                    relative_path = attachment[
                        "relative_path"
                    ]

                    media_asset, was_created = (
                        MediaAsset.objects.update_or_create(
                            wordpress_id=attachment[
                                "wordpress_id"
                            ],
                            defaults={
                                "title": attachment[
                                    "title"
                                ],
                                "file": (
                                    "uploads/"
                                    f"{relative_path}"
                                ),
                                "old_url": attachment[
                                    "old_url"
                                ],
                                "alt_text": attachment[
                                    "alt_text"
                                ],
                                "related_page": attachment[
                                    "related_page"
                                ],
                            },
                        )
                    )

                    if was_created:
                        created_count += 1
                    else:
                        updated_count += 1

            self.stdout.write("")
            self.stdout.write("Результат импорта:")
            self.stdout.write(
                f"  Извлечено файлов: {extracted_count}"
            )
            self.stdout.write(
                f"  MediaAsset создано: {created_count}"
            )
            self.stdout.write(
                f"  MediaAsset обновлено: {updated_count}"
            )
            self.stdout.write(
                f"  Всего MediaAsset: "
                f"{MediaAsset.objects.count()}"
            )

            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "Медиафайлы WordPress успешно перенесены."
                )
            )
            self.stdout.write(
                "Исходный ZIP и WordPress-БД не изменялись."
            )