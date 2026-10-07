"""Shared R02A transport primitives; domain services own their decisions."""
import uuid

from django.http import JsonResponse


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
    # Keep V02 response/replay bytes identical when JSON storage reorders keys.
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
