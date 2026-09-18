"""Render shared lesson components while leaving authored HTML/SVG untouched.

HTMLParser records source ranges: unlike DOM reserialization, slicing preserves
formula markup, SVG attribute case, inline scripts and whitespace inside blocks.
"""
import re
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser

from django.template.loader import render_to_string


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


@dataclass
class Element:
    tag: str
    attrs: dict
    start: int
    inner_start: int
    inner_end: int = 0
    end: int = 0
    children: list = field(default_factory=list)
    parent: object = None

    def has_class(self, value):
        return value in self.attrs.get("class", "").split()


class SourceTree(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.offsets = [0] + [match.end() for match in re.finditer("\n", source)]
        self.elements, self.stack = [], []
        self.feed(source)
        self.close()

    def source_offset(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        start = self.source_offset()
        node = Element(tag, dict(attrs), start, start + len(self.get_starttag_text()))
        if self.stack:
            node.parent = self.stack[-1]
            node.parent.children.append(node)
        self.elements.append(node)
        if tag in VOID:
            node.inner_end = node.end = node.inner_start
        else:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        node = self.elements[-1]
        if self.stack and self.stack[-1] is node:
            self.stack.pop()
        node.inner_end = node.end = node.inner_start

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].tag == tag:
                node = self.stack[index]
                node.inner_end = self.source_offset()
                node.end = self.source.find(">", node.inner_end) + 1
                del self.stack[index:]
                break

    def inner(self, node):
        return self.source[node.inner_start:node.inner_end]


def text_only(fragment):
    return " ".join(unescape(re.sub(r"<[^>]+>", "", fragment)).split())


def replace_ranges(source, replacements):
    for start, end, value in sorted(replacements, reverse=True):
        source = source[:start] + value + source[end:]
    return source


def component(name, value):
    return render_to_string(f"lessons/components/{name}.html", {name: value}).strip()


def render_legacy_contents(source):
    """Build the shared contents from real section headings on every publish."""
    tree = SourceTree(source)
    root = next((node for node in tree.elements if node.has_class("ms-legacy-lesson")), None)
    toc = next((node for node in tree.elements if node.has_class("ms-desktop-toc")), None)
    if not root or not toc:
        raise ValueError("В уроке отсутствует общий блок содержания.")
    entries = []
    for section in root.children:
        if section.tag != "section" or not (section.has_class("ms-section") or section.has_class("ms-section-soft")):
            continue
        heading = next((node for node in tree.elements if node.tag == "h2" and section.inner_start <= node.start < section.inner_end), None)
        if not heading:
            continue
        if not section.attrs.get("id"):
            raise ValueError("У нового раздела необходимо указать уникальный id для содержания.")
        title = re.sub(r"^\d+\.\s*", "", text_only(tree.inner(heading)))
        practice = bool(re.search(r"самопроверк|самостоятельн|проверь|задания", title, re.I))
        tasks = sum(node.has_class("ms-task") or node.has_class("v2-task") for node in tree.elements if section.start < node.start < section.end)
        if not tasks:
            tasks = sum(node.has_class("ms-answer") or node.has_class("v2-answer") for node in tree.elements if section.start < node.start < section.end)
        note = f"Заданий с решениями: {tasks}" if practice and tasks else ""
        entries.append({"id": section.attrs["id"], "title": title, "note": note, "practice": practice})
    html = component("contents", {"entries": entries})
    html = html.replace('class="ms-lesson-toc"', 'class="ms-lesson-toc ms-desktop-toc"', 1)
    return replace_ranges(source, [(toc.start, toc.end, html)])


def render_exercises(fragment):
    tree = SourceTree(fragment)
    changes = []
    for node in tree.elements:
        if not node.has_class("v2-task"):
            continue
        question = next((child for child in node.children if child.tag == "p"), None)
        answer = next((child for child in node.children if child.has_class("ms-answer")), None)
        if not question or not answer:
            raise ValueError("У задания отсутствует вопрос или решение.")
        label = next((child for child in question.children if child.tag == "strong"), None)
        answer_body = next((child for child in answer.children if child.tag == "div"), None)
        number = re.fullmatch(r"Задание (\d+)\.", text_only(tree.inner(label))) if label else None
        if not number or not answer_body:
            raise ValueError("Неподдерживаемая структура задания.")
        value = {"number": int(number[1]), "id": node.attrs.get("id"),
                 "question_html": fragment[label.end:question.inner_end].lstrip(),
                 "answer_html": tree.inner(answer_body)}
        changes.append((node.start, node.end, component("exercise", value)))
    return replace_ranges(fragment, changes)


def render_component_lesson(source):
    tree = SourceTree(source)
    root = next((node for node in tree.elements if node.has_class("ms-lesson-page")), None)
    if not root or root.attrs.get("data-lesson-theme") != "power-v2":
        raise ValueError("Урок должен использовать общий шаблон power-v2.")
    changes = []
    for section in root.children:
        if section.tag != "section" or not (section.has_class("ms-section") or section.has_class("ms-section-soft")):
            continue
        heading = next((child for child in section.children if child.tag == "h2"), None)
        if not heading:
            raise ValueError("В учебном разделе отсутствует h2.")
        title = text_only(tree.inner(heading))
        numbered = re.fullmatch(r"(\d+)\.\s+(.+)", title)
        body = source[heading.end:section.inner_end]
        value = {"id": section.attrs.get("id"), "title": numbered[2] if numbered else title,
                 "number": int(numbered[1]) if numbered else None,
                 "soft": section.has_class("ms-section-soft"), "body_html": render_exercises(body)}
        changes.append((section.start, section.end, component("section", value)))
    contents = next((node for node in root.children if node.has_class("ms-lesson-toc")), None)
    if contents:
        entries = []
        for link in tree.elements:
            if not (contents.start < link.start < contents.end and link.has_class("ms-toc-link")):
                continue
            nested = [node for node in tree.elements if link.start < node.start < link.end]
            title = next(node for node in nested if node.tag == "strong")
            note = next((node for node in nested if node.tag == "small"), None)
            entries.append({"id": link.attrs["href"][1:], "title": text_only(tree.inner(title)),
                            "note": text_only(tree.inner(note)) if note else ""})
        changes.append((contents.start, contents.end, component("contents", {"entries": entries})))
    return replace_ranges(source, changes)
