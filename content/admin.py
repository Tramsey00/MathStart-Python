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


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "order",
    )
    list_editable = ("order",)
    search_fields = (
        "title",
        "slug",
    )
    prepopulated_fields = {
        "slug": ("title",),
    }


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "grade",
        "slug",
        "order",
    )
    list_filter = ("grade",)
    list_editable = ("order",)
    search_fields = (
        "title",
        "slug",
    )
    prepopulated_fields = {
        "slug": ("title",),
    }
    autocomplete_fields = ("grade",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
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
    list_editable = ("order",)
    search_fields = (
        "title",
        "slug",
    )
    prepopulated_fields = {
        "slug": ("title",),
    }
    autocomplete_fields = ("subject",)


@admin.register(ContentPage)
class ContentPageAdmin(admin.ModelAdmin):
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
        "legacy_url",
    )
    # Use the detail form for standalone pages; managed lessons are read-only.
    list_editable = ()
    prepopulated_fields = {
        "slug": ("title",),
    }
    autocomplete_fields = (
        "grade",
        "subject",
        "section",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "content_checksum",
        "lesson_source",
    )

    @admin.display(description="Редактируемый исходник урока")
    def lesson_source(self, obj):
        if obj and obj.pk:
            state = LessonPublication.objects.filter(page_id=obj.pk).first()
            if state:
                return "curriculum/" + state.source_path + " — содержимое и метаданные редактируются в файлах; публикация: manage.py publish_lessons --slug " + obj.slug
        return "Страница редактируется в админке."

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj and LessonPublication.objects.filter(page_id=obj.pk).exists():
            fields += (
                "title", "slug", "page_type", "is_published", "grade", "subject",
                "section", "order", "body_html", "page_css", "page_js", "seo_title",
                "seo_description", "wordpress_id", "legacy_url", "source_file",
                "original_created_at", "original_updated_at",
            )
        return fields

    def get_prepopulated_fields(self, request, obj=None):
        if obj and LessonPublication.objects.filter(page_id=obj.pk).exists():
            return {}
        return super().get_prepopulated_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj and LessonPublication.objects.filter(page_id=obj.pk).exists():
            return False
        return super().has_change_permission(request, obj)
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
            "Содержимое",
            {
                "fields": (
                    "lesson_source",
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
            "Данные миграции",
            {
                "classes": ("collapse",),
                "fields": (
                    "wordpress_id",
                    "legacy_url",
                    "source_file",
                    "content_checksum",
                    "original_created_at",
                    "original_updated_at",
                ),
            },
        ),
        (
            "Служебные даты",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "file",
        "related_page",
        "wordpress_id",
    )
    search_fields = (
        "title",
        "file",
        "old_url",
        "alt_text",
    )
    autocomplete_fields = ("related_page",)


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
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
    list_editable = (
        "is_permanent",
        "is_active",
    )
    search_fields = (
        "old_path",
        "new_path",
    )


admin.site.site_header = "Администрирование MathStart"
admin.site.site_title = "MathStart"
admin.site.index_title = "Управление содержимым сайта"
