"""Public real-ID Grade adapter, using the existing V01 UoW."""
import re
from datetime import datetime, timezone

import sqlalchemy as sa

from backend.models.baseline import Grade
from backend.infrastructure.http.transport import invalid, unavailable, singleton_query, page_size

SALT = "content.grades.http-v1.cursor"
SCOPE = "public:/api/v1/grades/"


def utc_stamp(value):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise unavailable()
    return value.isoformat(timespec="microseconds")


def list_grades(uow, params, signer):
    query = singleton_query(params, {"cursor", "page_size"})
    size = page_size(query.get("page_size", "20"))
    statement = sa.select(Grade.id, Grade.title, Grade.slug, Grade.created_at).order_by(Grade.created_at, Grade.id)
    if "cursor" in query:
        value = signer.loads(query["cursor"], SALT)
        try:
            if (not isinstance(value, dict) or set(value) != {"scope", "page_size", "created_at", "id"}
                    or value["scope"] != SCOPE or type(value["page_size"]) is not int or value["page_size"] != size
                    or type(value["id"]) is not int or not 0 < value["id"] < 2**63
                    or not isinstance(value["created_at"], str)):
                raise ValueError()
            stamp = datetime.fromisoformat(value["created_at"])
            if stamp.tzinfo is None or stamp.utcoffset() != timezone.utc.utcoffset(stamp):
                raise ValueError()
        except (ValueError, TypeError, OverflowError):
            raise invalid() from None
        statement = statement.where(sa.or_(Grade.created_at > stamp, sa.and_(Grade.created_at == stamp, Grade.id > value["id"])))
    rows = list(uow.session.execute(statement.limit(size + 1)))
    more = len(rows) > size
    rows = rows[:size]
    data = []
    for row in rows:
        match = re.fullmatch(r"([1-9]|1[0-2])-klass", row.slug)
        if not match or not row.title:
            raise unavailable()
        data.append({"id": row.id, "number": int(match[1]), "title": row.title})
    cursor = None
    if more:
        last = rows[-1]
        stamp = last.created_at
        if uow.session.bind.dialect.name == 'sqlite' and stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        cursor = signer.dumps({"scope": SCOPE, "page_size": size, "created_at": utc_stamp(stamp), "id": last.id}, SALT)
    return data, {"next_cursor": cursor, "page_size": size, "has_more": more}
