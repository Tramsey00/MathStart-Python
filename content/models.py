from django.db import models
from django.urls import reverse


class Grade(models.Model):
    """Класс обучения: 5 класс, 6 класс и т. д."""

    title = models.CharField(
        "Название",
        max_length=100,
    )
    slug = models.SlugField(
        "Slug",
        max_length=100,
        unique=True,
    )
    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
    )
    description = models.TextField(
        "Описание",
        blank=True,
    )

    class Meta:
        ordering = ("order", "title")
        verbose_name = "Класс"
        verbose_name_plural = "Классы"

    def __str__(self):
        return self.title


class Subject(models.Model):
    """Предмет внутри класса."""

    title = models.CharField(
        "Название",
        max_length=150,
    )
    slug = models.SlugField(
        "Slug",
        max_length=150,
    )
    grade = models.ForeignKey(
        Grade,
        verbose_name="Класс",
        related_name="subjects",
        on_delete=models.CASCADE,
    )
    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
    )
    description = models.TextField(
        "Описание",
        blank=True,
    )

    class Meta:
        ordering = ("grade__order", "order", "title")
        constraints = [
            models.UniqueConstraint(
                fields=("grade", "slug"),
                name="unique_subject_slug_per_grade",
            ),
        ]
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    def __str__(self):
        return f"{self.title} — {self.grade.title}"


class Section(models.Model):
    """Учебный раздел внутри предмета."""

    title = models.CharField(
        "Название",
        max_length=255,
    )
    slug = models.SlugField(
        "Slug",
        max_length=255,
    )
    subject = models.ForeignKey(
        Subject,
        verbose_name="Предмет",
        related_name="sections",
        on_delete=models.CASCADE,
    )
    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
    )
    description = models.TextField(
        "Описание",
        blank=True,
    )

    class Meta:
        ordering = (
            "subject__grade__order",
            "subject__order",
            "order",
            "title",
        )
        constraints = [
            models.UniqueConstraint(
                fields=("subject", "slug"),
                name="unique_section_slug_per_subject",
            ),
        ]
        verbose_name = "Раздел"
        verbose_name_plural = "Разделы"

    def __str__(self):
        return f"{self.title} — {self.subject}"


class ContentPage(models.Model):
    """Страница сайта или отдельная учебная тема."""

    class PageType(models.TextChoices):
        HOME = "home", "Главная"
        GRADE = "grade", "Страница класса"
        SUBJECT = "subject", "Страница предмета"
        TOPIC = "topic", "Учебная тема"
        OGE = "oge", "Подготовка к ОГЭ"
        STATIC = "static", "Обычная страница"

    title = models.CharField(
        "Заголовок",
        max_length=255,
    )
    slug = models.SlugField(
        "Slug",
        max_length=255,
        unique=True,
    )
    page_type = models.CharField(
        "Тип страницы",
        max_length=20,
        choices=PageType.choices,
        default=PageType.TOPIC,
    )

    grade = models.ForeignKey(
        Grade,
        verbose_name="Класс",
        related_name="pages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    subject = models.ForeignKey(
        Subject,
        verbose_name="Предмет",
        related_name="pages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    section = models.ForeignKey(
        Section,
        verbose_name="Раздел",
        related_name="pages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
    )

    body_html = models.TextField(
        "HTML-содержимое",
        blank=True,
    )
    page_css = models.TextField(
        "CSS страницы",
        blank=True,
    )
    page_js = models.TextField(
        "JavaScript страницы",
        blank=True,
    )

    seo_title = models.CharField(
        "SEO title",
        max_length=255,
        blank=True,
    )
    seo_description = models.TextField(
        "SEO description",
        blank=True,
    )

    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
    )

    wordpress_id = models.PositiveBigIntegerField(
        "ID в WordPress",
        null=True,
        blank=True,
        unique=True,
    )
    legacy_url = models.CharField(
        "Старый URL",
        max_length=500,
        blank=True,
    )
    source_file = models.CharField(
        "Исходный файл",
        max_length=500,
        blank=True,
    )
    content_checksum = models.CharField(
        "Контрольная сумма",
        max_length=64,
        blank=True,
    )

    original_created_at = models.DateTimeField(
        "Дата создания в WordPress",
        null=True,
        blank=True,
    )
    original_updated_at = models.DateTimeField(
        "Дата изменения в WordPress",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        "Создано в Django",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        "Изменено в Django",
        auto_now=True,
    )

    class Meta:
        ordering = (
            "grade__order",
            "subject__order",
            "section__order",
            "order",
            "title",
        )
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.page_type == self.PageType.HOME:
            return reverse("content:home")

        return reverse(
            "content:page_detail",
            kwargs={"slug": self.slug},
        )
    @property
    def meta_title(self):
        """
        Возвращает заполненный SEO title
        или автоматически формирует его.
        """
        custom_title = (self.seo_title or "").strip()

        if custom_title:
            return custom_title

        if self.page_type == self.PageType.HOME:
            return "MathStart — математика для 5–10 классов"

        return f"{self.title} | MathStart"

    @property
    def meta_description(self):
        """
        Возвращает заполненное SEO description
        или автоматически формирует описание.
        """
        custom_description = (
            self.seo_description or ""
        ).strip()

        if custom_description:
            return custom_description

        if self.page_type == self.PageType.HOME:
            return (
                "MathStart — образовательный сайт по математике "
                "для 5–9 классов и первые разделы алгебры 10 класса. "
                "Теория, примеры, задания для самопроверки и подготовка к ОГЭ."
            )

        if self.page_type == self.PageType.GRADE:
            grade_title = (
                self.grade.title
                if self.grade
                else self.title
            )

            return (
                f"Математика для {grade_title}: теория, примеры, "
                "памятки и задания для самопроверки на сайте "
                "MathStart."
            )

        if self.page_type == self.PageType.SUBJECT:
            grade_title = (
                self.grade.title
                if self.grade
                else ""
            )

            subject_title = (
                self.subject.title
                if self.subject
                else self.title
            )

            return (
                f"{subject_title}, {grade_title}: учебные темы, "
                "теория, подробные примеры и задания для "
                "самопроверки на сайте MathStart."
            )

        if self.page_type == self.PageType.TOPIC:
            return (
                f"Тема «{self.title}»: теория, примеры, "
                "пошаговые разборы и задания для самопроверки "
                "на образовательном сайте MathStart."
            )

        if self.page_type == self.PageType.OGE:
            return (
                "Подготовка к ОГЭ по математике: теория, "
                "памятки, разборы заданий и материалы "
                "для самостоятельной подготовки."
            )

        return (
            f"{self.title} — информация на образовательном "
            "сайте MathStart."
        )


class LessonPublication(models.Model):
    """Last accepted filesystem edition; the visitor still reads ContentPage."""

    page = models.OneToOneField(
        ContentPage, on_delete=models.CASCADE, related_name="lesson_publication",
    )
    source_path = models.CharField(max_length=500, unique=True)
    published_digest = models.CharField(max_length=64)
    published_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Публикация урока из файлов"
        verbose_name_plural = "Публикации уроков из файлов"


class MediaAsset(models.Model):
    """Изображение, PDF или другой файл из WordPress."""

    title = models.CharField(
        "Название",
        max_length=255,
        blank=True,
    )
    file = models.FileField(
        "Файл",
        upload_to="uploads/",
    )
    old_url = models.CharField(
        "Старый URL",
        max_length=500,
        blank=True,
    )
    alt_text = models.CharField(
        "Альтернативный текст",
        max_length=255,
        blank=True,
    )
    related_page = models.ForeignKey(
        ContentPage,
        verbose_name="Связанная страница",
        related_name="media_assets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    wordpress_id = models.PositiveBigIntegerField(
        "ID в WordPress",
        null=True,
        blank=True,
        unique=True,
    )
    created_at = models.DateTimeField(
        "Добавлено",
        auto_now_add=True,
    )

    class Meta:
        ordering = ("title", "id")
        verbose_name = "Медиафайл"
        verbose_name_plural = "Медиафайлы"

    def __str__(self):
        return self.title or self.file.name


class Redirect(models.Model):
    """Перенаправление со старого адреса на новый."""

    old_path = models.CharField(
        "Старый путь",
        max_length=500,
        unique=True,
    )
    new_path = models.CharField(
        "Новый путь",
        max_length=500,
    )
    is_permanent = models.BooleanField(
        "Постоянный редирект",
        default=True,
    )
    is_active = models.BooleanField(
        "Активен",
        default=True,
    )

    class Meta:
        ordering = ("old_path",)
        verbose_name = "Редирект"
        verbose_name_plural = "Редиректы"

    def __str__(self):
        return f"{self.old_path} → {self.new_path}"
