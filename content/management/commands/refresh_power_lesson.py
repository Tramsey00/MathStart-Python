"""Refresh only the power-function lesson from its authored source."""
import hashlib
import sqlite3
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from content.lessons.v2.power import PAGE
from content.lessons.v2.layout import render
from content.models import ContentPage
from content.quality import inspect_html


class Command(BaseCommand):
    help='Обновляет только страницу о степенных функциях 2.0.'

    def handle(self,*args,**options):
        from content.services.legacy_publishing import require_unmanaged_database
        require_unmanaged_database()
        body=render(PAGE)
        issues=inspect_html(body)['issues']
        if issues: raise CommandError(str(issues))
        page=ContentPage.objects.get(slug=PAGE['slug'])
        if page.body_html==body:
            self.stdout.write('Страница уже актуальна.')
            return
        old_hash=hashlib.sha256(page.body_html.encode('utf-8')).hexdigest()
        if old_hash!=page.content_checksum:
            raise CommandError('Страница изменена вне исходников; проверьте редакторские правки.')
        backup=Path(settings.BASE_DIR)/'data'/'backup_before_power_style.sqlite3'
        database=settings.DATABASES['default']
        if database['ENGINE'].endswith('sqlite3') and not backup.exists():
            with sqlite3.connect(database['NAME']) as src,sqlite3.connect(backup) as dst:
                src.backup(dst)
        page.body_html=body
        page.content_checksum=hashlib.sha256(body.encode('utf-8')).hexdigest()
        page.save(update_fields=['body_html','content_checksum','updated_at'])
        self.stdout.write(self.style.SUCCESS('Обновлена только страница «Свойства степенных функций и их графики 2.0».'))
