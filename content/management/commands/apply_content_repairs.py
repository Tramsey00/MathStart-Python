"""Apply the reviewed September 2026 lessons without overwriting later edits."""
import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from content.models import ContentPage


def checksum(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


class Command(BaseCommand):
    help = 'Применяет проверенные правки учебных материалов с проверкой исходной версии.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Проверить правки без записи.')

    def handle(self, *args, **options):
        from content.services.legacy_publishing import require_unmanaged_database
        require_unmanaged_database()
        path = Path(settings.BASE_DIR) / 'data' / 'reviewed_content.json'
        records = json.loads(path.read_text(encoding='utf-8'))
        pending = []
        conflicts = []
        for record in records:
            try:
                page = ContentPage.objects.get(slug=record['slug'])
            except ContentPage.DoesNotExist:
                conflicts.append(record['slug'] + ': страница не найдена')
                continue
            current = checksum(page.body_html)
            if checksum(record['body_html']) != record['after_sha256']:
                raise CommandError('Повреждён файл правок: ' + record['slug'])
            if current == record['after_sha256']:
                continue
            if current != record['before_sha256']:
                conflicts.append(record['slug'] + ': содержимое изменено после аудита')
                continue
            pending.append((page, record))
        if conflicts:
            raise CommandError('Правки не применены. Проверьте конфликты:\n' + '\n'.join(conflicts))
        if options['dry_run'] or not pending:
            self.stdout.write(f'Страниц к обновлению: {len(pending)}. Конфликтов нет.')
            return

        database = settings.DATABASES['default']
        if database['ENGINE'] == 'django.db.backends.sqlite3' and Path(database['NAME']).is_file():
            backup = Path(settings.BASE_DIR) / 'data' / ('backup_content_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.sqlite3')
            with sqlite3.connect(database['NAME']) as source, sqlite3.connect(backup) as target:
                source.backup(target)
            self.stdout.write('Резервная копия: ' + str(backup))
        with transaction.atomic():
            for page, record in pending:
                # Re-check inside the transaction in case an editor saved a page.
                page.refresh_from_db()
                if checksum(page.body_html) != record['before_sha256']:
                    raise CommandError('Страница изменилась во время применения: ' + page.slug)
                page.body_html = record['body_html']
                page.content_checksum = record['after_sha256']
                page.save(update_fields=['body_html', 'content_checksum', 'updated_at'])
        self.stdout.write(self.style.SUCCESS(f'Обновлено страниц: {len(pending)}.'))
