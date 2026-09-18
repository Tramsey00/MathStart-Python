from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import ContentPage
from .services.lesson_theme import theme_context


def build_page_context(request, page):
    """
    Общий контекст для отображения страницы MathStart.
    """
    canonical_url = request.build_absolute_uri(
        page.get_absolute_url()
    )

    context = {
        "page": page,
        "canonical_url": canonical_url,
    }
    context.update(theme_context(page))
    if page.slug == "karta-sajta":
        published = ContentPage.objects.filter(is_published=True)
        context["catalogue_pages"] = published.exclude(
            page_type=ContentPage.PageType.TOPIC,
        )
        context["catalogue_topics"] = published.filter(
            page_type=ContentPage.PageType.TOPIC,
        ).select_related("grade", "subject", "section").order_by(
            "grade__order", "subject__order", "subject_id",
            "section__order", "section_id", "order", "title",
        )
    return context


def home(request):
    page = get_object_or_404(
        ContentPage,
        page_type=ContentPage.PageType.HOME,
        is_published=True,
    )

    return render(
        request,
        "page_detail.html",
        build_page_context(request, page),
    )


def page_detail(request, slug):
    page = get_object_or_404(
        ContentPage,
        slug=slug,
        is_published=True,
    )

    return render(
        request,
        "page_detail.html",
        build_page_context(request, page),
    )


def robots_txt(request):
    """
    Формирует robots.txt с актуальным адресом sitemap.
    """
    sitemap_url = request.build_absolute_uri(
        reverse("sitemap")
    )

    content = "\n".join(
        (
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            "",
            f"Sitemap: {sitemap_url}",
            "",
        )
    )

    return HttpResponse(
        content,
        content_type="text/plain; charset=utf-8",
    )
