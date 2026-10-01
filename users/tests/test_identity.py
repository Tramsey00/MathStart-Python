"""MS7-V02 runtime security/contract tests; all identities are synthetic."""
import json
import uuid
from datetime import timedelta
from unittest.mock import patch
import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.db import IntegrityError, connection, transaction
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from scripts.r02a_contract_reference import request_digest as contract_digest, validator
from users.http import APIError, json_response
from users.models import IdentityReceipt, LoginWindow, StudentProfile
from users.services import consume_login_budget, owned_profile, request_digest
from content.models import Grade

API = "/api/v1/"
PASSWORD = "Synthetic-Test-Only-47!"


def reordered_objects(value):
    """Simulate storage changing object order, without changing JSON values."""
    if isinstance(value, dict):
        return {key: reordered_objects(item) for key, item in reversed(list(value.items()))}
    if isinstance(value, list):
        return [reordered_objects(item) for item in value]
    return value


class ResponseSerializationTests(SimpleTestCase):
    def test_nested_object_order_does_not_change_response_bytes(self):
        body = {"meta": {"version": "http-v1", "request_id": "synthetic"},
                "data": {"username": "Ученик β", "selected_grade_id": None,
                         "items": [{"z": False, "a": 1}, {"b": 2, "a": True}]}}
        reordered = reordered_objects(body)
        self.assertEqual(body, reordered)
        first, second = json_response(body, 201), json_response(reordered, 201)
        self.assertEqual(first.content, second.content)
        self.assertEqual(first.status_code, second.status_code)
        self.assertEqual(json.loads(first.content), body)
        self.assertIn("Ученик β".encode("utf-8"), first.content)

    def test_response_serialization_preserves_array_order(self):
        body = {"data": [{"id": 2}, {"id": 1}]}
        original = json_response(body)
        reversed_array = json_response({"data": list(reversed(body["data"]))})
        self.assertNotEqual(original.content, reversed_array.content)
        self.assertEqual(json.loads(original.content)["data"], body["data"])


@override_settings(SECURE_SSL_REDIRECT=False, SESSION_COOKIE_SECURE=False,
                   CSRF_COOKIE_SECURE=False)
class IdentityAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.grade = Grade.objects.create(title="Synthetic grade", slug="synthetic-grade")
        cls.other_grade = Grade.objects.create(title="Other grade", slug="other-grade")
        cls.user = get_user_model().objects.create_user("student-a", password=PASSWORD)
        cls.other = get_user_model().objects.create_user("student-b", password=PASSWORD)
        cls.profile = StudentProfile.objects.create(user=cls.user)
        StudentProfile.objects.create(user=cls.other)

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def token(self, client=None):
        client = client or self.client
        response = client.get(API + "auth/csrf/")
        self.assert_wire(response, 200, "CsrfTokenResponse")
        return response.json()["data"]["csrf_token"]

    def mutate(self, route, body, *, method="post", key=None, client=None):
        client = client or self.client
        headers = {"HTTP_X_CSRFTOKEN": self.token(client)}
        if key is not None:
            headers["HTTP_IDEMPOTENCY_KEY"] = key
        return getattr(client, method)(API + route, data=json.dumps(body),
                                      content_type="application/json", **headers)

    def sign_in(self, client=None, username="student-a"):
        response = self.mutate("auth/login/", {"username": username, "password": PASSWORD},
                               client=client)
        self.assert_wire(response, 200, "UserResponse")
        return response

    def assert_wire(self, response, status, schema):
        self.assertEqual(response.status_code, status)
        validator(schema).validate(response.json())
        self.assertEqual(response["Content-Type"], "application/json; charset=utf-8")
        self.assertIn("no-store", response["Cache-Control"])
        self.assertNotIn(PASSWORD, response.content.decode())
        return response.json()

    def assert_error(self, response, status, code):
        schema = {400: "BadRequestError", 401: "AuthenticationError", 403: "ForbiddenError",
                  404: "NotFoundError", 409: "ConflictEnvelope", 429: "RateLimitError",
                  503: "UnavailableError"}[status]
        body = self.assert_wire(response, status, schema)
        self.assertEqual(body["error"]["code"], code)
        self.assertEqual(body["error"]["field_errors"], {})
        return {k: v for k, v in body["error"].items() if k != "request_id"}

    def test_register_creates_hashed_student_and_session(self):
        response = self.mutate("auth/register/", {
            "username": "new-student", "password": PASSWORD, "email": "synthetic@example.invalid",
        }, key="register-new")
        data = self.assert_wire(response, 201, "UserResponse")["data"]
        user = get_user_model().objects.get(pk=data["id"])
        self.assertTrue(user.check_password(PASSWORD))
        self.assertNotEqual(user.password, PASSWORD)
        self.assertFalse(user.is_staff or user.is_superuser)
        self.assertFalse(data["onboarding_complete"])
        self.assertIsNone(data["onboarding_mode"])
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)
        receipt = IdentityReceipt.objects.get(user=user)
        self.assertEqual(receipt.status, 201)
        self.assertNotIn(PASSWORD, json.dumps(receipt.response))
        self.assertGreaterEqual((receipt.expires_at - receipt.created_at).total_seconds(), 604799)

    def test_register_exact_retry_and_changed_digest(self):
        body = {"username": "replay-student", "password": PASSWORD}
        first = self.mutate("auth/register/", body, key="retry")
        old_session = self.client.session.session_key
        second = self.mutate("auth/register/", dict(reversed(list(body.items()))), key="retry")
        self.assertEqual(first.content, second.content)
        self.assertEqual(second.status_code, 201)
        self.assertEqual(self.client.session.session_key, old_session)
        self.assertEqual(get_user_model().objects.filter(username=body["username"]).count(), 1)
        self.assertEqual(IdentityReceipt.objects.count(), 1)
        changed = self.mutate("auth/register/", {**body, "email": "new@example.invalid"}, key="retry")
        self.assert_error(changed, 409, "IDEMPOTENCY_CONFLICT")

    def test_exact_replay_survives_reordered_persisted_response_on_any_backend(self):
        operations = [
            ("register", "auth/register/", {"username": "reordered-student", "password": PASSWORD}),
            ("complete_onboarding", "onboarding/complete/",
             {"selected_grade_id": self.grade.pk, "mode": "SELF_REPORT"}),
        ]
        for operation, route, body in operations:
            with self.subTest(operation=operation):
                first = self.mutate(route, body, key="reordered-receipt")
                self.assert_wire(first, 201 if operation == "register" else 200, "UserResponse")
                receipt = IdentityReceipt.objects.get(operation=operation)
                original = first.json()
                reordered = reordered_objects(original)
                self.assertEqual(original, reordered)
                # SQLite retains this changed order; jsonb may order it differently
                # again. Replay must tolerate either, while using real persistence.
                receipt.response = reordered
                receipt.save(update_fields=["response"])
                second = self.mutate(route, body, key="reordered-receipt")
                self.assertEqual(first.content, second.content)
                self.assertEqual(first.status_code, second.status_code)
                self.assertEqual(second.json()["meta"], original["meta"])
                self.assertEqual(IdentityReceipt.objects.filter(operation=operation).count(), 1)
        self.assertEqual(get_user_model().objects.filter(username="reordered-student").count(), 1)

    def test_register_lost_ack_replays_only_original_bootstrap(self):
        token = self.token()
        original_cookie = self.client.cookies["csrftoken"].value
        body = {"username": "lost-ack", "password": PASSWORD}
        first = self.client.post(API + "auth/register/", json.dumps(body), content_type="application/json",
                                 HTTP_X_CSRFTOKEN=token, HTTP_IDEMPOTENCY_KEY="lost")
        lost_client = Client(enforce_csrf_checks=True)
        lost_client.cookies["csrftoken"] = original_cookie
        replay = lost_client.post(API + "auth/register/", json.dumps(body), content_type="application/json",
                                  HTTP_X_CSRFTOKEN=token, HTTP_IDEMPOTENCY_KEY="lost")
        self.assertEqual(first.content, replay.content)
        self.assertIn("_auth_user_id", lost_client.session)
        stranger = Client(enforce_csrf_checks=True)
        self.assert_error(self.mutate("auth/register/", body, key="lost", client=stranger),
                          400, "INVALID_REQUEST")
        self.assertEqual(IdentityReceipt.objects.count(), 1)

    def test_register_replay_does_not_restore_revoked_password(self):
        token = self.token()
        cookie = self.client.cookies["csrftoken"].value
        body = {"username": "changed-password", "password": PASSWORD}
        self.mutate("auth/register/", body, key="changed")
        user = get_user_model().objects.get(username=body["username"])
        user.set_unusable_password()
        user.save(update_fields=["password"])
        replay_client = Client(enforce_csrf_checks=True)
        replay_client.cookies["csrftoken"] = cookie
        response = replay_client.post(API + "auth/register/", json.dumps(body), content_type="application/json",
                                       HTTP_X_CSRFTOKEN=token, HTTP_IDEMPOTENCY_KEY="changed")
        self.assert_error(response, 409, "STATE_CONFLICT")
        self.assertNotIn("_auth_user_id", replay_client.session)

    def test_registration_negative_cases_are_atomic(self):
        cases = [
            {"username": "student-a", "password": PASSWORD},
            {"username": "invalid space", "password": PASSWORD},
            {"username": "weak-password", "password": "123"},
            {"username": "email-invalid", "password": PASSWORD, "email": "bad"},
            {"username": "role-injection", "password": PASSWORD, "is_staff": True},
            {"username": "missing-password"},
        ]
        before = get_user_model().objects.count()
        for i, body in enumerate(cases):
            with self.subTest(case=i):
                self.assert_error(self.mutate("auth/register/", body, key=str(i)), 400, "INVALID_REQUEST")
        self.assertEqual(get_user_model().objects.count(), before)
        self.assertEqual(StudentProfile.objects.count(), 2)
        self.assertEqual(IdentityReceipt.objects.count(), 0)

    def test_registration_rotates_preexisting_session_and_csrf(self):
        session = self.client.session
        session["synthetic_marker"] = True
        session.save()
        self.client.cookies["sessionid"] = session.session_key
        old_session = session.session_key
        old_token = self.token()
        old_csrf = self.client.cookies["csrftoken"].value
        self.assert_wire(self.mutate("auth/register/", {"username": "rotation-student", "password": PASSWORD},
                                    key="rotation"), 201, "UserResponse")
        self.assertNotEqual(self.client.session.session_key, old_session)
        self.assertFalse(Session.objects.filter(session_key=old_session).exists())
        self.assertNotEqual(self.client.cookies["csrftoken"].value, old_csrf)
        self.assert_error(self.client.post(API + "auth/logout/", "{}", content_type="application/json",
                                          HTTP_X_CSRFTOKEN=old_token), 403, "CSRF_FAILED")

    def test_idempotency_header_required(self):
        self.assert_error(self.mutate("auth/register/", {"username": "headerless", "password": PASSWORD}),
                          400, "INVALID_REQUEST")
        self.sign_in()
        self.assert_error(self.mutate("onboarding/complete/", {
            "selected_grade_id": self.grade.pk, "mode": "START_ZERO",
        }), 400, "INVALID_REQUEST")
        self.assertEqual(IdentityReceipt.objects.count(), 0)

    def test_register_does_not_switch_an_authenticated_identity(self):
        self.sign_in()
        self.assert_error(self.mutate("auth/register/", {"username": "new-other", "password": PASSWORD},
                                      key="new-other"), 409, "STATE_CONFLICT")
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)
        self.assertFalse(get_user_model().objects.filter(username="new-other").exists())

    def test_login_missing_wrong_and_inactive_are_indistinguishable(self):
        self.other.is_active = False
        self.other.save(update_fields=["is_active"])
        results = []
        for username, password in [("missing-user", PASSWORD), ("student-a", "synthetic-wrong"),
                                   ("student-b", PASSWORD)]:
            response = self.mutate("auth/login/", {"username": username, "password": password})
            results.append(self.assert_error(response, 401, "AUTHENTICATION_REQUIRED"))
            self.assertNotIn(username, response.content.decode())
            self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[1], results[2])

    def test_login_failure_preserves_existing_authenticated_identity(self):
        self.sign_in()
        original = self.client.session.session_key
        self.assert_error(self.mutate("auth/login/", {"username": "student-b", "password": "wrong"}),
                          401, "AUTHENTICATION_REQUIRED")
        self.assertEqual(self.client.session.session_key, original)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_login_rotates_anonymous_and_repeat_sessions_and_csrf(self):
        session = self.client.session
        session["synthetic_marker"] = True
        session.save()
        self.client.cookies["sessionid"] = session.session_key
        old_key = session.session_key
        self.token()
        old_csrf = self.client.cookies["csrftoken"].value
        self.sign_in()
        first_key = self.client.session.session_key
        self.assertNotEqual(old_key, first_key)
        self.assertFalse(Session.objects.filter(session_key=old_key).exists())
        self.assertNotEqual(old_csrf, self.client.cookies["csrftoken"].value)
        self.sign_in()
        self.assertNotEqual(first_key, self.client.session.session_key)
        self.assertFalse(Session.objects.filter(session_key=first_key).exists())

    def test_switch_user_flushes_previous_session(self):
        self.sign_in()
        session = self.client.session
        session["previous_private_value"] = "synthetic"
        session.save()
        previous_key = session.session_key
        self.sign_in(username="student-b")
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.other.pk)
        self.assertNotIn("previous_private_value", self.client.session)
        self.assertFalse(Session.objects.filter(session_key=previous_key).exists())

    def test_logout_invalidates_session_and_repeat_requires_auth(self):
        self.sign_in()
        old_key = self.client.session.session_key
        response = self.mutate("auth/logout/", {})
        self.assertTrue(self.assert_wire(response, 200, "AcknowledgementResponse")["data"]["completed"])
        self.assertFalse(Session.objects.filter(session_key=old_key).exists())
        self.assert_error(self.client.get(API + "users/me/"), 401, "AUTHENTICATION_REQUIRED")
        self.assert_error(self.mutate("auth/logout/", {}), 401, "AUTHENTICATION_REQUIRED")

    def test_profile_persists_across_independent_login_sessions(self):
        self.sign_in()
        response = self.mutate("users/me/", {"selected_grade_id": str(self.grade.pk)}, method="patch")
        self.assertEqual(self.assert_wire(response, 200, "UserResponse")["data"]["selected_grade_id"], self.grade.pk)
        self.mutate("auth/logout/", {})
        another_client = Client(enforce_csrf_checks=True)
        data = self.sign_in(client=another_client).json()["data"]
        self.assertEqual(data["selected_grade_id"], self.grade.pk)
        self.assertEqual(another_client.get(API + "users/me/").json()["data"], data)

    def test_patch_owner_only_and_repeat_has_no_extra_rows(self):
        self.sign_in()
        body = {"selected_grade_id": self.grade.pk}
        first = self.mutate("users/me/", body, method="patch").json()["data"]
        second = self.mutate("users/me/", body, method="patch").json()["data"]
        self.assertEqual(first, second)
        self.assertIsNone(StudentProfile.objects.get(user=self.other).selected_grade_id)
        self.assertEqual(StudentProfile.objects.count(), 2)
        self.assertEqual(IdentityReceipt.objects.count(), 0)

    def test_patch_forbidden_fields_and_invalid_grade(self):
        self.sign_in()
        fields = {"id": self.other.pk, "user_id": self.other.pk, "profile_id": str(uuid.uuid4()),
                  "username": "changed", "password": PASSWORD, "email": "x@example.invalid",
                  "role": "staff", "is_staff": True, "is_superuser": True,
                  "onboarding_mode": "START_ZERO", "onboarding_complete": True,
                  "mastery": 100, "verdict": "CORRECT"}
        for field, value in fields.items():
            with self.subTest(field=field):
                self.assert_error(self.mutate("users/me/", {"selected_grade_id": self.grade.pk, field: value},
                                              method="patch"), 400, "INVALID_REQUEST")
        for value in [None, True, 1.5, -1, 0, 2**64, "invalid", "1e2", "９", "9" * 100, 99999]:
            with self.subTest(grade=value):
                self.assert_error(self.mutate("users/me/", {"selected_grade_id": value}, method="patch"),
                                  400, "INVALID_REQUEST")
        self.assert_error(self.mutate("users/me/", {}, method="patch"), 400, "INVALID_REQUEST")
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff or self.user.is_superuser)
        self.assertEqual(self.user.username, "student-a")
        self.assertIsNone(StudentProfile.objects.get(user=self.user).selected_grade_id)

    def test_all_three_onboarding_modes_save_and_replay(self):
        self.sign_in()
        for mode in ["START_ZERO", "DIAGNOSTIC", "SELF_REPORT"]:
            with self.subTest(mode=mode):
                body = {"selected_grade_id": self.grade.pk, "mode": mode}
                first = self.mutate("onboarding/complete/", body, key=mode)
                data = self.assert_wire(first, 200, "UserResponse")["data"]
                self.assertTrue(data["onboarding_complete"])
                self.assertEqual(data["onboarding_mode"], mode)
                self.assertEqual(data["selected_grade_id"], self.grade.pk)
                second = self.mutate("onboarding/complete/", body, key=mode)
                self.assertEqual(first.content, second.content)
                self.assertEqual(self.client.get(API + "users/me/").json()["data"], data)
                self.assertTrue(StudentProfile.objects.get(user=self.user).onboarding_complete)
        self.assertEqual(IdentityReceipt.objects.count(), 3)
        self.assertIsNone(StudentProfile.objects.get(user=self.other).onboarding_mode)

    def test_onboarding_persistence_and_explicit_rechoice(self):
        self.sign_in()
        body = {"selected_grade_id": self.grade.pk, "mode": "DIAGNOSTIC"}
        self.mutate("onboarding/complete/", body, key="diagnostic")
        self.mutate("auth/logout/", {})
        self.assertEqual(self.sign_in().json()["data"]["onboarding_mode"], "DIAGNOSTIC")
        result = self.mutate("onboarding/complete/", {**body, "mode": "START_ZERO"}, key="explicit-zero")
        self.assertEqual(result.json()["data"]["onboarding_mode"], "START_ZERO")

    def test_onboarding_conflict_and_old_exact_response_after_patch(self):
        self.sign_in()
        body = {"selected_grade_id": self.grade.pk, "mode": "START_ZERO"}
        first = self.mutate("onboarding/complete/", body, key="saved")
        self.assert_error(self.mutate("onboarding/complete/", {**body, "mode": "SELF_REPORT"}, key="saved"),
                          409, "IDEMPOTENCY_CONFLICT")
        self.mutate("users/me/", {"selected_grade_id": self.other_grade.pk}, method="patch")
        self.assertEqual(first.content, self.mutate("onboarding/complete/", body, key="saved").content)
        self.assertEqual(StudentProfile.objects.get(user=self.user).selected_grade_id, self.other_grade.pk)

    def test_onboarding_keys_are_scoped_to_authenticated_owner(self):
        self.sign_in()
        body = {"selected_grade_id": self.grade.pk, "mode": "START_ZERO"}
        first = self.mutate("onboarding/complete/", body, key="shared-key")
        other_client = Client(enforce_csrf_checks=True)
        self.sign_in(client=other_client, username="student-b")
        second = self.mutate("onboarding/complete/", body, key="shared-key", client=other_client)
        self.assertEqual(first.json()["data"]["id"], self.user.pk)
        self.assertEqual(second.json()["data"]["id"], self.other.pk)
        self.assertEqual(IdentityReceipt.objects.count(), 2)

    def test_onboarding_retains_identity_after_minimum_replay_window(self):
        self.sign_in()
        body = {"selected_grade_id": self.grade.pk, "mode": "START_ZERO"}
        first = self.mutate("onboarding/complete/", body, key="retained")
        IdentityReceipt.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
        self.assertEqual(first.content, self.mutate("onboarding/complete/", body, key="retained").content)
        self.assertEqual(IdentityReceipt.objects.count(), 1)
        self.assert_error(self.mutate("onboarding/complete/", {**body, "mode": "SELF_REPORT"}, key="retained"),
                          409, "IDEMPOTENCY_CONFLICT")
        self.assert_error(self.mutate("onboarding/complete/", {**body, "role": "staff"}, key="retained"),
                          400, "INVALID_REQUEST")

    def test_onboarding_invalid_mode_payload_no_state_change(self):
        self.sign_in()
        cases = [
            {"selected_grade_id": self.grade.pk, "mode": "UNSUPPORTED"},
            {"selected_grade_id": self.grade.pk, "mode": "start_zero"},
            {"selected_grade_id": self.grade.pk, "mode": None},
            {"mode": "START_ZERO"},
            {"selected_grade_id": self.grade.pk},
            {"selected_grade_id": 99999, "mode": "START_ZERO"},
            {"selected_grade_id": self.grade.pk, "mode": "SELF_REPORT", "skill_codes": ["x"]},
        ]
        for i, body in enumerate(cases):
            with self.subTest(case=i):
                self.assert_error(self.mutate("onboarding/complete/", body, key=str(i)), 400, "INVALID_REQUEST")
        self.assertFalse(StudentProfile.objects.get(user=self.user).onboarding_complete)
        self.assertEqual(IdentityReceipt.objects.count(), 0)

    def test_all_mutations_require_real_csrf(self):
        anonymous_routes = [("auth/register/", {"username": "csrf-new", "password": PASSWORD}),
                            ("auth/login/", {"username": "student-a", "password": PASSWORD})]
        for route, body in anonymous_routes:
            self.assert_error(self.client.post(API + route, json.dumps(body), content_type="application/json",
                                              HTTP_IDEMPOTENCY_KEY="csrf"), 403, "CSRF_FAILED")
        self.sign_in()
        routes = [*anonymous_routes, ("auth/logout/", {}),
                  ("users/me/", {"selected_grade_id": self.grade.pk}),
                  ("onboarding/complete/", {"selected_grade_id": self.grade.pk, "mode": "START_ZERO"})]
        for route, body in routes:
            method = "patch" if route == "users/me/" else "post"
            for headers in [{}, {"HTTP_X_CSRFTOKEN": "a" * 32}]:
                with self.subTest(route=route, invalid=bool(headers)):
                    self.assert_error(getattr(self.client, method)(API + route, json.dumps(body),
                        content_type="application/json", HTTP_IDEMPOTENCY_KEY="csrf", **headers),
                        403, "CSRF_FAILED")
        self.assertEqual(IdentityReceipt.objects.count(), 0)
        self.assertFalse(StudentProfile.objects.get(user=self.user).onboarding_complete)

    def test_csrf_rejects_bad_origin_and_post_form_token_without_header(self):
        token = self.token()
        response = self.client.post(API + "auth/login/", json.dumps({"username": "student-a", "password": PASSWORD}),
                                    content_type="application/json", HTTP_X_CSRFTOKEN=token,
                                    HTTP_ORIGIN="https://untrusted.invalid")
        self.assert_error(response, 403, "CSRF_FAILED")
        response = self.client.post(API + "auth/login/", {"csrfmiddlewaretoken": token,
                                    "username": "student-a", "password": PASSWORD})
        self.assert_error(response, 403, "CSRF_FAILED")

    def test_anonymous_private_routes_return_auth_before_payload_or_csrf(self):
        for route, method in [("users/me/", "get"), ("users/me/", "patch"),
                              ("auth/logout/", "post"), ("onboarding/complete/", "post")]:
            self.assert_error(getattr(self.client, method)(API + route), 401, "AUTHENTICATION_REQUIRED")

    def test_drf_routes_keep_csrf_and_only_session_authentication(self):
        from django.urls import resolve
        from rest_framework.authentication import SessionAuthentication
        from rest_framework.views import APIView
        for route in ["auth/csrf/", "auth/register/", "auth/login/", "auth/logout/",
                      "users/me/", "onboarding/complete/"]:
            callback = resolve(API + route).func
            self.assertTrue(issubclass(callback.cls, APIView))
            self.assertEqual(callback.cls.authentication_classes, [SessionAuthentication])
            self.assertFalse(getattr(callback, "csrf_exempt", False))
        authorization = "Basic " + base64.b64encode(("student-a:" + PASSWORD).encode()).decode()
        self.assert_error(self.client.get(API + "users/me/", HTTP_AUTHORIZATION=authorization),
                          401, "AUTHENTICATION_REQUIRED")

    def test_drf_content_negotiation_keeps_r02a_json_error(self):
        self.assert_error(self.client.get(API + "auth/csrf/", HTTP_ACCEPT="text/html"),
                          400, "INVALID_REQUEST")

    def test_get_is_read_only_even_if_a_profile_is_missing(self):
        self.sign_in()
        StudentProfile.objects.filter(user=self.user).delete()
        with CaptureQueriesContext(connection) as captured:
            for _ in range(2):
                self.token()
                response = self.client.get(API + "users/me/")
                self.assert_wire(response, 200, "UserResponse")
        writes = [q["sql"] for q in captured if q["sql"].lstrip().split()[0].upper()
                  in {"INSERT", "UPDATE", "DELETE", "REPLACE"}]
        self.assertEqual(writes, [])
        self.assertFalse(StudentProfile.objects.filter(user=self.user).exists())
        self.assertEqual(IdentityReceipt.objects.count(), 0)
        self.assertFalse(response.json()["data"]["onboarding_complete"])

    def test_csrf_bootstrap_get_does_not_create_auth_session(self):
        with CaptureQueriesContext(connection) as captured:
            self.token()
        self.assertNotIn("sessionid", self.client.cookies)
        self.assertEqual(Session.objects.count(), 0)
        self.assertFalse(any(q["sql"].lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE")) for q in captured))

    def test_foreign_and_missing_profile_uuid_service_are_same_404(self):
        self.assertEqual(owned_profile(self.user, self.profile.pk).user_id, self.user.pk)
        errors = []
        for identifier in [self.profile.pk, uuid.uuid4()]:
            with self.assertRaises(APIError) as result:
                owned_profile(self.other, identifier)
            errors.append((result.exception.status, result.exception.code, result.exception.message))
        self.assertEqual(errors[0], errors[1])
        self.assertEqual(errors[0][0], 404)
        with self.assertRaises(APIError) as result:
            owned_profile(AnonymousUser(), self.profile.pk)
        self.assertEqual(result.exception.status, 401)

    def test_no_public_other_user_uuid_route_or_secret_disclosure(self):
        self.sign_in()
        errors = [self.assert_error(self.client.get(API + f"users/{identifier}/"), 404, "NOT_FOUND")
                  for identifier in [self.profile.pk, uuid.uuid4()]]
        self.assertEqual(errors[0], errors[1])
        self.assertEqual(self.client.get(API + "users/me/").json()["data"]["id"], self.user.pk)

    def test_invalid_json_shape_size_encoding_and_method(self):
        token = self.token()
        invalid = ['{"username":"a","username":"b","password":"x"}', '{bad', '[]',
                   '{"username":"a","password":NaN}', '{"username":"a","password":Infinity}',
                   json.dumps({"username": "a", "password": 12})]
        for raw in invalid:
            response = self.client.post(API + "auth/login/", raw, content_type="application/json", HTTP_X_CSRFTOKEN=token)
            self.assert_error(response, 400, "INVALID_REQUEST")
        response = self.client.post(API + "auth/login/", b"\xff", content_type="application/json", HTTP_X_CSRFTOKEN=token)
        self.assert_error(response, 400, "INVALID_REQUEST")
        response = self.client.post(API + "auth/login/", "x" * 65537, content_type="application/json", HTTP_X_CSRFTOKEN=token)
        self.assert_error(response, 400, "LIMIT_EXCEEDED")
        self.assert_error(self.client.get(API + "auth/login/"), 400, "INVALID_REQUEST")
        self.assertEqual(LoginWindow.objects.count(), 0)

    def test_login_rate_limit_shared_between_clients_and_retry_after(self):
        client_a, client_b = Client(enforce_csrf_checks=True), Client(enforce_csrf_checks=True)
        body = {"username": "missing-account", "password": PASSWORD}
        for i in range(10):
            self.assert_error(self.mutate("auth/login/", body, client=client_a if i % 2 else client_b),
                              401, "AUTHENTICATION_REQUIRED")
        limited = self.mutate("auth/login/", body, client=client_a)
        self.assert_error(limited, 429, "RATE_LIMITED")
        self.assertTrue(1 <= int(limited["Retry-After"]) <= 300)
        self.assertEqual(LoginWindow.objects.get().count, 10)
        self.assertNotEqual(LoginWindow.objects.get().ip_digest, "127.0.0.1")

    def test_rate_window_boundary_and_distinct_ip(self):
        now = timezone.now()
        for _ in range(10):
            consume_login_budget("192.0.2.1", now)
        with self.assertRaises(APIError) as limited:
            consume_login_budget("192.0.2.1", now + timedelta(seconds=299))
        self.assertEqual(limited.exception.retry_after, 1)
        consume_login_budget("192.0.2.1", now + timedelta(seconds=300))
        consume_login_budget("192.0.2.2", now)
        self.assertEqual(sorted(LoginWindow.objects.values_list("count", flat=True)), [1, 1])

    def test_successful_logins_count_towards_limit(self):
        for _ in range(10):
            self.sign_in()
        old_key = self.client.session.session_key
        response = self.mutate("auth/login/", {"username": "student-a", "password": PASSWORD})
        self.assert_error(response, 429, "RATE_LIMITED")
        self.assertEqual(self.client.session.session_key, old_key)
        self.assertEqual(LoginWindow.objects.get().count, 10)

    def test_invalid_login_does_not_log_password(self):
        with self.assertLogs("django.request", level="WARNING") as captured:
            response = self.mutate("auth/login/", {"username": "missing-logged", "password": PASSWORD})
        self.assert_error(response, 401, "AUTHENTICATION_REQUIRED")
        self.assertNotIn(PASSWORD, "\n".join(captured.output))
        self.assertNotIn("missing-logged", "\n".join(captured.output))

    def test_forwarded_ip_cannot_evade_login_limit(self):
        token = self.token()
        body = json.dumps({"username": "missing", "password": PASSWORD})
        for i in range(11):
            response = self.client.post(API + "auth/login/", body, content_type="application/json",
                                        HTTP_X_CSRFTOKEN=token, HTTP_X_FORWARDED_FOR=f"192.0.2.{i}")
        self.assert_error(response, 429, "RATE_LIMITED")
        self.assertEqual(LoginWindow.objects.count(), 1)

    def test_digest_matches_frozen_reference(self):
        body = {"mode": "START_ZERO", "selected_grade_id": 1}
        args = ("1", "complete_onboarding", API + "onboarding/complete/", body)
        self.assertEqual(request_digest(*args), contract_digest(*args))

    def test_database_failure_has_safe_503_envelope(self):
        from django.db import DatabaseError
        with patch("users.services.consume_login_budget", side_effect=DatabaseError("private database details")):
            response = self.mutate("auth/login/", {"username": "student-a", "password": PASSWORD})
        self.assert_error(response, 503, "SERVICE_UNAVAILABLE")
        self.assertNotIn("private database details", response.content.decode())

    def test_profile_constraint_rejects_impossible_states(self):
        for values in [{"onboarding_mode": "INVALID"}, {"onboarding_complete": True},
                       {"onboarding_mode": "START_ZERO", "selected_grade": self.grade},
                       {"onboarding_complete": True, "onboarding_mode": "INVALID", "selected_grade": self.grade}]:
            with self.subTest(values=values), self.assertRaises(IntegrityError), transaction.atomic():
                StudentProfile.objects.filter(user=self.user).update(**values)
