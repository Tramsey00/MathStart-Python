"""Build the reviewed content patch from the untouched SQLite snapshot.

The generated manifest is applied by manage.py apply_content_repairs. This
authoring script never writes to the live database.
"""
import hashlib
import json
import re
import sqlite3
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'data' / 'backup_before_content_review.sqlite3'
OUTPUT = ROOT / 'data' / 'reviewed_content.json'


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def fragment(value):
    return BeautifulSoup(value, 'html.parser')


def replace_text(soup, old, new):
    """Replace a reviewed text passage, allowing source indentation."""
    pattern = re.compile(r'\s+'.join(map(re.escape, old.split())))
    found = 0
    for node in list(soup.find_all(string=pattern)):
        if node.parent.name in {'style', 'script'}:
            continue
        value, count = pattern.subn(lambda match: new, str(node))
        node.replace_with(value)
        found += count
    if not found:
        raise ValueError(f'Missing reviewed passage: {old}')


def section(soup, prefix):
    return next(h.parent for h in soup.select('h2') if h.get_text(strip=True).startswith(prefix))


def task(soup, label):
    return next(p.parent for p in soup.select('.ms-task > p')
                if p.find('strong') and p.find('strong').get_text(strip=True) == label)


def set_solution(soup, label, html):
    answer = task(soup, label).select_one('details > div')
    assert answer is not None, label
    answer.clear()
    answer.append(fragment(html))


def set_line(svg, old, new):
    keys = ('x1', 'y1', 'x2', 'y2')
    line = next(e for e in svg.select('line')
                if all(e.get(k) == str(v) for k, v in zip(keys, old)))
    line.attrs.update({k: str(v) for k, v in zip(keys, new)})


def serialize(soup):
    # html.parser lowercases SVG attributes; restore their XML spellings too.
    value = str(soup)
    for name in ('viewBox', 'preserveAspectRatio', 'markerWidth', 'markerHeight',
                 'refX', 'refY', 'gradientUnits', 'gradientTransform',
                 'patternUnits', 'patternContentUnits', 'clipPathUnits'):
        value = re.sub(r'\b' + name.lower() + r'=', name + '=', value)
    for name in ('linearGradient', 'radialGradient', 'clipPath', 'textPath'):
        value = re.sub(r'(<\/?)' + name.lower() + r'\b', r'\1' + name, value)
    return value


def fix_nets(soup):
    # Side faces alternate a*c, b*c; the two caps are b*a.
    configs = [(480, 255, 70, 40, 70), (185, 240, 110, 80, 90),
               (122, 245, 70, 40, 60), (170, 235, 110, 80, 80),
               (170, 230, 110, 80, 80)]
    for index, (x, y, a, b, c) in enumerate(configs):
        svg = soup.select('svg')[index]
        faces = [e for e in svg.select('rect')
                 if e.get('stroke') in {'#2563eb', '#15803d', '#f59e0b'}][:6]
        assert len(faces) == 6
        positions = [(x, y, a, c), (x+a, y, b, c),
                     (x+a+b, y, a, c), (x+2*a+b, y, b, c),
                     (x+a, y-a, b, a), (x+a, y+c, b, a)]
        for face, values in zip(faces, positions):
            face.attrs.update(dict(zip(('x', 'y', 'width', 'height'), map(str, values))))
            face['data-net-face'] = 'true'
        labels = [e for e in svg.select('text')
                  if e.get_text(strip=True) in {'1', '2', '3', '4', '5', '6', 'A', 'B', 'C', 'a·c', 'b·c', 'a·b'}]
        if labels:
            # Last two diagrams place labels in pair order A,A,B,B,C,C.
            order = [0, 1, 2, 3, 4, 5] if index < 3 else [0, 2, 1, 3, 4, 5]
            for label, face_index in zip(labels, order):
                px, py, pw, ph = positions[face_index]
                label['x'] = str(px + pw/2)
                label['y'] = str(py + ph/2 + 8)
        if index == 3:
            # Keep a clear gap between the lower cap and the legend.
            for e in svg.select('rect'):
                if e.get('y') == '430':
                    e['y'] = '450'
            for e in svg.select('text'):
                if e.get('y') == '466':
                    e['y'] = '486'
    # The deliberately invalid example uses matching squares; only its layout
    # is invalid, which makes the explanation about overlapping faces precise.
    svg = soup.select('svg')[2]
    bad_faces = [e for e in svg.select('rect') if e.get('stroke') == '#2563eb'
                 and float(e.get('x', 0)) >= 420]
    for e, (x, y) in zip(bad_faces, [(465,235),(530,235),(595,235),(660,235),(465,300),(530,300)]):
        e.attrs.update(x=str(x), y=str(y), width='65', height='65')


def edit(slug, soup):
    if slug == 'kontakty':
        return fragment('''<div class="ms-support-page">
<header><span class="ms-support-badge">Связь с MathStart</span><h1>Контакты</h1>
<p>Вопрос по теме, предложение или ошибка в материале? Напишите нам.</p></header>
<section><h2>Обратная связь</h2><p><a class="ms-contact-email" href="mailto:rr06@mail.ru">rr06@mail.ru</a></p>
<p>Укажите название темы и приложите ссылку на страницу. Если вопрос относится к заданию, добавьте его номер и свой ход решения — так будет проще разобраться.</p></section>
<section><h2>Найти нужный материал</h2><p>Все темы расположены по классам и предметам. Для быстрого повторения используйте памятки.</p>
<div class="ms-support-links"><a href="/karta-sajta/">Карта сайта</a><a href="/pamyatki/">Памятки</a><a href="/">Выбрать класс</a></div></section></div>''')
    if slug == 'karta-sajta':
        # The actual, current published catalogue is rendered by Django.
        return fragment('''<div class="ms-support-page"><header><span class="ms-support-badge">Навигация по сайту</span>
<h1>Карта сайта</h1><p>Выберите класс и предмет, затем откройте нужную тему. В каждом уроке есть объяснения, примеры и задания для самопроверки.</p></header></div>''')
    if slug == 'materialy':
        return fragment('''<div class="ms-support-page"><header><span class="ms-support-badge">Учебные материалы</span><h1>Материалы</h1>
<p>Теория, примеры и задания по математике для 5–9 классов. Выберите раздел для изучения или повторения.</p></header>
<section><h2>Курсы по классам</h2><div class="ms-support-links"><a href="/5-klass/">5 класс</a><a href="/6-klass/">6 класс</a><a href="/#classes">7–9 классы: выбрать предмет</a></div></section>
<section><h2>Быстрое повторение</h2><p>Правила действий, основные формулы и разборы типовых задач помогут подготовиться к самостоятельной работе.</p>
<div class="ms-support-links"><a href="/pamyatki/">Правила и формулы</a><a href="/karta-sajta/">Все учебные темы</a></div></section></div>''')
    if slug == 'o-proekte':
        # Retain the real gallery, remove the unsupported plugin blocks and
        # the project-development document from the learner-facing page.
        for css in ('.ms-extra-gallery-card', '.ms-doc-card'):
            for e in soup.select(css):
                e.decompose()
        for h in list(soup.select('h2')):
            if h.get_text(strip=True) == 'Слайдер учебных материалов':
                h.decompose()
        for e in list(soup.find_all(string=re.compile(r'\[(metaslider|ml_gallery)\b'))):
            e.extract()
    elif slug == 'pamyatki':
        cards = soup.select('.ms-card')
        additions = [
            '<ul><li><a href="/naibolshij-obshhij-delitel-i-naimenshee-obshhee-kratnoe/">НОД и НОК: алгоритм и задачи</a></li><li><a href="/slozhenie-i-vychitanie-obyknovennyh-drobej-i-smeshannyh-chisel/">Сложение и вычитание дробей</a></li><li><a href="/reshenie-raczionalnyh-uravnenij/">Рациональные уравнения и ОДЗ</a></li></ul>',
            '<ul><li><a href="/treugolnik-ploshhad-treugolnika/">Периметр и площадь треугольника</a></li><li><a href="/pryamougolnyj-parallelepiped-razvyortka/">Площадь поверхности параллелепипеда</a></li><li><a href="/stepen-s-naturalnym-pokazatelem/">Степени с натуральным показателем</a></li></ul>',
            '<ul><li><a href="/protivopolozhnye-chisla-modul-chisla-czelye-i-raczionalnye-chisla/">Модуль, целые и рациональные числа</a></li><li><a href="/linejnoe-uravnenie-ax-by-c-0-grafik-linejnogo-uravneniya/">Как построить прямую по уравнению</a></li></ul>',
        ]
        for card, html in zip(cards, additions):
            card.append(fragment(html))
    elif slug == 'glavnaya':
        replace_text(soup, 'На страницах классов и предметов разделы оформлены аккордеонами. Внутри каждого раздела размещены темы, а каждая тема открывается как отдельная учебная запись.',
                     'Выберите класс и предмет, раскройте нужный раздел и откройте тему. Уроки содержат объяснения, разобранные примеры и задания с решениями.')
    elif slug == '5-klass':
        replace_text(soup, 'тем для отдельных записей WordPress', 'учебных тем с примерами и заданиями')
        replace_text(soup, 'Каждая тема открывается как отдельная запись.', 'Каждая тема открывается на отдельной странице.')
        replace_text(soup, 'Записи раскрывают каждую тему отдельно', 'Каждая тема — отдельный урок')
        replace_text(soup, 'Внутри каждой записи будут теория, алгоритмы, разобранные примеры, задания для самопроверки и раскрывающиеся решения.', 'В каждом уроке есть теория, алгоритмы, разобранные примеры, задания для самопроверки и раскрывающиеся решения.')
    elif slug == 'protivopolozhnye-chisla-modul-chisla-czelye-i-raczionalnye-chisla':
        replace_text(soup, 'Из данного списка целыми являются: −8, 4, 0, −3, 16.', 'Из данного списка целыми являются: −8; 4; 0; 16.')
        replace_text(soup, 'Числа 2,5 и 5/2 не являются целыми, потому что они дробные.', 'Числа 2,5; −3,7 и 5/2 не являются целыми: у них есть ненулевая дробная часть.')
        replace_text(soup, 'Ответ: −8, 4, 0, −3, 16.', 'Ответ: −8; 4; 0; 16.')
        example = next(h for h in soup.select('h3') if h.get_text().startswith('Пример 9')).find_next_sibling('div')
        example.clear()
        example.append(fragment('<span class="ms-example-title">Условие</span>Среди чисел −8; 4; 0; 2,5; −3,7; 5/2; 16 выберите целые числа.'))
    elif slug == 'treugolnik-ploshhad-treugolnika':
        replace_text(soup, 'Треугольник можно рассматривать как половину прямоугольника.', 'Диагональ прямоугольника делит его на два равных прямоугольных треугольника.')
        caption = next(e for e in soup.select('svg')[2].select('text') if 'Диагональ делит' in e.get_text())
        caption.clear()
        caption['y'] = '40'
        caption.append(fragment('<tspan x="410" dy="0">Диагональ делит прямоугольник</tspan><tspan x="410" dy="30">на два равных треугольника</tspan>'))
        set_solution(soup, 'Задание 11.', '<p>Периметр: P = 10 + 10 + 16 = 36 см.</p><p>Для прямой подстановки в формулу S = a · h : 2 нужна высота, проведённая к основанию 16 см. В условии она не дана. Длины трёх сторон определяют площадь, но сначала нужно научиться находить по ним высоту.</p><p><strong>Ответ: периметр 36 см; для вычисления площади по изученной формуле сначала нужно найти высоту.</strong></p><p>Дополнительно: высота делит основание на отрезки по 8 см. По теореме Пифагора, которую вы изучите позже, h² = 10² − 8² = 36, h = 6 см. Поэтому S = 16 · 6 : 2 = 48 см².</p>')
    elif slug == 'naibolshij-obshhij-delitel-i-naimenshee-obshhee-kratnoe':
        for node in list(soup.find_all(string=re.compile('Самое маленькое число|самое маленькое число'))):
            node.replace_with(str(node).replace('самое маленькое число', 'наименьшее положительное число').replace('Самое маленькое число', 'Наименьшее положительное число'))
        section(soup, '4.').append(fragment('<div class="ms-note"><strong>Взаимно простые числа.</strong> Если общих простых множителей нет, НОД равен 1. Такие числа называют взаимно простыми. Например, 8 = 2³ и 15 = 3 · 5, поэтому НОД(8; 15) = 1, а НОК(8; 15) = 8 · 15 = 120. Если одно натуральное число делится на другое, их НОД равен меньшему, а НОК — большему.</div>'))
        section(soup, '4.').append(fragment('<h3>Как выбрать НОД или НОК в задаче</h3><div class="ms-example"><strong>Одинаковые наборы.</strong><p>Из 18 карандашей и 24 ручек составляют наибольшее число одинаковых наборов без остатка. Число наборов должно делить и 18, и 24, поэтому нужно найти НОД(18; 24) = 6. В каждом наборе 18 : 6 = 3 карандаша и 24 : 6 = 4 ручки.</p></div><div class="ms-example"><strong>Повторяющиеся события.</strong><p>Два сигнала звучат каждые 6 и 8 минут. Сейчас они прозвучали вместе. Следующее совпадение наступит через НОК(6; 8) = 24 минуты: это наименьшее положительное время, кратное обоим периодам.</p></div>'))
    elif slug == 'linejnoe-uravnenie-ax-by-c-0-grafik-linejnogo-uravneniya':
        rule = section(soup, '4.').select_one('.ms-rule-box')
        rule.insert_before(fragment('<p class="ms-text">Если b ≠ 0, выбирайте два разных значения x и вычисляйте y. Если b = 0, то a ≠ 0: найдите x = −c/a и выберите два разных значения y. Получится вертикальная прямая, все точки которой имеют одну абсциссу.</p>'))
        rule.find('strong').string = 'Алгоритм построения при b ≠ 0:'
        set_line(soup.select('svg')[0], (420,135,650,595), (447.5,135,677.5,595))
        set_line(soup.select('svg')[3], (260,90,670,500), (320,90,730,500))
    elif slug == 'linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii':
        set_line(soup.select('svg')[2], (210,90,670,550), (290,90,710,510))
    elif slug == 'linejnaya-funkcziya-y-kx-eyo-svojstva':
        set_line(soup.select('svg')[3], (75,372,645,238), (75,440,645,155))
        set_line(soup.select('svg')[4], (300,65,560,525), (280,75,570,510))
        svg = soup.select('svg')[4]
        # Make the intentionally different axis scales explicit.
        svg.append(fragment('<text x="470" y="297" text-anchor="middle" font-size="16" fill="#374151">1</text><text x="530" y="297" text-anchor="middle" font-size="16" fill="#374151">2</text><text x="393" y="336" text-anchor="end" font-size="16" fill="#374151">−2</text><text x="393" y="396" text-anchor="end" font-size="16" fill="#374151">−4</text><text x="393" y="456" text-anchor="end" font-size="16" fill="#374151">−6</text>'))
    elif slug == 'pryamougolnyj-parallelepiped-razvyortka':
        fix_nets(soup)
    elif slug == 'stepen-s-naturalnym-pokazatelem':
        svg = soup.select('svg')[4]
        for e in svg.select('text'):
            if e.get('x') == '585':
                e.string = {'146': 'один', '169': 'множитель 10',
                            '266': 'два', '289': 'множителя 10',
                            '386': 'три', '409': 'множителя 10'}[e['y']]
                e['font-size'] = '18'
        replace_text(soup, '3 умножили само на себя 4 раза', 'Четыре одинаковых множителя 3')
    elif slug == 'geometricheskie-ponyatiya-okruzhnost-i-krug':
        svg = soup.select('svg')[3]
        set_line(svg, (315,180,565,255), (313.6932,180,554.5683,255))
        for e in svg.select('circle'):
            if e.get('cx') == '315': e['cx'] = '313.6932'
            elif e.get('cx') == '565': e['cx'] = '554.5683'
    elif slug == 'povtorenie-kursa-geometrii-7-9-klassov-kompleksnye-zadachi':
        svg = soup.select('svg')[2]
        for e in svg.select('line'):
            for attr in ('x1','x2'):
                if e.get(attr) == '760': e[attr] = '730'
        for e in svg.select('circle'):
            if e.get('cx') == '760': e['cx'] = '730'
        for e in svg.select('text'):
            if e.get('x') == '771': e['x'] = '741'
    elif slug == 'dvizheniya-ploskosti-simmetriya-parallelnyj-perenos-i-povorot':
        svg = soup.select('svg')[2]
        circle = next(e for e in svg.select('circle') if e.get('cx')=='715' and e.get('r')=='145')
        circle['r'] = '135'
    elif slug == 'ponyatie-chislovyh-promezhutkov':
        for index, svg in enumerate(soup.select('svg')):
            mapping = {e['id']: f"interval-{index}-{e['id']}" for e in svg.select('[id]')}
            for e in svg.find_all(True):
                if e.get('id') in mapping: e['id'] = mapping[e['id']]
                for key, value in list(e.attrs.items()):
                    if isinstance(value, str):
                        for old, new in mapping.items(): value = value.replace(f'url(#{old})', f'url(#{new})')
                        e[key] = value
    elif slug == 'preobrazovanie-podobiya-i-gomotetiya':
        section(soup, '4.').insert(1, fragment('<p class="ms-text">Коэффициент гомотетии k ≠ 0. При k = 1 каждая точка остаётся на месте. Значение k = 0 исключено: оно сжимало бы всю плоскость в одну точку и не задавало бы подобие.</p>'))
        replace_text(soup, 'Прямая, не проходящая через центр, переходит в параллельную ей прямую.', 'При k ≠ 1 прямая, не проходящая через центр, переходит в параллельную ей прямую. При k = 1 она совпадает со своим образом.')
        replace_text(soup, 'если прямая AB не проходит через центр O.', 'если k ≠ 1 и прямая AB не проходит через центр O. При k = 1 прямые AB и A′B′ совпадают.')
        set_solution(soup, 'Задание 7.', '<p>Коэффициент гомотетии не равен нулю. При k = 1 все точки остаются на месте, поэтому l′ = l. При k ≠ 1 образ прямой, не проходящей через центр, параллелен исходной прямой.</p><p><strong>Ответ: при k = 1 прямые совпадают; при k ≠ 1 они параллельны.</strong></p>')
    elif slug == 'ispytaniya-bernulli-veroyatnosti-sobytij-v-serii-ispytanij':
        replace_text(soup, 'Иногда требуется сравнить вероятности k и k + 1 успехов, не вычисляя обе полностью. После сокращения получается:', 'Иногда требуется сравнить вероятности k и k + 1 успехов, не вычисляя обе полностью. При 0 < p < 1 и целом 0 ≤ k < n после сокращения получается:')
    elif slug == 'pryamaya-i-okruzhnost-kasatelnaya-vzaimnoe-raspolozhenie-dvuh-okruzhnostej':
        replace_text(soup, 'd = R − r', 'd = R − r > 0')
    elif slug == 'czentralnye-i-vpisannye-ugly-dugi-hordy-sekushhie-i-kasatelnye':
        replace_text(soup, 'Сначала рассмотрим случай, когда центр O лежит на одной из сторон угла ACB. Тогда OC является продолжением одной стороны угла.', 'Сначала рассмотрим случай, когда центр O лежит на стороне CA угла ACB. Тогда CA — диаметр, а точки C, O и A расположены на одной прямой именно в этом порядке.')
    elif slug == 'reshenie-raczionalnogo-uravneniya-svodyashhegosya-k-kvadratnomu':
        replace_text(soup, 'имеет один положительный корень t?', 'имеет ровно один положительный корень t?')
        set_solution(soup, 'Задание 9.', '<p>После замены получаем t² − 6t + m = 0. Нужно посчитать именно положительные корни, а не все действительные.</p><ul><li>При m &lt; 0 произведение корней отрицательно, поэтому один корень положительный, а другой отрицательный.</li><li>При m = 0 корни равны 0 и 6: положительный корень только один.</li><li>При 0 &lt; m &lt; 9 дискриминант D = 36 − 4m &gt; 0, сумма корней 6 и произведение m положительны: оба корня положительны.</li><li>При m = 9 есть единственный корень t = 3, он положителен.</li><li>При m &gt; 9 действительных корней нет.</li></ul><p><strong>Ответ: m ∈ (−∞; 0] ∪ {9}.</strong></p>')
    elif slug == 'ispolzovanie-sistem-raczionalnyh-uravnenij-dlya-resheniya-zadach':
        replace_text(soup, 'Подходящая положительная целочисленная пара: x = 18, y = 14.', 'Выразим y = (2x + 6)/3 и подставим в xy = 252: 2x² + 6x = 756, то есть x² + 3x − 378 = 0. Разложим: (x − 18)(x + 21) = 0. Отрицательное число рядов невозможно, поэтому x = 18, y = 14. Это единственная положительная пара.')
        replace_text(soup, 'Подходящая положительная пара: x = 9, y = 8, но она не удовлетворяет условию x < y.', 'Подставим y = (2x + 6)/3 в xy = 72: 2x² + 6x = 216, то есть x² + 3x − 108 = 0. Получаем (x − 9)(x + 12) = 0. При x > 0 остаётся только x = 9, тогда y = 8. Эта единственная положительная пара не удовлетворяет условию x < y.')
    elif slug == 'ponyatie-chislovoj-posledovatelnosti-sposoby-zadaniya-posledovatelnostej':
        replace_text(soup, '12. Финальная настройка последовательности', '12. Памятка: как работать с последовательностью')
    else:
        raise ValueError(f'Unreviewed page: {slug}')
    return soup


SLUGS = '''kontakty karta-sajta materialy o-proekte pamyatki glavnaya 5-klass
protivopolozhnye-chisla-modul-chisla-czelye-i-raczionalnye-chisla treugolnik-ploshhad-treugolnika
naibolshij-obshhij-delitel-i-naimenshee-obshhee-kratnoe
linejnoe-uravnenie-ax-by-c-0-grafik-linejnogo-uravneniya linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii linejnaya-funkcziya-y-kx-eyo-svojstva
pryamougolnyj-parallelepiped-razvyortka stepen-s-naturalnym-pokazatelem
geometricheskie-ponyatiya-okruzhnost-i-krug povtorenie-kursa-geometrii-7-9-klassov-kompleksnye-zadachi
dvizheniya-ploskosti-simmetriya-parallelnyj-perenos-i-povorot ponyatie-chislovyh-promezhutkov
preobrazovanie-podobiya-i-gomotetiya ispytaniya-bernulli-veroyatnosti-sobytij-v-serii-ispytanij
pryamaya-i-okruzhnost-kasatelnaya-vzaimnoe-raspolozhenie-dvuh-okruzhnostej
czentralnye-i-vpisannye-ugly-dugi-hordy-sekushhie-i-kasatelnye
reshenie-raczionalnogo-uravneniya-svodyashhegosya-k-kvadratnomu
ispolzovanie-sistem-raczionalnyh-uravnenij-dlya-resheniya-zadach
ponyatie-chislovoj-posledovatelnosti-sposoby-zadaniya-posledovatelnostej'''.split()


def main():
    if not BASELINE.exists():
        with sqlite3.connect(ROOT / 'db.sqlite3') as source, sqlite3.connect(BASELINE) as target:
            source.backup(target)
    records = []
    with sqlite3.connect(BASELINE) as db:
        for slug in SLUGS:
            old, = db.execute('SELECT body_html FROM content_contentpage WHERE slug=?', (slug,)).fetchone()
            new = serialize(edit(slug, fragment(old)))
            assert new != old, slug
            records.append({'slug': slug, 'before_sha256': digest(old), 'after_sha256': digest(new), 'body_html': new})
    OUTPUT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Reviewed pages: {len(records)}. Manifest: {OUTPUT}')


if __name__ == '__main__':
    main()
