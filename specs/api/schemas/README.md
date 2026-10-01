# HTTP schema sources

`dto-v1.schema.json` is the canonical public HTTP DTO bundle (JSON Schema
2020-12). `scenario-v1.schema.json` validates serial transaction fixture inputs
and expected observations only; it is not an HTTP response or database schema.

`openapi-3.1-2025-09-15.schema.json` is the unmodified official OpenAPI Initiative
structural schema downloaded from
https://spec.openapis.org/oas/3.1/schema/2025-09-15 on 2026-09-30.
It explicitly validates the OAS document **without Schema Object validation**.
The task suite additionally meta-validates the DTO schema definitions,
resolves local references offline, validates typed examples and checks operation
semantics. No claim of a separate installed OpenAPI validator package is made.
No JSON Schema or OpenAPI library is added; `jsonschema==4.26.0` is already locked.

The candidate manifest in the parent directory pins exact bytes of OpenAPI,
external schemas, policy, fixtures and review sources. Its acceptance remains
PENDING; do not substitute a newly edited schema behind an accepted OpenAPI
digest. Contract JSON/source artifacts use LF line endings.

All public references resolve locally. No tests download resources or contact
providers. Schema validation does not establish mathematical truth, PostgreSQL
locking or freedom from answer-equivalent prose; the task and downstream human
gates still apply.
