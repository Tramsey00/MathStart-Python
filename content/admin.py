from django.contrib import admin

from .models import (
    ContentPage,
    Grade,
    LessonPublication,
    MediaAsset,
    Redirect,
    Section,
    Subject,
)


class SourceManagedAdminMixin:
    """Source-controlled content is view-only in Django admin."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Grade)
class GradeAdmin(SourceManagedAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "order",
    )
    search_fields = (
        "title",
        "slug",
    )
    ordering = (
        "order",
        "title",
    )


@admin.register(Subject)
class SubjectAdmin(SourceManagedAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "grade",
        "slug",
        "order",
    )
    list_filter = ("grade",)
    search_fields = (
        "title",
        "slug",
    )
    ordering = (
        "grade__order",
        "order",
        "title",
    )
    list_select_related = ("grade",)


@admin.register(Section)
class SectionAdmin(SourceManagedAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "subject",
        "slug",
        "order",
    )
    list_filter = (
        "subject__grade",
        "subject",
    )
    search_fields = (
        "title",
        "slug",
    )
    ordering = (
        "subject__grade__order",
        "subject__order",
        "order",
        "title",
    )
    list_select_related = (
        "subject",
        "subject__grade",
    )


@admin.register(ContentPage)
class ContentPageAdmin(SourceManagedAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "page_type",
        "grade",
        "subject",
        "section",
        "order",
        "is_published",
        "updated_at",
    )
    list_filter = (
        "page_type",
        "is_published",
        "grade",
        "subject",
    )
    search_fields = (
        "title",
        "slug",
        "body_html",
    )
    ordering = (
        "page_type",
        "grade__order",
        "subject__order",
        "section__order",
        "order",
        "title",
    )
    list_select_related = (
        "grade",
        "subject",
        "section",
    )

    readonly_fields = (
        "source_location",
        "title",
        "slug",
        "page_type",
        "is_published",
        "grade",
        "subject",
        "section",
        "order",
        "body_html",
        "page_css",
        "page_js",
        "seo_title",
        "seo_description",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Основные данные",
            {
                "fields": (
                    "title",
                    "slug",
                    "page_type",
                    "is_published",
                ),
            },
        ),
        (
            "Структура",
            {
                "fields": (
                    "grade",
                    "subject",
                    "section",
                    "order",
                ),
            },
        ),
        (
            "Источник",
            {
                "fields": (
                    "source_location",
                ),
            },
        ),
        (
            "Содержимое",
            {
                "fields": (
                    "body_html",
                    "page_css",
                    "page_js",
                ),
            },
        ),
        (
            "SEO",
            {
                "fields": (
                    "seo_title",
                    "seo_description",
                ),
            },
        ),
        (
            "Служебные данные",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    @admin.display(description="Источник данных")
    def source_location(self, obj):
        if not obj or not obj.pk:
            return "—"

        publication = (
            LessonPublication.objects
            .filter(page_id=obj.pk)
            .only("source_path")
            .first()
        )

        if publication:
            return f"curriculum/{publication.source_path}"

        return f"site_content/pages/{obj.slug}/"


@admin.register(LessonPublication)
class LessonPublicationAdmin(SourceManagedAdminMixin, admin.ModelAdmin):
    list_display = (
        "page",
        "source_path",
        "published_at",
    )
    search_fields = (
        "page__title",
        "page__slug",
        "source_path",
        "published_digest",
    )
    ordering = ("source_path",)
    list_select_related = ("page",)

    readonly_fields = (
        "page",
        "source_path",
        "published_digest",
        "published_at",
    )


@admin.register(MediaAsset)
class MediaAssetAdmin(SourceManagedAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "file",
        "related_page",
    )
    search_fields = (
        "title",
        "file",
        "alt_text",
    )
    list_select_related = ("related_page",)


@admin.register(Redirect)
class RedirectAdmin(SourceManagedAdminMixin, admin.ModelAdmin):
    list_display = (
        "old_path",
        "new_path",
        "is_permanent",
        "is_active",
    )
    list_filter = (
        "is_permanent",
        "is_active",
    )
    search_fields = (
        "old_path",
        "new_path",
    )
    ordering = ("old_path",)


admin.site.site_header = "MathStart"
admin.site.site_title = "MathStart"
admin.site.index_title = "Содержимое сайта"