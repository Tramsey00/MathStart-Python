"""Filesystem lesson sources for MathStart.

The curriculum directory is the editable source of truth.
Lesson markup is read without unnecessary reserialization so authored
HTML, CSS, JavaScript, SVG, whitespace and line endings remain intact.
"""
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

from content.models import ContentPage


PAYLOAD_FILES = {"body_html": "body.html", "page_css": "page.css", "page_js": "page.js"}
OPTIONAL_PAYLOADS = {"page_css", "page_js"}
EDITABLE_FIELDS = ("title", "order", "seo_title", "seo_description", "is_published", *PAYLOAD_FILES)
IDENTITY_FIELDS = ("slug", "page_type", "grade", "subject", "section")
PAGE_FIELDS = (*IDENTITY_FIELDS, *EDITABLE_FIELDS[:5])
SLUG = re.compile(r"[a-zA-Z0-9_-]+\Z")


class LessonSourceError(ValueError):
    pass


def source_root(root=None):
    return Path(root or settings.LESSON_SOURCE_ROOT).resolve()


def digest(snapshot):
    raw = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def page_snapshot(page):
    data = {field: getattr(page, field) for field in (*EDITABLE_FIELDS, "slug", "page_type")}
    for field in ("grade", "subject", "section"):
        related = getattr(page, field)
        data[field] = related.slug if related else None
    return data




def read_utf8(path):
    # Path.read_text() normalizes CRLF even when encoding='utf-8'.
    return path.read_bytes().decode("utf-8")



def inside(root, path):
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise LessonSourceError(f"Путь выходит за каталог исходников: {path}")
    return resolved


@dataclass(frozen=True)
class LessonBundle:
    path: Path
    relative_path: str
    metadata: dict
    snapshot: dict

    @property
    def slug(self):
        return self.snapshot["slug"]


def load_bundle(path, root):
    try:
        inside(root, path)
        metadata = json.loads(read_utf8(path))
        if (
                not isinstance(metadata, dict)
                or set(metadata)
                != {
            "schema_version",
            "format",
            "page",
        }
        ):
            raise LessonSourceError(
                f"{path}: неверные поля lesson.json."
            )

        if (
                metadata["schema_version"] != 2
                or metadata["format"]
                not in (
                "html",
                "component_html",
                "themed_html",
        )
        ):
            raise LessonSourceError(
                f"{path}: неподдерживаемая версия или формат урока."
            )
        data = metadata["page"]
        if data["page_type"] != "topic":
            raise LessonSourceError(f"{path}: допускаются только учебные темы.")
        for field in ("slug", "grade", "subject", "section"):
            if not isinstance(data[field], str) or not SLUG.fullmatch(data[field]):
                raise LessonSourceError(f"{path}: неверное поле {field}.")
        for field in ("title", "seo_title", "seo_description"):
            if not isinstance(data[field], str):
                raise LessonSourceError(f"{path}: {field} должен быть строкой.")
        if not data["title"].strip() or type(data["order"]) is not int or data["order"] < 0 or type(data["is_published"]) is not bool:
            raise LessonSourceError(f"{path}: проверьте название, порядок и статус публикации.")
        snapshot = dict(data)
        for field, filename in PAYLOAD_FILES.items():
            file = inside(root, path.parent / filename)
            snapshot[field] = "" if field in OPTIONAL_PAYLOADS and not file.exists() else read_utf8(file)
        if metadata["format"] in ("component_html", "themed_html"):
            from .lesson_components import (
                render_component_lesson,
                render_themed_contents,
            )
            try:
                renderer = render_component_lesson if metadata["format"] == "component_html" else render_themed_contents
                snapshot["body_html"] = renderer(snapshot["body_html"])
            except (ValueError, StopIteration) as exc:
                raise LessonSourceError(f"{path}: не удалось собрать компоненты урока: {exc}") from exc
        return LessonBundle(path, path.relative_to(root).as_posix(), metadata, snapshot)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LessonSourceError(f"Не удалось прочитать {path}: {exc}") from exc


def select_pages(slugs=None, all_lessons=False):
    if bool(slugs) == bool(all_lessons):
        raise LessonSourceError("Укажите --slug АДРЕС [АДРЕС ...] либо --all.")
    pages = ContentPage.objects.filter(page_type="topic").select_related("grade", "subject", "section")
    if slugs:
        pages = pages.filter(slug__in=slugs)
    result = list(pages.order_by("grade__order", "subject__order", "subject_id", "section__order", "section_id", "order", "slug"))
    if slugs and set(slugs) != {page.slug for page in result}:
        raise LessonSourceError("Не найдены уроки: " + ", ".join(sorted(set(slugs) - {page.slug for page in result})))
    if not result:
        raise LessonSourceError("Не найдено ни одного урока.")
    return result


def load_bundles(root, slugs=None, all_lessons=False):
    if bool(slugs) == bool(all_lessons):
        raise LessonSourceError("Укажите --slug АДРЕС [АДРЕС ...] либо --all.")
    bundles = [load_bundle(path, root) for path in sorted(root.rglob("lesson.json"))]
    seen = set()
    for bundle in bundles:
        if bundle.slug in seen:
            raise LessonSourceError(f"Два исходника для одного адреса: {bundle.slug}")
        seen.add(bundle.slug)
    if slugs and not set(slugs).issubset(seen):
        raise LessonSourceError("Не найдены исходники: " + ", ".join(sorted(set(slugs) - seen)))
    selected = [bundle for bundle in bundles if all_lessons or bundle.slug in slugs]
    if not selected:
        raise LessonSourceError("Не найдено ни одного исходника урока.")
    return selected


def write_lesson_index(root=None):
    """Human-readable map; generated separately so export remains non-overwriting."""
    root = source_root(root)
    bundles = load_bundles(root, all_lessons=True)
    paths = {bundle.slug: bundle for bundle in bundles}
    pages = select_pages(all_lessons=True)
    lines = ["# Уроки MathStart", "", "Исходники сгруппированы по классу, предмету и разделу. Ссылка открывает HTML урока; рядом находится `lesson.json` с его метаданными.", ""]
    previous = (None, None, None)
    count = 0
    for page in pages:
        bundle = paths.get(page.slug)
        if not bundle:
            continue
        if (page.grade_id, page.subject_id, page.section_id) != previous:
            lines.append("")
        if page.grade_id != previous[0]:
            lines += [f"## {page.grade.title}", ""]
        if page.subject_id != previous[1]:
            lines += [f"### {page.subject.title}", ""]
        if page.section_id != previous[2]:
            lines += [f"**{page.section.order}. {page.section.title}**", ""]
        path = Path(bundle.relative_path).parent.as_posix()
        title = bundle.snapshot["title"].replace("[", r"\[").replace("]", r"\]")
        lines += [f"- {page.section.order}.{bundle.snapshot['order']} [{title}]({path}/body.html)"]
        previous = (page.grade_id, page.subject_id, page.section_id)
        count += 1
    lines += ["", f"Всего исходников в указателе: {count}.", ""]
    payload = "\n".join(lines).encode("utf-8")
    destination = root / "INDEX.md"
    if not destination.exists() or destination.read_bytes() != payload:
        destination.write_bytes(payload)
    return count
