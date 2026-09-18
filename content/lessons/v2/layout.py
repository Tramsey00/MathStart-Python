from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).parent


def clean(text):
    return re.sub('<[^>]+>', '', str(text))


def F(top, bottom):
    label = escape(f'{clean(top)} делённое на {clean(bottom)}',quote=True)
    return f'<span class="v2-frac" role="math" aria-label="{label}"><span>{top}</span><span>{bottom}</span></span>'


def P(base, power):
    return f'<span class="v2-power">{base}<sup>{power}</sup></span>'


def R(value, index=''):
    return f'<span class="v2-root">{f"<sup>{index}</sup>" if index else ""}<span class="v2-root-sign">√</span><span class="v2-radicand">{value}</span></span>'


def para(text):
    return f'<p>{text}</p>'


def box(title, body, tone='rule'):
    return f'<aside class="v2-{tone}"><strong class="v2-box-title">{title}</strong>{body}</aside>'


def eq(*lines):
    return '<div class="v2-equations">'+''.join(f'<div>{line}</div>' for line in lines)+'</div>'


def example(title, body):
    return f'<article class="v2-example"><h3>{title}</h3>{body}</article>'


def table(headers, rows):
    return '<div class="v2-table-wrap"><table class="v2-table"><thead><tr>'+''.join(f'<th scope="col">{c}</th>' for c in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{c}</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'


def steps(items):
    return '<ol class="v2-steps">'+''.join(f'<li>{item}</li>' for item in items)+'</ol>'


def cards(items):
    return '<div class="v2-cards">'+''.join(f'<article><h3>{title}</h3>{body}</article>' for title,body in items)+'</div>'


def figure(svg, caption):
    return f'<figure class="v2-figure">{svg}<figcaption>{caption}</figcaption></figure>'


def render(page):
    if page.get('layout') == 'site':
        from .power_layout import render as render_power
        return render_power(page)
    toc = ''.join(f'<a href="#{key}"><span>{i:02}</span>{title}</a>' for i,(key,title,body) in enumerate(page['sections'],1))
    sections=''.join(f'<section class="v2-section" id="{key}"><div class="v2-section-heading"><span>{i:02}</span><h2>{title}</h2></div>{body}</section>' for i,(key,title,body) in enumerate(page['sections'],1))
    tasks=''.join(f'<article class="v2-task"><div class="v2-task-label">{i:02} · {level}</div><p>{q}</p><details class="v2-answer"><summary>Разбор задания {i}</summary><div>{a}</div></details></article>' for i,(level,q,a) in enumerate(page['tasks'],1))
    return f'''<style>{(ROOT/'lesson.css').read_text(encoding='utf-8')}</style>
    <main class="ms-post ms-v2"><header class="v2-hero"><div class="v2-eyebrow">10 класс · Алгебра <span>Версия 2.0</span></div><h1>{page['title']}</h1><p>{page['intro']}</p><nav class="v2-actions" aria-label="Быстрые переходы"><a class="v2-button" href="#interactive-lab">Исследовать {page['lab_word']}</a><a href="#practice">К заданиям</a><a href="/10-klass-algebra/#program">Все темы</a></nav></header>
    <nav class="v2-toc" aria-label="Содержание урока"><h2>В этом уроке</h2><div>{toc}<a href="#practice"><span>✓</span>Самопроверка с решениями</a></div></nav>
    {sections}<section class="v2-section" id="practice"><div class="v2-section-heading"><span>✓</span><h2>Самопроверка</h2></div><p>Решайте по порядку: от основных свойств к задачам, где нужно соединить несколько идей. Открывайте разбор после собственной попытки.</p>{tasks}</section>
    <section class="v2-finish"><h2>Опора для повторения</h2>{page['summary']}</section>
    <div class="v2-sources"><span>Ещё задания по теме:</span> <a href="{page['source']}">ЯКласс</a> · <a href="{page['practice_source']}">{page['practice_name']}</a></div>
    <nav class="v2-bottom" aria-label="Другие темы"><a href="/10-klass-algebra/#program">← К алгебре 10 класса</a><a href="/{page['other_slug']}/">{page['other_title']} →</a></nav></main>
    <script>{(ROOT/'math.js').read_text(encoding='utf-8')}\n{(ROOT/page['script']).read_text(encoding='utf-8')}</script>'''
