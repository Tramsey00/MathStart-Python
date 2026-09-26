"""Explicit database selection; PostgreSQL errors never select SQLite."""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


def database_config(base_dir, environ=None):
    env = os.environ if environ is None else environ
    backend = env.get("DJANGO_DB_BACKEND", "postgresql").strip()
    if backend == "sqlite":
        return {"ENGINE": "django.db.backends.sqlite3",
                "NAME": env.get("DJANGO_DB_PATH") or Path(base_dir) / "db.sqlite3"}
    if backend != "postgresql":
        raise ImproperlyConfigured("DJANGO_DB_BACKEND must be postgresql or sqlite")
    required = ("NAME", "USER", "PASSWORD", "HOST")
    missing = [f"DJANGO_DB_{key}" for key in required
               if not env.get(f"DJANGO_DB_{key}", "").strip()]
    if missing:
        raise ImproperlyConfigured("Missing PostgreSQL configuration: " + ", ".join(missing))

    def integer(key, default, minimum, maximum):
        try:
            value = int(env.get(key, default))
        except (TypeError, ValueError):
            raise ImproperlyConfigured(f"{key} must be an integer") from None
        if not minimum <= value <= maximum:
            raise ImproperlyConfigured(f"{key} must be between {minimum} and {maximum}")
        return value

    port = integer("DJANGO_DB_PORT", "5432", 1, 65535)
    timeout = integer("DJANGO_DB_CONNECT_TIMEOUT", "5", 2, 30)
    name = env["DJANGO_DB_NAME"].strip()
    test_name = env.get("DJANGO_DB_TEST_NAME", "test_" + name).strip()
    if not test_name or test_name == name:
        raise ImproperlyConfigured("DJANGO_DB_TEST_NAME must differ from DJANGO_DB_NAME")
    return {
        "ENGINE": "django.db.backends.postgresql",
        **{key: env[f"DJANGO_DB_{key}"] for key in required},
        "PORT": port,
        "CONN_MAX_AGE": 0,
        "OPTIONS": {"connect_timeout": timeout},
        "TEST": {"NAME": test_name},
    }
