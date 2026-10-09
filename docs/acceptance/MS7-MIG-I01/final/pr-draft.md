# Proposed PR

Title: MS7-MIG-I01: React foundation без изменения дизайна
Base: ms7-mig-react-fastapi
Head: ms7-mig-i01-foundation
Refs #40

## Body

React foundation переносит текущий shell и утверждённые UI states в отдельный frontend
на React/TypeScript/Vite/React Router framework mode, сохраняя CSS и дизайн Django baseline.
Добавлены route/layout boundaries,debug-only gallery,строгий четырёхрежимный dispatcher
и typed API/CSRF/error/cancellation/stale-read foundation по принятым R02 contracts.
Full public SSG,LessonHost/widgets,account/staff и backend остаются в своих downstream tasks.

Accepted integration input:8d958aeeb17da46839722441425ccbb5889e2ab7.
Canonical appearance:8c11edadc8debc81432d1db1145feac504f09061.
MIG_BASE provenance:60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7.
Implementation commit: c54a98b91195458b22a14aa4a6cbf14c7fe57e28.
Final PR candidate HEAD / CI / tested merge-ref: заполнить после docs-only publication-binding commit и публикации.

Validation:clean npm ci,generated types+41pins,typecheck,88 frontend tests,5 unchanged historical JS
tests,production build/graph/export guards,npm audit0 vulnerabilities.
verify_repo exit0,8/8 SQLite compatibility checks;Django99PASS/8SKIP,R0318,Harness73.
Separate unchanged R02A30/R03A41/UI7/migrationR0263 model/contract tests PASS.
Three live fresh task-local Django SQLite gallery comparison pairs byte-identical
at360×800/768×1024/1440×1000;keyboard/focus/CSS isolation/overflow pass.
[Final evidence](report.md),[requirements matrix](requirements-matrix.md),
[old-to-new mapping](old-to-new-evidence.json),[screenshots](screenshot-index.md),
[file/checksum manifest](content-manifest.json).

Limits:PostgreSQL-only checks unavailable locally (Docker daemon unavailable);
dedicated hover requires manual review;no whole-site/R01PG/target runtime parity;
localpreview404 does not prove productiongateway behavior.
Root CI unchanged baseline-only;R03/root-CI owner must wire frontend checks.
Current implementation has no CI result before actual PR publication.
WorkingDB/R01baseline/main untouched. No schema/API semantics change.
F01–F04 preserved,fix≤I03,verifyI05;F04 ordinary-scale readable360×800 without clipping/overlap,
math/controls preserved and768/1440 regression;no new numeric threshold.
Rollback:revert foundation commit(s),preserve existing source/styles/contracts/runtime.

## Independent review plan (request after publication; no messages sent)

- Руслан / Tramsey00:exact implementation SHA + CI/tested merge-ref,scope/layout/CSS,
  screenshots360/768/1440,keyboard/manualhover,§17 history/provenance,downstreamCI handoff.
- Владимир / VladimirFrolov777:canonical generation/pins/runtime validation,CSRF/session/error
  handling,unknownmutation/cancellation/stale reads,productiondebug/private isolation,
  no backend/DB changes;confirm required PostgreSQL evidence on isolated CI/infrastructure.
- Neither review accepts full I02/I03/I04 or target backend;no self-approval.
- CI/approvals/merge/Issue closure/global MIG gate remain separate facts.
  Use Refs #40,not Closes #40;no Issue closure at integration-only stage.
