"""Closed equivalent of the three reviewed lesson templates, without Django.

Only metadata is escaped; authored HTML fragments remain byte-for-byte intact.
The source templates remain the independent golden-render oracle.
"""
from html import escape


def text(value):
    return escape(str(value), quote=True).replace('&#x27;', '&#x27;')


def render_to_string(template, context):
    name = template.removeprefix('lessons/components/').removesuffix('.html')
    value = context[name]
    if name == 'section':
        identity = f' id="{text(value["id"])}"' if value.get('id') else ''
        style = 'ms-section-soft' if value.get('soft') else 'ms-section'
        number = f'{value["number"]}. ' if value.get('number') else ''
        return f'<section{identity} class="{style}"><h2>{number}{text(value["title"])}</h2>{value["body_html"]}</section>'
    if name == 'exercise':
        identity = f' id="{text(value["id"])}"' if value.get('id') else ''
        number = value['number']
        return (f'<div{identity} class="ms-task v2-task"><p><strong>Задание {number}.</strong> '
                f'{value["question_html"]}</p><details class="ms-answer v2-answer">'
                f'<summary aria-label="Показать решение задания {number}">Показать решение</summary>'
                f'<div>{value["answer_html"]}</div></details></div>')
    if name != 'contents':
        raise ValueError('Unknown reviewed component')
    links = []
    for position, entry in enumerate(value['entries'], 1):
        practice = ' ms-toc-practice' if entry.get('practice') or entry['id'] == 'practice' else ''
        note = f'<small>{text(entry["note"])}</small>' if entry.get('note') else ''
        links.append(f'<a class="ms-toc-link{practice}" href="#{text(entry["id"])}">'
                     f'<span class="ms-toc-number">{entry.get("number") or position:02d}</span>'
                     f'<span class="ms-toc-copy"><strong>{text(entry["title"])}</strong>{note}</span>'
                     '<span class="ms-toc-arrow" aria-hidden="true">→</span></a>')
    return ('<details class="ms-lesson-toc" open><summary>\n'
            '    <span class="ms-toc-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M9 6h11M9 12h11M9 18h11M4 6h.01M4 12h.01M4 18h.01"/></svg></span>\n'
            '    <span class="ms-toc-heading"><strong>Содержание урока</strong><small>Теория, примеры и задания для самостоятельной работы</small></span><span class="ms-toc-chevron" aria-hidden="true"></span></summary>\n'
            '    <nav class="ms-lesson-links" aria-label="Содержание урока">' + ''.join(links) + '</nav></details>')
