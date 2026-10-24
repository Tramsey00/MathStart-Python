"""Explicit publication adapter for the user-approved home and catalogue UI."""
VERSION = 'approved-public-v1'


def public_design_kind(page):
    if page['slug'] == 'glavnaya' and page['page_type'] == 'home':
        return 'home'
    if page['slug'] == 'karta-sajta':
        return 'catalogue'
    return None


def uses_react_public(page):
    return page.get('renderer_version', 'legacy') == 'react-v1' or public_design_kind(page) is not None


def public_design_is_rendered(page, text):
    from bs4 import BeautifulSoup
    kind = public_design_kind(page)
    soup = BeautifulSoup(text, 'html.parser')
    host = soup.find(attrs={'data-public-design': kind}) if kind else None
    if host is None or host.select_one('.lesson-header') is None or host.select_one('.lesson-footer') is None:
        return False
    return host.select_one('#home-main' if kind == 'home' else '#learning') is not None


def public_catalogue(catalogue):
    grades = {row['id']: row for row in catalogue['grades']}
    subjects = {row['id']: row for row in catalogue['subjects']}
    sections = {row['id']: row for row in catalogue['sections']}
    return {
        'grades': [dict(title=f"{row['slug'].split('-')[0]} класс", slug=row['slug'], order=row['order']) for row in grades.values()],
        'subjects': [dict(title=row['title'], slug=row['slug'], order=row['order'], grade=grades[row['grade_id']]['slug']) for row in subjects.values()],
        'sections': [dict(title=row['title'], slug=row['slug'], order=row['order'], grade=grades[subjects[row['subject_id']]['grade_id']]['slug'], subject=subjects[row['subject_id']]['slug']) for row in sections.values()],
        'topics': [dict(title=row['title'], slug=row['slug'], order=row['order'], url=row['url'], grade=grades[row['grade_id']]['slug'], subject=subjects[row['subject_id']]['slug'], section=sections[row['section_id']]['slug']) for row in catalogue['topics']],
    }
