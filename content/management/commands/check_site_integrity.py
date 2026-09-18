import html
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from content.models import ContentPage, MediaAsset, Redirect


OLD_WORDPRESS_MARKERS = (
    "localhost/mathstart",
    "127.0.0.1/mathstart",
    "cy874851.tw1.ru",
    "wp-content/uploads",
)

INTERNAL_HOSTS = {
    "localhost",
    "127.0.0.1",
    "cy874851.tw1.ru",
}

IGNORED_SCHEMES = {
    "mailto",
    "tel",
    "javascript",
    "data",
    "blob",
}

HTML_ATTRIBUTES = (
    ("a", "href"),
    ("img", "src"),
    ("script", "src"),
    ("link", "href"),
    ("source", "src"),
    ("iframe", "src"),
    ("video", "src"),
    ("video", "poster"),
    ("audio", "src"),
    ("object", "data"),
)


def normalize_internal_path(raw_url):
    """
    Возвращает внутренний URL-путь либо None,
    если ссылка внешняя или не требует проверки.
    """
    if not raw_url:
        return None

    value = html.unescape(str(raw_url)).strip()

    if not value or value.startswith("#"):
        return None

    if value.startswith("//"):
        value = "https:" + value

    parsed = urlparse(value)

    scheme = parsed.scheme.lower()

    if scheme in IGNORED_SCHEMES:
        return None

    if scheme in {"http", "https"}:
        hostname = (parsed.hostname or "").lower()

        if hostname not in INTERNAL_HOSTS:
            return None

    elif scheme:
        return None

    path = unquote(parsed.path or "")
    path = path.replace("\\", "/")
    path = re.sub(r"/+", "/", path)

    if not path:
        return "/"

    if not path.startswith("/"):
        path = "/" + path

    return path


def normalize_page_path(path):
    """
    Нормализует адрес страницы к формату /slug/.
    Пути к файлам не изменяет.
    """
    if not path:
        return "/"

    if path == "/":
        return "/"

    suffix = PurePosixPath(path).suffix

    if suffix:
        return path

    return "/" + path.strip("/") + "/"


def extract_css_urls(css_text):
    if not css_text:
        return []

    pattern = re.compile(
        r"url\(\s*(['\"]?)(.*?)\1\s*\)",
        flags=re.IGNORECASE,
    )

    return [
        match.group(2).strip()
        for match in pattern.finditer(css_text)
        if match.group(2).strip()
    ]


def extract_page_references(page):
    references = []

    soup = BeautifulSoup(
        page.body_html or "",
        "html.parser",
    )

    for tag_name, attribute_name in HTML_ATTRIBUTES:
        for tag in soup.find_all(
            tag_name,
            attrs={attribute_name: True},
        ):
            references.append(
                {
                    "kind": f"{tag_name}[{attribute_name}]",
                    "url": tag.get(attribute_name, ""),
                }
            )

    for tag in soup.find_all(
        attrs={"srcset": True},
    ):
        srcset = tag.get("srcset", "")

        for item in srcset.split(","):
            candidate = item.strip().split(" ")[0]

            if candidate:
                references.append(
                    {
                        "kind": "srcset",
                        "url": candidate,
                    }
                )

    for style_tag in soup.find_all("style"):
        for url in extract_css_urls(
            style_tag.get_text("\n")
        ):
            references.append(
                {
                    "kind": "style:url",
                    "url": url,
                }
            )

    for url in extract_css_urls(page.page_css):
        references.append(
            {
                "kind": "page_css:url",
                "url": url,
            }
        )

    return references


def static_file_exists(relative_path):
    relative_path = relative_path.lstrip("/")

    for static_directory in getattr(
        settings,
        "STATICFILES_DIRS",
        [],
    ):
        candidate = Path(static_directory) / relative_path

        if candidate.is_file():
            return True

    static_root = getattr(
        settings,
        "STATIC_ROOT",
        None,
    )

    if static_root:
        candidate = Path(static_root) / relative_path

        if candidate.is_file():
            return True

    return False


class Command(BaseCommand):
    help = (
        "Проверяет структуру, внутренние ссылки, "
        "медиафайлы и остаточные адреса WordPress."
    )

    def handle(self, *args, **options):
        pages = list(
            ContentPage.objects.select_related(
                "grade",
                "subject",
                "section",
            ).all()
        )

        media_assets = list(
            MediaAsset.objects.all()
        )

        redirects = list(
            Redirect.objects.filter(
                is_active=True,
            )
        )

        known_page_paths = {
            normalize_page_path(
                f"/{page.slug}/"
            )
            for page in pages
            if page.slug
        }

        known_page_paths.add("/")

        for redirect in redirects:
            old_path = normalize_internal_path(
                redirect.old_path
            )

            if old_path:
                known_page_paths.add(
                    normalize_page_path(old_path)
                )

        duplicate_slugs = list(
            ContentPage.objects.values("slug")
            .annotate(total=Count("id"))
            .filter(total__gt=1)
            .order_by("slug")
        )

        empty_content_pages = [
            {
                "id": page.id,
                "title": page.title,
                "slug": page.slug,
            }
            for page in pages
            if not (page.body_html or "").strip()
        ]

        empty_slug_pages = [
            {
                "id": page.id,
                "title": page.title,
            }
            for page in pages
            if not (page.slug or "").strip()
        ]

        topics = [
            page
            for page in pages
            if page.page_type == ContentPage.PageType.TOPIC
        ]

        topics_without_grade = [
            page.slug
            for page in topics
            if page.grade_id is None
        ]

        topics_without_subject = [
            page.slug
            for page in topics
            if page.subject_id is None
        ]

        topics_without_section = [
            page.slug
            for page in topics
            if page.section_id is None
        ]

        broken_internal_links = []
        broken_media_references = []
        broken_static_references = []
        old_marker_details = []

        referenced_media_paths = set()
        checked_reference_count = 0

        for page in pages:
            combined_content = "\n".join(
                (
                    page.body_html or "",
                    page.page_css or "",
                    page.page_js or "",
                )
            )

            lower_content = combined_content.lower()

            for marker in OLD_WORDPRESS_MARKERS:
                occurrence_count = lower_content.count(
                    marker.lower()
                )

                if occurrence_count:
                    old_marker_details.append(
                        {
                            "page": page.slug,
                            "marker": marker,
                            "count": occurrence_count,
                        }
                    )

            references = extract_page_references(page)

            for reference in references:
                raw_url = reference["url"]
                path = normalize_internal_path(raw_url)

                if path is None:
                    continue

                checked_reference_count += 1

                if path.startswith(settings.MEDIA_URL):
                    relative_path = path[
                        len(settings.MEDIA_URL):
                    ].lstrip("/")

                    referenced_media_paths.add(
                        f"uploads/{relative_path[len('uploads/'):]}"
                        if relative_path.startswith("uploads/")
                        else relative_path
                    )

                    file_path = (
                        Path(settings.MEDIA_ROOT)
                        / relative_path
                    )

                    if not file_path.is_file():
                        broken_media_references.append(
                            {
                                "page": page.slug,
                                "kind": reference["kind"],
                                "url": raw_url,
                                "expected_file": str(file_path),
                            }
                        )

                    continue

                if path.startswith(settings.STATIC_URL):
                    relative_path = path[
                        len(settings.STATIC_URL):
                    ].lstrip("/")

                    if not static_file_exists(relative_path):
                        broken_static_references.append(
                            {
                                "page": page.slug,
                                "kind": reference["kind"],
                                "url": raw_url,
                            }
                        )

                    continue

                if path.startswith("/admin/"):
                    continue

                normalized_path = normalize_page_path(
                    path
                )

                if normalized_path not in known_page_paths:
                    broken_internal_links.append(
                        {
                            "page": page.slug,
                            "kind": reference["kind"],
                            "url": raw_url,
                            "normalized_path": normalized_path,
                        }
                    )

        missing_media_assets = []

        for asset in media_assets:
            if (
                not asset.file
                or not asset.file.storage.exists(
                    asset.file.name
                )
            ):
                missing_media_assets.append(
                    {
                        "id": asset.id,
                        "title": asset.title,
                        "file": (
                            asset.file.name
                            if asset.file
                            else ""
                        ),
                    }
                )

        unused_media_assets = [
            {
                "id": asset.id,
                "title": asset.title,
                "file": asset.file.name,
            }
            for asset in media_assets
            if (
                asset.file
                and asset.file.name
                not in referenced_media_paths
            )
        ]

        page_type_counts = Counter(
            page.page_type
            for page in pages
        )

        report = {
            "summary": {
                "pages_total": len(pages),
                "topics_total": len(topics),
                "media_assets_total": len(media_assets),
                "checked_references": checked_reference_count,
                "duplicate_slugs": len(duplicate_slugs),
                "empty_content_pages": len(
                    empty_content_pages
                ),
                "empty_slug_pages": len(
                    empty_slug_pages
                ),
                "topics_without_grade": len(
                    topics_without_grade
                ),
                "topics_without_subject": len(
                    topics_without_subject
                ),
                "topics_without_section": len(
                    topics_without_section
                ),
                "broken_internal_links": len(
                    broken_internal_links
                ),
                "broken_media_references": len(
                    broken_media_references
                ),
                "broken_static_references": len(broken_static_references),
                "missing_media_assets": len(
                    missing_media_assets
                ),
                "old_wordpress_markers": sum(
                    item["count"]
                    for item in old_marker_details
                ),
                "unused_media_assets": len(
                    unused_media_assets
                ),
            },
            "page_type_counts": dict(
                page_type_counts
            ),
            "duplicate_slugs": duplicate_slugs,
            "empty_content_pages": empty_content_pages,
            "empty_slug_pages": empty_slug_pages,
            "topics_without_grade": topics_without_grade,
            "topics_without_subject": topics_without_subject,
            "topics_without_section": topics_without_section,
            "broken_internal_links": broken_internal_links,
            "broken_media_references": (
                broken_media_references
            ),
            "broken_static_references": (
                broken_static_references
            ),
            "missing_media_assets": missing_media_assets,
            "old_marker_details": old_marker_details,
            "unused_media_assets": unused_media_assets,
        }

        report_path = (
            Path(settings.BASE_DIR)
            / "data"
            / "site_integrity_report.json"
        )

        report_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        report_path.write_text(
            json.dumps(
                report,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        summary = report["summary"]

        self.stdout.write(
            "Проверка целостности MathStart:"
        )
        self.stdout.write(
            f"  Всего материалов: "
            f"{summary['pages_total']}"
        )
        self.stdout.write(
            f"  Учебных тем: "
            f"{summary['topics_total']}"
        )
        self.stdout.write(
            f"  Медиафайлов: "
            f"{summary['media_assets_total']}"
        )
        self.stdout.write(
            f"  Проверено ссылок и ресурсов: "
            f"{summary['checked_references']}"
        )
        self.stdout.write("")
        self.stdout.write(
            f"  Дубликатов slug: "
            f"{summary['duplicate_slugs']}"
        )
        self.stdout.write(
            f"  Пустых материалов: "
            f"{summary['empty_content_pages']}"
        )
        self.stdout.write(
            f"  Тем без класса: "
            f"{summary['topics_without_grade']}"
        )
        self.stdout.write(
            f"  Тем без предмета: "
            f"{summary['topics_without_subject']}"
        )
        self.stdout.write(
            f"  Тем без раздела: "
            f"{summary['topics_without_section']}"
        )
        self.stdout.write(
            f"  Битых внутренних ссылок: "
            f"{summary['broken_internal_links']}"
        )
        self.stdout.write(
            f"  Битых ссылок на медиа: "
            f"{summary['broken_media_references']}"
        )
        self.stdout.write(
            f"  Отсутствующих MediaAsset-файлов: "
            f"{summary['missing_media_assets']}"
        )
        self.stdout.write(
            f"  Остатков WordPress-адресов: "
            f"{summary['old_wordpress_markers']}"
        )
        self.stdout.write(
            f"  Неиспользуемых медиафайлов: "
            f"{summary['unused_media_assets']}"
        )
        self.stdout.write("")
        self.stdout.write(
            f"Полный отчёт: {report_path}"
        )

        critical_error_count = (
            summary["duplicate_slugs"]
            + summary["empty_content_pages"]
            + summary["empty_slug_pages"]
            + summary["topics_without_grade"]
            + summary["topics_without_subject"]
            + summary["topics_without_section"]
            + summary["broken_internal_links"]
            + summary["broken_media_references"]
            + summary["broken_static_references"]
            + summary["missing_media_assets"]
            + summary["old_wordpress_markers"]
        )

        self.stdout.write("")

        if critical_error_count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "Критических проблем целостности "
                    "сайта не обнаружено."
                )
            )
        else:
            raise CommandError("Найдены проблемы. Подробности записаны в JSON-отчёт.")
