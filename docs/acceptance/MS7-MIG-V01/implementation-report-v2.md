# MS7-MIG-V01 Implementation Report — continuation v2

**Local verification PASS; independent DDL/Task Approval and CI pending.**
Continuation from the preserved implementation, without commit/push/PR.
The [initial report](implementation-report.md) and its failed verification remain
historical evidence; they are not rewritten as passing results.

1. **Exact branch / starting SHA / final local HEAD.**
   `ms7-mig-v01-schema`; starting and final HEAD both
   `8d958aeeb17da46839722441425ccbb5889e2ab7`, workspace
   `C:/Projects/MathStart-Python-V01`. Distinct MIG_BASE_SHA remains
   `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
2. **Changed files and preserved work.** All 33 prior uncommitted files were
   present; all 31 prior manifest hashes matched before continuation. Their
   original bytes are retained in ignored `var/ms7-mig-v01-resume-input`.
   Existing tracked files have no diff. Changes stay in `backend/`, V01 plan,
   trace and dedicated acceptance records. See [delta](continuation-delta-v2.json)
   and [current manifest](file-manifest-v2.json).
3. **SQLAlchemy models / B01.** The 20 baseline models and seven additive
   protocol tables are retained. Only the PKs `auth_group_permissions.id`,
   `auth_user_groups.id`, `auth_user_user_permissions.id` use PostgreSQL BIGINT;
   adjacent FK columns remain INTEGER. Fixtures preserve join IDs above int4.
   [Compatibility addendum v1.0.0](compatibility-addendum-v1.0.0.md) records source
   SHA and the [approval evidence](b01-owner-approval-v1.json): the user's direct
   written report of Ruslan's decision, not an independently retrieved signature.
4. **Alembic migrations / ordering.** One head: `v01_0001` baseline ->
   `v01_0002` additive protocol persistence. Runtime has no Django dependency.
   Direct uninspected Alembic operations and destructive downgrade are refused.
   The separate additive catalog is proposed DDL for independent review.
5. **Fresh install.** Fresh twice in separate marked PostgreSQL databases
   passes exact baseline/additive catalog comparison. An additional clean
   runtime-only venv executes both fresh/check pairs with Django absent.
6. **Upgrade A/B/C and CHECK investigation.** All three profiles pass in new
   disposable fixtures. A uses content0001 plus full baseline auth/admin/
   contenttypes/session heads; no users/Grade time. Other legacy variants are
   refused. PostgreSQL deparsed CHECK text reparses with different cast syntax;
   the original IN expression reproduces the frozen definition exactly.
   [Investigation](check-canonicalization-v1.md): 42 acceptance combinations,
   zero semantic mismatches. Comparison remains strict; CHECK(true) is rejected
   before stamp. No real schema differences are ignored.
7. **IDs/FKs/data preservation.** A/B/C compare hashes of baseline row
   projections, auth joins/password hashes, content/storage fields, UUIDs,
   completed/pending receipts and exact `django_migrations` rows. Declared
   additive Grade/profile backfills are checked separately. Deployed data is
   not part of this synthetic evidence.
8. **Constraints/defaults/timestamps/sequences.** UNIQUE/CHECK/FK/nullability,
   JSON null, deferred NO ACTION, PROTECT and collector CASCADE/SET_NULL pass.
   Python defaults remain separate from SQL defaults. Save/bulk timestamps,
   UTC/microseconds, sequence ownership/type/next-value/already-ahead and
   empty/uncalled semantics pass. A real second connection times out on a held
   row lock; receipt/profile/publication ordering follows existing R02 keys.
9. **Grade epoch / users backfill.** A assigns only new NULL Grade timestamps
   `2026-10-04T00:00:00Z`; B/C keep existing instants and state. Missing profiles
   are additive; backfill twice leaves existing row hashes unchanged.
10. **Failure/rollback.** Failures after DDL, backfill and protocol DDL/stamp
    restore schema/data/history. Unknown heads and table/column/check/index/FK/
    identity/sequence drift are refused; unexpected schemas/views/orphan
    sequences are detected. setval is nontransactional, runs last after immediate
    FK validation and only advances. Commit loss after setval is NOT VERIFIED.
11. **PostgreSQL/SQLite behavior.** Explicit psycopg PostgreSQL config and
    bounded timeouts; failed connection never selects SQLite. SQLite is an
    explicit unit compatibility mode and does not establish upgrade/locking
    acceptance. Safe CLI errors omit DB parameters/credentials.
12. **Frozen-contract preservation.** No tracked changes to frozen R02/R03/
    R02A/R03A, historical approvals, Django migrations, frontend, root locks,
    README, verification or CI. `baseline-v1.json` stays byte-identical to the
    frozen checkout mapping. Git contract digest and checkout-byte audits are
    distinguished in [verification v2](verification-v2.json).
13. **Actually executed tests.** Final target suite **22/22 PASS, zero skips**
    (27.285s; 11 unit + 11 PostgreSQL methods with subcases). Earlier repair and
    expanded runs 18/18 and 22/22 passed. Clean runtime fresh twice/A/B/C/check
    **10/10 CLI calls PASS**, Django absent. Unchanged verify_repo **8/8 PASS**
    on another disposable migrated/bootstrapped PostgreSQL runtime: Django
    discovery 129 tests, 118 executed/11 explicit target PG skips; the separate
    target suite covers all 22 without skips. R03 18, Harness 73, R02 migration
    63 and R02A/R03A 71 pass. Both venvs pass pip check. Python3.12.10,
    SQLAlchemy2.0.46, Alembic1.18.4, psycopg3.3.6, Django5.2.16, PostgreSQL16.15.
14. **NOT RUN / NOT VERIFIED.** Linux/CI execution, independent DDL/Task Approval,
    actual deployed legacy profile variants, post-setval commit-loss
    reconciliation, full collector/service races and V03/V04 lifecycle are not
    claimed. No distinct historical MS6-V02 source was found; its reconciliation
    stays open. Target protocol constraints are proposed, not accepted by tests.
15. **Open gates / handoff.** B01 and CHECK local failures are resolved. Root CI
    currently lacks backend dependencies required by discovered backend tests.
    [R03 handoff](r03-ci-handoff-v2.md) includes an exact proposed patch; not
    applied because those files belong to Ruslan. Its whitespace-tolerant
    applicability check passes against this CRLF checkout; CI is not run.
    Disposable container identity/label checked, zero test databases remain,
    and only the owned container was stopped. No production/shared DB access.
16. **Readiness for independent review.** Ready for Ruslan to review the scoped
    addendum, SQLAlchemy/Alembic DDL, strict catalog checks, local evidence and
    proposed CI handoff. Active plan remains active until human acceptance.
    No broader Task Approval, downstream start, commit/push/PR or cutover is
    inferred from the reported B01 approval.

Reproduce target tests using the reserved disposable environment described in
the initial report, the backend runtime/test locks and the command recorded in
verification-v2.json. Local raw logs are ignored under `var/`; their SHA256
digests are recorded in verification-v2.json. The receipt/projection links are
in [old-to-new evidence v2](old-to-new-evidence-v2.json); original results remain
unchanged. The standalone catalog capture refuses an existing snapshot and
generates proposed DDL without depending on that not-yet-created reference;
normal fresh installation always validates against the committed reference.
