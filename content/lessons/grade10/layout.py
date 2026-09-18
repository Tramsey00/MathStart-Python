"""Render lessons with MathStart's existing visual vocabulary."""
import math
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
COURSE_SLUG = '10-klass-algebra'
SECTIONS = [
    ('deistvitelnye-chisla', 'Действительные числа', 'Числовые множества, делимость, дроби и приближения.'),
    ('stepeni-korni-stepennye-funkcii', 'Степени с рациональным показателем. Корни. Степенные функции',
     'Корни любой натуральной степени, преобразования выражений и графики.'),
]


def p(text):
    return f'<p class="ms-text">{text}</p>'


def rule(text):
    return f'<div class="ms-rule-box">{text}</div>'


def note(text):
    return f'<div class="ms-note">{text}</div>'


def example(title, text):
    return f'<div class="ms-example"><span class="ms-example-title">{title}</span>{text}</div>'


def formulas(*rows):
    return '<div class="ms-math-box">' + ''.join(f'<div class="ms-math-row">{r}</div>' for r in rows) + '</div>'


def table(headers, rows):
    return '<div class="ms-table-wrap" tabindex="0" role="region" aria-label="Таблица: прокрутите при необходимости"><table class="ms-table"><thead><tr>' + ''.join(f'<th scope="col">{h}</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>'+''.join(f'<td>{cell}</td>' for cell in row)+'</tr>' for row in rows) + '</tbody></table></div>'


def figure(title, svg, caption):
    return f'<figure class="ms-figure"><p class="ms-figure-title">{title}</p><div class="ms-svg-wrap">{svg}</div><figcaption class="ms-text">{caption}</figcaption></figure>'


def graph(title, curves, bounds, xticks, yticks, caption):
    """curves = (label, color, [(x,y), ...]); each list is ONE continuous branch.

    Polylines contain actual function samples; out-of-frame points break paths.
    Equal x/y scales are used when bounds have equal spans.
    """
    xmin, xmax, ymin, ymax = bounds
    left, top, size = 66, 35, 440
    sx = lambda x: left + (x-xmin)/(xmax-xmin)*size
    sy = lambda y: top + (ymax-y)/(ymax-ymin)*size
    items = [f'<svg class="ms-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 570" role="img" aria-label="{escape(title, quote=True)}">', '<rect width="620" height="570" fill="white"/>']
    for ticks, vertical in [(xticks, True), (yticks, False)]:
        for value in ticks:
            pos = sx(value) if vertical else sy(value)
            if vertical:
                items.append(f'<line x1="{pos}" y1="{top}" x2="{pos}" y2="{top+size}" stroke="#e2e8f0"/><text x="{pos}" y="{top+size+25}" text-anchor="middle" font-size="16" fill="#475569">{value}</text>')
            else:
                items.append(f'<line x1="{left}" y1="{pos}" x2="{left+size}" y2="{pos}" stroke="#e2e8f0"/><text x="{left-12}" y="{pos+5}" text-anchor="end" font-size="16" fill="#475569">{value}</text>')
    items.append(f'<path d="M {left} {sy(0)} H {left+size+12} M {sx(0)} {top+size} V {top-12}" fill="none" stroke="#475569" stroke-width="2"/>')
    items.append(f'<text x="{left+size+22}" y="{sy(0)+6}" font-size="19">x</text><text x="{sx(0)-6}" y="{top-18}" font-size="19">y</text>')
    legends = []
    for label, color, points in curves:
        path, connected = [], False
        for x, y in points:
            if not (math.isfinite(x) and math.isfinite(y) and xmin <= x <= xmax and ymin <= y <= ymax):
                connected = False
                continue
            path.append(f'{"L" if connected else "M"}{sx(x):.3f},{sy(y):.3f}')
            connected = True
        items.append(f'<path data-function="{escape(label, quote=True)}" d="{" ".join(path)}" stroke="{color}" fill="none" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
        if (label, color) not in legends:
            legends.append((label, color))
    for i, (label, color) in enumerate(legends):
        x, y = 66+(i % 2)*245, 528+(i//2)*27
        items.append(f'<line x1="{x}" y1="{y-5}" x2="{x+25}" y2="{y-5}" stroke="{color}" stroke-width="4"/><text x="{x+34}" y="{y}" fill="{color}" font-size="17">{escape(label)}</text>')
    items.append('</svg>')
    return figure(title, ''.join(items), caption)


def samples(fn, start, stop, count=401):
    return [(x, fn(x)) for x in (start+(stop-start)*i/(count-1) for i in range(count))]


def root_samples(n, start, stop):
    # Sample y, not x: near zero this preserves the vertical tangent.
    return [(y**n, y) for y in (start+(stop-start)*i/400 for i in range(401))]


def render_lesson(lesson, previous=None, following=None):
    sec = lesson['section']
    badge = f'10 класс · Алгебра · Тема {sec}.{lesson["order"]}'
    sections = []
    for i, (heading, html) in enumerate(lesson['parts'], 1):
        anchor = 'theory' if i == 1 else f'part-{i}'
        sections.append(f'<section class="ms-section{"-soft" if i%2==0 else ""}" id="{anchor}"><h2>{i}. {heading}</h2>{html}</section>')
    tasks = ''.join(f'<div class="ms-task"><p><strong>Задание {i}.</strong> {q}</p><details class="ms-answer"><summary>Показать решение {i}</summary><div>{a}</div></details></div>' for i, (q, a) in enumerate(lesson['tasks'], 1))
    nav = f'<a class="ms-btn ms-btn-secondary" href="/{COURSE_SLUG}/#program">Все темы алгебры 10 класса</a>'
    if previous:
        nav += f'<a class="ms-btn ms-btn-secondary" href="/{previous["slug"]}/">← {escape(previous["title"])}</a>'
    if following:
        nav += f'<a class="ms-btn" href="/{following["slug"]}/">{escape(following["title"])} →</a>'
    else:
        nav += f'<a class="ms-btn" href="/{COURSE_SLUG}/">Повторить два раздела</a>'
    return f'''<style>{(ROOT / 'lesson.css').read_text(encoding='utf-8')}
    .ms-post .ms-nav .ms-btn{{height:auto;padding:13px 20px;line-height:1.5;text-align:center;max-width:100%;white-space:normal}}
    .ms-post .ms-figure figcaption{{margin:16px 0 0;font-size:15px}}
    .ms-post .ms-table{{min-width:560px}}
    .ms-post .ms-badge{{max-width:100%;line-height:1.5}}
    @media(max-width:420px){{.ms-post .ms-title{{font-size:30px}}.ms-post .ms-hero{{padding:26px 20px}}.ms-post .ms-section,.ms-post .ms-section-soft{{padding:20px 16px}}.ms-post .ms-figure{{padding:12px}}}}
    </style><main class="ms-post">
    <section class="ms-hero"><div class="ms-badge">{badge}</div><h1 class="ms-title">{escape(lesson['title'])}</h1>
    <p class="ms-subtitle">{lesson['intro']}</p><div class="ms-hero-actions"><a class="ms-btn" href="#theory">Перейти к теории</a><a class="ms-btn ms-btn-secondary" href="#practice">Самопроверка</a><a class="ms-btn ms-btn-secondary" href="/{COURSE_SLUG}/">К темам алгебры</a></div></section>
    {''.join(sections)}<section class="ms-section" id="practice"><h2>Проверьте себя</h2>{p('Сначала решите задания самостоятельно. Затем откройте решения и сравните не только ответ, но и условия применения формул.')}{tasks}</section>
    <section class="ms-section-soft"><h2>Что нужно запомнить</h2>{rule(lesson['summary'])}{p(f'<a href="{lesson["source"]}">Дополнительные задания по этой теме на ЯКласс</a>')}</section>
    <nav class="ms-nav" aria-label="Переходы между темами">{nav}</nav></main>'''


def render_course(lessons):
    program = []
    for i, (slug, title, description) in enumerate(SECTIONS, 1):
        links = ''.join(f'<a class="ms-topic" href="/{l["slug"]}/"><span class="ms-topic-number">{i}.{l["order"]}</span><span class="ms-topic-name">{escape(l["title"])}</span></a>' for l in lessons if l['section'] == i)
        program.append(f'<details class="ms-accordion" id="{slug}"><summary><span class="ms-accordion-left"><span class="ms-section-icon">{i}</span><span class="ms-accordion-main"><span class="ms-accordion-title">{i}. {title}</span><span class="ms-accordion-subtitle">{description}</span></span></span><span class="ms-acc-arrow" aria-hidden="true"></span></summary><div class="ms-topic-list">{links}</div></details>')
    return f'''<style>{(ROOT/'course.css').read_text(encoding='utf-8')}
    .ms-hero-grid{{grid-template-columns:1fr}}.ms-badge{{line-height:1.5}}.ms-title{{overflow-wrap:anywhere}}.ms-map-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:620px){{.ms-map-grid{{grid-template-columns:1fr}}}}@media(max-width:520px){{.ms-accordion .ms-section-icon{{display:none}}.ms-accordion summary{{gap:10px;align-items:flex-start}}.ms-accordion .ms-acc-arrow{{width:30px;height:30px}}}}
    </style><main class="ms-post"><section class="ms-hero"><div class="ms-badge">MathStart · 10 класс · Алгебра</div><h1 class="ms-title">Алгебра 10 класс</h1><p class="ms-subtitle">Первые два раздела: действительные числа, корни, степени с рациональным показателем и степенные функции. Повторите числовые множества, научитесь преобразовывать выражения и читать графики.</p><div class="ms-hero-actions"><a class="ms-btn" href="#program">Открыть темы</a><a class="ms-btn ms-btn-secondary" href="/{lessons[0]['slug']}/">Начать с первой темы</a><a class="ms-btn ms-btn-secondary" href="/">На главную</a></div></section>
    <section class="ms-section"><h2>Что входит в программу</h2>{p('Девять уроков идут от знакомых чисел и дробей к новым определениям и свойствам функций. В каждом уроке есть теория, разборы примеров и самостоятельные задания с решениями. В задачах с переменными всегда учитываем область допустимых значений.')}
    <div class="ms-stat-grid"><div class="ms-stat"><span class="ms-stat-number">2</span><span class="ms-stat-text">учебных раздела</span></div><div class="ms-stat"><span class="ms-stat-number">9</span><span class="ms-stat-text">тем с теорией и примерами</span></div><div class="ms-stat"><span class="ms-stat-number">{sum(len(l['tasks']) for l in lessons)}</span><span class="ms-stat-text">задания с подробными решениями</span></div></div></section>
    <section class="ms-section-soft"><h2>Карта курса</h2><div class="ms-map-grid"><div class="ms-map-card"><div class="ms-map-symbol">ℝ</div><h3 class="ms-map-title">От натуральных к действительным</h3><p class="ms-map-text">Делимость → обыкновенные и периодические дроби → иррациональные числа и их оценки.</p></div><div class="ms-map-card"><div class="ms-map-symbol">ⁿ√a</div><h3 class="ms-map-title">От корней к графикам</h3><p class="ms-map-text">Корень n-й степени → свойства и преобразования → рациональные показатели → степенные функции.</p></div></div></section>
    <section class="ms-section-soft" id="program"><h2>Разделы и темы</h2>{p('Раскройте раздел и выберите тему. Нумерация показывает рекомендуемый порядок изучения.')}<div class="ms-program">{''.join(program)}</div></section>
    <section class="ms-section"><h2>Как проходить материалы</h2>{p('Начните с трёх уроков повторения. В разделе о корнях сначала разберитесь с чётностью показателя и знаком результата, затем переходите к преобразованиям. Степенные функции изучайте после рациональных показателей: так ограничения на аргумент будут понятны.')}{p('Для закрепления решите задания без подсказок. Если ответ не совпал, найдите первый неверный шаг и вернитесь к соответствующему примеру.')}</section>
    <section class="ms-section-soft"><h2>Дополнительная практика</h2>{p('<a href="https://www.yaklass.ru/p/algebra/10-klass?YklShowAll=1">ЯКласс: программа и задания по темам</a>')}{p('<a href="https://math100.ru/algebra10-11_4_1/">Math100: выражения с радикалами</a>')}{p('<a href="https://math-ege.sdamgia.ru/problem?id=512331">Сдам ГИА: преобразование степенного выражения</a>')}</section></main>'''
