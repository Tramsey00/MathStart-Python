# MS7-MIG-V01 B01 — incompatible ID types inside accepted R02 mapping

Status: BLOCKING / owner decision required. Discovered 2026-10-09, Europe/Moscow.
Owner Владимир; R02 contract owner / V01 Task Approver Руслан.
Input `8d958aeeb17da46839722441425ccbb5889e2ab7`;
MIG_BASE_SHA `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7` remains distinct.

The user's task explicitly requires stopping when accepted contracts disagree
with one another or the real baseline. This is that stop condition, not a new
approval inferred from historical PROPOSED status. The user's accepted input is
the current intake; historical R02 status wording was preserved.

## Observed conflict

In [frozen schema mapping](../../../specs/migration/r02-v1/schema-mapping-v1.json),
`models[].fields[]` says `type=AutoField`, `db_type=integer` for these columns,
but `physical_baseline.columns` says `data_type=bigint`, `udt_name=int8`:

| Table | Column | Model metadata | Physical baseline / Django fixture |
| --- | --- | --- | --- |
| auth_group_permissions | id | AutoField / integer | bigint / int8 |
| auth_user_groups | id | AutoField / integer | bigint / int8 |
| auth_user_user_permissions | id | AutoField / integer | bigint / int8 |

The same mapping's `fresh_disposable_sequence_evidence` has bigint owned
sequences for all three. [Platform addendum](../../../specs/migration/r02-v1/platform-v1.md)
states: “Auth User/Group/Permission IDs are int4; content and M2M auto IDs are int8.”
`config/settings.py` has `DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"`.
The real PostgreSQL source fixtures built from unchanged Django migrations match
the physical baseline. The initial target builder selected `field.db_type` and
therefore fresh Alembic creates int4 for these three columns. Strict fresh schema
comparison correctly rejected it. No deployed/user database was accessed.

## Minimal proposed resolution — not applied

Confirm that physical baseline types/widths and sequence ownership are
authoritative for all baseline DDL; model metadata remains authoritative for
application defaults, save behavior, relationships and collector semantics.
Then use the physical int8 mapping for these three ID columns, with regression
tests independently asserting catalog types and sequence ownership. Keep the
frozen R02 JSON, digests and original evidence unchanged. Record the decision as
a new owner clarification/handoff tied to the accepted input SHA.

No ID renumbering, cast of existing data, narrower sequence, Django migration
edit, DROP, API change, or new architecture is required. R02/root owned records
must be updated by their owner if a current clarification there is desired.

## Separate implementation issue — not a contract change

Re-emitting PostgreSQL's deparsed `users_consistent_onboarding` CHECK expression
reparses a varchar-array-to-text-array cast into per-element text casts. PostgreSQL
then prints syntactically different equivalent SQL. Profile A/fresh comparison
also fails on this exact-string check. Baseline B/C (unmodified physical CHECK)
passes. Fixing the builder to emit the original IN expression, or comparing a
reviewed PostgreSQL canonical expression, needs a regression test; weakening the
entire constraint comparator is not an acceptable repair. This issue is pending
because implementation stopped at B01.

## Required next action

Human owner/approver confirms or rejects the proposed physical-type precedence.
Resume only after that response; then finish implementation and all acceptance
checks. Existing partial code is INCOMPLETE and must not be adopted or deployed.
