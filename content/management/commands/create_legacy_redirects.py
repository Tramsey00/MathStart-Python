from django.core.management.base import BaseCommand
from django.db import transaction

from content.models import ContentPage, Redirect


CATEGORY_REDIRECTS = {
    "/category/5-класс/": "/5-klass/",
    "/category/6-класс/": "/6-klass/",

    "/category/7-klass-algebra/": "/7-klass-algebra/",
    "/category/7-klass-geometriya/": "/7-klass-geometriya/",
    "/category/7-klass-veroyatnost-i-statistika/": (
        "/7-klass-veroyatnost-i-statistika/"
    ),

    "/category/8-klass-algebra/": "/8-klass-algebra/",
    "/category/8-klass-geometriya/": "/8-klass-geometriya/",
    "/category/8-klass-veroyatnost-i-statistika/": (
        "/8-klass-veroyatnost-i-statistika/"
    ),

    "/category/9-klass-algebra/": "/9-klass-algebra/",
    "/category/9-klass-geometriya/": "/9-klass-geometriya/",
    "/category/9-klass-veroyatnost-i-statistika/": (
        "/9-klass-veroyatnost-i-statistika/"
    ),
}


class Command(BaseCommand):
    help = (
        "Создаёт редиректы со старых адресов WordPress "
        "на канонические адреса Django."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Проверить создание без сохранения изменений.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        redirect_map = {
            "/glavnaya/": "/",
            "/mathstart/": "/",
            "/mathstart/glavnaya/": "/",
        }

        pages = ContentPage.objects.filter(
            is_published=True
        ).order_by("id")

        for page in pages:
            canonical_path = page.get_absolute_url()

            if page.page_type == ContentPage.PageType.HOME:
                continue

            # Старый локальный путь WordPress.
            redirect_map[
                f"/mathstart/{page.slug}/"
            ] = canonical_path

        redirect_map.update(CATEGORY_REDIRECTS)

        created_count = 0
        updated_count = 0
        unchanged_count = 0

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Режим dry-run: изменения не будут сохранены."
                )
            )

        with transaction.atomic():
            for old_path, new_path in sorted(
                redirect_map.items()
            ):
                redirect_rule, was_created = (
                    Redirect.objects.get_or_create(
                        old_path=old_path,
                        defaults={
                            "new_path": new_path,
                            "is_permanent": True,
                            "is_active": True,
                        },
                    )
                )

                if was_created:
                    created_count += 1
                    continue

                changed_fields = []

                if redirect_rule.new_path != new_path:
                    redirect_rule.new_path = new_path
                    changed_fields.append("new_path")

                if not redirect_rule.is_permanent:
                    redirect_rule.is_permanent = True
                    changed_fields.append("is_permanent")

                if not redirect_rule.is_active:
                    redirect_rule.is_active = True
                    changed_fields.append("is_active")

                if changed_fields:
                    redirect_rule.save(
                        update_fields=changed_fields
                    )
                    updated_count += 1
                else:
                    unchanged_count += 1

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write("")
        self.stdout.write("Результат:")
        self.stdout.write(
            f"  Подготовлено правил: {len(redirect_map)}"
        )
        self.stdout.write(
            f"  Создано: {created_count}"
        )
        self.stdout.write(
            f"  Обновлено: {updated_count}"
        )
        self.stdout.write(
            f"  Без изменений: {unchanged_count}"
        )

        self.stdout.write("")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Dry-run завершён. Изменения отменены."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Старые адреса WordPress защищены редиректами."
                )
            )