# TRACE MS7-MIG-R02: Contracts and equivalence

- Date:2026-10-08 Europe/Moscow; Owner Руслан / Tramsey00
- Coding surface:Codex bootstrap engineering surface permitted by migration§9,
  not a fabricated Harness/productG1 run; no delegated agents
- Issue:[29](https://github.com/Tramsey00/MathStart-Python/issues/29)
- Input:c133f920fc14ab18a463e039f8e480e064ced81c; MIG_BASE_SHA60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7
- Specs:[canonical v1.1](../../specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md),
  [new contracts](../../specs/migration/r02-v1/README.md); ADR0006/0002/0003/0004/0005
- [Active plan](../exec-plans/active/MS7-MIG-R02.md); human review PENDING
- Final containing HEAD/PR/CI/tested checkout:external exact fields in draft PR;
  no approval/integration status invented in this containing commit

## Task and inputs

Only R02 card plus§§2–11 and§17: separately versioned platform/auth/content
contracts, actual routes/full mapping/parity/security/publication and historical
adapter index. Required AGENTS/PRODUCT/ARCHITECTURE/README/verification skill,
pipeline docs/ADRs, R01 handoff/inventory/manifests/evidence/acceptance/ownership,
original R02/R03/R02A/R03A/grades/I03 contracts, URLs/views/admin/models/migrations/
tests inspected. Root docs/source/frozen manifests/reference suites left unchanged.

## Initial state and isolation

Original C:/Projects/MathStart-Python main8c11eda with untracked recovery trace,
output/tmp and two R01 worktrees. No reset/clean/stash performed. Remote fetch
verified main60b341f, integrationc133f920 and no R02 branch. Live PR46 merge60b341f
and PR47 mergec133f920; both independent PR47 APPROVED on66e9fd8 confirmed from
live API. R01 ACCEPTED_INTEGRATION input recognized despite historical pending.
Managed worktree C:/Users/Tramsey/.codex/worktrees/ms7-mig-r02/MathStart-Python
created at exactc133f920 then branch ms7-mig-r02-contracts. User confirmed full
canonical SHA256 with missing f corrected in intake only, source file unchanged.

## Added files / result

specs/migration/r02-v1 contains platform/auth/content/staff/adapters, closed
delivery schemas and separate OAS, full code/physical schema+fresh sequences,
actual/planned route map, domain/task DAG, parity matrix with F01–F04 and
synthetic examples. docs/acceptance/MS7-MIG-R02 has intake/full input-tree digests,
literal old-to-new original_result copies, independent baseline probes,
verification/handoff and reproduction tools. New standalone contract test20.
No existing input file modified or deleted. No FastAPI/Alembic/React/runtime/
dependency/Harness changes, no UI fix or working DB access.

## Commands and verification

Exact argv/results/versions/log digests in
[verification.json](../acceptance/MS7-MIG-R02/verification.json).
New venv Python3.12.10, requirements.lock installed --no-deps, pip check PASS.
Separate container ms7-mig-r02-pg-20261008 on55439, PGserver160015;
DB ms6_v01_smoke_ms7_mig_r02_20261008, test DB test_ms7_mig_r02_20261008;
runtime<worktree>/var/r02-runtime. Credentials supplied only to disposable env.
Working5432/R01container55438 unchanged. fresh_install_smoke --disposable PASS;
verify_repo PASS8/8,Django107/R0318/Harness73; R02A30/R03A41/I027 PASS.
New suite20 PASS: official OAS+closed JSON Schema/offline refs, all input blobs/
original pins, mappings/DAG+negative cycle, independent frozen exchanges+
errors/invalid/business shapes, raw parser65536/65537/UTF8/duplicates/NaN,
literal PBKDF2 vector and independent legacy cursor HMAC, private DTO rejection,
F01–F04 exact preservation and original_result linking.

Baseline route probes and schema sequence query run only in disposable PG.
Probes assert zero domain INSERT/UPDATE/DELETE; schema REPEATABLE READ READ ONLY
endsROLLBACK. Not target runtime/upgrade or browser evidence. All16 identity
sequences reflected; R01's empty sequences array limitation explicitly retained.
New suite isn't wired to existing integration CI; unchanged baseline workflow
verification at final head is recorded separately in PR, no R03 scope expansion.

## Observable failures and corrections

| Failure | Classification / resolution |
| --- | --- |
| Initial sandbox git fetch denied and gh absent | Environment/tool availability; authorized git escalation and GitHub connector used. |
| Prompt SHA25663 characters vs input64 | Input typo; explicit user confirmation of unchanged canonical file/R01 digest before dependent contract work. |
| One-off git show failed on Windows long path | Task assembly tooling; replaced per-file path command with ls-tree -z and cat-file batch by object IDs. No source truncation. |
| First new suite14:3 errors+1 failure | Task-owned refs/fixture dependency shape/incomplete recorder metadata/missing assembly manifest; corrected actual OAS schema names, migration edges and all20-table mapping including django_migrations. |
| Extended new suite pending result=None/settings initialization | Task-owned test harness errors corrected; no domain validation/pins weakened. Final20PASS. |
| First route probe lacked DJANGO_RUNTIME_ROOT | Invocation environment; missing collected static manifest, rerun with already-built isolated runtime. No working fallback/setup. |
| Baseline probes contradicted drafted slash/body assumptions | Task contract correction: slashless301, ignored GET grades body, public unsafe200 afterCSRF recorded honestly. |
| pip update-notice TLS probe failed after locked installation | External optional pip-version lookup only; exact lock install exit0/pip check0, no dependency skipped. |

## Acceptance and remaining gates

Requested proposed deliverables and applicable local checks prepared. Future
runtime assertions/PG upgrade/hash algorithms/secure scope bridge/SSG recovery/
React browser visual parity NOT_RUN; assigned V/I tasks verify at exact heads.
F01–F04 not fixed/closed,13baybars byI03/I05; all widths ordinary-scale criterion
retained. Historical approvals/digests untouched, no retrospective acceptance.
[Handoff](../acceptance/MS7-MIG-R02/handoff.md) lists concrete review decisions:
new namespace/lock/bridge/journal and complete baseline staff permissions.
Both independent R02 exact-head approvals and accepted integration intake are
PENDING. Issue29 open; plan remains active. R02 status INCOMPLETE for human
acceptance; agent delivery ready for review. No next task started or PR merge.
Initial published HEAD/CI receipt: [publication](../acceptance/MS7-MIG-R02/publication.json).
Final review found missing disable-password and own-password-change behavior;
addendum schemas/OAS and a Django-form comparison test now preserve both,
including explicit disable confirmation and self-session rotation.
