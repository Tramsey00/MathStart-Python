import html
import re
import unicodedata
from collections import defaultdict
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from content.models import ContentPage, Section, Subject


EXPECTED_NAVIGATION_PAGE_COUNT = 11
EXPECTED_SECTION_COUNT = 60
EXPECTED_TOPIC_COUNT = 250


def extract_slug_from_url(url):
    """
    Извлекает последний сегмент URL.

    Поддерживает:
    http://localhost/mathstart/topic-slug/
    https://example.ru/topic-slug/
    /topic-slug/
    """
    if not url:
        return ""

    url = url.strip()

    if (
        url.startswith("#")
        or url.startswith("mailto:")
        or url.startswith("tel:")
        or url.startswith("javascript:")
    ):
        return ""

    parsed_url = urlparse(url)
    path = unquote(parsed_url.path or "")
    path_parts = [
        part
        for part in path.strip("/").split("/")
        if part
    ]

    if not path_parts:
        return ""

    return path_parts[-1].strip()


def normalize_title(value):
    """
    Нормализует заголовок для резервного сопоставления.

    Например:
    «1.2. Линейная функция y = kx»
    и
    «Линейная функция y = kx»
    будут считаться одинаковыми.
    """
    value = html.unescape(value or "")
    value = unicodedata.normalize("NFKC", value)
    value = value.replace("\xa0", " ")
    value = value.replace("ё", "е").replace("Ё", "Е")

    value = re.sub(
        r"^\s*\d+(?:\.\d+)+\.?\s*",
        "",
        value,
    )

    value = value.lower()

    value = re.sub(
        r"[^0-9a-zа-я]+",
        " ",
        value,
        flags=re.IGNORECASE,
    )

    return " ".join(value.split())


class Command(BaseCommand):
    help = (
        "Распределяет 250 учебных тем по 60 разделам, "
        "используя аккордеоны страниц классов и предметов."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Проверить распределение без сохранения "
                "изменений в базе Django."
            ),
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        navigation_pages = list(
            ContentPage.objects.select_related(
                "grade",
                "subject",
            ).filter(
                page_type__in=(
                    ContentPage.PageType.GRADE,
                    ContentPage.PageType.SUBJECT,
                ),
                is_published=True,
            )
        )

        navigation_pages.sort(
            key=lambda page: (
                page.grade.order if page.grade else 999,
                page.subject.order if page.subject else 0,
                page.title,
            )
        )

        if len(navigation_pages) != EXPECTED_NAVIGATION_PAGE_COUNT:
            raise CommandError(
                "Найдено неожиданное количество навигационных "
                f"страниц: {len(navigation_pages)} вместо "
                f"{EXPECTED_NAVIGATION_PAGE_COUNT}."
            )

        all_topics = list(
            ContentPage.objects.select_related(
                "grade",
                "subject",
                "section",
            ).filter(
                page_type=ContentPage.PageType.TOPIC,
                is_published=True,
            )
        )

        if len(all_topics) != EXPECTED_TOPIC_COUNT:
            raise CommandError(
                "Найдено неожиданное количество учебных тем: "
                f"{len(all_topics)} вместо "
                f"{EXPECTED_TOPIC_COUNT}."
            )

        topics_by_subject = defaultdict(list)

        for topic in all_topics:
            if topic.subject_id is None:
                raise CommandError(
                    f"У темы «{topic.title}» не указан предмет."
                )

            topics_by_subject[topic.subject_id].append(topic)

        assignments = []
        assigned_topic_ids = set()
        parsed_section_count = 0
        parsed_topic_count = 0
        title_fallback_count = 0
        validation_errors = []

        self.stdout.write(
            "Чтение структуры из страниц MathStart..."
        )
        self.stdout.write("")

        for navigation_page in navigation_pages:
            if navigation_page.page_type == ContentPage.PageType.GRADE:
                try:
                    subject = Subject.objects.select_related(
                        "grade"
                    ).get(
                        grade=navigation_page.grade,
                        slug="matematika",
                    )
                except Subject.DoesNotExist as error:
                    raise CommandError(
                        "Для страницы класса не найден предмет "
                        f"«Математика»: {navigation_page.title}."
                    ) from error
            else:
                subject = navigation_page.subject

            if subject is None:
                raise CommandError(
                    "У страницы предмета не указан предмет: "
                    f"{navigation_page.title}."
                )

            sections = list(
                Section.objects.filter(
                    subject=subject,
                ).order_by(
                    "order",
                    "id",
                )
            )

            subject_topics = topics_by_subject.get(
                subject.id,
                [],
            )

            topics_by_slug = {
                topic.slug: topic
                for topic in subject_topics
            }

            topics_by_title = defaultdict(list)

            for topic in subject_topics:
                topics_by_title[
                    normalize_title(topic.title)
                ].append(topic)

            soup = BeautifulSoup(
                navigation_page.body_html,
                "lxml",
            )

            accordions = soup.select(
                "details.ms-accordion"
            )

            if len(accordions) != len(sections):
                validation_errors.append(
                    f"{navigation_page.title}: "
                    f"в HTML найдено разделов {len(accordions)}, "
                    f"а в Django — {len(sections)}."
                )
                continue

            self.stdout.write(
                f"{subject.grade.title} — {subject.title}: "
                f"{len(sections)} разделов, "
                f"{len(subject_topics)} тем"
            )

            subject_assigned_ids = set()
            subject_link_count = 0

            for section, accordion in zip(
                sections,
                accordions,
            ):
                topic_order = 0

                for link in accordion.find_all(
                    "a",
                    href=True,
                ):
                    href = link.get("href", "")
                    linked_slug = extract_slug_from_url(
                        href
                    )

                    if not linked_slug:
                        continue

                    topic = topics_by_slug.get(
                        linked_slug
                    )

                    match_method = "slug"

                    if topic is None:
                        linked_title = normalize_title(
                            link.get_text(
                                " ",
                                strip=True,
                            )
                        )

                        title_candidates = topics_by_title.get(
                            linked_title,
                            [],
                        )

                        if len(title_candidates) == 1:
                            topic = title_candidates[0]
                            match_method = "title"

                        elif len(title_candidates) > 1:
                            validation_errors.append(
                                f"{navigation_page.title}: "
                                "неоднозначное совпадение по "
                                f"заголовку ссылки «"
                                f"{link.get_text(' ', strip=True)}»."
                            )
                            continue

                        else:
                            validation_errors.append(
                                f"{navigation_page.title}: "
                                "не найдена тема для ссылки "
                                f"«{href}»."
                            )
                            continue

                    if topic.subject_id != subject.id:
                        validation_errors.append(
                            f"Тема «{topic.title}» связана "
                            "с другим предметом."
                        )
                        continue

                    if topic.id in assigned_topic_ids:
                        validation_errors.append(
                            f"Тема «{topic.title}» встречается "
                            "в навигации более одного раза."
                        )
                        continue

                    topic_order += 1
                    subject_link_count += 1
                    parsed_topic_count += 1

                    assigned_topic_ids.add(topic.id)
                    subject_assigned_ids.add(topic.id)

                    if match_method == "title":
                        title_fallback_count += 1

                    assignments.append(
                        {
                            "topic": topic,
                            "section": section,
                            "order": topic_order,
                        }
                    )

                if topic_order == 0:
                    validation_errors.append(
                        f"Раздел «{section.title}» не содержит "
                        "ни одной распознанной темы."
                    )

                parsed_section_count += 1

            expected_subject_topic_ids = {
                topic.id
                for topic in subject_topics
            }

            missing_subject_topics = (
                expected_subject_topic_ids
                - subject_assigned_ids
            )

            if missing_subject_topics:
                missing_titles = [
                    topic.title
                    for topic in subject_topics
                    if topic.id in missing_subject_topics
                ]

                validation_errors.append(
                    f"{subject.grade.title} — "
                    f"{subject.title}: не распределены темы: "
                    + "; ".join(missing_titles)
                )

            if subject_link_count != len(subject_topics):
                validation_errors.append(
                    f"{subject.grade.title} — "
                    f"{subject.title}: в аккордеонах найдено "
                    f"{subject_link_count} тем, "
                    f"в базе находится {len(subject_topics)}."
                )

        if parsed_section_count != EXPECTED_SECTION_COUNT:
            validation_errors.append(
                "Обработано неожиданное количество разделов: "
                f"{parsed_section_count} вместо "
                f"{EXPECTED_SECTION_COUNT}."
            )

        if parsed_topic_count != EXPECTED_TOPIC_COUNT:
            validation_errors.append(
                "Обработано неожиданное количество тем: "
                f"{parsed_topic_count} вместо "
                f"{EXPECTED_TOPIC_COUNT}."
            )

        all_topic_ids = {
            topic.id
            for topic in all_topics
        }

        missing_global_topics = (
            all_topic_ids - assigned_topic_ids
        )

        if missing_global_topics:
            missing_titles = [
                topic.title
                for topic in all_topics
                if topic.id in missing_global_topics
            ]

            validation_errors.append(
                "Не назначены разделы для тем: "
                + "; ".join(missing_titles)
            )

        if validation_errors:
            error_preview = "\n".join(
                f"  - {error}"
                for error in validation_errors[:30]
            )

            if len(validation_errors) > 30:
                error_preview += (
                    "\n  - ... и ещё "
                    f"{len(validation_errors) - 30} ошибок."
                )

            raise CommandError(
                "Распределение остановлено из-за ошибок:\n"
                f"{error_preview}"
            )

        self.stdout.write("")
        self.stdout.write("Предварительный результат:")
        self.stdout.write(
            f"  Навигационных страниц: "
            f"{len(navigation_pages)}"
        )
        self.stdout.write(
            f"  Распознано разделов: "
            f"{parsed_section_count}"
        )
        self.stdout.write(
            f"  Распознано тем: {parsed_topic_count}"
        )
        self.stdout.write(
            "  Резервных совпадений по заголовку: "
            f"{title_fallback_count}"
        )

        if dry_run:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "Режим dry-run: изменения не будут "
                    "сохранены."
                )
            )

        changed_count = 0
        unchanged_count = 0

        with transaction.atomic():
            for assignment in assignments:
                topic = assignment["topic"]
                section = assignment["section"]
                topic_order = assignment["order"]

                if (
                    topic.section_id == section.id
                    and topic.order == topic_order
                ):
                    unchanged_count += 1
                    continue

                topic.section = section
                topic.order = topic_order

                topic.save(
                    update_fields=(
                        "section",
                        "order",
                        "updated_at",
                    )
                )

                changed_count += 1

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write("")
        self.stdout.write("Результат:")
        self.stdout.write(
            f"  Изменено тем: {changed_count}"
        )
        self.stdout.write(
            f"  Уже соответствовали карте: "
            f"{unchanged_count}"
        )
        self.stdout.write(
            f"  Всего обработано: "
            f"{len(assignments)}"
        )
        self.stdout.write("")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Dry-run завершён. Изменения "
                    "в базе Django отменены."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Все 250 тем распределены "
                    "по 60 учебным разделам."
                )
            )