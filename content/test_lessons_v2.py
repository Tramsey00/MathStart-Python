import io
import math
from bs4 import BeautifulSoup
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase

from content.lessons.v2.power import PAGE as POWER
from content.lessons.v2.circle import PAGE as CIRCLE
from content.lessons.v2.natural import PAGE as NATURAL
from content.lessons.v2.rational import PAGE as RATIONAL
from content.lessons.v2.layout import render
from content.models import ContentPage
from content.quality import inspect_html


class LessonV2ContentTests(SimpleTestCase):
    def test_revised_pages_have_no_external_site_promotions(self):
        for lesson in [POWER,NATURAL,RATIONAL]:
            soup=BeautifulSoup(render(lesson),'html.parser')
            self.assertFalse(soup.select('a[href^="http"],a[href^="//"]'))
            for hidden in soup.select('style,script'):
                hidden.decompose()
            for name in ['ЯКласс','Math100','Сдам ГИА','СдамГиа']:
                self.assertNotIn(name,soup.get_text())

    def test_readable_math_complete_answers_and_valid_navigation(self):
        for lesson in [POWER,CIRCLE,NATURAL,RATIONAL]:
            with self.subTest(lesson=lesson['slug']):
                body=render(lesson)
                self.assertEqual(inspect_html(body)['issues'],[])
                soup=BeautifulSoup(body,'html.parser')
                self.assertEqual(len(soup.select('.v2-answer > div')),12)
                self.assertTrue(all(answer.get_text(strip=True) for answer in soup.select('.v2-answer > div')))
                for hidden in soup.select('style, script'):
                    hidden.decompose()
                self.assertNotIn('/',soup.get_text())
                self.assertNotIn('Далее здесь',soup.get_text())

    def test_circle_model_points_match_their_angle_labels(self):
        soup=BeautifulSoup(render(CIRCLE),'html.parser')
        for svg,count in zip(soup.select('#models svg'),[8,12]):
            points=svg.select('[data-angle-step]')
            self.assertEqual(len(points),count)
            for point in points:
                angle=int(point['data-angle-step'])*math.pi/12
                self.assertAlmostEqual((float(point['cx'])-210)/139,math.cos(angle),places=4)
                self.assertAlmostEqual((210-float(point['cy']))/139,math.sin(angle),places=4)


class LessonV2PublishingTests(TestCase):
    def test_rational_revision_preserves_lessons_and_course_entries(self):
        call_command('add_grade10_algebra',stdout=io.StringIO())
        call_command('add_grade10_v2',stdout=io.StringIO())
        call_command('add_natural_v2',stdout=io.StringIO())
        before=list(ContentPage.objects.order_by('pk').values())
        call_command('add_rational_v2',dry_run=True,stdout=io.StringIO())
        self.assertEqual(before,list(ContentPage.objects.order_by('pk').values()))
        call_command('add_rational_v2',stdout=io.StringIO())
        for record in before:
            if record['slug']!='10-klass-algebra':
                self.assertEqual(record,ContentPage.objects.filter(pk=record['id']).values().get())
        after=list(ContentPage.objects.order_by('pk').values())
        call_command('add_rational_v2',stdout=io.StringIO())
        self.assertEqual(after,list(ContentPage.objects.order_by('pk').values()))
        page=ContentPage.objects.get(slug=RATIONAL['slug'])
        self.assertEqual(page.body_html,render(RATIONAL))
        self.assertEqual(page.section.slug,'deistvitelnye-chisla')
        self.assertEqual(self.client.get(page.get_absolute_url(),HTTP_HOST='localhost').status_code,200)
        course=BeautifulSoup(ContentPage.objects.get(slug='10-klass-algebra').body_html,'html.parser')
        self.assertEqual(len(course.select(f'#deistvitelnye-chisla a[href="/{page.slug}/"]')),1)
        self.assertEqual([e.get_text() for e in course.select('.ms-stat-number')],['3','13','120'])

    def test_natural_revision_preserves_existing_lessons_and_links_once(self):
        call_command('add_grade10_algebra',stdout=io.StringIO())
        call_command('add_grade10_v2',stdout=io.StringIO())
        before=list(ContentPage.objects.order_by('pk').values())
        call_command('add_natural_v2',dry_run=True,stdout=io.StringIO())
        self.assertEqual(before,list(ContentPage.objects.order_by('pk').values()))
        call_command('add_natural_v2',stdout=io.StringIO())
        for record in before:
            if record['slug']!='10-klass-algebra':
                self.assertEqual(record,ContentPage.objects.filter(pk=record['id']).values().get())
        after=list(ContentPage.objects.order_by('pk').values())
        call_command('add_natural_v2',stdout=io.StringIO())
        self.assertEqual(after,list(ContentPage.objects.order_by('pk').values()))
        page=ContentPage.objects.get(slug=NATURAL['slug'])
        self.assertEqual(page.section.slug,'deistvitelnye-chisla')
        self.assertEqual(page.body_html,render(NATURAL))
        self.assertEqual(self.client.get(page.get_absolute_url(),HTTP_HOST='localhost').status_code,200)
        course=BeautifulSoup(ContentPage.objects.get(slug='10-klass-algebra').body_html,'html.parser')
        self.assertEqual(len(course.select(f'#deistvitelnye-chisla a[href="/{page.slug}/"]')),1)
        self.assertEqual([e.get_text() for e in course.select('.ms-stat-number')],['3','12','108'])

    def test_targeted_refresh_keeps_every_other_page_unchanged(self):
        import hashlib
        call_command('add_grade10_algebra',stdout=io.StringIO())
        call_command('add_grade10_v2',stdout=io.StringIO())
        page=ContentPage.objects.get(slug=POWER['slug'])
        page.body_html='<p>Предыдущее оформление</p>'
        page.content_checksum=hashlib.sha256(page.body_html.encode('utf-8')).hexdigest()
        page.save()
        others=ContentPage.objects.exclude(pk=page.pk).order_by('pk')
        before=list(others.values())
        call_command('refresh_power_lesson',stdout=io.StringIO())
        self.assertEqual(before,list(others.values()))
        page.refresh_from_db()
        self.assertEqual(page.body_html,render(POWER))

    def test_additions_preserve_old_lessons_and_link_from_their_sections(self):
        call_command('add_grade10_algebra',stdout=io.StringIO())
        old=list(ContentPage.objects.filter(page_type='topic').values_list('slug','body_html'))
        call_command('add_grade10_v2',stdout=io.StringIO())
        call_command('add_grade10_v2',stdout=io.StringIO())
        for slug,body in old:
            self.assertEqual(ContentPage.objects.get(slug=slug).body_html,body)
        self.assertEqual(ContentPage.objects.count(),12)
        course=BeautifulSoup(ContentPage.objects.get(slug='10-klass-algebra').body_html,'html.parser')
        for lesson,section in [(POWER,'stepeni-korni-stepennye-funkcii'),(CIRCLE,'sinus-kosinus-tangens-kotangens')]:
            page=ContentPage.objects.get(slug=lesson['slug'])
            self.assertEqual(page.section.slug,section)
            self.assertEqual(page.title,lesson['title']+' 2.0')
            self.assertEqual(len(course.select(f'#{section} a[href="/{page.slug}/"]')),1)
            self.assertEqual(self.client.get(page.get_absolute_url(),HTTP_HOST='localhost').status_code,200)
