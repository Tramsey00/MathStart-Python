"""Plan the lossless extraction of old lesson CSS into shared and local rules.

This is a migration tool, not a runtime dependency.  It deliberately handles
only the ordinary rules and width media queries present in the source corpus;
an unfamiliar construct stops the migration instead of silently rewriting it.
The public ``plan_css_cleanup`` function does not write or publish anything.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from functools import lru_cache
import re

from bs4 import BeautifulSoup


BASE_ASSET = "mathstart/css/lesson-base.css"
BASE_MARKER = 'data-lesson-base="classic"'


@dataclass(frozen=True)
class Declaration:
    name: str
    value: str
    important: bool = False

    def text(self):
        return f"{self.name}: {self.value}{' !important' if self.important else ''};"


@dataclass(frozen=True)
class Rule:
    media: tuple
    selector: str
    declarations: tuple


@dataclass
class PagePlan:
    path: Path
    links: tuple
    css: str
    use_base: bool
    before_rules: int
    after_rules: int
    unused_selectors: int


def split_css(text, delimiter):
    """Split outside quoted strings, comments and parenthesized values."""
    result, start, depth, quote, comment = [], 0, 0, None, False
    index = 0
    while index < len(text):
        char = text[index]
        if comment:
            if text[index:index + 2] == "*/":
                comment = False
                index += 2
                continue
        elif quote:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
        elif text[index:index + 2] == "/*":
            comment = True
            index += 2
            continue
        elif char in "\"'":
            quote = char
        elif char in "([":
            depth += 1
        elif char in ")]":
            depth -= 1
        elif char == delimiter and depth == 0:
            result.append(text[start:index].strip())
            start = index + 1
        index += 1
    if quote or comment or depth:
        raise ValueError("Unbalanced CSS value")
    result.append(text[start:].strip())
    return result


def blocks(css):
    start, depth, quote, comment, opening = 0, 0, None, False, None
    index = 0
    while index < len(css):
        char = css[index]
        if comment:
            if css[index:index + 2] == "*/":
                comment = False
                index += 2
                continue
        elif quote:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
        elif css[index:index + 2] == "/*":
            comment = True
            index += 2
            continue
        elif char in "\"'":
            quote = char
        elif char == "{":
            if depth == 0:
                opening = index
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                yield re.sub(r"/\*.*?\*/", "", css[start:opening], flags=re.S).strip(), css[opening + 1:index].strip()
                start = index + 1
        index += 1
    if depth or quote or comment or re.sub(r"/\*.*?\*/", "", css[start:], flags=re.S).strip():
        raise ValueError("Unsupported or unbalanced CSS")


def canonical_selector(selector):
    selector = re.sub(r"\s+", " ", selector).strip()
    return re.sub(r"\s*([>+~])\s*", r" \1 ", selector)


def parse_rules(css, media=()):
    for selector, body in blocks(css):
        if selector.startswith("@media"):
            match = re.fullmatch(r"@media\s*\(\s*(max|min)-width\s*:\s*(\d+)px\s*\)", selector)
            if not match:
                raise ValueError(f"Unsupported media query: {selector}")
            condition = f"@media ({match[1]}-width: {match[2]}px)"
            yield from parse_rules(body, media + (condition,))
            continue
        if selector.startswith("@"):
            raise ValueError(f"Unsupported CSS directive: {selector}")
        declarations = []
        for item in split_css(re.sub(r"/\*.*?\*/", "", body, flags=re.S), ";"):
            if not item:
                continue
            name, separator, value = item.partition(":")
            if not separator or not re.fullmatch(r"[-\w]+", name.strip()):
                raise ValueError(f"Unsupported CSS declaration: {item}")
            value = value.strip()
            important = bool(re.search(r"\s*!important\s*$", value, flags=re.I))
            value = re.sub(r"\s*!important\s*$", "", value, flags=re.I)
            declarations.append(Declaration(name.strip().lower(), value, important))
        for item in split_css(selector, ","):
            yield Rule(media, canonical_selector(item), tuple(declarations))


def serialize_rules(rules, header=""):
    """Join adjacent equal blocks without changing their cascade order."""
    groups = []
    for rule in rules:
        if not rule.declarations:
            continue
        if groups and groups[-1][0] == rule.media and groups[-1][2] == rule.declarations:
            groups[-1][1].append(rule.selector)
        else:
            groups.append([rule.media, [rule.selector], rule.declarations])
    result = [f"/* {header} */\n"] if header and groups else []
    open_media = ()
    for media, selectors, declarations in groups:
        if media != open_media:
            for level in reversed(range(len(open_media))):
                result.append("  " * level + "}\n")
            for level, condition in enumerate(media):
                result.append("  " * level + condition + " {\n")
            open_media = media
        indent = "  " * len(media)
        result.append((",\n".join(indent + selector for selector in selectors)) + " {\n")
        result.extend(indent + "  " + declaration.text() + "\n" for declaration in declarations)
        result.append(indent + "}\n")
    for level in reversed(range(len(open_media))):
        result.append("  " * level + "}\n")
    return "".join(result).rstrip() + "\n" if groups else ""


def selector_words(selector):
    # A missing class inside :not() does NOT make a selector unused.
    selector = re.sub(r":not\([^)]*\)", "", selector)
    selector = re.sub(r"\[[^]]*\]", "", selector)
    return set(re.findall(r"[.#]([a-zA-Z_][\w-]*)", selector))


def relevant(selector, words):
    return selector_words(selector) <= words


@lru_cache(maxsize=None)
def properties(name):
    """Longhand footprint; sibling longhands do not overwrite one another."""
    sides = ("top", "right", "bottom", "left")
    expanded = {
        "margin": [f"margin-{side}" for side in sides],
        "padding": [f"padding-{side}" for side in sides],
        "border": [f"border-{side}-{part}" for side in sides for part in ("width", "style", "color")] + ["border-image"],
        "border-radius": [f"border-{corner}-radius" for corner in ("top-left", "top-right", "bottom-right", "bottom-left")],
        "background": [f"background-{part}" for part in ("color", "image", "position", "size", "repeat", "origin", "clip", "attachment")],
        "font": ["font-family", "font-size", "font-weight", "font-style", "font-variant", "font-stretch", "line-height", "font-size-adjust", "font-kerning"],
        "flex": ["flex-grow", "flex-shrink", "flex-basis"],
        "flex-flow": ["flex-direction", "flex-wrap"],
        "grid": [f"grid-{part}" for part in ("template-rows", "template-columns", "template-areas", "auto-rows", "auto-columns", "auto-flow")],
        "grid-template": ["grid-template-rows", "grid-template-columns", "grid-template-areas"],
        "grid-area": ["grid-row-start", "grid-row-end", "grid-column-start", "grid-column-end"],
        "grid-row": ["grid-row-start", "grid-row-end"],
        "grid-column": ["grid-column-start", "grid-column-end"],
        "gap": ["row-gap", "column-gap"],
        "place-items": ["align-items", "justify-items"],
        "place-content": ["align-content", "justify-content"],
        "place-self": ["align-self", "justify-self"],
        "outline": ["outline-width", "outline-style", "outline-color"],
        "list-style": ["list-style-type", "list-style-position", "list-style-image"],
        "overflow": ["overflow-x", "overflow-y"],
        "text-decoration": ["text-decoration-line", "text-decoration-color", "text-decoration-style", "text-decoration-thickness"],
        "transition": [f"transition-{part}" for part in ("property", "duration", "delay", "timing-function", "behavior")],
        "animation": [f"animation-{part}" for part in ("name", "duration", "delay", "timing-function", "iteration-count", "direction", "fill-mode", "play-state", "timeline")],
        "columns": ["column-width", "column-count"],
    }
    for part in ("width", "style", "color"):
        expanded[f"border-{part}"] = [f"border-{side}-{part}" for side in sides]
    for side in sides:
        expanded[f"border-{side}"] = [f"border-{side}-{part}" for part in ("width", "style", "color")]
    if name == "all":
        raise ValueError("The CSS 'all' shorthand requires manual review")
    return frozenset(expanded.get(name, [name]))


def conflicting(left, right):
    return left.important == right.important and bool(properties(left.name) & properties(right.name)) and left != right


@lru_cache(maxsize=None)
def specificity(selector):
    # All selectors in the old corpus are ordinary selectors, :not() with a
    # simple argument, and structural/dynamic pseudo classes. Fail closed when
    # a future source introduces specificity-changing functional selectors.
    if re.search(r":(?:is|where|has|nth-child)\([^)]*(?: of |[.#])", selector):
        return None
    selector = re.sub(r":not\(([^()]*(?:\([^()]*\)[^()]*)?)\)", r"\1", selector)
    pseudo_elements = len(re.findall(r"::[-\w]+", selector))
    selector = re.sub(r"::[-\w]+", "", selector)
    attributes = len(re.findall(r"\[[^]]*\]", selector))
    selector = re.sub(r"\[[^]]*\]", "", selector)
    pseudos = len(re.findall(r":[-\w]+(?:\([^)]*\))?", selector))
    selector = re.sub(r":[-\w]+(?:\([^)]*\))?", "", selector)
    ids = len(re.findall(r"#[\w-]+", selector))
    classes = len(re.findall(r"\.[\w-]+", selector))
    selector = re.sub(r"[.#][\w-]+", "", selector)
    elements = len(re.findall(r"\b[a-zA-Z][\w-]*\b", selector))
    return ids, attributes + pseudos + classes, elements + pseudo_elements


class Targets:
    """Conservative overlap for authored HTML, including every dynamic state."""
    def __init__(self, source):
        self.soup = BeautifulSoup(source, "html.parser")
        self.cache = {}
        self.overlaps = {}

    def get(self, selector):
        if selector not in self.cache:
            pseudo = tuple(re.findall(r"::[-\w]+", selector))
            broad = re.sub(r"::[-\w]+", "", selector)
            broad = re.sub(r":(?:hover|focus-visible|disabled)\b", "", broad)
            broad = re.sub(r"\[(?:data-[\w-]+|aria-[\w-]+|open)(?:[^]]*)\]", "", broad)
            try:
                nodes = frozenset(id(node) for node in self.soup.select(broad))
            except Exception:
                nodes = frozenset(id(node) for node in self.soup.find_all())
            self.cache[selector] = (pseudo, nodes)
        return self.cache[selector]

    def overlap(self, left, right):
        key = (left, right)
        if key not in self.overlaps:
            self.overlaps[key] = self._overlap(left, right)
        return self.overlaps[key]

    def _overlap(self, left, right):
        if left == right:
            return True
        left_specificity, right_specificity = specificity(left), specificity(right)
        if left_specificity is not None and right_specificity is not None and left_specificity != right_specificity:
            return False
        left_pseudo, left_nodes = self.get(left)
        right_pseudo, right_nodes = self.get(right)
        return left_pseudo == right_pseudo and bool(left_nodes & right_nodes)


def choose_base(pages, minimum_uses=12):
    """Only add properties already defined for this selector on every user page.

    The most common value is just a default. Every differing authored value is
    retained after this sheet. In particular, an !important default is allowed
    only when all affected pages already have an !important declaration.
    """
    keys = defaultdict(list)
    for page in pages:
        by_key = defaultdict(list)
        for rule in page["rules"]:
            by_key[(rule.media, rule.selector)].extend(rule.declarations)
        page["by_key"] = by_key
        for key, declarations in by_key.items():
            keys[key].append((page, declarations))
    base = []
    for key, users in keys.items():
        if len(users) < minimum_uses:
            continue
        applicable = [page for page in pages if relevant(key[1], page["words"])]
        if len(applicable) != len(users):
            continue
        names = set.intersection(*(set(declaration.name for declaration in declarations) for _, declarations in users))
        if not names:
            continue
        values = {name: Counter() for name in names}
        order = {}
        important_allowed = {name: all(any(declaration.name == name and declaration.important for declaration in declarations) for _, declarations in users) for name in names}
        for _, declarations in users:
            last = {}
            for declaration in declarations:
                if declaration.name not in names:
                    continue
                order.setdefault(declaration.name, len(order))
                if not declaration.important or important_allowed[declaration.name]:
                    last[declaration.name] = declaration
            for name, declaration in last.items():
                values[name][declaration] += 1
        chosen = tuple(values[name].most_common(1)[0][0] for name in sorted(names, key=order.get) if values[name])
        if chosen:
            base.append(Rule(key[0], key[1], chosen))
    return base


def local_rules(page, base):
    """Remove common declarations only if moving them earlier is harmless.

    A declaration stays local when an equal-specificity competing selector can
    override it, or a shorthand/longhand could depend on its original position.
    The overlap test considers open, hover, ready, pressed and disabled states
    together, so these controls keep their original cascade as well.
    """
    targets = Targets(page["source"])
    common_flat = [(rule.media, rule.selector, declaration) for rule in base for declaration in rule.declarations]
    common = {item: index for index, item in enumerate(common_flat)}
    original = [(rule.media, rule.selector, declaration) for rule in page["rules"] for declaration in rule.declarations]
    last_authored = {(media, selector, declaration.name, declaration.important): index for index, (media, selector, declaration) in enumerate(original)}
    earlier = defaultdict(set)
    shared_by_property = defaultdict(set)
    for index, (_, _, declaration) in enumerate(common_flat):
        for name in properties(declaration.name):
            shared_by_property[(name, declaration.important)].add(index)
    removed = set()
    for index, item in enumerate(original):
        media, selector, declaration = item
        base_index = common.get(item)
        keys = [(name, declaration.important) for name in properties(declaration.name)]
        if base_index is not None:
            obstruction = False
            # Earlier authored competitors may move with us only when their
            # relative order in the shared sheet is unchanged.
            for other_index in set().union(*(earlier[key] for key in keys)):
                other = original[other_index]
                if not conflicting(declaration, other[2]) or not targets.overlap(selector, other[1]):
                    continue
                if other_index not in removed or common[other] > base_index:
                    obstruction = True
                    break
            # A later shared competitor is safe if its authored counterpart
            # also followed this declaration. It will still win in that state,
            # whether the counterpart stays local or moves to the shared sheet.
            if not obstruction:
                for other_index in set().union(*(shared_by_property[key] for key in keys)):
                    if other_index <= base_index:
                        continue
                    other_media, other_selector, other_declaration = common_flat[other_index]
                    if not conflicting(declaration, other_declaration) or not targets.overlap(selector, other_selector):
                        continue
                    counterpart = last_authored.get((other_media, other_selector, other_declaration.name, other_declaration.important), -1)
                    if counterpart <= index:
                        obstruction = True
                        break
            if not obstruction:
                removed.add(index)
        for key in keys:
            earlier[key].add(index)
    result, index = [], 0
    for rule in page["rules"]:
        kept = tuple(declaration for offset, declaration in enumerate(rule.declarations) if index + offset not in removed)
        index += len(rule.declarations)
        if kept:
            result.append(Rule(rule.media, rule.selector, kept))
    return result


def plan_css_cleanup(project_root):
    root = Path(project_root)
    pages = []
    for path in sorted((root / "curriculum").rglob("body.html")):
        source = path.read_bytes().decode("utf-8")
        soup = BeautifulSoup(source, "html.parser")
        links = soup.select("link[data-lesson-legacy-style]")
        if not links:
            continue
        script_path = path.with_name("page.js")
        script = script_path.read_text(encoding="utf-8") if script_path.exists() else ""
        words = set(re.findall(r"[a-zA-Z_][\w-]*", source + script))
        all_rules = []
        for link in links:
            href = link["href"]
            if not re.fullmatch(r"/static/mathstart/css/legacy/[a-f0-9]+\.css", href):
                raise ValueError(f"Unexpected legacy CSS link: {href}")
            all_rules.extend(parse_rules((root / href.removeprefix("/")).read_text(encoding="utf-8")))
        filtered = [rule for rule in all_rules if relevant(rule.selector, words)]
        # An identical later rule has exactly the same specificity and media
        # condition; retaining its last occurrence preserves the cascade.
        seen, unique = set(), []
        for rule in reversed(filtered):
            if rule not in seen:
                seen.add(rule)
                unique.append(rule)
        rules = list(reversed(unique))
        pages.append({"path": path, "source": source, "words": words, "links": tuple(link["href"] for link in links), "all_rules": all_rules, "rules": rules, "unused": len(all_rules) - len(filtered), "classic": "ms-v2" not in (soup.select_one(".ms-post").get("class") or [])})
    classic = [page for page in pages if page["classic"]]
    base = choose_base(classic)
    plans = []
    for page in pages:
        rules = local_rules(page, base) if page["classic"] else page["rules"]
        css = serialize_rules(rules, "Особенности этого урока. Общие элементы оформлены в lesson-base.css и lesson.css.")
        plans.append(PagePlan(page["path"], page["links"], css, page["classic"], len(page["all_rules"]), len(rules), page["unused"]))
    return {"base_asset": BASE_ASSET, "base_marker": BASE_MARKER, "base_css": serialize_rules(base, "Общие базовые элементы уроков. Существующие мобильные правила сохранены без изменения дизайна."), "base_rules": base, "pages": plans, "source_pages": pages}


def build_css_plan(project_root):
    """Small serializable interface for the backed-up asset migration command."""
    from .lesson_components import SourceTree

    plan = plan_css_cleanup(project_root)
    lessons = []
    for page in plan["pages"]:
        source = page.path.read_bytes().decode("utf-8")
        tree = SourceTree(source)
        ranges = [(node.start, node.end) for node in tree.elements if node.tag == "link" and "data-lesson-legacy-style" in node.attrs]
        lessons.append({"path": page.path, "page_css": page.css, "base": page.use_base, "ranges": ranges})
    stats = {
        "lessons": len(lessons),
        "base_rules": len(plan["base_rules"]),
        "base_bytes": len(plan["base_css"].encode("utf-8")),
        "original_selectors": sum(page.before_rules for page in plan["pages"]),
        "local_selectors": sum(page.after_rules for page in plan["pages"]),
        "unused_selectors_removed": sum(page.unused_selectors for page in plan["pages"]),
        "lessons_without_local_css": sum(not page.css for page in plan["pages"]),
        "largest_local_css_bytes": max((len(page.css.encode("utf-8")) for page in plan["pages"]), default=0),
    }
    return {"base_asset": plan["base_asset"], "base_marker": plan["base_marker"], "base_css": plan["base_css"], "lessons": lessons, "stats": stats}
