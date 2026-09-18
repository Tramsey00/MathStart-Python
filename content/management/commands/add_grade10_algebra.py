"""Publish the authored grade 10 lessons without replacing subsequent edits."""
import hashlib
import re
import sqlite3
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from content.lessons.grade10 import get_lessons
from content.lessons.grade10.layout import COURSE_SLUG, SECTIONS, render_course, render_lesson
from content.models import ContentPage, Grade, Section, Subject
from content.quality import inspect_html

SOURCE = 'content/lessons/grade10/'


def checksum(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def navigation_html(page):
    html = page.body_html
    if page.slug in ('glavnaya', 'materialy', 'o-proekte'):
        html = html.replace('5–9', '5–10')
    if page.page_type == ContentPage.PageType.HOME and 'id="class-10"' not in html:
        # Insert inside the existing class picker, following class 9.
        match = re.search(r'<details\b[^>]*id="class-9".*?</details>', html, re.S)
        if not match:
            raise CommandError('На главной странице не найден блок 9 класса; проверьте навигацию.')
        block = '''
<details class="ms-accordion" id="class-10"><summary><span><span class="ms-accordion-title">10 класс</span><span class="ms-accordion-subtitle">Алгебра · Первые два раздела</span></span><span class="ms-accordion-arrow" aria-hidden="true">›</span></summary><div class="ms-subjects"><a class="ms-subject-btn" href="/10-klass-algebra/"><span class="ms-subject-name">Алгебра</span><span class="ms-subject-note">Действительные числа, корни, степени с рациональным показателем и степенные функции.</span></a></div></details>'''
        html = html[:match.end()] + block + html[match.end():]
    if page.slug in ('materialy', 'o-proekte') and '/10-klass-algebra/' not in html:
        intro = re.search(r'<p\b[^>]*class="ms-subtitle"[^>]*>.*?</p>', html, re.S)
        if not intro:
            intro = re.search(r'<p\b[^>]*>.*?</p>', html, re.S)
        if intro:
            block = '<p class="ms-text">Для 10 класса доступны <a href="/10-klass-algebra/">первые два раздела алгебры: действительные числа, корни и степени</a>.</p>'
            html = html[:intro.end()] + block + html[intro.end():]
    return html


class Command(BaseCommand):
    help = 'Добавляет два первых раздела алгебры 10 класса, девять тем и навигацию.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Проверить без изменения базы.')

    def handle(self, *args, **options):
        from content.services.legacy_publishing import require_unmanaged_database
        require_unmanaged_database()
        lessons = get_lessons()
        records = [dict(slug=COURSE_SLUG, title='Алгебра 10 класс', body_html=render_course(lessons),
                        page_type='subject', order=0, section=None)]
        for i, lesson in enumerate(lessons):
            records.append(dict(slug=lesson['slug'], title=lesson['title'], page_type='topic',
                                section=lesson['section'], order=lesson['order'],
                                body_html=render_lesson(lesson, lessons[i-1] if i else None,
                                                        lessons[i+1] if i+1 < len(lessons) else None)))
        planned = []
        for record in records:
            issues = inspect_html(record['body_html'])['issues']
            if issues:
                raise CommandError(f'Ошибка содержимого {record["slug"]}: {issues}')
            page = ContentPage.objects.filter(slug=record['slug']).first()
            if page:
                if page.source_file != SOURCE or checksum(page.body_html) != page.content_checksum:
                    raise CommandError(f'Страница {page.slug} изменена вручную или принадлежит другому источнику. Ничего не записано.')
                if (page.body_html == record['body_html'] and page.title == record['title']
                        and page.order == record['order'] and page.is_published):
                    continue
            planned.append((page, record))
        nav_updates = []
        for page in ContentPage.objects.filter(slug__in=['glavnaya', 'materialy', 'o-proekte']):
            html = navigation_html(page)
            if html != page.body_html:
                nav_updates.append((page, page.body_html, html))
        self.stdout.write(f'Учебных страниц к записи: {len(planned)}; страниц навигации: {len(nav_updates)}.')
        if options['dry_run'] or not (planned or nav_updates):
            return
        database = settings.DATABASES['default']
        if database['ENGINE'] == 'django.db.backends.sqlite3' and Path(database['NAME']).is_file():
            backup = Path(settings.BASE_DIR)/'data'/('backup_grade10_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.sqlite3')
            with sqlite3.connect(database['NAME']) as src, sqlite3.connect(backup) as dst:
                src.backup(dst)
            self.stdout.write('Резервная копия: '+str(backup))
        with transaction.atomic():
            grade, _ = Grade.objects.get_or_create(slug='10-klass', defaults={'title':'10 класс', 'order':10})
            subject, _ = Subject.objects.get_or_create(grade=grade, slug='algebra', defaults={'title':'Алгебра', 'order':1})
            sections = {}
            for i, (slug, title, description) in enumerate(SECTIONS, 1):
                sections[i], _ = Section.objects.get_or_create(subject=subject, slug=slug,
                    defaults={'title':title, 'order':i, 'description':description})
            for page, record in planned:
                if page:
                    old_body = page.body_html
                    page.refresh_from_db()
                    if page.body_html != old_body:
                        raise CommandError('Страница изменилась во время записи: '+page.slug)
                else:
                    page = ContentPage(slug=record['slug'])
                for field in ('title','body_html','page_type','order'):
                    setattr(page, field, record[field])
                page.grade, page.subject = grade, subject
                page.section = sections.get(record['section'])
                page.source_file = SOURCE
                page.content_checksum = checksum(page.body_html)
                page.is_published = True
                page.save()
            for page, old_body, html in nav_updates:
                page.refresh_from_db()
                if page.body_html != old_body:
                    raise CommandError('Навигация изменилась во время записи: '+page.slug)
                page.body_html, page.content_checksum = html, checksum(html)
                page.save(update_fields=['body_html','content_checksum','updated_at'])
        self.stdout.write(self.style.SUCCESS('Алгебра 10 класса добавлена: два раздела, девять тем.'))
