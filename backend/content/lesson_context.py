"""Shared lesson chrome derived only from the pinned catalogue, without DB writes."""
from urllib.parse import urlencode


def lesson_context(catalogue, page):
    grades = {g['id']: g for g in catalogue['grades']}
    subjects = {s['id']: s for s in catalogue['subjects']}
    sections = {s['id']: s for s in catalogue['sections']}
    grade, subject, section = grades[page['grade_id']], subjects[page['subject_id']], sections[page['section_id']]
    siblings = [t for t in catalogue['topics'] if t['grade_id'] == page['grade_id'] and t['subject_id'] == page['subject_id']]
    siblings.sort(key=lambda t: (sections[t['section_id']]['order'], t['order'], t['id']))
    position = next(i for i, topic in enumerate(siblings) if topic['id'] == page['id'])

    def item(topic):
        value = {key: topic[key] for key in ('slug', 'title', 'order', 'url')}
        if topic['section_id'] != page['section_id']:
            value['boundary'] = 'section'
        return value

    section_url = '/materials?' + urlencode({'grade': grade['slug'], 'subject': subject['slug'], 'section': section['slug']})
    return {
        'lesson_navigation': {
            'previous': item(siblings[position - 1]) if position else None,
            'next': item(siblings[position + 1]) if position + 1 < len(siblings) else None,
        },
        'lesson_section': {'title': section['title'], 'href': section_url},
        # Titles of imported historical grade pages are not display labels.
        'grade_links': [{'title': f'{number} класс', 'href': f'/materials?grade={number}-klass'} for number in range(5, 11)],
    }
