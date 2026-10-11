# MS7-MIG-V01 compatibility addendum v1.0.0 — B01

- Source input: `8d958aeeb17da46839722441425ccbb5889e2ab7`.
- MIG_BASE_SHA remains separately `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
- Frozen R02 schema mapping SHA256: `4faf862e8810e817d241b9134a2f52a2d62a8236b491bdc7c658e588a863f588`.
- Decision owner: Руслан, R02 Owner; decision reported directly by the user in
  the continuation request, recorded 2026-10-09 Europe/Moscow.
- [Approval evidence and its provenance limits](b01-owner-approval-v1.json).

## Accepted compatibility decision

| Table | Column | SQLAlchemy / Alembic PostgreSQL type |
| --- | --- | --- |
| auth_group_permissions | id | BIGINT |
| auth_user_groups | id | BIGINT |
| auth_user_user_permissions | id | BIGINT |

Use the physical PostgreSQL baseline for precisely these three PK columns.
Preserve their generated-by-default identity and bigint sequence ownership.
`group_id`, `permission_id`, `user_id`, parent IDs, FK targets, constraints,
defaults, nullability and every other column are unchanged. This is a scoped
resolution, not a general rule allowing model metadata to be overridden.

The [machine-readable adapter](../../../backend/models/compatibility-v1.json)
is consumed by the existing baseline metadata builder used by Alembic revision
`v01_0001` and by SQLAlchemy models. Revision chain/order remains unchanged;
it has only run on disposable test databases and has no accepted deployment.
Future applied revision snapshots require the existing immutability rule.

Frozen R02 JSON, hashes, historical finding/verification and prior uncommitted
files remain preserved. Initial files were checked against the prior manifest
and copied to an ignored local continuation snapshot before edits. The original
finding remains a historical record; this addendum records its current resolution.

CHECK canonicalization is a separate implementation investigation. This approval
does not permit ignoring expressions, accepting weaker constraints, editing
frozen contracts or silently changing application semantics. V01 DDL review and
Task Approval, production ownership/cutover, commit/push/PR remain separate gates.
