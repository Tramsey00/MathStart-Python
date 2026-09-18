"""Detailed lessons in MathStart's established lesson 6.6 design."""
from html import escape
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).parent


def style_content(html):
    soup=BeautifulSoup(html,'html.parser')
    mapping={
        'v2-rule':'ms-rule-box', 'v2-note':'ms-note', 'v2-box-title':'ms-example-title',
        'v2-example':'ms-example', 'v2-equations':'ms-math-box',
        'v2-table-wrap':'ms-table-wrap', 'v2-table':'ms-table',
        'v2-steps':'ms-list', 'v2-cards':'ms-card-grid', 'v2-figure':'ms-figure',
        'v2-frac':'ms-frac',
    }
    for element in soup.find_all(class_=True):
        classes=element.get('class',[])
        element['class']=classes+[mapping[c] for c in classes if c in mapping]
    for paragraph in soup.find_all('p'):
        paragraph['class']=paragraph.get('class',[])+['ms-text']
    for example in soup.select('.ms-example'):
        title=example.find('h3',recursive=False)
        if title:
            title.name='strong'
            title['class']=['ms-example-title']
    for row in soup.select('.ms-math-box > div'):
        row['class']=['ms-math-row']
    for card in soup.select('.ms-card-grid > article'):
        card['class']=['ms-card']
        title=card.find('h3',recursive=False)
        if title: title['class']=['ms-card-title']
        for paragraph in card.find_all('p',recursive=False):
            paragraph['class']=['ms-card-text']
    for caption in soup.select('figcaption'):
        caption['class']=['ms-card-text','ms-power-caption']
    for fraction in soup.select('.v2-frac'):
        spans=fraction.find_all('span',recursive=False)
        if len(spans)==2:
            spans[0]['class']=['ms-num']
            spans[1]['class']=['ms-den']
    for power in soup.select('.v2-power'):
        if power.find('span',class_='ms-power-base',recursive=False): continue
        exponent=power.find('sup',recursive=False)
        if exponent is None: continue
        base=soup.new_tag('span',attrs={'class':'ms-power-base'})
        for child in list(power.contents):
            if child is exponent: break
            base.append(child.extract())
        power.insert(0,base)
    return str(soup)


def contents(page):
    notes = page.get('toc_notes', {})
    entries = [(key, title, notes.get(key, '')) for key, title, _ in page['sections']]
    entries.append(('practice', 'Самопроверка', '12 заданий с подробными решениями'))
    links = []
    for i, (key, title, note) in enumerate(entries, 1):
        extra = ' ms-toc-practice' if key == 'practice' else ''
        subtitle = f'<small>{escape(note)}</small>' if note else ''
        links.append(f'<a class="ms-toc-link{extra}" href="#{key}"><span class="ms-toc-number">{i:02}</span><span class="ms-toc-copy"><strong>{title}</strong>{subtitle}</span><span class="ms-toc-arrow" aria-hidden="true">→</span></a>')
    return f'''<details class="ms-lesson-toc" open><summary>
    <span class="ms-toc-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M9 6h11M9 12h11M9 18h11M4 6h.01M4 12h.01M4 18h.01"/></svg></span>
    <span class="ms-toc-heading"><strong>Содержание урока</strong><small>Теория, примеры и задания для самостоятельной работы</small></span><span class="ms-toc-chevron" aria-hidden="true"></span></summary>
    <nav class="ms-lesson-links" aria-label="Содержание урока">{''.join(links)}</nav></details>'''


def render(page):
    sections=[]
    for i,(key,title,body) in enumerate(page['sections'],1):
        section_class='ms-section-soft' if i in (4,6,8,10) else 'ms-section'
        sections.append(f'<section id="{key}" class="{section_class}"><h2>{i}. {title}</h2>{style_content(body)}</section>')
    tasks=''.join(f'<div class="ms-task v2-task"><p><strong>Задание {i}.</strong> {style_content(question)}</p><details class="ms-answer v2-answer"><summary aria-label="Показать решение задания {i}">Показать решение</summary><div>{style_content(answer)}</div></details></div>' for i,(_,question,answer) in enumerate(page['tasks'],1))
    styles=['power_page.css','power_math.css','lesson_navigation.css']
    if page.get('extra_css'):
        styles.append(page['extra_css'])
    scripts=['lesson_navigation.js']
    if page.get('script'):
        scripts += ['math.js',page['script']]
    if page.get('script') == 'power.js':
        styles.append('power_lab.css')
    css='\n'.join((ROOT/name).read_text(encoding='utf-8').replace('.ms-power-page','.ms-lesson-page') for name in styles)
    script='\n'.join((ROOT/name).read_text(encoding='utf-8') for name in scripts)
    badge=page.get('badge','10 класс · Алгебра · Степенные функции · Тема 2.6 · Версия 2.0')
    hero_target=page.get('hero_target','interactive-lab')
    hero_label=page.get('hero_label','Перейти к интерактиву')
    practice_number=len(sections)+1
    return f'''<style>{css}</style><main class="ms-post ms-lesson-page">
    <section class="ms-hero"><div class="ms-badge">{badge}</div>
    <h1 class="ms-title">{page['title']}</h1><p class="ms-subtitle">{page['intro']}</p>
    <nav class="ms-hero-actions" aria-label="Быстрые переходы"><a class="ms-btn" href="#{hero_target}">{hero_label}</a><a class="ms-btn ms-btn-secondary" href="#practice">К самопроверке</a><a class="ms-btn ms-btn-secondary" href="/10-klass-algebra/#program">К темам алгебры</a></nav></section>
    {contents(page)}
    {''.join(sections)}
    <section id="practice" class="ms-section-soft"><h2>{practice_number}. Самопроверка</h2><p class="ms-text">Решите задания самостоятельно, затем откройте решение и сравните ход рассуждений.</p>{tasks}</section>
    <section class="ms-section"><h2>Что важно запомнить</h2>{style_content(page['summary'])}
    <nav class="ms-nav" aria-label="Другие темы"><a class="ms-btn" href="/10-klass-algebra/#program">К темам алгебры</a><a class="ms-btn ms-btn-secondary" href="/{page['other_slug']}/">{page['other_title']}</a><a class="ms-btn ms-btn-secondary" href="/">На главную</a></nav></section></main>
    <script>{script}</script>'''
