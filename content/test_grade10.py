import io
import re
from fractions import Fraction

from bs4 import BeautifulSoup
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase

from content.lessons.grade10 import get_lessons
from content.lessons.grade10.layout import SECTIONS, render_lesson
from content.models import ContentPage, Grade, Section, Subject
from content.quality import inspect_html


class Grade10ContentTests(SimpleTestCase):
    def test_complete_curriculum_and_self_checks(self):
        lessons = get_lessons()
        self.assertEqual([(p['section'], p['order']) for p in lessons],
                         [(1,1),(1,2),(1,3),(2,1),(2,2),(2,3),(2,4),(2,5),(2,6)])
        self.assertEqual(len({p['slug'] for p in lessons}), 9)
        for lesson in lessons:
            with self.subTest(title=lesson['title']):
                body = render_lesson(lesson)
                self.assertEqual(inspect_html(body)['issues'], [])
                soup = BeautifulSoup(body, 'html.parser')
                self.assertEqual(soup.h1.get_text(), lesson['title'])
                self.assertEqual(len(soup.select('.ms-task')), 8)
                self.assertEqual(len(soup.select('.ms-answer > div')), 8)
                self.assertGreaterEqual(len(soup.select('.ms-example')), 7)

    def test_root_plot_points_satisfy_their_equations(self):
        lesson = get_lessons()[4]
        soup = BeautifulSoup(render_lesson(lesson), 'html.parser')
        for svg_index, box in [(0,(0,16,0,4)), (1,(-8,8,-2,2)), (2,(0,8,0,4))]:
            xmin,xmax,ymin,ymax = box
            for path in soup.select('svg')[svg_index].select('path[data-function]'):
                label = path['data-function']
                for px,py in re.findall(r'[ML]([\d.]+),([\d.]+)', path['d']):
                    x = xmin+(float(px)-66)/440*(xmax-xmin)
                    y = ymax-(float(py)-35)/440*(ymax-ymin)
                    if label == 'y = √(x − 2) + 1':
                        self.assertAlmostEqual((y-1)**2,x-2,delta=0.001)
                    else:
                        n = 4 if '⁴' in label else 3 if '∛' in label else 2
                        self.assertAlmostEqual(y**n,x,delta=0.001)

    def test_reciprocal_branches_never_cross_the_missing_zero(self):
        soup = BeautifulSoup(render_lesson(get_lessons()[-1]),'html.parser')
        paths = soup.select('svg')[1].select('path[data-function]')
        self.assertEqual(len(paths),4)
        for path in paths:
            xvalues = [(float(x)-66)/440*8-4 for x,y in re.findall(r'[ML]([\d.]+),([\d.]+)',path['d'])]
            self.assertTrue(all(x<0 for x in xvalues) or all(x>0 for x in xvalues))

    def test_periodic_fraction_and_rounding_examples(self):
        # Independent exact arithmetic checks on error-prone worked examples.
        self.assertEqual(Fraction(27,99),Fraction(3,11))
        self.assertEqual(Fraction(25,90),Fraction(5,18))
        self.assertEqual((Fraction(-2,3)+Fraction(5,6))/2,Fraction(1,12))
        self.assertLess(Fraction(2645,1000)**2,7)
        self.assertGreater(Fraction(1735,1000)**2,3)


class Grade10PublishingTests(TestCase):
    def publish(self, **kwargs):
        call_command('add_grade10_algebra',stdout=io.StringIO(),**kwargs)

    def test_dry_run_and_repeat_are_safe(self):
        self.publish(dry_run=True)
        self.assertEqual(Grade.objects.count(),0)
        self.publish()
        self.assertEqual(ContentPage.objects.count(),10)
        self.assertEqual(Subject.objects.count(),1)
        self.assertEqual(list(Section.objects.values_list('title',flat=True)),[s[1] for s in SECTIONS])
        before = list(ContentPage.objects.values_list('id','updated_at','body_html'))
        self.publish()
        self.assertEqual(before,list(ContentPage.objects.values_list('id','updated_at','body_html')))
        for page in ContentPage.objects.all():
            response = self.client.get(page.get_absolute_url(),HTTP_HOST='localhost')
            self.assertEqual(response.status_code,200)

    def test_manual_edits_are_not_overwritten(self):
        self.publish()
        page = ContentPage.objects.get(slug=get_lessons()[0]['slug'])
        page.body_html += '<p>Дополнительный пример редактора.</p>'
        page.save()
        with self.assertRaises(CommandError):
            self.publish()
        page.refresh_from_db()
        self.assertIn('Дополнительный пример редактора.',page.body_html)

    def test_existing_navigation_and_lesson_chain(self):
        from content.tests import reviewed_pages
        for slug in ['glavnaya','materialy','o-proekte']:
            record = reviewed_pages()[slug]
            ContentPage.objects.create(slug=slug,title=slug,body_html=record['body_html'],
                                       page_type='home' if slug=='glavnaya' else 'static')
        self.publish()
        self.publish()
        home = BeautifulSoup(ContentPage.objects.get(slug='glavnaya').body_html,'html.parser')
        self.assertEqual(len(home.select('#class-10')),1)
        self.assertIsNotNone(home.select_one('#class-9'))
        lessons = get_lessons()
        for i, lesson in enumerate(lessons):
            page = ContentPage.objects.get(slug=lesson['slug'])
            soup = BeautifulSoup(page.body_html,'html.parser')
            links = [a['href'] for a in soup.select('.ms-nav a')]
            if i:
                self.assertIn('/'+lessons[i-1]['slug']+'/',links)
            if i<len(lessons)-1:
                self.assertIn('/'+lessons[i+1]['slug']+'/',links)
        self.assertNotIn('В помощь учителю',ContentPage.objects.get(slug='10-klass-algebra').body_html)
