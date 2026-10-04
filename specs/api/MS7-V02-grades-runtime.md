# MS7-V02 follow-up: Grade catalogue runtime mapping (Issue 23)

- **Status:** Implemented; review and acceptance pending
- **Owner:** Владимир
- **Reviewer / Task Approver:** Руслан
- **Consumer:** Илья, MS7-I03
- **Date:** 2026-10-04
- **Issue:** https://github.com/Tramsey00/MathStart-Python/issues/23
- **Plan:** [grades API plan](../../docs/exec-plans/active/MS7-V02-grades-api.md)

## Authority and scope

This document records a legacy-model adapter for the already accepted R02A
`GET /api/v1/grades/`; it does not replace OpenAPI, DTO schemas or HTTP policy.
Those frozen files and their manifest digests remain unchanged. Content owns
the catalogue and DTO adapter. Shared HTTP helpers live in infrastructure;
Content has no Users business dependency. Existing V02 imports and identity
response bytes are preserved through compatibility exports.

## Persistence and DTO mapping

| Wire field | Existing model source | Rule |
| --- | --- | --- |
| `id` | `Grade.pk` | Real database ID; do not substitute the class number. |
| `number` | `Grade.slug` | Canonical `<number>-klass`, integer 1..12. Repository catalogue uses this convention. |
| `title` | `Grade.title` | Existing nonempty title, serialized as UTF-8. |

Display `order` and PK allocation do not define the semantic school year. Slug,
description, display order and timestamp are not public DTO fields. A row with
an unsupported slug or empty title fails safely with the contract 503 envelope;
the service does not skip it or fabricate a number. Administrators must keep
catalogue slugs canonical. This task does not rewrite catalogue data or bootstrap.

The user explicitly agreed on 2026-10-04 to add `Grade.created_at` after discovery
that R02A ordering cannot be implemented faithfully from the old schema. The
additive `0002_grade_created_at` migration preserves all existing IDs, fields and
references. Legacy rows receive the same UTC tracking epoch `2026-10-04T00:00:00Z`:
their original creation timestamps were not recorded. Their relative order uses
the existing ID tie-breaker. New rows use Django `auto_now_add`; normal edits and
repeated bootstrap retain this timestamp. Do not interpret the legacy epoch as
a recovered historical creation time. Review the migration before merge;
prefer forward fixes over reversing a populated timestamp column.

## Pagination and errors

Ascending `(created_at,id)` keyset pagination, default `page_size=20`, maximum
100, one bounded query fetching at most `page_size+1` rows. No offset pagination.
The signed opaque cursor binds the public route, protocol salt, position and
page size. This anonymous catalogue has no private owner or filters. Supply the
same `page_size` when continuing a page. Mutable title/order do not move rows;
deletion of a delivered row does not shift the next page. New later rows can
appear on later pages; this is not a snapshot of the catalogue.

Only `cursor` and `page_size` are supported. Repeated/unknown parameters, invalid
sizes, malformed/oversized/tampered/cross-route cursors and page-size changes
return safe R02A `400 INVALID_REQUEST`. Database failure or an unmappable row
returns `503 SERVICE_UNAVAILABLE` with `retryable=true`, without raw row/SQL
details. Anonymous and signed-in readers share the public catalogue cursor scope.

The endpoint supports GET only. It creates no authentication session, profile,
onboarding state, receipt, attempt or evidence. `GradeListResponse` contains
`data`, `meta.request_id`, `meta.version=http-v1` and mandatory pagination with
`next_cursor`, `page_size`, `has_more`.

## I03 handoff

Fetch `/api/v1/grades/`, show `title`, retain each returned `id` as the option's
value and pass it as `selected_grade_id` to the existing profile/onboarding API.
Continue pages using `meta.pagination.next_cursor` until `has_more=false`.

Synthetic example (IDs vary per database):

```json
{
  "data": [{"id": 70, "number": 5, "title": "5 класс"}],
  "meta": {
    "request_id": "00000000-0000-4000-8000-000000000001",
    "version": "http-v1",
    "pagination": {"next_cursor": null, "page_size": 20, "has_more": false}
  }
}
```

The integration test deliberately uses `id=70` for class 5, retrieves it through
the API and submits it successfully with START_ZERO, DIAGNOSTIC and SELF_REPORT
through V02 with real CSRF checks. Numeric knowledge initialization is unchanged.

## Verification and acceptance

Tests cover DTOs, anonymous/empty reads, bounded pagination, equal timestamps,
edits/deletion/new rows, signed query binding, safe errors, no writes and V02
integration. Upgrade verification preserves Grade/Subject/User/StudentProfile
values and references. Bootstrap regression checks timestamp stability. Actual
commands/results and interpreter/database versions belong in the task trace.
Руслан review, merge and I03 handoff remain required before Issue closure.
