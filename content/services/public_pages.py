"""Scoped source publication for the existing public information pages."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core import serializers
from django.db import transaction

from content.models import ContentPage, LessonPublication, MediaAsset, Redirect
from content.services.publishing import publish_lessons, verify_lessons
from content.services.site_bootstrap import (
    SiteBootstrapError,
    copy_runtime_media,
    load_site_source,
    sync_media_rows,
    sync_structure,
    validate_runtime_media,
)

PUBLIC_PAGE_SLUGS = ("glavnaya", "karta-sajta", "o-proekte", "kontakty")
RETIRED_SLUGS = ("materialy", "pamyatki")
POWER_LESSON = "bazovye-svojstva-stepenej-s-naturalnym-pokazatelem"
POWER_PDF = "uploads/2026/07/pamyatka-stepeni.pdf"
RETIRED_PATHS = ("/materialy/", "/mathstart/materialy/", "/pamyatki/", "/mathstart/pamyatki/")


def backup_public_pages():
    """A Django fixture of public records, without users or credentials."""
    records = list(ContentPage.objects.filter(slug__in=(*PUBLIC_PAGE_SLUGS, *RETIRED_SLUGS, POWER_LESSON)))
    records += list(LessonPublication.objects.filter(page__slug=POWER_LESSON))
    records += list(MediaAsset.objects.filter(file=POWER_PDF))
    records += list(Redirect.objects.filter(old_path__in=RETIRED_PATHS))
    directory = Path(settings.LESSON_BACKUP_ROOT)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    target = directory / f"before-public-pages-{stamp}-{uuid4().hex[:8]}.json"
    target.write_text(serializers.serialize("json", records, indent=2), encoding="utf-8")
    return str(target)


def update_public_pages(dry_run=False):
    """Reuse bootstrap for four pages; never bootstrap unrelated lessons."""
    source = load_site_source()
    source = {
        **source,
        "grades": [], "subjects": [], "sections": [],
        "pages": [row for row in source["pages"] if row["page"]["slug"] in PUBLIC_PAGE_SLUGS],
        "redirects": [row for row in source["redirects"] if row["old_path"] in RETIRED_PATHS],
        "assets": [row for row in source["assets"] if row["file"] == POWER_PDF],
    }
    if (len(source["pages"]) != 4 or len(source["redirects"]) != 4 or len(source["assets"]) != 1
            or any(any(row["page"][key] is not None for key in ("grade", "subject", "section")) for row in source["pages"])):
        raise SiteBootstrapError("Неполный или несовместимый источник публичных страниц.")
    # This command updates an already installed site, not a fresh curriculum.
    if not ContentPage.objects.filter(slug=POWER_LESSON, page_type="topic").exists():
        raise SiteBootstrapError("Для точечного обновления нужен существующий урок со ссылкой на PDF.")
    validate_runtime_media(source)
    # Validate all lesson conflicts before writing a backup or copying media.
    publish_lessons(slugs=[POWER_LESSON], dry_run=True)
    backup = None if dry_run else backup_public_pages()
    copied = 0 if dry_run else copy_runtime_media(source)
    with transaction.atomic():
        # Publication retains its own locked conflict recheck. Run it before
        # bootstrap writes so SQLite's existing backup remains usable as well.
        publication = publish_lessons(slugs=[POWER_LESSON], dry_run=dry_run)
        if not dry_run:
            verify_lessons(slugs=[POWER_LESSON])
        structure = sync_structure(source)
        media_created = sync_media_rows(source)
        if dry_run:
            transaction.set_rollback(True)
    return {
        "dry_run": dry_run, "backup": backup, "pages_selected": len(source["pages"]),
        "redirects_selected": len(source["redirects"]), "structure": structure,
        "publication": publication, "media_created": media_created, "media_copied": copied,
    }
