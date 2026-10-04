"""Issue 23: real catalogue identities, cursor integrity and read-only GET."""
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core import signing
from django.db import DatabaseError, connection
from django.test import Client, TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from content.models import Grade
from content.services.grade_catalogue import CURSOR_SALT, CURSOR_SCOPE
from scripts.r02a_contract_reference import validator
from users.models import IdentityReceipt, LoginWindow, StudentProfile

URL = "/api/v1/grades/"
STAMP = datetime(2026, 10, 4, tzinfo=timezone.utc)


@override_settings(SECURE_SSL_REDIRECT=False, SESSION_COOKIE_SECURE=False,
                   CSRF_COOKIE_SECURE=False)
class GradeAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Reverse display/number/PK order and tie timestamps to exercise both keys.
        cls.grades = [
            Grade.objects.create(id=70, slug="5-klass", title="5 класс", order=99),
            Grade.objects.create(id=30, slug="10-klass", title="10 класс", order=1),
            Grade.objects.create(id=50, slug="6-klass", title="6 класс", order=0),
        ]
        Grade.objects.filter(id__in=[70, 30]).update(created_at=STAMP)
        Grade.objects.filter(id=50).update(created_at=STAMP + timedelta(seconds=1))

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def wire(self, response, status=200, schema="GradeListResponse"):
        self.assertEqual(response.status_code, status)
        validator(schema).validate(response.json())
        self.assertEqual(response["Content-Type"], "application/json; charset=utf-8")
        return response.json()

    def error(self, response, status=400, schema="BadRequestError"):
        body = self.wire(response, status, schema)["error"]
        self.assertEqual(body["code"], "INVALID_REQUEST" if status == 400 else "SERVICE_UNAVAILABLE")
        self.assertEqual(body["field_errors"], {})
        self.assertEqual(body["retryable"], status == 503)
        return body

    def test_anonymous_dto_contains_real_ids_and_canonical_numbers(self):
        response = self.client.get(URL)
        body = self.wire(response)
        self.assertEqual(body["data"], [
            {"id": 30, "number": 10, "title": "10 класс"},
            {"id": 70, "number": 5, "title": "5 класс"},
            {"id": 50, "number": 6, "title": "6 класс"},
        ])
        self.assertEqual(body["meta"]["pagination"],
                         {"next_cursor": None, "page_size": 20, "has_more": False})
        self.assertEqual(body["meta"]["version"], "http-v1")
        self.assertIn("5 класс", response.content.decode("utf-8"))
        self.assertEqual(dict(response.cookies), {})

    def test_empty_catalogue(self):
        Grade.objects.all().delete()  # Synthetic test storage only.
        body = self.wire(self.client.get(URL, {"page_size": 100}))
        self.assertEqual(body["data"], [])
        self.assertEqual(body["meta"]["pagination"],
                         {"next_cursor": None, "page_size": 100, "has_more": False})

    def test_cursor_pages_keep_timestamp_id_order_after_catalogue_edits(self):
        first = self.wire(self.client.get(URL, {"page_size": 1}))
        cursor = first["meta"]["pagination"]["next_cursor"]
        self.assertTrue(first["meta"]["pagination"]["has_more"])
        self.assertEqual(first["data"][0]["id"], 30)
        # Removing a delivered row must not shift an offset past the next one.
        Grade.objects.filter(id=30).delete()
        Grade.objects.filter(id=70).update(order=0, title="Пятый класс")
        new = Grade.objects.create(slug="7-klass", title="7 класс", order=1)
        second = self.wire(self.client.get(URL, {"page_size": 1, "cursor": cursor}))
        self.assertEqual(second["data"][0]["id"], 70)
        ids = [30, 70]
        while second["meta"]["pagination"]["has_more"]:
            second = self.wire(self.client.get(URL, {
                "page_size": 1, "cursor": second["meta"]["pagination"]["next_cursor"],
            }))
            ids += [row["id"] for row in second["data"]]
        self.assertEqual(ids, [30, 70, 50, new.pk])
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIsNone(second["meta"]["pagination"]["next_cursor"])

    def test_bad_query_values_are_closed_contract_errors(self):
        for size in ["0", "101", "-1", "1.5", "", "true", "２０", "1000", "9" * 1000]:
            with self.subTest(page_size=size):
                self.error(self.client.get(URL, {"page_size": size}))
        for query in ["page_size=1&page_size=2", "cursor=x&cursor=y", "grade_id=5"]:
            with self.subTest(query=query):
                self.error(self.client.get(URL + "?" + query))
        for cursor in ["", "garbage", "x" * 1025]:
            with self.subTest(cursor=cursor):
                self.error(self.client.get(URL, {"cursor": cursor}))

    def test_cursor_is_signed_and_bound_to_catalogue_and_page_size(self):
        body = self.wire(self.client.get(URL, {"page_size": 1}))
        cursor = body["meta"]["pagination"]["next_cursor"]
        self.error(self.client.get(URL, {"page_size": 2, "cursor": cursor}))
        self.error(self.client.get(URL, {"page_size": 1, "cursor": "x" + cursor[1:]}))
        base = {"scope": CURSOR_SCOPE, "page_size": 1, "created_at": STAMP.isoformat(), "id": 30}
        for changes in [{"scope": "public:/api/v1/topics/"}, {"id": True}, {"id": 0},
                        {"id": 2**63}, {"created_at": "invalid"},
                        {"created_at": "2026-10-04T00:00:00"}, {"page_size": True},
                        {"extra": "filter"}]:
            with self.subTest(changes=changes):
                token = signing.dumps({**base, **changes}, salt=CURSOR_SALT)
                self.error(self.client.get(URL, {"page_size": 1, "cursor": token}))
        wrong_salt = signing.dumps(base, salt="unrelated-endpoint")
        self.error(self.client.get(URL, {"page_size": 1, "cursor": wrong_salt}))

    def test_unknown_grade_number_and_database_errors_are_safe(self):
        Grade.objects.filter(id=70).update(slug="private-unmapped-value")
        response = self.client.get(URL)
        self.error(response, 503, "UnavailableError")
        self.assertNotIn("private-unmapped-value", response.content.decode())
        with patch("content.services.grade_catalogue.Grade.objects.order_by",
                   side_effect=DatabaseError("private SQL credentials")):
            response = self.client.get(URL)
            self.error(response, 503, "UnavailableError")
            self.assertNotIn("private SQL credentials", response.content.decode())

    def test_get_does_not_write_identity_or_catalogue_state(self):
        user = get_user_model().objects.create_user("catalogue-reader")
        profile = StudentProfile.objects.create(user=user, selected_grade_id=70,
                    onboarding_mode="START_ZERO", onboarding_complete=True)
        tables = [Grade, get_user_model(), StudentProfile, IdentityReceipt, LoginWindow, Session]

        def snapshot():
            return [list(model.objects.order_by("pk").values()) for model in tables]

        for authenticated in [False, True]:
            with self.subTest(authenticated=authenticated):
                if authenticated:
                    self.client.force_login(user)
                before = snapshot()
                with CaptureQueriesContext(connection) as captured:
                    self.wire(self.client.get(URL))
                self.assertEqual(snapshot(), before)
                for query in captured.captured_queries:
                    self.assertTrue(query["sql"].lstrip().startswith("SELECT"), query["sql"])
        profile.refresh_from_db()
        self.assertEqual(profile.selected_grade_id, 70)

    def test_get_does_not_create_a_missing_profile(self):
        user = get_user_model().objects.create_user("catalogue-no-profile")
        self.client.force_login(user)
        self.wire(self.client.get(URL))
        self.assertFalse(StudentProfile.objects.filter(user=user).exists())
        self.assertEqual(IdentityReceipt.objects.count(), 0)

    def test_catalogue_id_is_accepted_by_all_three_onboarding_modes(self):
        data = self.wire(self.client.get(URL))["data"]
        selected = next(row for row in data if row["number"] == 5)
        self.assertNotEqual(selected["id"], selected["number"])
        user = get_user_model().objects.create_user("catalogue-onboarding")
        self.client.force_login(user)
        token = self.client.get("/api/v1/auth/csrf/").json()["data"]["csrf_token"]
        for mode in ["START_ZERO", "DIAGNOSTIC", "SELF_REPORT"]:
            with self.subTest(mode=mode):
                response = self.client.post("/api/v1/onboarding/complete/",
                    data=json.dumps({"selected_grade_id": selected["id"], "mode": mode}),
                    content_type="application/json", HTTP_X_CSRFTOKEN=token,
                    HTTP_IDEMPOTENCY_KEY="catalogue-" + mode)
                body = self.wire(response, 200, "UserResponse")
                self.assertEqual(body["data"]["selected_grade_id"], selected["id"])
                self.assertTrue(body["data"]["onboarding_complete"])

    def test_only_get_is_supported(self):
        self.error(self.client.post(URL, data="{}", content_type="application/json"))
