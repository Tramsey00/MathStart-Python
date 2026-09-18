"""Publish the revised natural-number lesson beside its original edition."""
import sqlite3
from pathlib import Path

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from content.lessons.v2.natural import PAGE
from content.lessons.v2.layout import render
from content.management.commands.add_grade10_v2 import SOURCE, checksum, course_html
from content.models import ContentPage
from content.quality import inspect_html


def navigation(body):
    soup = BeautifulSoup(body, 'html.parser')
    original = soup.select_one('#deistvitelnye-chisla .ms-topic[href="/10-klass-naturalnye-chisla-povtorenie/"]')
    if original is None:
        raise CommandError('В программе не найдена тема 1.1 о натуральных числах.')
    link = soup.select_one(f'.ms-topic[href="/{PAGE["slug"]}/"]')
    if link is None:
        link = BeautifulSoup(f'<a class="ms-topic" href="/{PAGE["slug"]}/"><span class="ms-topic-number">1.1</span><span class="ms-topic-name">{PAGE["title"]} 2.0</span></a>', 'html.parser').a
    original.insert_after(link.extract())
    start = soup.select_one('.ms-hero-actions a[href="/10-klass-naturalnye-chisla-povtorenie/"]')
    if start:
        start['href'] = f'/{PAGE["slug"]}/'
    return course_html(str(soup))


class Command(BaseCommand):
    help = 'Добавляет натуральные числа 2.0 и ссылку в разделе 1, сохраняя прежний урок.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        from content.services.legacy_publishing import require_unmanaged_database
        require_unmanaged_database()
        original = ContentPage.objects.get(slug='10-klass-naturalnye-chisla-povtorenie')
        course = ContentPage.objects.get(slug='10-klass-algebra')
        current = ContentPage.objects.filter(slug=PAGE['slug']).first()
        for existing in [course, current]:
            if existing and checksum(existing.body_html) != existing.content_checksum:
                raise CommandError('Обнаружены редакторские правки: ' + existing.slug)
        body, nav = render(PAGE), navigation(course.body_html)
        for html in [body, nav]:
            issues = inspect_html(html)['issues']
            if issues:
                raise CommandError(str(issues))
        if options['dry_run']:
            self.stdout.write('Проверены новый урок и ссылка в разделе 1. База не изменена.')
            return
        if current and current.body_html == body and course.body_html == nav:
            self.stdout.write('Урок и программа уже актуальны.')
            return
        database = settings.DATABASES['default']
        backup = Path(settings.BASE_DIR) / 'data' / 'backup_before_natural_v2.sqlite3'
        if database['ENGINE'].endswith('sqlite3') and not backup.exists():
            with sqlite3.connect(database['NAME']) as src, sqlite3.connect(backup) as dst:
                src.backup(dst)
        with transaction.atomic():
            if current is None or current.body_html != body:
                ContentPage.objects.update_or_create(slug=PAGE['slug'], defaults={
                    'title': PAGE['title'] + ' 2.0', 'page_type': 'topic',
                    'grade': original.grade, 'subject': original.subject,
                    'section': original.section, 'order': original.order,
                    'body_html': body, 'is_published': True,
                    'source_file': SOURCE, 'content_checksum': checksum(body),
                })
            if course.body_html != nav:
                course.body_html = nav
                course.content_checksum = checksum(nav)
                course.save(update_fields=['body_html', 'content_checksum', 'updated_at'])
        self.stdout.write(self.style.SUCCESS('Добавлена тема «Натуральные числа. Повторение 2.0». Прежний урок сохранён.'))
