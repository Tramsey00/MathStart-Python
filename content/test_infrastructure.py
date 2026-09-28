"""V01 safety checks; PostgreSQL integration stays in the existing DB suites."""
import io
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.database import database_config
from scripts import check_database
from scripts.fresh_install_smoke import ROOT, require_disposable


class DatabaseConfigurationTests(SimpleTestCase):
    def env(self):
        return {"DJANGO_DB_NAME": "mathstart", "DJANGO_DB_USER": "dev",
                "DJANGO_DB_PASSWORD": "sentinel-secret", "DJANGO_DB_HOST": "localhost"}

    def test_default_is_postgresql_and_missing_config_never_falls_back(self):
        with self.assertRaises(ImproperlyConfigured):
            database_config(ROOT, {})
        config = database_config(ROOT, self.env())
        self.assertEqual(config["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(config["OPTIONS"]["connect_timeout"], 5)
        self.assertEqual(config["TEST"]["NAME"], "test_mathstart")

    def test_sqlite_requires_explicit_selection(self):
        config = database_config(ROOT, {"DJANGO_DB_BACKEND": "sqlite", "DJANGO_DB_PATH": ":memory:"})
        self.assertEqual(config["NAME"], ":memory:")
        with self.assertRaises(ImproperlyConfigured):
            database_config(ROOT, {"DJANGO_DB_BACKEND": "typo"})

    def test_invalid_parameters_do_not_echo_values(self):
        for key, value in (("DJANGO_DB_PORT", "sentinel-secret"),
                           ("DJANGO_DB_PORT", "65536"),
                           ("DJANGO_DB_CONNECT_TIMEOUT", "0"),
                           ("DJANGO_DB_CONNECT_TIMEOUT", "31"),
                           ("DJANGO_DB_TEST_NAME", "mathstart")):
            with self.subTest(key=key, value=value):
                with self.assertRaises(ImproperlyConfigured) as error:
                    database_config(ROOT, {**self.env(), key: value})
                self.assertNotIn("sentinel-secret", str(error.exception))

    def test_connection_error_is_nonzero_and_redacted(self):
        output = io.StringIO()
        with patch("django.setup"), patch("django.db.connection") as connection:
            connection.cursor.side_effect = RuntimeError("sentinel-secret")
            with redirect_stdout(output):
                code = check_database.probe()
        self.assertEqual(code, 1)
        self.assertIn("Database connection failed", output.getvalue())
        self.assertNotIn("sentinel-secret", output.getvalue())

    def test_timeout_is_bounded_and_nonzero(self):
        import subprocess
        with patch("sys.argv", ["check_database.py"]), patch(
            "scripts.check_database.subprocess.run",
            side_effect=subprocess.TimeoutExpired("probe", 35),
        ) as process, redirect_stdout(io.StringIO()):
            self.assertEqual(check_database.main(), 1)
        self.assertEqual(process.call_args.kwargs["timeout"], 35)


class SmokeSafetyTests(SimpleTestCase):
    def test_rejects_sqlite_nonempty_database_and_unsafe_runtime(self):
        cases = [
            ("sqlite", "ms6_v01_smoke_x", ROOT / "var/smoke", []),
            ("postgresql", "mathstart", ROOT / "var/smoke", []),
            ("postgresql", "ms6_v01_smoke_x", ROOT / "var/smoke", ["auth_user"]),
            ("postgresql", "ms6_v01_smoke_x", ROOT, []),
            ("postgresql", "ms6_v01_smoke_x", ROOT / "curriculum/generated", []),
        ]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                require_disposable(*case)

    def test_accepts_isolated_empty_target(self):
        import tempfile
        with tempfile.TemporaryDirectory() as runtime:
            require_disposable("postgresql", "ms6_v01_smoke_test", Path(runtime), [])
