"""One-way, backed-up adoption of the approved power-functions 2.0 theme."""
import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from django.conf import settings

from .lesson_components import SourceTree, component, replace_ranges, text_only, render_legacy_contents
from .lesson_sources import LessonSourceError, json_bytes, load_bundles, read_utf8, source_root
from .lesson_theme import MARKER
from .publishing import backup_database, publish_lessons, verify_lessons


MODERN_SLUGS = {
    "10-klass-stepennye-funkcii-i-grafiki-2-0",
    "10-klass-naturalnye-chisla-povtorenie-2-0",
    "10-klass-racionalnye-chisla-povtorenie-2-0",
}
ALIASES = {
    "v2-hero": "ms-hero", "v2-eyebrow": "ms-badge", "v2-actions": "ms-hero-actions",
    "v2-button": "ms-btn", "v2-section": "ms-section", "v2-rule": "ms-rule-box",
    "v2-note": "ms-note", "v2-example": "ms-example", "v2-box-title": "ms-example-title",
    "v2-task": "ms-task", "v2-answer": "ms-answer", "v2-finish": "ms-section",
    "v2-bottom": "ms-nav",
}


def set_attributes(opening, additions):
    for key, value in additions.items():
        pattern = rf'\b{re.escape(key)}\s*=\s*([\"\']).*?\1'
        attribute = f'{key}="{escape(value, quote=True)}"'
        if re.search(pattern, opening, flags=re.S):
            opening = re.sub(pattern, lambda _: attribute, opening, count=1, flags=re.S)
        else:
            opening = opening[:-1] + " " + attribute + ">"
    return opening


def modern_resources():
    historical = settings.BASE_DIR / "content" / "lessons" / "v2"
    names = ["power_page.css", "power_math.css", "lesson_navigation.css"]
    common = "\n".join((historical / name).read_text(encoding="utf-8").replace(".ms-power-page", ".ms-lesson-page") for name in names)
    return historical, common


def prepare_lesson(bundle):
    raw = read_utf8(bundle.path.parent / "body.html")
    if MARKER in raw:
        return None
    tree = SourceTree(raw)
    root = next((node for node in tree.elements if node.has_class("ms-post")), None)
    if not root or not root.end:
        raise LessonSourceError(f"{bundle.slug}: не удалось определить границы урока.")
    modern = bundle.slug in MODERN_SLUGS
    attrs = {"class": root.attrs["class"] + ("" if root.has_class("ms-lesson-page") else " ms-lesson-page") + ("" if modern else " ms-legacy-lesson"),
             "data-lesson-theme": "power-v2", "data-lesson-layout": "components" if modern else "legacy"}
    power = bundle.slug == "10-klass-stepennye-funkcii-i-grafiki-2-0"
    if power:
        attrs["data-lesson-widget"] = "power-functions"
    openings = {root.start: (root, attrs)}
    changes, assets = [], {}
    if modern:
        historical, common = modern_resources()
        expected_css = common
        if power:
            expected_css += "\n" + (historical / "power_lab.css").read_text(encoding="utf-8").replace(".ms-power-page", ".ms-lesson-page")
        elif "racionalnye" in bundle.slug:
            expected_css += "\n" + (historical / "rational.css").read_text(encoding="utf-8")
        expected_js = (historical / "lesson_navigation.js").read_text(encoding="utf-8")
        if power:
            expected_js += "\n" + (historical / "math.js").read_text(encoding="utf-8") + "\n" + (historical / "power.js").read_text(encoding="utf-8")
        styles = [node for node in tree.elements if node.tag == "style"]
        scripts = [node for node in tree.elements if node.tag == "script"]
        if len(styles) != 1 or tree.inner(styles[0]) != expected_css or len(scripts) != 1 or tree.inner(scripts[0]) != expected_js:
            raise LessonSourceError(f"{bundle.slug}: эталонные ресурсы отличаются от ожидаемых; требуется проверка правок.")
        for node in styles + scripts:
            changes.append((node.start, node.end, ""))
    else:
        for node in tree.elements:
            if node.tag != "style":
                continue
            css = tree.inner(node)
            if re.search(r"url\s*\(|@import", css, flags=re.I):
                raise LessonSourceError(f"{bundle.slug}: перед переносом CSS требуется проверить относительные ресурсы.")
            filename = hashlib.sha256(css.encode("utf-8")).hexdigest()[:20] + ".css"
            asset = "mathstart/css/legacy/" + filename
            assets[asset] = css.encode("utf-8")
            extra = "".join(f' {key}="{escape(value or "", quote=True)}"' for key, value in node.attrs.items() if key != "type")
            link = f'<link rel="stylesheet" href="{settings.STATIC_URL}{asset}" data-lesson-legacy-style{extra}>'
            changes.append((node.start, node.end, link))
        if root.has_class("ms-v2"):
            for node in tree.elements:
                extra = [target for original, target in ALIASES.items() if node.has_class(original)]
                if node.parent and node.parent.has_class("v2-hero"):
                    if node.tag == "h1": extra.append("ms-title")
                    if node.tag == "p": extra.append("ms-subtitle")
                if node.tag == "a" and node.parent and node.parent.has_class("v2-actions") and not node.has_class("v2-button"):
                    extra += ["ms-btn", "ms-btn-secondary"]
                if extra:
                    openings[node.start] = (node, {"class": " ".join(node.attrs.get("class", "").split() + extra)})
        entries, used_ids = [], {node.attrs["id"] for node in tree.elements if node.attrs.get("id")}
        for section in root.children:
            if section.tag != "section" or not (section.has_class("ms-section") or section.has_class("ms-section-soft") or section.has_class("v2-section") or section.has_class("v2-finish")):
                continue
            heading = next((node for node in tree.elements if node.tag == "h2" and section.inner_start <= node.start < section.inner_end), None)
            if not heading:
                continue
            ident = section.attrs.get("id")
            if not ident:
                number = len(entries) + 1
                ident = f"lesson-section-{number}"
                while ident in used_ids:
                    number += 1
                    ident = f"lesson-section-{number}"
                used_ids.add(ident)
                _, values = openings.setdefault(section.start, (section, {}))
                values["id"] = ident
            title = re.sub(r"^\d+\.\s*", "", text_only(tree.inner(heading)))
            tasks = sum(node.has_class("ms-answer") or node.has_class("v2-answer") for node in tree.elements if section.start < node.start < section.end)
            note = f"Заданий для самостоятельной проверки: {tasks}" if tasks else ""
            entries.append({"id": ident, "title": title, "note": note, "practice": bool(tasks)})
        hero = next((node for node in root.children if node.has_class("ms-hero") or node.has_class("v2-hero")), None)
        if not hero or not entries:
            raise LessonSourceError(f"{bundle.slug}: не удалось построить содержание.")
        toc = component("contents", {"entries": entries})
        # Keep the existing mobile DOM flow: this desktop-only block is hidden
        # by default, then enabled by the desktop adapter stylesheet.
        toc = toc.replace('class="ms-lesson-toc"', 'class="ms-lesson-toc ms-desktop-toc" style="display:none"', 1)
        changes.append((hero.end, hero.end, "\n" + toc + "\n"))
    for node, additions in openings.values():
        changes.append((node.start, node.inner_start, set_attributes(raw[node.start:node.inner_start], additions)))
    metadata = dict(bundle.metadata)
    metadata["format"] = "component_html" if modern else "themed_html"
    body = replace_ranges(raw, changes)
    if not modern:
        body = render_legacy_contents(body)
    return {"bundle": bundle, "body": body, "metadata": metadata, "assets": assets, "modern": modern}


def adopt_theme(dry_run=False):
    root = source_root()
    verify_lessons(root, all_lessons=True)
    plans = [plan for bundle in load_bundles(root, all_lessons=True) if (plan := prepare_lesson(bundle))]
    result = {"lessons": len(plans), "component_lessons": sum(plan["modern"] for plan in plans), "assets": len({path for plan in plans for path in plan["assets"]})}
    if dry_run or not plans:
        return result
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_dir = Path(settings.LESSON_BACKUP_ROOT)
    backup_dir.mkdir(parents=True, exist_ok=True)
    archive = backup_dir / f"lesson-sources-before-theme-{stamp}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for path in root.rglob("*"):
            if path.is_file():
                zip_file.write(path, path.relative_to(root))
    result["database_backup"] = backup_database()
    result["source_backup"] = str(archive)
    # Sources are recoverable from the archive even if filesystem work fails.
    originals = {}
    try:
        for plan in plans:
            bundle = plan["bundle"]
            body_file = bundle.path.parent / "body.html"
            originals[body_file] = body_file.read_bytes()
            originals[bundle.path] = bundle.path.read_bytes()
            body_file.write_bytes(plan["body"].encode("utf-8"))
            bundle.path.write_bytes(json_bytes(plan["metadata"]))
            for name, payload in plan["assets"].items():
                target = settings.BASE_DIR / "static" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists() and target.read_bytes() != payload:
                    raise LessonSourceError("Конфликт статического ресурса: " + name)
                if not target.exists():
                    target.write_bytes(payload)
        publish_lessons(root, all_lessons=True, dry_run=True)
        publish_lessons(root, all_lessons=True)
    except Exception:
        for path, payload in originals.items():
            path.write_bytes(payload)
        raise
    return result
