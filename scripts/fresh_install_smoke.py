"""Migrate and verify an explicitly disposable, empty PostgreSQL database."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ("curriculum", "site_content", "templates", "static")


def require_disposable(vendor, name, runtime, tables):
    if (vendor != "postgresql" or not name.startswith("ms6_v01_smoke_")
            or not name.removeprefix("ms6_v01_smoke_")):
        raise ValueError("Requires PostgreSQL database named ms6_v01_smoke_<unique suffix>")
    if tables:
        raise ValueError("Refusing a nonempty database; use a new disposable database")
    runtime = Path(runtime).resolve()
    # Never put generated files over source trees, the checkout root or ancestors.
    if runtime == ROOT or runtime in ROOT.parents:
        raise ValueError("Set DJANGO_RUNTIME_ROOT to an isolated runtime directory")
    for material in MATERIALS:
        source = ROOT / material
        if runtime == source or source in runtime.parents or runtime in source.parents:
            raise ValueError("Runtime directory overlaps source materials")
    for directory in (runtime / "media", runtime / "staticfiles"):
        if directory.exists() and any(directory.iterdir()):
            raise ValueError("Smoke requires empty runtime media/staticfiles directories")


def files_digest(root):
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob("*")) if path.is_file()}


def materials_digest():
    return {name: files_digest(ROOT / name) for name in MATERIALS}


def run(*args):
    print("$ python " + " ".join(args), flush=True)
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True, timeout=600)


def snapshot(models):
    result = {}
    for model in models:
        # Auto timestamps may change during catalogue synchronization; all other
        # persisted values, including PK/FK identities and content, must not.
        fields = [f.attname for f in model._meta.concrete_fields
                  if not getattr(f, "auto_now", False) and not getattr(f, "auto_now_add", False)]
        result[model.__name__] = list(model.objects.order_by("pk").values(*fields))
    return result


def smoke():
    sys.path.insert(0, str(ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()
    from django.conf import settings
    from django.db import connection
    # Reject a wrong target before opening it (even SQLite connect can create a file).
    require_disposable(connection.vendor, connection.settings_dict["NAME"],
                       settings.RUNTIME_ROOT, [])
    run("scripts/check_database.py")
    require_disposable(connection.vendor, connection.settings_dict["NAME"],
                       settings.RUNTIME_ROOT, connection.introspection.table_names(include_views=True))
    original = materials_digest()
    try:
        run("manage.py", "migrate", "--noinput")
        run("manage.py", "migrate", "--check")
        run("manage.py", "makemigrations", "--check", "--dry-run")
        from content.models import Grade, Subject, Section, ContentPage, LessonPublication, MediaAsset, Redirect
        from django.contrib.auth import get_user_model
        models = (Grade, Subject, Section, ContentPage, LessonPublication, MediaAsset, Redirect)
        sentinel = get_user_model().objects.create_user(username="v01-smoke-preserved-user")
        user_before = get_user_model().objects.filter(pk=sentinel.pk).values().get()
        run("manage.py", "bootstrap_site")
        expected = (6, 12, 63, 279, 263, 29, 282)
        actual = tuple(model.objects.count() for model in models)
        if actual != expected:
            raise ValueError(f"Unexpected catalogue counts: {actual}; expected {expected}")
        if ContentPage.objects.filter(page_type="topic").count() != 263:
            raise ValueError("Expected exactly 263 topics")
        first = snapshot(models)
        media = files_digest(settings.MEDIA_ROOT)
        if len(media) != 29:
            raise ValueError("Expected exactly 29 runtime media files")
        run("manage.py", "bootstrap_site")
        if snapshot(models) != first or files_digest(settings.MEDIA_ROOT) != media:
            raise ValueError("Second bootstrap changed identities/content/media or duplicated rows")
        if get_user_model().objects.filter(pk=sentinel.pk).values().get() != user_before:
            raise ValueError("Bootstrap changed an existing user")
        run("manage.py", "collectstatic", "--noinput")
        if not (settings.STATIC_ROOT / "staticfiles.json").is_file():
            raise ValueError("Static manifest missing")
        run("manage.py", "check_lesson_sources", "--all")
        run("manage.py", "check_content_quality")
        run("manage.py", "check_site_integrity")
        print("PASS: fresh PostgreSQL migrations, bootstrap idempotency, identities/content/media, static and content checks")
    finally:
        connection.close()
        if materials_digest() != original:
            raise ValueError("Repository source materials changed during smoke")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("legacy", "target"), default="legacy")
    parser.add_argument("--disposable", action="store_true", required=True,
                        help="Acknowledge writes to a new disposable database/runtime")
    args = parser.parse_args(argv)
    if args.profile == "target":
        sys.path.insert(0, str(ROOT))
        from scripts.target_check import main as target_main
        return target_main(["fresh-install", "--disposable"])
    try:
        smoke()
    except (ValueError, subprocess.SubprocessError) as exc:
        print(f"Smoke failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
