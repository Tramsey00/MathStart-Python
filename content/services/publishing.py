"""Publish existing lesson sources with conflict detection and one transaction."""
import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connections, transaction

from content.models import ContentPage, LessonPublication
from content.quality import inspect_html
from .lesson_sources import (
    EDITABLE_FIELDS, IDENTITY_FIELDS, LessonSourceError, digest, load_bundles,
    page_snapshot, source_root,
)


def backup_database():
    database = connections["default"].settings_dict
    name = str(database["NAME"])
    if not database["ENGINE"].endswith("sqlite3") or name == ":memory:" or "mode=memory" in name:
        return None
    source = Path(name).resolve()
    if not source.is_file():
        raise LessonSourceError("Не найдена база для резервного копирования: " + str(source))
    directory = Path(settings.LESSON_BACKUP_ROOT)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    target = directory / f"before-lesson-publication-{stamp}-{uuid4().hex[:8]}.sqlite3"
    with sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as src, sqlite3.connect(target) as dst:
        src.backup(dst)
    return str(target)


def publication_plan(bundles, lock=False):
    query = ContentPage.objects.filter(slug__in=[bundle.slug for bundle in bundles])
    if lock:
        query = query.select_for_update()
    pages = {page.slug: page for page in query}
    states = LessonPublication.objects.filter(page_id__in=[page.pk for page in pages.values()])
    if lock:
        states = states.select_for_update()
    states = {state.page_id: state for state in states}
    plan = []
    for bundle in bundles:
        page = pages.get(bundle.slug)
        if page is None or page.page_type != "topic":
            raise LessonSourceError(f"{bundle.slug}: существующий урок не найден. Создание и смена адресов не входят в перенос.")
        current = page_snapshot(page)
        if any(current[field] != bundle.snapshot[field] for field in IDENTITY_FIELDS):
            raise LessonSourceError(f"{bundle.slug}: нельзя менять адрес, тип, класс, предмет или раздел при публикации содержимого.")
        if page.subject.grade_id != page.grade_id or page.section.subject_id != page.subject_id:
            raise LessonSourceError(f"{bundle.slug}: противоречивые связи в каталоге.")
        state = states.get(page.pk)
        if state and state.source_path != bundle.relative_path:
            raise LessonSourceError(f"{bundle.slug}: зарегистрирован другой путь исходника: {state.source_path}")
        owner = LessonPublication.objects.filter(source_path=bundle.relative_path).exclude(page_id=page.pk).exists()
        if owner:
            raise LessonSourceError(f"{bundle.relative_path}: путь уже закреплён за другим уроком.")
        current_digest, desired_digest = digest(current), digest(bundle.snapshot)
        baseline = state.published_digest if state else bundle.metadata["baseline_digest"]
        if current_digest not in (baseline, desired_digest):
            raise LessonSourceError(f"{bundle.slug}: конфликт — страница изменена в базе после экспорта или публикации. Правки не перезаписаны.")
        changed = [field for field in EDITABLE_FIELDS if current[field] != bundle.snapshot[field]]
        if changed:
            for field in changed:
                setattr(page, field, bundle.snapshot[field])
            try:
                page.full_clean()
            except ValidationError as exc:
                raise LessonSourceError(f"{bundle.slug}: {exc}") from exc
            issues = inspect_html(page.body_html)["issues"]
            if issues:
                raise LessonSourceError(f"{bundle.slug}: проверка HTML не пройдена: {issues[:8]}")
        state_changed = state is None or state.published_digest != desired_digest
        plan.append((bundle, page, state, changed, desired_digest, state_changed))
    return plan


def publish_lessons(root=None, slugs=None, all_lessons=False, dry_run=False):
    bundles = load_bundles(source_root(root), slugs, all_lessons)
    plan = publication_plan(bundles)
    result = {
        "selected": len(plan), "changed": sum(bool(item[3]) for item in plan),
        "registered": sum(item[2] is None for item in plan), "backup": None,
        "slugs_changed": [item[0].slug for item in plan if item[3]],
    }
    if dry_run or not any(item[3] or item[5] for item in plan):
        return result
    result["backup"] = backup_database()
    # Check again while holding database locks: a stale preflight must never
    # overwrite an edit made while the backup was being taken.
    with transaction.atomic():
        plan = publication_plan(bundles, lock=True)
        for bundle, page, state, changed, desired_digest, state_changed in plan:
            if changed:
                fields = list(changed) + ["updated_at"]
                if "body_html" in changed:
                    page.content_checksum = hashlib.sha256(page.body_html.encode("utf-8")).hexdigest()
                    fields.append("content_checksum")
                page.save(update_fields=fields)
            if state_changed:
                LessonPublication.objects.update_or_create(page=page, defaults={
                    "source_path": bundle.relative_path, "published_digest": desired_digest,
                })
    return result


def verify_lessons(root=None, slugs=None, all_lessons=False):
    bundles = load_bundles(source_root(root), slugs, all_lessons)
    pages = {page.slug: page for page in ContentPage.objects.filter(page_type="topic").select_related("grade", "subject", "section")}
    if all_lessons and set(pages) != {bundle.slug for bundle in bundles}:
        missing = sorted(set(pages) - {bundle.slug for bundle in bundles})
        extra = sorted({bundle.slug for bundle in bundles} - set(pages))
        raise LessonSourceError(f"Неполный каталог исходников. Без файлов: {missing}; без страниц: {extra}.")
    for bundle in bundles:
        page = pages.get(bundle.slug)
        if page is None:
            raise LessonSourceError(f"{bundle.slug}: нет страницы в базе.")
        snapshot = page_snapshot(page)
        differing = [field for field in snapshot if snapshot[field] != bundle.snapshot[field]]
        if differing:
            raise LessonSourceError(f"{bundle.slug}: файлы отличаются от базы: {', '.join(differing)}")
    return {"verified": len(bundles)}
