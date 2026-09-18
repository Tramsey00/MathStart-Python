from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from content.models import ContentPage, MediaAsset


class Command(BaseCommand):
    help = (
        "Ищет использование медиафайлов в HTML/CSS/JS страниц "
        "и привязывает MediaAsset.related_page, если файл найден "
        "ровно на одной странице."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Проверить связи без сохранения изменений.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        assets = list(
            MediaAsset.objects.select_related("related_page")
            .all()
            .order_by("id")
        )

        self.stdout.write(
            f"Проверка использования {len(assets)} медиафайлов..."
        )

        linked_count = 0
        cleared_count = 0
        unchanged_count = 0
        ambiguous_count = 0
        unused_count = 0

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Режим dry-run: изменения не будут сохранены."
                )
            )

        with transaction.atomic():
            for asset in assets:
                if not asset.file:
                    unused_count += 1
                    continue

                media_url = f"/media/{asset.file.name}"

                pages = list(
                    ContentPage.objects.filter(
                        Q(body_html__icontains=media_url)
                        | Q(page_css__icontains=media_url)
                        | Q(page_js__icontains=media_url)
                    ).order_by("id")
                )

                if len(pages) == 1:
                    page = pages[0]

                    if asset.related_page_id == page.id:
                        unchanged_count += 1
                        continue

                    asset.related_page = page
                    asset.save(update_fields=("related_page",))
                    linked_count += 1

                elif len(pages) == 0:
                    if asset.related_page_id is None:
                        unchanged_count += 1
                    else:
                        asset.related_page = None
                        asset.save(update_fields=("related_page",))
                        cleared_count += 1

                    unused_count += 1

                else:
                    # Если файл встречается на нескольких страницах,
                    # лучше не привязывать его к одной из них,
                    # чтобы не получить ложную связь.
                    if asset.related_page_id is not None:
                        asset.related_page = None
                        asset.save(update_fields=("related_page",))
                        cleared_count += 1
                    else:
                        unchanged_count += 1

                    ambiguous_count += 1

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write("")
        self.stdout.write("Результат:")
        self.stdout.write(f"  Привязано к одной странице: {linked_count}")
        self.stdout.write(f"  Снято неверных связей: {cleared_count}")
        self.stdout.write(f"  Без изменений: {unchanged_count}")
        self.stdout.write(
            f"  Найдены на нескольких страницах: {ambiguous_count}"
        )
        self.stdout.write(f"  Не найдены в контенте: {unused_count}")

        self.stdout.write("")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Dry-run завершён. Изменения в базе отменены."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Связи медиафайлов со страницами обновлены."
                )
            )