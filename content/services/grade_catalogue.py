"""Read-only Grade DTOs and R02A keyset pagination owned by Content."""
import re
from datetime import datetime, timezone

from django.core import signing
from django.db.models import Q

from config.api_http import APIError
from content.models import Grade

CURSOR_SALT = "content.grades.http-v1.cursor"
CURSOR_SCOPE = "public:/api/v1/grades/"
MAX_CURSOR_LENGTH = 1024


def invalid_query():
    return APIError(400, "INVALID_REQUEST", "Invalid catalogue query.")


def unavailable():
    return APIError(503, "SERVICE_UNAVAILABLE", "Service temporarily unavailable.")


def query_options(params):
    # The catalogue has no filters. Bind cursors to its explicit query surface.
    if set(params) - {"cursor", "page_size"} or any(len(params.getlist(key)) != 1 for key in params):
        raise invalid_query()
    raw_size = params.get("page_size", "20")
    if not re.fullmatch(r"[0-9]{1,3}", raw_size) or not 1 <= int(raw_size) <= 100:
        raise invalid_query()
    page_size = int(raw_size)
    cursor = params.get("cursor")
    if cursor is None:
        return page_size, None
    if not cursor or len(cursor) > MAX_CURSOR_LENGTH:
        raise invalid_query()
    try:
        value = signing.loads(cursor, salt=CURSOR_SALT)
        if (not isinstance(value, dict)
                or set(value) != {"scope", "page_size", "created_at", "id"}
                or value["scope"] != CURSOR_SCOPE
                or type(value["page_size"]) is not int or value["page_size"] != page_size
                or type(value["id"]) is not int or not 0 < value["id"] < 2**63
                or not isinstance(value["created_at"], str)):
            raise ValueError()
        stamp = datetime.fromisoformat(value["created_at"])
        if stamp.tzinfo is None or stamp.utcoffset() != timezone.utc.utcoffset(stamp):
            raise ValueError()
    except (signing.BadSignature, ValueError, TypeError, OverflowError):
        raise invalid_query() from None
    return page_size, (stamp, value["id"])


def grade_data(grade):
    # The repository catalogue defines semantic numbers in canonical slugs.
    # Neither mutable display order nor a database PK is a class number.
    match = re.fullmatch(r"([1-9]|1[0-2])-klass", grade.slug)
    if match is None or not grade.title:
        raise unavailable()
    return {"id": grade.pk, "number": int(match[1]), "title": grade.title}


def list_grades(params):
    page_size, position = query_options(params)
    query = Grade.objects.order_by("created_at", "id")
    if position is not None:
        stamp, pk = position
        query = query.filter(Q(created_at__gt=stamp) | Q(created_at=stamp, id__gt=pk))
    rows = list(query.only("id", "slug", "title", "created_at")[:page_size + 1])
    has_more = len(rows) > page_size
    page = rows[:page_size]
    data = [grade_data(grade) for grade in page]
    next_cursor = None
    if has_more:
        last = page[-1]
        next_cursor = signing.dumps({
            "scope": CURSOR_SCOPE, "page_size": page_size,
            "created_at": last.created_at.astimezone(timezone.utc).isoformat(timespec="microseconds"),
            "id": last.pk,
        }, salt=CURSOR_SALT)
    return data, {"next_cursor": next_cursor, "page_size": page_size, "has_more": has_more}
