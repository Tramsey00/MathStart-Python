"""The public page only chooses known local assets; it never reads lesson files."""
MARKER = 'data-lesson-theme="power-v2"'
CSS = "mathstart/css/"
JS = "mathstart/js/"


def theme_context(page):
    body = page.body_html
    if MARKER not in body:
        return {}
    assets = {
        "theme_enabled": True,
        "theme_before": [CSS + name for name in (
            "lesson.css", "lesson-math.css", "lesson-components.css", "lesson-diagrams.css", "lesson-contents.css",
        )],
        "theme_scripts": [JS + "lesson-navigation.js"],
    }
    if page.page_type != "topic":
        assets["theme_before"].append(CSS + "site-pages.css")
    if 'data-lesson-widget="power-functions"' in body:
        assets["theme_before"].append(CSS + "widgets/power-functions.css")
        assets["theme_scripts"] += [JS + "math.js", JS + "widgets/power-functions.js"]
    elif 'ms-graph-layout' in body:
        assets["theme_before"].append(CSS + "widgets/function-graphs.css")
    return assets
