from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from content.models import Section, Subject
from content.wordpress_map import (
    EXPECTED_SECTION_TOTAL,
    SECTION_STRUCTURE,
)


class Command(BaseCommand):
    help = (
        "Создаёт учебные разделы MathStart. "
        "Команда безопасна для повторного запуска."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Проверить импорт без сохранения изменений "
                "в базе Django."
            ),
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        created_count = 0
        updated_count = 0
        processed_count = 0

        self.stdout.write(
            "Подготовка учебных разделов MathStart..."
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Режим dry-run: изменения не будут сохранены."
                )
            )

        with transaction.atomic():
            for subject_key, sections in SECTION_STRUCTURE.items():
                grade_slug, subject_slug = subject_key

                try:
                    subject = Subject.objects.select_related(
                        "grade"
                    ).get(
                        grade__slug=grade_slug,
                        slug=subject_slug,
                    )
                except Subject.DoesNotExist as error:
                    raise CommandError(
                        "Не найден предмет: "
                        f"{grade_slug} → {subject_slug}. "
                        "Сначала выполните "
                        "import_wordpress_structure."
                    ) from error

                self.stdout.write("")
                self.stdout.write(
                    f"{subject.grade.title} — {subject.title}:"
                )

                for title, slug, order in sections:
                    section, was_created = (
                        Section.objects.update_or_create(
                            subject=subject,
                            slug=slug,
                            defaults={
                                "title": title,
                                "order": order,
                                "description": "",
                            },
                        )
                    )

                    processed_count += 1

                    if was_created:
                        created_count += 1
                        action = "создан"
                    else:
                        updated_count += 1
                        action = "обновлён"

                    self.stdout.write(
                        f"  {order}. {section.title} — {action}"
                    )

            if processed_count != EXPECTED_SECTION_TOTAL:
                raise CommandError(
                    "Количество разделов в карте отличается "
                    f"от ожидаемого: {processed_count} вместо "
                    f"{EXPECTED_SECTION_TOTAL}."
                )

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write("")
        self.stdout.write("Результат:")
        self.stdout.write(
            f"  Обработано разделов: {processed_count}"
        )
        self.stdout.write(
            f"  Создано разделов: {created_count}"
        )
        self.stdout.write(
            f"  Обновлено разделов: {updated_count}"
        )

        self.stdout.write("")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Dry-run завершён. "
                    "Изменения в базе Django отменены."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Все учебные разделы сохранены."
                )
            )