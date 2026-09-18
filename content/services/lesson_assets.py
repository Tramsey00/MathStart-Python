"""Move authored lesson resources out of HTML without changing their contents."""
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.db import transaction

from .lesson_components import SourceTree, replace_ranges
from .lesson_sources import LessonSourceError, read_utf8


def extract_scripts(body, existing_js=""):
    """Classic inline scripts retain their order and run after the lesson DOM.

    Refuse scripts whose loading mode or parser-position dependency cannot be
    preserved by the page's single, bottom-of-body script slot. Data scripts
    (e.g. JSON) remain part of the authored HTML.
    """
    tree = SourceTree(body)
    scripts = []
    for node in tree.elements:
        if node.tag != "script":
            continue
        script_type = (node.attrs.get("type") or "").lower().strip()
        if script_type in {"application/json", "application/ld+json"}:
            continue
        if set(node.attrs) - {"type"} or script_type not in {"", "text/javascript", "application/javascript"}:
            raise LessonSourceError("Скрипт с особыми атрибутами требует отдельного переноса.")
        if not node.end:
            raise LessonSourceError("Не найден конец встроенного скрипта.")
        source = tree.inner(node)
        if re.search(r"document\s*\.\s*(?:write|writeln|currentScript)\b", source):
            raise LessonSourceError("Скрипт зависит от позиции в HTML и требует отдельного переноса.")
        scripts.append((node, source))
    if not scripts:
        return body, existing_js
    chunks = [source for _, source in scripts]
    if existing_js:
        chunks.append(existing_js)
    return (
        replace_ranges(body, [(node.start, node.end, "") for node, _ in scripts]),
        "\n;\n".join(chunks),
    )


def prepare_scripts(bundle):
    body = read_utf8(bundle.path.parent / "body.html")
    return extract_scripts(body, bundle.snapshot["page_js"])


def organize_assets(dry_run=False):
    """Back up, organize optional resources and publish one consistent batch."""
    from .css_cleanup import plan_css_cleanup
    from .lesson_sources import inside, load_bundles, source_root
    from .publishing import backup_database, publish_lessons, verify_lessons
    from .theme_migration import set_attributes

    root = source_root()
    project = Path(settings.BASE_DIR).resolve()
    if root != project / "curriculum":
        raise LessonSourceError("Перенос ресурсов допускается только для основного curriculum проекта.")
    verify_lessons(root, all_lessons=True)
    css_plan = plan_css_cleanup(project)
    css_by_path = {plan.path.resolve(): plan for plan in css_plan["pages"]}
    writes, removals = {}, []
    script_lessons = 0
    for bundle in load_bundles(root, all_lessons=True):
        body_file = bundle.path.parent / "body.html"
        original = read_utf8(body_file)
        body, script = extract_scripts(original, bundle.snapshot["page_js"])
        script_lessons += body != original
        css = bundle.snapshot["page_css"]
        plan = css_by_path.get(body_file.resolve())
        if plan:
            tree = SourceTree(body)
            links = [node for node in tree.elements if node.tag == "link" and "data-lesson-legacy-style" in node.attrs]
            if tuple(node.attrs["href"] for node in links) != plan.links:
                raise LessonSourceError(f"{bundle.slug}: набор старых CSS изменился во время переноса.")
            changes = [(node.start, node.end, "") for node in links]
            if plan.use_base:
                post = next(node for node in tree.elements if node.has_class("ms-post"))
                changes.append((post.start, post.inner_start, set_attributes(body[post.start:post.inner_start], {"data-lesson-base": "classic"})))
            body = replace_ranges(body, changes)
            css = plan.css + ("\n" + css if css.strip() else "")
        if body != original:
            writes[body_file] = body.encode("utf-8")
        for filename, value in (("page.css", css), ("page.js", script)):
            path = inside(root, bundle.path.parent / filename)
            if value.strip():
                payload = value.encode("utf-8")
                if not path.exists() or path.read_bytes() != payload:
                    writes[path] = payload
            elif path.exists():
                removals.append(path)
    if css_plan["pages"]:
        base_path = inside(project, project / "static" / css_plan["base_asset"])
        payload = css_plan["base_css"].encode("utf-8")
        if not base_path.exists() or base_path.read_bytes() != payload:
            writes[base_path] = payload
    result = {
        "css_lessons": len(css_plan["pages"]), "script_lessons": script_lessons,
        "empty_files_removed": len(removals), "files_written": len(writes),
        "unused_selectors_removed": sum(plan.unused_selectors for plan in css_plan["pages"]),
        "common_rules": len(css_plan["base_rules"]),
    }
    if dry_run or not (writes or removals):
        return result
    backups = Path(settings.LESSON_BACKUP_ROOT)
    backups.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    archive = backups / f"lesson-assets-before-organization-{stamp}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zipped:
        for folder in (root, project / "static/mathstart"):
            for path in folder.rglob("*"):
                if path.is_file():
                    zipped.write(path, path.relative_to(project))
    result.update(source_backup=str(archive), database_backup=backup_database())
    legacy_dir = inside(project, project / "static/mathstart/css/legacy")
    legacy_files = [inside(legacy_dir, path) for path in legacy_dir.glob("*.css")] if css_plan["pages"] else []
    originals = {path: path.read_bytes() if path.exists() else None for path in [*writes, *removals, *legacy_files]}
    try:
        with transaction.atomic():
            for path, payload in writes.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            for path in removals:
                path.unlink()
            publish_lessons(root, all_lessons=True, dry_run=True)
            result["publication"] = publish_lessons(root, all_lessons=True)
            verify_lessons(root, all_lessons=True)
            from content.models import ContentPage
            for page in ContentPage.objects.only("slug", "body_html", "page_css", "page_js"):
                if "/mathstart/css/legacy/" in page.body_html + page.page_css + page.page_js:
                    raise LessonSourceError(f"{page.slug}: осталась ссылка на прежний CSS; архивирование отменено.")
            for path in legacy_files:
                path.unlink()
    except Exception:
        for path, payload in originals.items():
            if payload is None:
                if path.exists():
                    path.unlink()
            else:
                path.write_bytes(payload)
        raise
    result["legacy_css_retired"] = len(legacy_files)
    if legacy_dir.is_dir() and not any(legacy_dir.iterdir()):
        legacy_dir.rmdir()
    return result
