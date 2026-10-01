"""Real PostgreSQL concurrent connections; SQLite never counts as locking proof."""
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest import skipUnless

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.db import connection, connections
from django.test import RequestFactory, TransactionTestCase
from django.utils import timezone

from content.models import Grade
from users.http import APIError
from users.models import IdentityReceipt, LoginWindow, StudentProfile
from users.services import complete_onboarding, consume_login_budget, register


@skipUnless(connection.vendor == "postgresql", "Requires actual PostgreSQL; SQLite is compatibility only")
class PostgreSQLIdentityConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.grade = Grade.objects.create(title="Concurrent grade", slug="concurrent-grade")
        self.user = get_user_model().objects.create_user(username="concurrent-owner")
        self.other = get_user_model().objects.create_user(username="other-concurrent-owner")

    def parallel(self, functions):
        barrier = threading.Barrier(len(functions))

        def run(function):
            try:
                barrier.wait(timeout=15)
                return function()
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=len(functions)) as executor:
            futures = [executor.submit(run, function) for function in functions]
            return [future.result(timeout=30) for future in futures]

    def registration(self, username):
        request = RequestFactory().post("/api/v1/auth/register/")
        request.user = AnonymousUser()
        request.session = SessionStore()
        request.META["CSRF_COOKIE"] = "a" * 32  # Synthetic bootstrap identity.
        request.META["HTTP_IDEMPOTENCY_KEY"] = "concurrent-key"
        try:
            user, response, status = register(request, {"username": username, "password": "Synthetic-Concurrent-Only-47!"})
            return status, user.pk, response
        except APIError as error:
            return error.status, error.code

    def onboarding(self, user, mode="START_ZERO"):
        request = RequestFactory().post("/api/v1/onboarding/complete/")
        request.user = user
        request.META["HTTP_IDEMPOTENCY_KEY"] = "onboarding-concurrent"
        try:
            return complete_onboarding(request, {"selected_grade_id": self.grade.pk, "mode": mode})
        except APIError as error:
            return error.status, error.code

    def test_same_registration_key_creates_one_user_profile_and_response(self):
        results = self.parallel([lambda: self.registration("same-concurrent") for _ in range(4)])
        self.assertTrue(all(result == results[0] for result in results))
        self.assertEqual(results[0][0], 201)
        self.assertEqual(get_user_model().objects.filter(username="same-concurrent").count(), 1)
        self.assertEqual(StudentProfile.objects.count(), 1)
        self.assertEqual(IdentityReceipt.objects.count(), 1)

    def test_same_registration_key_different_payload_one_winner(self):
        results = self.parallel([lambda: self.registration("first-concurrent"),
                                 lambda: self.registration("second-concurrent")])
        self.assertEqual(sorted(result[0] for result in results), [201, 409])
        self.assertIn((409, "IDEMPOTENCY_CONFLICT"), results)
        self.assertEqual(StudentProfile.objects.count(), 1)
        self.assertEqual(IdentityReceipt.objects.count(), 1)

    def test_onboarding_same_key_is_one_persisted_action(self):
        results = self.parallel([lambda: self.onboarding(self.user) for _ in range(4)])
        self.assertTrue(all(result == results[0] for result in results))
        self.assertEqual(results[0][1], 200)
        self.assertEqual(StudentProfile.objects.filter(user=self.user).count(), 1)
        self.assertEqual(IdentityReceipt.objects.count(), 1)

    def test_onboarding_conflicting_payload_serializes(self):
        results = self.parallel([lambda: self.onboarding(self.user, "START_ZERO"),
                                 lambda: self.onboarding(self.user, "SELF_REPORT")])
        self.assertEqual(sum(isinstance(result[0], dict) for result in results), 1)
        self.assertIn((409, "IDEMPOTENCY_CONFLICT"), results)
        self.assertEqual(IdentityReceipt.objects.count(), 1)

    def test_same_onboarding_key_different_owners_is_isolated(self):
        results = self.parallel([lambda: self.onboarding(self.user), lambda: self.onboarding(self.other)])
        self.assertEqual({result[0]["data"]["id"] for result in results}, {self.user.pk, self.other.pk})
        self.assertEqual(IdentityReceipt.objects.count(), 2)
        self.assertEqual(StudentProfile.objects.count(), 2)

    def test_login_limit_is_atomic_on_concurrent_first_requests(self):
        now = timezone.now()

        def login_budget():
            try:
                consume_login_budget("192.0.2.10", now)
                return 200
            except APIError as error:
                return error.status

        results = self.parallel([login_budget for _ in range(12)])
        self.assertEqual(results.count(200), 10)
        self.assertEqual(results.count(429), 2)
        self.assertEqual(LoginWindow.objects.count(), 1)
        self.assertEqual(LoginWindow.objects.get().count, 10)
