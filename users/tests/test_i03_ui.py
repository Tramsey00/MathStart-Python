"""I03 semantic markup and production JS/API flow; no browser acceptance claims."""
from html.parser import HTMLParser
from pathlib import Path
import os
import shutil
import subprocess

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase, RequestFactory, SimpleTestCase, override_settings
from django.urls import resolve, reverse

from content.models import Grade
from users.models import IdentityReceipt, StudentProfile
from users.ui_views import account

ROOT = Path(__file__).resolve().parents[2]
STATIC_STORAGE = {"staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}}


class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elements = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


@override_settings(STORAGES=STATIC_STORAGE)
class I03PresentationTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.response = account(self.factory.get("/account/"))
        self.html = self.response.content.decode()
        self.elements = Elements(self.html).elements
        self.ids = {attrs["id"]: (tag, attrs) for tag, attrs in self.elements if "id" in attrs}

    def test_presentation_get_only_no_database_or_personal_state(self):
        self.assertEqual(resolve(reverse("users_ui:account")).func, account)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response["Cache-Control"], "private, no-store")
        self.assertEqual(account(self.factory.post("/account/")).status_code, 405)
        # SimpleTestCase disallows database queries; page contains no profile or credential JSON.
        self.assertNotIn('type="application/json"', self.html)
        self.assertNotIn("ui-fixtures", self.html)

    def test_forms_have_semantic_submit_and_post_no_get_credential_fallback(self):
        forms = [attrs for tag, attrs in self.elements if tag == "form"]
        self.assertEqual({item["id"] for item in forms}, {name + "-form" for name in ["register", "login", "logout", "profile", "onboarding"]})
        self.assertTrue(all(item.get("method") == "post" and "aria-describedby" in item for item in forms))
        self.assertEqual(sum(tag == "button" and attrs.get("type") == "submit" for tag, attrs in self.elements), 5)
        self.assertNotIn("novalidate", self.html)
        self.assertIn("<noscript>", self.html)

    def test_controls_labels_error_relationships_and_native_keyboard_contract(self):
        labels = {attrs["for"] for tag, attrs in self.elements if tag == "label" and "for" in attrs}
        controls = [(tag, attrs) for tag, attrs in self.elements if tag in {"input", "select"}]
        for tag, attrs in controls:
            with self.subTest(control=attrs["id"]):
                self.assertIn(attrs["id"], labels)
                if attrs["id"] != "register-email":
                    self.assertIn("required", attrs)
                if attrs.get("type") != "radio":
                    for target in attrs["aria-describedby"].split():
                        self.assertIn(target, self.ids)
        self.assertEqual({attrs["value"] for tag, attrs in controls if attrs.get("type") == "radio"}, {"START_ZERO", "SELF_REPORT", "DIAGNOSTIC"})
        self.assertEqual(len(self.ids), sum("id" in attrs for _, attrs in self.elements))
        self.assertTrue(all(int(attrs.get("tabindex", "0")) <= 0 for _, attrs in self.elements))
        self.assertIn('href="#account-main"', self.html)
        self.assertIn('role="alert"', self.html)
        self.assertIn('aria-live="polite"', self.html)
        self.assertIn("hidden", self.ids["account-refresh"][1])
        self.assertIn('id="account-refresh" class="ms-ui-button" hidden>Повторить загрузку</button>', self.html)
        self.assertNotIn("Обновить сохранённое состояние", self.html)
        self.assertIn(":focus-visible", (ROOT / "static/mathstart/css/ui/foundation.css").read_text())

    def test_password_semantics_foundation_reuse_and_no_fabricated_diagnostic(self):
        for field, autocomplete in [("login-password", "current-password"), ("register-password", "new-password")]:
            attrs = self.ids[field][1]
            self.assertEqual(attrs["type"], "password")
            self.assertEqual(attrs["autocomplete"], autocomplete)
            self.assertEqual(attrs["value"], "")
        for resource in ["ui/tokens.css", "ui/foundation.css", "ui/identity-api.js", "ui/account.js"]:
            self.assertIn(resource, self.html)
        self.assertIn("Диагностические задания на этом экране не запускаются", self.html)
        self.assertIn("Знакомые темы на этом экране не отмечаются", self.html)


@override_settings(STORAGES=STATIC_STORAGE, SECURE_SSL_REDIRECT=False,
                   SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False)
class I03RealConsumerFlowTests(LiveServerTestCase):
    def setUp(self):
        Grade.objects.create(pk=70, title="5 класс", slug="5-klass")
        Grade.objects.create(pk=50, title="6 класс", slug="6-klass")
        Grade.objects.create(pk=30, title="10 класс", slug="10-klass")
        get_user_model().objects.create_user("i03-inactive", password="Synthetic-I03-Test-Only-47!", is_active=False)

    def test_production_javascript_consumes_current_runtime(self):
        executable = shutil.which("node")
        if not executable:
            self.skipTest("Existing Node runtime unavailable; production JS/runtime integration NOT VERIFIED")
        env = {**os.environ, "MATHSTART_I03_TEST_URL": self.live_server_url}
        result = subprocess.run([executable, "--test", "--test-reporter=tap", "tests/i03_runtime_flow.js"],
                                cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", timeout=90)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("# pass 3", result.stdout)
        user = get_user_model().objects.get(username="i03-runtime-student")
        profile = StudentProfile.objects.get(user=user)
        self.assertEqual(profile.selected_grade_id, 70)
        self.assertEqual(profile.onboarding_mode, "DIAGNOSTIC")
        self.assertTrue(profile.onboarding_complete)
        self.assertEqual(StudentProfile.objects.filter(user=user).count(), 1)
        self.assertEqual(IdentityReceipt.objects.filter(user=user, operation="register").count(), 1)
        self.assertEqual(IdentityReceipt.objects.filter(user=user, operation="complete_onboarding").count(), 3)
        self.assertFalse(get_user_model().objects.filter(username="i03-no-csrf").exists())
