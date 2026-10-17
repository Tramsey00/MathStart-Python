"""R02/R02A wire errors and raw JSON. Never return exception text."""
import json
import re
import uuid
from email.message import Message
from datetime import timezone

from starlette.responses import Response


class APIError(Exception):
    def __init__(self, status, code, message):
        self.status, self.code, self.message = status, code, message


def invalid():
    return APIError(400, "INVALID_REQUEST", "Invalid request.")


def unavailable():
    return APIError(503, "SERVICE_UNAVAILABLE", "Service temporarily unavailable.")


def missing():
    return APIError(404, "NOT_FOUND", "Resource unavailable.")


def forbidden():
    return APIError(403, "FORBIDDEN", "Access denied.")


def authentication_required():
    return APIError(401, "AUTHENTICATION_REQUIRED", "Authentication required.")


def request_id(request):
    if not hasattr(request.state, "request_id"):
        request.state.request_id = str(uuid.uuid4())
    return request.state.request_id


def json_response(body, status=200):
    return Response(json.dumps(body, ensure_ascii=False, sort_keys=True, allow_nan=False), status_code=status,
                    headers={"Content-Type": "application/json; charset=utf-8", "Cache-Control": "private, no-store"})


def success(request, data, *, pagination=None, delivery=False, schema=None):
    body = {"data": data, "meta": {"request_id": request_id(request),
                                     "version": "migration-r02-v1" if delivery else "http-v1"}}
    if pagination is not None:
        body["meta"]["pagination"] = pagination
    if schema:
        from .contracts import validate
        validate(body, schema, delivery)
    return json_response(body)


def error_response(request, error):
    return json_response({"error": {"code": error.code, "message": error.message, "field_errors": {},
                                   "retryable": error.status in (429, 503), "request_id": request_id(request)}}, error.status)


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate key")
        value[key] = item
    return value


def decode_json(raw):
    def reject_constant(_):
        raise ValueError("Nonfinite value")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object, parse_constant=reject_constant)


async def parse_request(request, schema, *, delivery=False):
    # Read bounded chunks even when Content-Length is absent or incorrect.
    content_type = Message()
    content_type['content-type'] = request.headers.get('content-type', '')
    if content_type.get_content_type() != 'application/json' or content_type.get_content_charset() not in (None, 'utf-8'):
        raise invalid()
    raw = bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw) > 65536:
            raise APIError(400, "LIMIT_EXCEEDED", "Request exceeds the size limit.")
    try:
        value = decode_json(bytes(raw))
        from .contracts import validator
        if not validator(schema, delivery).is_valid(value):
            raise invalid()
        return value
    except (ValueError, UnicodeError, RecursionError, OverflowError):
        raise invalid() from None


def singleton_query(params, allowed):
    if set(params) - set(allowed) or any(len(params.getlist(key)) != 1 for key in params):
        raise invalid()
    return dict(params)


def page_size(raw="20"):
    if not isinstance(raw, str) or not re.fullmatch(r"[0-9]{1,3}", raw) or not 1 <= int(raw) <= 100:
        raise invalid()
    return int(raw)


def identity(raw):
    if not isinstance(raw, str) or not re.fullmatch(r"[0-9]+", raw) or len(raw) > 19 or not 0 < int(raw) < 2**63:
        raise invalid()
    return int(raw)


def timestamp(value):
    if value is None:
        return None
    # Explicit SQLite compatibility loses timezone data; PostgreSQL retains it.
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat(timespec='microseconds')
