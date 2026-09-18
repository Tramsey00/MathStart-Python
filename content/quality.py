"""Checks for authoring debris and broken illustrations in published HTML."""
import re
from collections import Counter
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

from bs4 import BeautifulSoup


AUTHORING_MARKERS = re.compile(
    r'далее\s+здесь|здесь\s+можно\s+(?:изменить|редактировать|вставить|добавить)'
    r'|(?:изменить|редактировать|вставить)\s+html'
    r'|html[-\s]*код|\bTODO\b|заглушк|контент\s+будет\s+добавлен'
    r'|страница\s+в\s+разработке|example@|WordPress'
    r'|\[(?:contact-form-7|metaslider|ml_gallery|wshs_list)\b',
    re.IGNORECASE,
)


def inspect_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    issues = []
    ids = Counter(e['id'] for e in soup.select('[id]'))
    for ident, count in ids.items():
        if count > 1:
            issues.append({'kind': 'duplicate_id', 'detail': ident})
    for link in soup.select('a[href]'):
        parsed = urlsplit(link['href'])
        if not parsed.path and not parsed.netloc and parsed.fragment:
            if unquote(parsed.fragment) not in ids:
                issues.append({'kind': 'missing_anchor', 'detail': link['href']})
    svg_count = 0
    for raw in re.findall(r'<svg\b.*?</svg>', html, re.DOTALL | re.IGNORECASE):
        index = svg_count
        svg_count += 1
        try:
            svg = ElementTree.fromstring(raw)
            box = svg.get('viewBox', svg.get('viewbox', '')).split()
            if len(box) != 4 or any(float(value) <= 0 for value in box[2:]):
                issues.append({'kind': 'invalid_svg_viewbox', 'detail': index})
        except (ElementTree.ParseError, ValueError):
            issues.append({'kind': 'invalid_svg', 'detail': index})
        for ident in re.findall(r'url\(#([^\)]+)\)', raw):
            if ident not in ids:
                issues.append({'kind': 'missing_svg_reference', 'detail': ident})
    for element in soup(['style', 'script']):
        element.decompose()
    text = ' '.join(soup.get_text(' ', strip=True).split())
    for match in AUTHORING_MARKERS.finditer(text):
        issues.append({'kind': 'authoring_text', 'detail': text[max(0, match.start()-35):match.end()+80]})
    return {'svg_count': svg_count, 'issues': issues}
