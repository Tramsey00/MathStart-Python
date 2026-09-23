"""Publish lesson sources with conflict-safe create/update semantics."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connections, transaction

from content.models import (
    ContentPage,
    Grade,
    LessonPublication,
    Section,
    Subject,
)
from content.quality import inspect_html
from .lesson_sources import (
    EDITABLE_FIELDS,
    IDENTITY_FIELDS,
    LessonBundle,
    LessonSourceError,
    digest,
    load_bundles,
    page_snapshot,
    source_root,
)


@dataclass(frozen=True)
class PublicationAction:
    bundle: LessonBundle
    page: ContentPage | None
    state: LessonPublication | None
    grade: Grade
    subject: Subject
    section: Section
    created: bool
    changed: tuple[str, ...]
    desired_digest: str
    state_changed: bool


def backup_database():
    database = connections["default"].settings_dict
    name = str(database["NAME"])

    if (
        not database["ENGINE"].endswith("sqlite3")
        or name == ":memory:"
        or "mode=memory" in name
    ):
        return None

    source = Path(name).resolve()

    if not source.is_file():
        raise LessonSourceError(
            "Не найдена база для резервного копирования: "
            + str(source)
        )

    directory = Path(settings.LESSON_BACKUP_ROOT)
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    stamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%S%fZ")

    target = (
        directory
        / (
            "before-lesson-publication-"
            f"{stamp}-{uuid4().hex[:8]}.sqlite3"
        )
    )

    with (
        sqlite3.connect(
            source.as_uri() + "?mode=ro",
            uri=True,
        ) as src,
        sqlite3.connect(target) as dst,
    ):
        src.backup(dst)

    return str(target)


def resolve_catalog(bundles):
    grade_slugs = {
        bundle.snapshot["grade"]
        for bundle in bundles
    }

    subject_slugs = {
        bundle.snapshot["subject"]
        for bundle in bundles
    }

    section_slugs = {
        bundle.snapshot["section"]
        for bundle in bundles
    }

    grades = {
        grade.slug: grade
        for grade in Grade.objects.filter(
            slug__in=grade_slugs
        )
    }

    subjects = {
        (
            subject.grade.slug,
            subject.slug,
        ): subject
        for subject in (
            Subject.objects
            .filter(
                grade__slug__in=grade_slugs,
                slug__in=subject_slugs,
            )
            .select_related("grade")
        )
    }

    sections = {
        (
            section.subject.grade.slug,
            section.subject.slug,
            section.slug,
        ): section
        for section in (
            Section.objects
            .filter(
                subject__grade__slug__in=grade_slugs,
                subject__slug__in=subject_slugs,
                slug__in=section_slugs,
            )
            .select_related(
                "subject",
                "subject__grade",
            )
        )
    }

    result = {}

    for bundle in bundles:
        snapshot = bundle.snapshot

        grade_slug = snapshot["grade"]
        subject_slug = snapshot["subject"]
        section_slug = snapshot["section"]

        grade = grades.get(grade_slug)

        if grade is None:
            raise LessonSourceError(
                f"{bundle.slug}: класс "
                f"{grade_slug!r} отсутствует в каталоге."
            )

        subject = subjects.get(
            (
                grade_slug,
                subject_slug,
            )
        )

        if subject is None:
            raise LessonSourceError(
                f"{bundle.slug}: предмет "
                f"{subject_slug!r} отсутствует "
                f"в классе {grade_slug!r}."
            )

        section = sections.get(
            (
                grade_slug,
                subject_slug,
                section_slug,
            )
        )

        if section is None:
            raise LessonSourceError(
                f"{bundle.slug}: раздел "
                f"{section_slug!r} отсутствует "
                f"в предмете {subject_slug!r} "
                f"класса {grade_slug!r}."
            )

        result[bundle.slug] = (
            grade,
            subject,
            section,
        )

    return result


def build_candidate(
    bundle,
    grade,
    subject,
    section,
    existing_page=None,
):
    snapshot = bundle.snapshot

    page = ContentPage(
        slug=snapshot["slug"],
        page_type=snapshot["page_type"],
        grade=grade,
        subject=subject,
        section=section,
        **{
            field: snapshot[field]
            for field in EDITABLE_FIELDS
        },
    )

    if existing_page is not None:
        page.pk = existing_page.pk
        page._state.adding = False
        page._state.db = existing_page._state.db

    return page


def validate_candidate(
    bundle,
    grade,
    subject,
    section,
    existing_page=None,
):
    candidate = build_candidate(
        bundle,
        grade,
        subject,
        section,
        existing_page=existing_page,
    )

    try:
        candidate.full_clean()
    except ValidationError as exc:
        raise LessonSourceError(
            f"{bundle.slug}: {exc}"
        ) from exc

    issues = inspect_html(
        candidate.body_html
    )["issues"]

    if issues:
        raise LessonSourceError(
            f"{bundle.slug}: проверка HTML "
            f"не пройдена: {issues[:8]}"
        )

    return candidate


def publication_plan(
    bundles,
    lock=False,
):
    catalog = resolve_catalog(bundles)

    page_query = (
        ContentPage.objects
        .filter(
            slug__in=[
                bundle.slug
                for bundle in bundles
            ]
        )
        .select_related(
            "grade",
            "subject",
            "section",
            "subject__grade",
            "section__subject",
        )
    )

    if lock:
        page_query = (
            page_query.select_for_update()
        )

    pages = {
        page.slug: page
        for page in page_query
    }

    state_query = (
        LessonPublication.objects
        .filter(
            page_id__in=[
                page.pk
                for page in pages.values()
            ]
        )
    )

    if lock:
        state_query = (
            state_query.select_for_update()
        )

    states = {
        state.page_id: state
        for state in state_query
    }

    owner_query = (
        LessonPublication.objects
        .filter(
            source_path__in=[
                bundle.relative_path
                for bundle in bundles
            ]
        )
    )

    if lock:
        owner_query = (
            owner_query.select_for_update()
        )

    source_owners = {
        state.source_path: state.page_id
        for state in owner_query
    }

    plan = []

    for bundle in bundles:
        (
            grade,
            subject,
            section,
        ) = catalog[bundle.slug]

        page = pages.get(bundle.slug)

        desired_digest = digest(
            bundle.snapshot
        )

        owner_page_id = source_owners.get(
            bundle.relative_path
        )

        # -------------------------------------------------
        # New lesson
        # -------------------------------------------------

        if page is None:
            if owner_page_id is not None:
                raise LessonSourceError(
                    f"{bundle.relative_path}: "
                    "путь уже закреплён "
                    "за другой страницей."
                )

            validate_candidate(
                bundle,
                grade,
                subject,
                section,
            )

            plan.append(
                PublicationAction(
                    bundle=bundle,
                    page=None,
                    state=None,
                    grade=grade,
                    subject=subject,
                    section=section,
                    created=True,
                    changed=tuple(
                        EDITABLE_FIELDS
                    ),
                    desired_digest=(
                        desired_digest
                    ),
                    state_changed=True,
                )
            )

            continue

        # -------------------------------------------------
        # Existing lesson
        # -------------------------------------------------

        if (
            page.page_type
            != ContentPage.PageType.TOPIC
        ):
            raise LessonSourceError(
                f"{bundle.slug}: этот slug "
                "уже занят страницей другого типа."
            )

        current = page_snapshot(page)

        identity_differences = [
            field
            for field in IDENTITY_FIELDS
            if (
                current[field]
                != bundle.snapshot[field]
            )
        ]

        if identity_differences:
            raise LessonSourceError(
                f"{bundle.slug}: нельзя менять "
                "адрес, тип, класс, предмет "
                "или раздел при публикации. "
                "Отличаются поля: "
                + ", ".join(
                    identity_differences
                )
            )

        if (
            page.subject is None
            or page.section is None
            or page.grade is None
            or (
                page.subject.grade_id
                != page.grade_id
            )
            or (
                page.section.subject_id
                != page.subject_id
            )
        ):
            raise LessonSourceError(
                f"{bundle.slug}: "
                "противоречивые связи "
                "в каталоге."
            )

        state = states.get(page.pk)

        if (
            state is not None
            and state.source_path
            != bundle.relative_path
        ):
            raise LessonSourceError(
                f"{bundle.slug}: "
                "зарегистрирован другой "
                "путь исходника: "
                f"{state.source_path}"
            )

        if (
            owner_page_id is not None
            and owner_page_id != page.pk
        ):
            raise LessonSourceError(
                f"{bundle.relative_path}: "
                "путь уже закреплён "
                "за другим уроком."
            )

        current_digest = digest(current)

        if state is not None:
            if current_digest not in (
                state.published_digest,
                desired_digest,
            ):
                raise LessonSourceError(
                    f"{bundle.slug}: конфликт — "
                    "страница изменена в базе "
                    "после последней публикации. "
                    "Правки не перезаписаны."
                )

        elif (
            current_digest
            != desired_digest
        ):
            raise LessonSourceError(
                f"{bundle.slug}: исходник ещё "
                "не зарегистрирован, а его "
                "содержимое отличается от базы. "
                "Сначала синхронизируйте "
                "страницу и исходник."
            )

        changed = tuple(
            field
            for field in EDITABLE_FIELDS
            if (
                current[field]
                != bundle.snapshot[field]
            )
        )

        if changed:
            validate_candidate(
                bundle,
                grade,
                subject,
                section,
                existing_page=page,
            )

        state_changed = (
            state is None
            or (
                state.published_digest
                != desired_digest
            )
        )

        plan.append(
            PublicationAction(
                bundle=bundle,
                page=page,
                state=state,
                grade=grade,
                subject=subject,
                section=section,
                created=False,
                changed=changed,
                desired_digest=(
                    desired_digest
                ),
                state_changed=(
                    state_changed
                ),
            )
        )

    return plan


def publish_lessons(
    root=None,
    slugs=None,
    all_lessons=False,
    dry_run=False,
):
    bundles = load_bundles(
        source_root(root),
        slugs,
        all_lessons,
    )

    plan = publication_plan(bundles)

    result = {
        "selected": len(plan),
        "created": sum(
            action.created
            for action in plan
        ),
        "changed": sum(
            (
                action.created
                or bool(action.changed)
            )
            for action in plan
        ),
        "registered": sum(
            action.state is None
            for action in plan
        ),
        "backup": None,
        "slugs_changed": [
            action.bundle.slug
            for action in plan
            if (
                action.created
                or action.changed
            )
        ],
    }

    has_work = any(
        (
            action.created
            or action.changed
            or action.state_changed
        )
        for action in plan
    )

    if dry_run or not has_work:
        return result

    result["backup"] = backup_database()

    try:
        with transaction.atomic():
            # Rebuild the plan while database rows
            # are locked. A stale preflight must
            # never overwrite a concurrent edit.
            plan = publication_plan(
                bundles,
                lock=True,
            )

            for action in plan:
                if action.created:
                    page = build_candidate(
                        action.bundle,
                        action.grade,
                        action.subject,
                        action.section,
                    )

                    page.save(
                        force_insert=True
                    )

                else:
                    page = action.page

                    if action.changed:
                        for field in (
                            action.changed
                        ):
                            setattr(
                                page,
                                field,
                                action.bundle.snapshot[
                                    field
                                ],
                            )

                        page.save(
                            update_fields=[
                                *action.changed,
                                "updated_at",
                            ]
                        )

                if action.state_changed:
                    (
                        LessonPublication
                        .objects
                        .update_or_create(
                            page=page,
                            defaults={
                                "source_path": (
                                    action.bundle
                                    .relative_path
                                ),
                                "published_digest": (
                                    action
                                    .desired_digest
                                ),
                            },
                        )
                    )

    except IntegrityError as exc:
        raise LessonSourceError(
            "Публикация отменена из-за "
            "конфликта целостности данных: "
            f"{exc}"
        ) from exc

    return result


def verify_lessons(
    root=None,
    slugs=None,
    all_lessons=False,
):
    bundles = load_bundles(
        source_root(root),
        slugs,
        all_lessons,
    )

    pages = {
        page.slug: page
        for page in (
            ContentPage.objects
            .filter(
                page_type=(
                    ContentPage.PageType.TOPIC
                )
            )
            .select_related(
                "grade",
                "subject",
                "section",
            )
        )
    }

    if (
        all_lessons
        and set(pages)
        != {
            bundle.slug
            for bundle in bundles
        }
    ):
        without_sources = sorted(
            set(pages)
            - {
                bundle.slug
                for bundle in bundles
            }
        )

        without_pages = sorted(
            {
                bundle.slug
                for bundle in bundles
            }
            - set(pages)
        )

        raise LessonSourceError(
            "Неполный каталог исходников. "
            f"Без файлов: {without_sources}; "
            f"без страниц: {without_pages}."
        )

    for bundle in bundles:
        page = pages.get(bundle.slug)

        if page is None:
            raise LessonSourceError(
                f"{bundle.slug}: "
                "нет страницы в базе."
            )

        snapshot = page_snapshot(page)

        differing = [
            field
            for field in snapshot
            if (
                snapshot[field]
                != bundle.snapshot[field]
            )
        ]

        if differing:
            raise LessonSourceError(
                f"{bundle.slug}: "
                "файлы отличаются от базы: "
                + ", ".join(differing)
            )

    return {
        "verified": len(bundles)
    }