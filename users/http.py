"""R02A wire validation and safe envelopes, using the frozen local DTO bundle."""
import json
import uuid
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user
from django.core.exceptions import RequestDataTooBig
from django.http import JsonResponse
from django.db import DatabaseError
from django.views.csrf import csrf_failure as django_csrf_failure
from jsonschema import Draft202012Validator, FormatChecker


class APIError(Exception):
    def __init__(self, status, code, message, field_errors=None, retry_after=None):
        self.status = status
        self.code = code
        self.message = message
        self.field_errors = field_errors or {}
        self.retry_after = retry_after


def request_id(request):
    if not hasattr(request, "identity_request_id"):
        request.identity_request_id = str(uuid.uuid4())
    return request.identity_request_id


def envelope(request, data):
    return {"data": data, "meta": {"request_id": request_id(request), "version": "http-v1"}}


def json_response(body, status=200):
    # JSONField/jsonb may reorder nested object keys. Both the first response
    # and persisted receipt replay must use the same deterministic wire bytes.
    response = JsonResponse(body, status=status,
                            json_dumps_params={"ensure_ascii": False, "sort_keys": True})
    response["Content-Type"] = "application/json; charset=utf-8"
    response["Cache-Control"] = "private, no-store"
    return response


def error_response(request, error):
    response = json_response({"error": {
        "code": error.code, "message": error.message, "field_errors": error.field_errors,
        "retryable": error.status in (429, 503), "request_id": request_id(request),
    }}, error.status)
    if error.retry_after is not None:
        response["Retry-After"] = str(error.retry_after)
    return response


def csrf_failure(request, reason=""):
    if request.path.startswith("/api/v1/"):
        return error_response(request, APIError(403, "CSRF_FAILED", "CSRF validation failed."))
    return django_csrf_failure(request, reason=reason)


def authentication_required():
    return APIError(401, "AUTHENTICATION_REQUIRED", "Authentication required.")


class IdentityBoundaryMiddleware:
    """Authenticate private identity routes before CSRF; preserve legacy pages."""

    PRIVATE_PATHS = {
        "/api/v1/users/me/", "/api/v1/auth/logout/", "/api/v1/onboarding/complete/",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in self.PRIVATE_PATHS:
            try:
                request._cached_user = get_user(request)
                if not request._cached_user.is_authenticated:
                    return error_response(request, authentication_required())
            except DatabaseError:
                return error_response(request, APIError(
                    503, "SERVICE_UNAVAILABLE", "Service temporarily unavailable.",
                ))
        response = self.get_response(request)
        if request.path.startswith("/api/v1/") and response.status_code == 404:
            return error_response(request, APIError(404, "NOT_FOUND", "Resource unavailable."))
        return response


@lru_cache(maxsize=1)
def schema_bundle():
    path = Path(settings.BASE_DIR) / "specs/api/schemas/dto-v1.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def wire_validator(name):
    bundle = schema_bundle()
    return Draft202012Validator(
        {"$defs": bundle["$defs"], "$ref": f"#/$defs/{name}"},
        format_checker=FormatChecker(),
    )


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("Nonfinite JSON number")


def parse_request(request, schema):
    if request.content_type != "application/json" or request.encoding not in (None, "utf-8", "UTF-8"):
        raise APIError(400, "INVALID_REQUEST", "Expected UTF-8 JSON.")
    try:
        raw = request.body
        if len(raw) > 65536:
            raise RequestDataTooBig()
        body = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                          parse_constant=_reject_constant)
    except RequestDataTooBig:
        raise APIError(400, "LIMIT_EXCEEDED", "Request exceeds the size limit.") from None
    except (ValueError, UnicodeError, RecursionError):
        raise APIError(400, "INVALID_REQUEST", "Invalid JSON request.") from None
    # Never return jsonschema's message: it can contain the submitted password.
    if not wire_validator(schema).is_valid(body):
        raise APIError(400, "INVALID_REQUEST", "Request does not match the schema.")
    return body
