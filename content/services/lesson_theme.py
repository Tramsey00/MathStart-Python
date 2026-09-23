"""Builds the local CSS and JavaScript asset set for a content page."""

CSS = "mathstart/css/"
JS = "mathstart/js/"


def theme_context(page):
    body = page.body_html

    assets = {
        "theme_before": [
            CSS + name
            for name in (
                "lesson.css",
                "lesson-math.css",
                "lesson-components.css",
                "lesson-diagrams.css",
                "lesson-contents.css",
            )
        ],
        "theme_scripts": [
            JS + "lesson-navigation.js",
        ],
    }

    if page.page_type != "topic":
        assets["theme_before"].append(
            CSS + "site-pages.css"
        )

    if 'data-lesson-widget="power-functions"' in body:
        assets["theme_before"].append(
            CSS + "widgets/power-functions.css"
        )
        assets["theme_scripts"] += [
            JS + "math.js",
            JS + "widgets/power-functions.js",
        ]
    elif "ms-graph-layout" in body:
        assets["theme_before"].append(
            CSS + "widgets/function-graphs.css"
        )

    return assets