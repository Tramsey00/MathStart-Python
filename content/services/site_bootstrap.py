"""Rebuild database-backed site content from version-controlled sources."""

import hashlib
import json
from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.db import transaction

from content.models import (
    ContentPage,
    Grade,
    MediaAsset,
    Redirect,
    Section,
    Subject,
)
from content.quality import inspect_html
from content.services.lesson_sources import (
    load_bundles,
    source_root as lesson_source_root,
)
from content.services.publishing import (
    publish_lessons,
    verify_lessons,
)


class SiteBootstrapError(ValueError):
    pass


def site_source_root(root=None):
    return Path(
        root or settings.BASE_DIR / "site_content"
    ).resolve()


def read_json(path):
    try:
        return json.loads(
            path.read_text(encoding="utf-8")
        )
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
    ) as exc:
        raise SiteBootstrapError(
            f"Не удалось прочитать {path}: {exc}"
        ) from exc


def read_utf8(path):
    try:
        return path.read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise SiteBootstrapError(
            f"Не удалось прочитать {path}: {exc}"
        ) from exc


def sha256_path(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def sha256_storage(name):
    digest = hashlib.sha256()

    with default_storage.open(name, "rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def validate_keys(data, expected, location):
    if not isinstance(data, dict):
        raise SiteBootstrapError(
            f"{location}: ожидался JSON-объект."
        )

    actual = set(data)

    if actual != set(expected):
        raise SiteBootstrapError(
            f"{location}: неверные поля. "
            f"Ожидались {sorted(expected)}, "
            f"получены {sorted(actual)}."
        )


def validate_relative_file(value, location):
    if not isinstance(value, str) or not value:
        raise SiteBootstrapError(
            f"{location}: неверный путь файла."
        )

    path = PurePosixPath(value)

    if path.is_absolute() or ".." in path.parts:
        raise SiteBootstrapError(
            f"{location}: путь должен быть "
            "относительным и не выходить "
            "за каталог источников."
        )

    return path


def load_site_source(root=None):
    root = site_source_root(root)

    if not root.is_dir():
        raise SiteBootstrapError(
            f"Не найден каталог site_content: {root}"
        )

    # --------------------------------------------------
    # Catalog
    # --------------------------------------------------

    catalog = read_json(
        root / "catalog.json"
    )

    validate_keys(
        catalog,
        {
            "schema_version",
            "grades",
            "subjects",
            "sections",
        },
        "catalog.json",
    )

    if catalog["schema_version"] != 1:
        raise SiteBootstrapError(
            "catalog.json: неподдерживаемая "
            "schema_version."
        )

    grades = catalog["grades"]
    subjects = catalog["subjects"]
    sections = catalog["sections"]

    if not all(
        isinstance(value, list)
        for value in (
            grades,
            subjects,
            sections,
        )
    ):
        raise SiteBootstrapError(
            "catalog.json: grades, subjects "
            "и sections должны быть списками."
        )

    grade_slugs = set()

    for index, item in enumerate(grades):
        validate_keys(
            item,
            {
                "title",
                "slug",
                "order",
                "description",
            },
            f"catalog.grades[{index}]",
        )

        slug = item["slug"]

        if slug in grade_slugs:
            raise SiteBootstrapError(
                f"Повтор класса: {slug}"
            )

        grade_slugs.add(slug)

    subject_keys = set()

    for index, item in enumerate(subjects):
        validate_keys(
            item,
            {
                "title",
                "slug",
                "grade",
                "order",
                "description",
            },
            f"catalog.subjects[{index}]",
        )

        if item["grade"] not in grade_slugs:
            raise SiteBootstrapError(
                f"{item['slug']}: неизвестный "
                f"класс {item['grade']}."
            )

        key = (
            item["grade"],
            item["slug"],
        )

        if key in subject_keys:
            raise SiteBootstrapError(
                f"Повтор предмета: {key}"
            )

        subject_keys.add(key)

    section_keys = set()

    for index, item in enumerate(sections):
        validate_keys(
            item,
            {
                "title",
                "slug",
                "grade",
                "subject",
                "order",
                "description",
            },
            f"catalog.sections[{index}]",
        )

        subject_key = (
            item["grade"],
            item["subject"],
        )

        if subject_key not in subject_keys:
            raise SiteBootstrapError(
                f"{item['slug']}: неизвестный "
                "предмет "
                f"{subject_key}."
            )

        key = (
            item["grade"],
            item["subject"],
            item["slug"],
        )

        if key in section_keys:
            raise SiteBootstrapError(
                f"Повтор раздела: {key}"
            )

        section_keys.add(key)

    # --------------------------------------------------
    # Site pages
    # --------------------------------------------------

    pages_root = root / "pages"

    if not pages_root.is_dir():
        raise SiteBootstrapError(
            f"Не найден каталог: {pages_root}"
        )

    pages = []
    page_slugs = set()

    for directory in sorted(
        path
        for path in pages_root.iterdir()
        if path.is_dir()
    ):
        metadata_path = (
            directory / "page.json"
        )

        body_path = (
            directory / "body.html"
        )

        if not metadata_path.is_file():
            raise SiteBootstrapError(
                f"{directory}: нет page.json."
            )

        if not body_path.is_file():
            raise SiteBootstrapError(
                f"{directory}: нет body.html."
            )

        metadata = read_json(
            metadata_path
        )

        validate_keys(
            metadata,
            {
                "schema_version",
                "page",
            },
            str(metadata_path),
        )

        if metadata["schema_version"] != 1:
            raise SiteBootstrapError(
                f"{metadata_path}: "
                "неподдерживаемая версия."
            )

        page = metadata["page"]

        validate_keys(
            page,
            {
                "title",
                "slug",
                "page_type",
                "grade",
                "subject",
                "section",
                "order",
                "seo_title",
                "seo_description",
                "is_published",
            },
            str(metadata_path),
        )

        slug = page["slug"]

        if directory.name != slug:
            raise SiteBootstrapError(
                f"{metadata_path}: slug "
                "не совпадает с именем каталога."
            )

        if page["page_type"] == "topic":
            raise SiteBootstrapError(
                f"{slug}: учебные темы должны "
                "находиться в curriculum."
            )

        if slug in page_slugs:
            raise SiteBootstrapError(
                f"Повтор страницы: {slug}"
            )

        page_slugs.add(slug)

        grade_slug = page["grade"]
        subject_slug = page["subject"]
        section_slug = page["section"]

        if (
            grade_slug is not None
            and grade_slug not in grade_slugs
        ):
            raise SiteBootstrapError(
                f"{slug}: неизвестный класс "
                f"{grade_slug}."
            )

        if subject_slug is not None:
            if (
                grade_slug,
                subject_slug,
            ) not in subject_keys:
                raise SiteBootstrapError(
                    f"{slug}: неизвестный предмет."
                )

        if section_slug is not None:
            if (
                grade_slug,
                subject_slug,
                section_slug,
            ) not in section_keys:
                raise SiteBootstrapError(
                    f"{slug}: неизвестный раздел."
                )

        pages.append(
            {
                "page": page,
                "body_html": read_utf8(
                    body_path
                ),
                "page_css": (
                    read_utf8(
                        directory / "page.css"
                    )
                    if (
                        directory / "page.css"
                    ).is_file()
                    else ""
                ),
                "page_js": (
                    read_utf8(
                        directory / "page.js"
                    )
                    if (
                        directory / "page.js"
                    ).is_file()
                    else ""
                ),
            }
        )

    # --------------------------------------------------
    # Curriculum slugs
    # --------------------------------------------------

    bundles = load_bundles(
        lesson_source_root(),
        all_lessons=True,
    )

    lesson_slugs = {
        bundle.slug
        for bundle in bundles
    }

    overlap = (
        page_slugs
        & lesson_slugs
    )

    if overlap:
        raise SiteBootstrapError(
            "Одинаковые slug в site_content "
            "и curriculum: "
            + ", ".join(sorted(overlap))
        )

    all_page_slugs = (
        page_slugs
        | lesson_slugs
    )

    # --------------------------------------------------
    # Redirects
    # --------------------------------------------------

    redirects_data = read_json(
        root / "redirects.json"
    )

    validate_keys(
        redirects_data,
        {
            "schema_version",
            "redirects",
        },
        "redirects.json",
    )

    if redirects_data["schema_version"] != 1:
        raise SiteBootstrapError(
            "redirects.json: "
            "неподдерживаемая версия."
        )

    redirects = redirects_data["redirects"]
    old_paths = set()

    for index, item in enumerate(redirects):
        validate_keys(
            item,
            {
                "old_path",
                "new_path",
                "is_permanent",
                "is_active",
            },
            f"redirects[{index}]",
        )

        if item["old_path"] in old_paths:
            raise SiteBootstrapError(
                "Повтор redirect: "
                + item["old_path"]
            )

        old_paths.add(
            item["old_path"]
        )

    # --------------------------------------------------
    # Media
    # --------------------------------------------------

    media_data = read_json(
        root / "media.json"
    )

    validate_keys(
        media_data,
        {
            "schema_version",
            "assets",
        },
        "media.json",
    )

    if media_data["schema_version"] != 1:
        raise SiteBootstrapError(
            "media.json: "
            "неподдерживаемая версия."
        )

    assets = media_data["assets"]
    media_files = set()

    for index, item in enumerate(assets):
        validate_keys(
            item,
            {
                "title",
                "file",
                "alt_text",
                "related_page",
                "sha256",
            },
            f"media.assets[{index}]",
        )

        relative = validate_relative_file(
            item["file"],
            f"media.assets[{index}]",
        )

        name = relative.as_posix()

        if name in media_files:
            raise SiteBootstrapError(
                f"Повтор media: {name}"
            )

        media_files.add(name)

        related = item["related_page"]

        if (
            related is not None
            and related not in all_page_slugs
        ):
            raise SiteBootstrapError(
                f"{name}: неизвестная "
                f"related_page {related}."
            )

        source_file = (
            root / "media" / Path(*relative.parts)
        )

        if not source_file.is_file():
            raise SiteBootstrapError(
                f"Нет seed-media: {source_file}"
            )

        actual_digest = sha256_path(
            source_file
        )

        if (
            actual_digest
            != item["sha256"]
        ):
            raise SiteBootstrapError(
                f"{name}: SHA-256 "
                "не совпадает с media.json."
            )

    seed_root = root / "media"

    seed_files = {
        path.relative_to(
            seed_root
        ).as_posix()
        for path in seed_root.rglob("*")
        if path.is_file()
    }

    if seed_files != media_files:
        extra = sorted(
            seed_files - media_files
        )
        missing = sorted(
            media_files - seed_files
        )

        raise SiteBootstrapError(
            "site_content/media не совпадает "
            "с media.json. "
            f"Лишние: {extra}; "
            f"отсутствуют: {missing}."
        )

    return {
        "root": root,
        "grades": grades,
        "subjects": subjects,
        "sections": sections,
        "pages": pages,
        "redirects": redirects,
        "assets": assets,
        "lesson_count": len(bundles),
    }


def update_fields(instance, values):
    changed = False

    for field, value in values.items():
        if getattr(instance, field) != value:
            setattr(
                instance,
                field,
                value,
            )
            changed = True

    return changed


def sync_structure(source):
    grade_models = {}
    subject_models = {}
    section_models = {}

    counts = {
        "grades_created": 0,
        "subjects_created": 0,
        "sections_created": 0,
        "pages_created": 0,
        "redirects_created": 0,
    }

    for row in source["grades"]:
        grade = Grade.objects.filter(
            slug=row["slug"]
        ).first()

        created = grade is None

        if created:
            grade = Grade(
                slug=row["slug"]
            )

        update_fields(
            grade,
            {
                "title": row["title"],
                "order": row["order"],
                "description": (
                    row["description"]
                ),
            },
        )

        grade.full_clean()
        grade.save()

        grade_models[
            row["slug"]
        ] = grade

        counts[
            "grades_created"
        ] += int(created)

    for row in source["subjects"]:
        grade = grade_models[
            row["grade"]
        ]

        subject = (
            Subject.objects
            .filter(
                grade=grade,
                slug=row["slug"],
            )
            .first()
        )

        created = subject is None

        if created:
            subject = Subject(
                grade=grade,
                slug=row["slug"],
            )

        update_fields(
            subject,
            {
                "title": row["title"],
                "order": row["order"],
                "description": (
                    row["description"]
                ),
            },
        )

        subject.full_clean()
        subject.save()

        subject_models[
            (
                row["grade"],
                row["slug"],
            )
        ] = subject

        counts[
            "subjects_created"
        ] += int(created)

    for row in source["sections"]:
        subject = subject_models[
            (
                row["grade"],
                row["subject"],
            )
        ]

        section = (
            Section.objects
            .filter(
                subject=subject,
                slug=row["slug"],
            )
            .first()
        )

        created = section is None

        if created:
            section = Section(
                subject=subject,
                slug=row["slug"],
            )

        update_fields(
            section,
            {
                "title": row["title"],
                "order": row["order"],
                "description": (
                    row["description"]
                ),
            },
        )

        section.full_clean()
        section.save()

        section_models[
            (
                row["grade"],
                row["subject"],
                row["slug"],
            )
        ] = section

        counts[
            "sections_created"
        ] += int(created)

    for record in source["pages"]:
        row = record["page"]

        page = ContentPage.objects.filter(
            slug=row["slug"]
        ).first()

        created = page is None

        if created:
            page = ContentPage(
                slug=row["slug"]
            )
        elif (
            page.page_type
            == ContentPage.PageType.TOPIC
        ):
            raise SiteBootstrapError(
                f"{row['slug']}: site page "
                "не может перезаписать topic."
            )

        grade = (
            grade_models[
                row["grade"]
            ]
            if row["grade"]
            else None
        )

        subject = (
            subject_models[
                (
                    row["grade"],
                    row["subject"],
                )
            ]
            if row["subject"]
            else None
        )

        section = (
            section_models[
                (
                    row["grade"],
                    row["subject"],
                    row["section"],
                )
            ]
            if row["section"]
            else None
        )

        update_fields(
            page,
            {
                "title": row["title"],
                "page_type": (
                    row["page_type"]
                ),
                "grade": grade,
                "subject": subject,
                "section": section,
                "order": row["order"],
                "body_html": (
                    record["body_html"]
                ),
                "page_css": (
                    record["page_css"]
                ),
                "page_js": (
                    record["page_js"]
                ),
                "seo_title": (
                    row["seo_title"]
                ),
                "seo_description": (
                    row["seo_description"]
                ),
                "is_published": (
                    row["is_published"]
                ),
            },
        )

        try:
            page.full_clean()
        except ValidationError as exc:
            raise SiteBootstrapError(
                f"{row['slug']}: {exc}"
            ) from exc

        issues = inspect_html(
            page.body_html
        )["issues"]

        if issues:
            raise SiteBootstrapError(
                f"{row['slug']}: "
                "проверка HTML не пройдена: "
                f"{issues[:8]}"
            )

        page.save()

        counts[
            "pages_created"
        ] += int(created)

    for row in source["redirects"]:
        redirect = Redirect.objects.filter(
            old_path=row["old_path"]
        ).first()

        created = redirect is None

        if created:
            redirect = Redirect(
                old_path=row["old_path"]
            )

        update_fields(
            redirect,
            {
                "new_path": (
                    row["new_path"]
                ),
                "is_permanent": (
                    row["is_permanent"]
                ),
                "is_active": (
                    row["is_active"]
                ),
            },
        )

        redirect.full_clean()
        redirect.save()

        counts[
            "redirects_created"
        ] += int(created)

    return counts


def validate_runtime_media(source):
    for item in source["assets"]:
        name = item["file"]

        if not default_storage.exists(name):
            continue

        actual = sha256_storage(name)

        if actual != item["sha256"]:
            raise SiteBootstrapError(
                f"{name}: runtime-файл "
                "уже существует, но отличается "
                "от seed-media."
            )


def copy_runtime_media(source):
    validate_runtime_media(source)

    copied = 0
    source_root = (
        source["root"] / "media"
    )

    for item in source["assets"]:
        name = item["file"]

        if default_storage.exists(name):
            continue

        source_file = (
            source_root
            / Path(
                *PurePosixPath(name).parts
            )
        )

        with source_file.open("rb") as file:
            saved_name = (
                default_storage.save(
                    name,
                    File(file),
                )
            )

        if saved_name != name:
            raise SiteBootstrapError(
                f"Storage изменил имя "
                f"{name} на {saved_name}."
            )

        if (
            sha256_storage(name)
            != item["sha256"]
        ):
            raise SiteBootstrapError(
                f"{name}: ошибка проверки "
                "после копирования."
            )

        copied += 1

    return copied


def sync_media_rows(source):
    created_count = 0

    for row in source["assets"]:
        matches = list(
            MediaAsset.objects.filter(
                file=row["file"]
            )
        )

        if len(matches) > 1:
            raise SiteBootstrapError(
                f"{row['file']}: "
                "в БД несколько MediaAsset "
                "для одного файла."
            )

        related_page = None

        if row["related_page"]:
            related_page = (
                ContentPage.objects
                .filter(
                    slug=row["related_page"]
                )
                .first()
            )

            if related_page is None:
                raise SiteBootstrapError(
                    f"{row['file']}: "
                    "не найдена related_page "
                    f"{row['related_page']}."
                )

        created = not matches

        if created:
            asset = MediaAsset(
                file=row["file"]
            )
        else:
            asset = matches[0]

        update_fields(
            asset,
            {
                "title": row["title"],
                "alt_text": (
                    row["alt_text"]
                ),
                "related_page": (
                    related_page
                ),
            },
        )

        asset.full_clean()
        asset.save()

        created_count += int(created)

    return created_count


def bootstrap_site(
    root=None,
    dry_run=False,
):
    source = load_site_source(root)

    validate_runtime_media(source)

    if dry_run:
        with transaction.atomic():
            structure = sync_structure(
                source
            )

            publication = publish_lessons(
                all_lessons=True,
                dry_run=True,
            )

            transaction.set_rollback(True)

        return {
            "structure": structure,
            "publication": publication,
            "media_total": len(
                source["assets"]
            ),
            "media_copied": 0,
            "media_created": 0,
            "dry_run": True,
        }

    with transaction.atomic():
        structure = sync_structure(
            source
        )

    publication = publish_lessons(
        all_lessons=True,
    )

    verify_lessons(
        all_lessons=True,
    )

    media_copied = copy_runtime_media(
        source
    )

    with transaction.atomic():
        media_created = sync_media_rows(
            source
        )

    return {
        "structure": structure,
        "publication": publication,
        "media_total": len(
            source["assets"]
        ),
        "media_copied": media_copied,
        "media_created": media_created,
        "dry_run": False,
    }