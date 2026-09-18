from django.core.management.base import BaseCommand
from django.db import transaction

from content.models import Grade, Subject
from content.wordpress_map import (
    GRADE_STRUCTURE,
    WORDPRESS_CATEGORY_TO_SUBJECT,
)


class Command(BaseCommand):
    help = (
        "Создаёт классы и предметы MathStart. "
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

        grade_created = 0
        grade_updated = 0
        subject_created = 0
        subject_updated = 0

        self.stdout.write(
            "Подготовка структуры классов и предметов MathStart..."
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Режим dry-run: изменения не будут сохранены."
                )
            )

        with transaction.atomic():
            for grade_data in GRADE_STRUCTURE:
                subjects_data = grade_data["subjects"]

                grade, created = Grade.objects.update_or_create(
                    slug=grade_data["slug"],
                    defaults={
                        "title": grade_data["title"],
                        "order": grade_data["order"],
                        "description": grade_data["description"],
                    },
                )

                if created:
                    grade_created += 1
                    action = "создан"
                else:
                    grade_updated += 1
                    action = "обновлён"

                self.stdout.write(
                    f"  Класс: {grade.title} — {action}"
                )

                for subject_data in subjects_data:
                    subject, subject_was_created = (
                        Subject.objects.update_or_create(
                            grade=grade,
                            slug=subject_data["slug"],
                            defaults={
                                "title": subject_data["title"],
                                "order": subject_data["order"],
                                "description": subject_data[
                                    "description"
                                ],
                            },
                        )
                    )

                    if subject_was_created:
                        subject_created += 1
                        subject_action = "создан"
                    else:
                        subject_updated += 1
                        subject_action = "обновлён"

                    self.stdout.write(
                        "    Предмет: "
                        f"{subject.title} — {subject_action}"
                    )

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write("")
        self.stdout.write("Результат:")
        self.stdout.write(
            f"  Классы созданы: {grade_created}"
        )
        self.stdout.write(
            f"  Классы обновлены: {grade_updated}"
        )
        self.stdout.write(
            f"  Предметы созданы: {subject_created}"
        )
        self.stdout.write(
            f"  Предметы обновлены: {subject_updated}"
        )

        self.stdout.write("")
        self.stdout.write(
            "Карта рубрик WordPress:"
        )

        for term_id, mapping in (
            WORDPRESS_CATEGORY_TO_SUBJECT.items()
        ):
            grade_slug, subject_slug = mapping

            self.stdout.write(
                f"  term_id={term_id}: "
                f"{grade_slug} → {subject_slug}"
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
                    "Структура классов и предметов сохранена."
                )
            )