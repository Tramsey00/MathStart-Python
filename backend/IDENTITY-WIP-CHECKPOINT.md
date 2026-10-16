# Deferred V03 checkpoint; do not integrate as completed work

The user narrowed the active execution to I02/I03 and their required publication
interfaces. Identity/staff-write work is retained here only to prevent loss.

Base before checkpoint:`cd62406c6e0ff029c6e4445e8f015243731fd194`.
Files:backend/users/**,backend/tests/v03/**,backend/staff/{writes,http_writes}.py,
and V03 additions to backend/cli.py and backend/infrastructure/http/{app.py,
transport.py,requirements.txt,requirements.lock}.

Observed before the staff-write additions:10 identity/password tests passed on
synthetic PostgreSQL16.15 in34.771s. They covered five Django hash formats,
Unicode/old iterations, registration/replay/conflict/concurrency/lost cookies,
logout revocation, CSRF/Origin/Host/strict JSON and shared login rate budget.
Several subsequent session/key-ring refinements and all staff-write additions
have not received complete runtime verification or independent review. No V03
acceptance, complete bridge lifecycle/cutover, production readiness or safe
integration is claimed. No schema migration was added.

Dependencies added only in this checkpoint:argon2-cffi25.1.0,
argon2-cffi-bindings25.1.0,bcrypt4.3.0,cffi2.0.0,pycparser2.23. The common-password
list is synthetic validation data vendored from Django5.2.16 with its license.
Normal target modules do not import Django; the old-template/hash oracle uses a
separate legacy test environment. Runtime test data is under ignored var/ and a
reserved disposable identity DB on the task-owned PG container.

Follow-up after explicit scope resumes:review the implementation against P2
bridge lifecycle, lock ordering and staff contracts; add staff-write and expired/
revoked/foreign-owner/role/password/race regressions; correct any failures; then
run the full exact-SHA suites and independent review. Preserve this checkpoint
and do not cherry-pick it into the I02/I03 result by accident.
