"""Identity transactions. No imports/writes of Assessment or Progress."""
import hashlib
import json
import math
from datetime import timedelta

from django.contrib.auth import authenticate, get_user_model, login as django_login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.views.decorators.debug import sensitive_variables

from content.models import Grade
from .http import APIError, authentication_required, envelope
from .models import IdentityReceipt, LoginWindow, StudentProfile

RECEIPT_RETENTION = timedelta(days=7)
LOGIN_WINDOW_SECONDS = 300
LOGIN_LIMIT = 10
REGISTRATION_SCOPE = "identity_registration_scope"


def require_user(user):
    if not user.is_authenticated or not user.is_active:
        raise authentication_required()


def owned_profile(user, profile_id=None, lock=False):
    """Filter by authenticated owner before resolving an optional internal UUID."""
    require_user(user)
    query = StudentProfile.objects.filter(user_id=user.pk)
    if lock:
        query = query.select_for_update()
    if profile_id is not None:
        profile = query.filter(pk=profile_id).first()
        if profile is None:
            raise APIError(404, "NOT_FOUND", "Resource unavailable.")
        return profile
    return query.first()


def user_data(user, profile=None):
    if profile is None:
        profile = owned_profile(user)
    return {
        "id": user.pk, "username": user.username,
        "selected_grade_id": profile.selected_grade_id if profile else None,
        "onboarding_mode": profile.onboarding_mode if profile else None,
        "onboarding_complete": profile.onboarding_complete if profile else False,
    }


def selected_grade(value):
    # Wire permits integer/string IDs; existing Content Grade has an integer PK.
    if isinstance(value, str):
        if not value.isascii() or not value.isdecimal() or len(value) > 19:
            raise APIError(400, "INVALID_REQUEST", "Invalid selected grade.")
        value = int(value)
    if isinstance(value, bool) or not isinstance(value, int) or not 0 < value < 2**63:
        raise APIError(400, "INVALID_REQUEST", "Invalid selected grade.")
    grade = Grade.objects.filter(pk=value).first()
    if grade is None:
        raise APIError(400, "INVALID_REQUEST", "Invalid selected grade.")
    return grade


def request_digest(owner, operation, route, body):
    value = {"owner": owner, "operation": operation, "canonical_route": route,
             "body": body, "expected_revision": body.get("expected_revision")}
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def receipt_key(request):
    key = request.headers.get("Idempotency-Key")
    if not key:
        raise APIError(400, "INVALID_REQUEST", "Idempotency-Key is required.")
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def _locked_receipt(scope, operation, key_digest, digest):
    # get_or_create's unique constraint resolves concurrent first writers. The
    # outer transaction and row lock cover the action and persisted response.
    receipt, _ = IdentityReceipt.objects.get_or_create(
        scope=scope, operation=operation, key_digest=key_digest,
        defaults={"request_digest": digest, "expires_at": timezone.now() + RECEIPT_RETENTION},
    )
    receipt = IdentityReceipt.objects.select_for_update().get(pk=receipt.pk)
    if receipt.request_digest != digest:
        raise APIError(409, "IDEMPOTENCY_CONFLICT", "Idempotency key conflicts with this request.")
    # Retain identity receipts, including after their minimum replay window.
    # No expiry job silently removes registration/onboarding action identity.
    return receipt


def _save_receipt(receipt, user, body, status):
    receipt.user = user
    receipt.response = body
    receipt.status = status
    receipt.save(update_fields=["user", "response", "status"])


def _registration_scope(request):
    scope = request.session.get(REGISTRATION_SCOPE)
    if scope is None:
        # Anonymous bootstrap identity is bound to the verified CSRF cookie.
        # POST stores it across the login CSRF/session rotation; GET writes no session.
        csrf_secret = request.META["CSRF_COOKIE"]
        scope = "bootstrap:" + salted_hmac("users.register.bootstrap", csrf_secret,
                                          algorithm="sha256").hexdigest()
        request.session[REGISTRATION_SCOPE] = scope
    return scope


@sensitive_variables("body", "password")
@transaction.atomic
def register(request, body):
    key = receipt_key(request)
    scope = _registration_scope(request)
    digest = request_digest(scope, "register", "/api/v1/auth/register/", body)
    receipt = _locked_receipt(scope, "register", key, digest)
    if receipt.status is not None:
        user = get_user_model().objects.get(pk=receipt.user_id)
        if not user.is_active:
            raise APIError(409, "STATE_CONFLICT", "Registration cannot be completed.")
        if request.user.is_authenticated and request.user.pk != user.pk:
            raise APIError(409, "STATE_CONFLICT", "Registration cannot be completed.")
        if not request.user.is_authenticated and not user.check_password(body["password"]):
            raise APIError(409, "STATE_CONFLICT", "Registration cannot be completed.")
        return user, receipt.response, receipt.status
    if request.user.is_authenticated:
        raise APIError(409, "STATE_CONFLICT", "Registration cannot be completed.")
    user = get_user_model()(username=body["username"], email=body.get("email", ""))
    password = body["password"]
    try:
        user._meta.get_field("username").run_validators(user.username)
        user._meta.get_field("email").run_validators(user.email)
        validate_password(password, user=user)
    except ValidationError:
        raise APIError(400, "INVALID_REQUEST", "Registration details are invalid.") from None
    user.set_password(password)
    try:
        with transaction.atomic():
            user.save()
    except IntegrityError:
        raise APIError(400, "INVALID_REQUEST", "Registration details are invalid.") from None
    profile = StudentProfile.objects.create(user=user)
    response = envelope(request, user_data(user, profile))
    _save_receipt(receipt, user, response, 201)
    return user, response, 201


def establish_session(request, user):
    # Django rotates on an anonymous/different-user transition. Rotate also on
    # repeated login as the accepted contract requires for every successful login.
    old_key = request.session.session_key
    django_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    if request.session.session_key == old_key:
        request.session.cycle_key()


def consume_login_budget(remote_addr, now=None):
    initial_time = now or timezone.now()
    ip_digest = salted_hmac("users.login.ip", remote_addr, algorithm="sha256").hexdigest()
    retry_after = None
    with transaction.atomic():
        counter, _ = LoginWindow.objects.get_or_create(
            ip_digest=ip_digest, defaults={"started_at": initial_time},
        )
        counter = LoginWindow.objects.select_for_update().get(pk=counter.pk)
        # Evaluate the window after waiting for the lock, so queued workers do
        # not reset/count with a timestamp from before another worker's reset.
        current_time = now or timezone.now()
        elapsed = (current_time - counter.started_at).total_seconds()
        if elapsed >= LOGIN_WINDOW_SECONDS:
            counter.started_at = current_time
            counter.count = 0
        if counter.count >= LOGIN_LIMIT:
            retry_after = max(1, math.ceil(LOGIN_WINDOW_SECONDS - elapsed))
        else:
            counter.count += 1
            counter.save(update_fields=["started_at", "count"])
    if retry_after is not None:
        raise APIError(429, "RATE_LIMITED", "Too many login requests.", retry_after=retry_after)


@sensitive_variables("body")
def login(request, body):
    # Forwarded headers are untrusted; use the server-provided remote address.
    consume_login_budget(request.META.get("REMOTE_ADDR", ""))
    user = authenticate(request, username=body["username"], password=body["password"])
    if user is None:
        # Standard ModelBackend performs a dummy password hash for missing users.
        raise APIError(401, "AUTHENTICATION_REQUIRED", "Invalid username or password.")
    with transaction.atomic():
        get_user_model().objects.select_for_update().get(pk=user.pk)
        StudentProfile.objects.get_or_create(user=user)
    establish_session(request, user)
    return user_data(user)


@transaction.atomic
def update_profile(user, body):
    require_user(user)
    grade = selected_grade(body["selected_grade_id"])
    get_user_model().objects.select_for_update().get(pk=user.pk)
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    if profile.selected_grade_id != grade.pk:
        profile.selected_grade = grade
        profile.save(update_fields=["selected_grade"])
    return user_data(user, profile)


@transaction.atomic
def complete_onboarding(request, body):
    require_user(request.user)
    key = receipt_key(request)
    # Serialize profile changes and all onboarding keys on the authenticated user.
    user = get_user_model().objects.select_for_update().get(pk=request.user.pk)
    scope = "user:" + str(user.pk)
    digest = request_digest(str(user.pk), "complete_onboarding", "/api/v1/onboarding/complete/", body)
    receipt = _locked_receipt(scope, "complete_onboarding", key, digest)
    if receipt.status is not None:
        return receipt.response, receipt.status
    grade = selected_grade(body["selected_grade_id"])
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    if (profile.selected_grade_id != grade.pk or profile.onboarding_mode != body["mode"]
            or not profile.onboarding_complete):
        profile.selected_grade = grade
        profile.onboarding_mode = body["mode"]
        profile.onboarding_complete = True
        profile.save(update_fields=["selected_grade", "onboarding_mode", "onboarding_complete"])
    response = envelope(request, user_data(user, profile))
    _save_receipt(receipt, user, response, 200)
    return response, 200
