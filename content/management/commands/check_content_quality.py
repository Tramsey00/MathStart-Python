import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.test import Client, override_settings

from content.models import ContentPage
from content.quality import inspect_html


class Command(BaseCommand):
    help = 'Проверяет опубликованные страницы: ответы, заглушки, SVG, идентификаторы и якоря.'

    def handle(self, *args, **options):
        pages = ContentPage.objects.filter(is_published=True)
        report = {'pages_checked': 0, 'svg_checked': 0, 'issues': []}
        client = Client(HTTP_HOST='localhost')
        with override_settings(ALLOWED_HOSTS=['localhost'], SECURE_SSL_REDIRECT=False):
            for page in pages:
                response = client.get(page.get_absolute_url())
                report['pages_checked'] += 1
                if response.status_code != 200:
                    report['issues'].append({'page': page.slug, 'kind': 'http_status', 'detail': response.status_code})
                    continue
                result = inspect_html(response.content.decode('utf-8'))
                report['svg_checked'] += result['svg_count']
                report['issues'].extend({'page': page.slug, **issue} for issue in result['issues'])
        report_dir = Path(settings.BASE_DIR) / "var" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)

        path = report_dir / "content_quality_report.json"

        path.write_text(
            json.dumps(
                report,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        self.stdout.write(
            f"Проверено страниц: {report['pages_checked']}; "
            f"SVG: {report['svg_checked']}; "
            f"проблем: {len(report['issues'])}."
        )

        if report["issues"]:
            raise CommandError(
                "Подробности: " + str(path)
            )
