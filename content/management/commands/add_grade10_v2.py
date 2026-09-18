"""Publish two independent second editions and link them from the course."""
import hashlib
import sqlite3
from pathlib import Path

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from content.lessons.v2.circle import PAGE as CIRCLE
from content.lessons.v2.power import PAGE as POWER
from content.lessons.v2.layout import render
from content.models import ContentPage, Section, Subject
from content.quality import inspect_html

SOURCE = 'content/lessons/v2/'
TRIG_SLUG = 'sinus-kosinus-tangens-kotangens'
TRIG_TITLE = 'Синус и косинус. Тангенс и котангенс. Свойства и графики тригонометрических функций'


def checksum(body):
    return hashlib.sha256(body.encode('utf-8')).hexdigest()


def course_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    def topic(page, number):
        return BeautifulSoup(f'<a class="ms-topic" href="/{page["slug"]}/"><span class="ms-topic-number">{number}</span><span class="ms-topic-name">{page["title"]} 2.0</span></a>', 'html.parser').a

    if not soup.find('a', href=f'/{POWER["slug"]}/'):
        previous = soup.find('a', href='/10-klass-stepennye-funkcii-i-grafiki/')
        if previous is None:
            raise CommandError('Не найдена прежняя тема о степенных функциях в программе.')
        previous.insert_after(topic(POWER, '2.6'))
    if not soup.find('a', href=f'/{CIRCLE["slug"]}/'):
        section = soup.find(id=TRIG_SLUG)
        if section is None:
            section = BeautifulSoup(f'<details class="ms-accordion" id="{TRIG_SLUG}"><summary><span class="ms-accordion-left"><span class="ms-section-icon">4</span><span class="ms-accordion-main"><span class="ms-accordion-title">4. {TRIG_TITLE}</span><span class="ms-accordion-subtitle">Числовая окружность: радианы, координаты и полные обороты.</span></span></span><span class="ms-acc-arrow" aria-hidden="true"></span></summary><div class="ms-topic-list"></div></details>', 'html.parser').details
            soup.select_one('.ms-program').append(section)
        section.select_one('.ms-topic-list').append(topic(CIRCLE, '4.1'))
    soup.select_one('.ms-subtitle').string = 'Действительные числа, корни, степени и числовая окружность. Повторите числовые множества, научитесь преобразовывать выражения, исследовать графики и находить координаты точек на окружности.'
    soup.select_one('.ms-section .ms-text').string = 'В уроках есть теория, разборы примеров и самостоятельные задания с решениями. Для степенных функций и числовой окружности доступны подробные версии 2.0 с интерактивными рисунками.'
    topic_count = len(soup.select('.ms-topic-list .ms-topic'))
    task_count = 72 + (topic_count - 9) * 12
    for item, number, label in zip(soup.select('.ms-stat'), ['3', str(topic_count), str(task_count)], ['учебных раздела', 'учебных страниц, включая версии 2.0', 'заданий с подробными решениями']):
        item.select_one('.ms-stat-number').string = number
        item.select_one('.ms-stat-text').string = label
    return str(soup)


class Command(BaseCommand):
    help = 'Добавляет версии 2.0 тем о степенных функциях и числовой окружности; прежние уроки сохраняются.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        from content.services.legacy_publishing import require_unmanaged_database
        require_unmanaged_database()
        subject = Subject.objects.get(grade__slug='10-klass', slug='algebra')
        course = ContentPage.objects.get(slug='10-klass-algebra')
        records = []
        for lesson in (POWER, CIRCLE):
            body = render(lesson)
            issues = inspect_html(body)['issues']
            if issues:
                raise CommandError(f'{lesson["slug"]}: {issues}')
            previous = ContentPage.objects.filter(slug=lesson['slug']).first()
            if previous and (previous.source_file != SOURCE or checksum(previous.body_html) != previous.content_checksum):
                raise CommandError('Содержимое изменено вручную: '+previous.slug)
            records.append((lesson, body))
        navigation = course_html(course.body_html)
        if inspect_html(navigation)['issues']:
            raise CommandError('Ошибка структуры страницы курса.')
        if options['dry_run']:
            self.stdout.write('Проверены две новые версии и ссылки в программе курса.')
            return
        database = settings.DATABASES['default']
        backup = Path(settings.BASE_DIR)/'data'/'backup_before_lessons_v2.sqlite3'
        if database['ENGINE'].endswith('sqlite3') and not backup.exists():
            with sqlite3.connect(database['NAME']) as src, sqlite3.connect(backup) as dst:
                src.backup(dst)
        with transaction.atomic():
            roots = Section.objects.get(subject=subject, slug='stepeni-korni-stepennye-funkcii')
            trig, _ = Section.objects.get_or_create(subject=subject, slug=TRIG_SLUG, defaults={'title':TRIG_TITLE, 'order':4})
            for lesson, body in records:
                ContentPage.objects.update_or_create(slug=lesson['slug'], defaults={
                    'title':lesson['title']+' 2.0', 'page_type':'topic', 'grade':subject.grade,
                    'subject':subject, 'section':roots if lesson is POWER else trig,
                    'order':7 if lesson is POWER else 1, 'body_html':body, 'is_published':True,
                    'source_file':SOURCE, 'content_checksum':checksum(body)})
            course.body_html = navigation
            course.content_checksum = checksum(navigation)
            course.source_file = SOURCE
            course.save(update_fields=['body_html','content_checksum','source_file','updated_at'])
            for page in ContentPage.objects.filter(slug__in=['glavnaya','materialy','o-proekte']):
                body = page.body_html.replace('Алгебра · Первые два раздела', 'Алгебра · Числа, функции и окружность').replace('Действительные числа, корни, степени с рациональным показателем и степенные функции.', 'Действительные числа, корни, степенные функции и числовая окружность.').replace('первые два раздела алгебры: действительные числа, корни и степени', 'темы алгебры: действительные числа, корни, степени и числовая окружность')
                if body != page.body_html:
                    page.body_html, page.content_checksum = body, checksum(body)
                    page.save(update_fields=['body_html','content_checksum','updated_at'])
        self.stdout.write(self.style.SUCCESS('Добавлены две версии 2.0. Прежние учебные страницы сохранены.'))
