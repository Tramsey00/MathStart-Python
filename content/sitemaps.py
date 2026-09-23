from django.contrib.sitemaps import Sitemap

from .models import ContentPage


class ContentPageSitemap(Sitemap):
    """
    XML-карта всех опубликованных страниц MathStart.
    """

    def items(self):
        return ContentPage.objects.filter(
            is_published=True,
        ).order_by("id")

    def location(self, page):
        return page.get_absolute_url()


    def lastmod(self, page):
        return page.updated_at


    def changefreq(self, page):
        if page.page_type == ContentPage.PageType.HOME:
            return "weekly"

        if page.page_type in {
            ContentPage.PageType.GRADE,
            ContentPage.PageType.SUBJECT,
        }:
            return "weekly"

        if page.page_type == ContentPage.PageType.TOPIC:
            return "monthly"

        return "monthly"

    def priority(self, page):
        if page.page_type == ContentPage.PageType.HOME:
            return 1.0

        if page.page_type in {
            ContentPage.PageType.GRADE,
            ContentPage.PageType.SUBJECT,
        }:
            return 0.8

        if page.page_type == ContentPage.PageType.TOPIC:
            return 0.7

        return 0.5