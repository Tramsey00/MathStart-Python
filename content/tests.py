import io
import json
from pathlib import Path

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase

from .models import ContentPage, Grade, Section, Subject
from .quality import inspect_html


def reviewed_pages():
    path = Path(settings.BASE_DIR) / 'data' / 'reviewed_content.json'
    return {r['slug']: r for r in json.loads(path.read_text(encoding='utf-8'))}


class LessonGeometryTests(SimpleTestCase):
    def soup(self, slug):
        return BeautifulSoup(reviewed_pages()[slug]['body_html'], 'html.parser')

    def test_corrected_straight_lines_pass_through_all_labelled_points(self):
        cases = [
            ('linejnoe-uravnenie-ax-by-c-0-grafik-linejnogo-uravneniya', 0, '#2563eb', [(460,160),(515,270),(570,380)]),
            ('linejnoe-uravnenie-ax-by-c-0-grafik-linejnogo-uravneniya', 3, '#2563eb', [(410,180),(470,240),(530,300)]),
            ('linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii', 2, '#2563eb', [(410,210),(530,330)]),
            ('linejnaya-funkcziya-y-kx-eyo-svojstva', 3, '#15803d', [(345,305),(465,245)]),
            ('linejnaya-funkcziya-y-kx-eyo-svojstva', 4, '#2563eb', [(410,270),(530,450)]),
        ]
        for slug, index, color, points in cases:
            with self.subTest(page=slug, svg=index):
                svg = self.soup(slug).select('svg')[index]
                line = svg.find('line', stroke=color)
                x1,y1,x2,y2 = [float(line[a]) for a in ('x1','y1','x2','y2')]
                for x,y in points:
                    self.assertAlmostEqual((x-x1)*(y2-y1)-(y-y1)*(x2-x1), 0, places=4)

    def test_nets_have_compatible_shared_edges_and_opposite_faces(self):
        soup = self.soup('pryamougolnyj-parallelepiped-razvyortka')
        for index, svg in enumerate(soup.select('svg')):
            with self.subTest(svg=index):
                faces = [tuple(float(e[k]) for k in ('x','y','width','height'))
                         for e in svg.select('[data-net-face]')]
                self.assertEqual(len(faces), 6)
                left,front,right,back,top,bottom = faces
                self.assertEqual(left[2:], right[2:])
                self.assertEqual(front[2:], back[2:])
                self.assertEqual(top[2:], bottom[2:])
                self.assertEqual(top[2:], (front[2],left[2]))
                for a,b in zip(faces[:3], faces[1:4]):
                    self.assertEqual(a[0]+a[2], b[0])
                    self.assertEqual(a[1], b[1])
                    self.assertEqual(a[3], b[3])
                self.assertEqual(top[1]+top[3], front[1])
                self.assertEqual(bottom[1], front[1]+front[3])

    def test_chord_endpoints_are_on_circle(self):
        svg = self.soup('geometricheskie-ponyatiya-okruzhnost-i-krug').select('svg')[3]
        chord = next(e for e in svg.select('line') if e.get('x1') == '313.6932')
        for suffix in ('1','2'):
            x,y = float(chord['x'+suffix]),float(chord['y'+suffix])
            self.assertAlmostEqual(((x-410)**2+(y-295)**2)**0.5, 150, places=3)

    def test_parameter_answer_includes_nonpositive_values(self):
        soup = self.soup('reshenie-raczionalnogo-uravneniya-svodyashhegosya-k-kvadratnomu')
        self.assertIn('m ∈ (−∞; 0] ∪ {9}', soup.get_text())
        for m, positive_count in [(-7,1),(0,1),(5,2),(9,1),(10,0)]:
            discriminant = 36-4*m
            roots = set() if discriminant < 0 else {(6-discriminant**0.5)/2,(6+discriminant**0.5)/2}
            self.assertEqual(sum(root > 0 for root in roots), positive_count)


class ContentQualityTests(SimpleTestCase):
    def test_detects_visible_instructions_and_shortcodes_but_ignores_comments(self):
        self.assertTrue(inspect_html('<p>Далее здесь можно изменить html-код</p>')['issues'])
        self.assertTrue(inspect_html('<p>[contact-form-7 id="x"]</p>')['issues'])
        self.assertFalse(inspect_html('<!-- edit HTML --><script>// TODO</script><p>Найдите x.</p>')['issues'])

    def test_detects_invalid_svg_reference_and_duplicate_ids(self):
        result = inspect_html('<svg viewBox="0 0 10 10"><path id="a" fill="url(#missing)"/><path id="a"/></svg>')
        self.assertEqual({i['kind'] for i in result['issues']}, {'duplicate_id','missing_svg_reference'})


class CatalogueTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        grade = Grade.objects.create(title='5 класс', slug='5', order=5)
        subject = Subject.objects.create(title='Математика', slug='math', grade=grade)
        section = Section.objects.create(title='Дроби', slug='fractions', subject=subject)
        ContentPage.objects.create(title='Карта сайта', slug='karta-sajta', page_type='static')
        ContentPage.objects.create(title='Дроби', slug='fractions', grade=grade, subject=subject, section=section)
        ContentPage.objects.create(title='Черновик', slug='draft', is_published=False)

    def test_catalogue_lists_published_lessons_with_working_links(self):
        response = self.client.get('/karta-sajta/')
        self.assertContains(response, 'href="/fractions/"')
        self.assertContains(response, '5 класс')
        self.assertNotContains(response, '/draft/')


class RepairCommandTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for record in reviewed_pages().values():
            ContentPage.objects.create(title=record['slug'], slug=record['slug'], body_html=record['body_html'])

    def test_second_run_does_not_change_already_reviewed_pages(self):
        output = io.StringIO()
        call_command('apply_content_repairs', stdout=output)
        self.assertIn('Страниц к обновлению: 0', output.getvalue())

    def test_refuses_to_overwrite_subsequent_editor_changes(self):
        page = ContentPage.objects.get(slug='kontakty')
        page.body_html = '<p>Новая редакция</p>'
        page.save()
        with self.assertRaises(CommandError):
            call_command('apply_content_repairs', stdout=io.StringIO())
        page.refresh_from_db()
        self.assertEqual(page.body_html, '<p>Новая редакция</p>')
