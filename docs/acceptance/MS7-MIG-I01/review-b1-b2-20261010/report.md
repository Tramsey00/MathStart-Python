# PR50 B1/B2 review corrections — 2026-10-10

Status: scoped fixes locally verified; owner checkpoint and independent review pending.
No commit, push or PR update authorized for this iteration.

## Provenance and boundaries

- Task branch: ms7-mig-i01-foundation; reviewed/base HEAD:
  `79e0c19c234e36381662cbbf57e5b042727b1a61`. HEAD has not moved.
- Accepted integration input: `8d958aeeb17da46839722441425ccbb5889e2ab7`.
- Recorded full run: 2026-10-10T13:25:28.758Z to 2026-10-10T13:26:27.366Z (UTC).
- The tested working code was uncommitted: dirty=true,
  tested_implementation_sha=null, source_changed_during_run=false.
- Stable run source fingerprint: `54ce2e3a19d32df72ca71ce0d947fcc32f1740d64d81ec00cb0c5ceeb1cc29ea`.
  README/own plan/trace/new evidence were documented afterwards; no functional edit.
- R02 schemas/OpenAPI/generated files, historical contracts/approvals, lesson
  HTML/CSS/JS, root dependencies/workflows, primary checkout and all DBs untouched.
  F01–F04 and I03/I05 obligations unchanged; no I02/I04 implementation.

## B1 — FIXED: durable logout acknowledgement

Cause: schema validity allows a boolean completed, while R02 operational semantics
require completed:true. The generic success branch previously accepted false.
[Accepted auth/P2 contract](../../../../specs/migration/r02-v1/auth-v1.md),
P2 lifecycle table, Explicit logout (line214), remains unchanged.

The adapter now requires validated HTTP200 envelope plus strictly completed===true.
False returns INVALID_RESPONSE/status200/outcome unknown/retryable false without
automatic POST/GET, session acknowledgement, replay or raw/private detail exposure.
Other operation validators and CSRF bootstrap are unchanged. An explicit later
GET me does not rewrite the failed logout result. Full lost-response reconciliation,
private-client-state clearing and receipt lifecycle remain I04 responsibilities.

[Adapter](../../../../frontend/src/shared/api/client.ts),
[12 logout regressions](../../../../frontend/tests/logout-acknowledgement.test.ts):
true/false; missing/string/numeric/null completed; extra private field; bad envelope
version/JSON/status; lost response; single POST and unchanged unknown result.
RED before fix:2 FAIL/10 PASS. Final full run: all12 PASS.

## B2 — FIXED: immutable verification captures

Cause: the runner hard-coded checkpoint2/command-results.json and an old source SHA,
so a routine rerun replaced historical results and misrepresented current provenance.

Default output is NEW ignored frontend/.cache/verification-runs/run-<UTC>-<unique>/
command-results.json. Optional --output NEW.json is relative to frontend, must stay
inside this task repository, and rejects historical checkpoint1/checkpoint2/final,
Git metadata (case-insensitive on Windows), unsafe directory links and external
paths. Exclusive wx creation refuses an existing file before any verification
commands. Historical recorders are documented as capture-only, not rerun commands.

Each run records real Git HEAD/branch/tree, before/after dirty status and source
fingerprints, exact argv/cwd, versions, start/end/duration, exit codes and captured
outputs. Dirty/uncommitted code has tested_implementation_sha=null. Source or
historical changes during a run fail verification; no restoration hides mutation.

[Runner](../../../../frontend/scripts/verify-foundation.mjs),
[12 runner regressions](../../../../frontend/tests/verification-evidence.test.ts):
actual npm runner in isolated synthetic Git repositories, immutable historical JSON,
unique/default and explicit output, no overwrite/no repeated checks, clean and dirty
provenance, protected/invalid paths, source-mutation failure. These fixture-local Git
commits create test history only; the task branch is never committed or published.
RED on original runner:1 FAIL/10 deselected in targeted test; only synthetic historical
JSON was overwritten. Final full run: all12 PASS.

## Verification results

Tooling: Node24.21.0, npm11.19.0; direct locked versions in raw dependency-tree output.

| Check | Actual result |
| --- | --- |
| npm ci --no-fund | exit0;217 packages,218 audited |
| generate:api / pinned contracts | exit0;17 frozen+24 R02 pins,37 operations,16 validators |
| typecheck (includes check:contracts/typegen) | exit0 |
| native ESM validators / Unicode / approved pack | exit0 |
| npm test | exit0;112 PASS/0 FAIL,12 test files;24 new regressions |
| historical dispatcher | exit0;5 PASS/0 FAIL,source unchanged |
| production build + security guards | exit0;47 client modules,12 artifacts,anonymous index only |
| dependency tree / audit --audit-level=low | exit0;0 vulnerabilities |
| actual npm run verify:foundation | exit0;all10 constituent commands exit0 |
| git diff --check | exit0 |

Raw [runner capture](command-results.json), [full session including clean install](verification-session.json),
[meaningful RED runs](regression-red.json), [history proof](history-integrity.json).
Early regression-fixture setup had CommonJS/escaping errors, corrected before the
meaningful RED run; no application contract/test was weakened. Narrow first GREEN
was23 PASS; the final Windows-case negative case raises new tests to24.

All84 pre-existing checkpoint1/checkpoint2/final files match pre-run size/SHA256,
including checkpoint2/command-results.json. History aggregate before=after:
`96188177e8a439b5e136bf882e6368c895994d5c81adaaf30d3457420f71feb2`.
No old timestamp, screenshot, JSON or manifest was refreshed.
All12 rebuilt client artifacts match the original final build manifest byte-for-byte.
The API adapter is currently tree-shaken from empty route placeholders; direct tests
exercise B1. Artifact identity supports no UI change, not full browser/API parity.

Non-blocking warnings: existing esbuild postinstall allowScripts coverage warning
and React Router v8 future notices. No dependency/config/policy changes made.
No fresh browser/full-site/live Django parity, production gateway404, target API,
session/recovery/concurrency, PostgreSQL or full verify_repo claims for this run.
Existing evidence remains historical. Current baseline CI does not run frontend;
R03/Ruslan owns frontend CI wiring. No root workflow edits or GitHub mutation.

## Inventory and review gate

[All proposed commit paths](changed-files.txt), [new scope hashes](content-manifest.json).
Separate raw local patch: var/i01-b1-b2-20261010/scoped-review.patch.
Original captures and final manifests are immutable; this directory is a new record.
Owner should review B1 semantic guard/negative tests and B2 real-run immutability/
dirty provenance before authorizing a scoped commit/push to existing PR50.
No independent acceptance or task completion is claimed.
