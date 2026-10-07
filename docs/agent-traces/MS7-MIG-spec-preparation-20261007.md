# TRACE MS7-MIG-SPEC: Migration specification preparation

- **Date:** 2026-10-07.
- **Task ID:** MS7-MIG-SPEC (preparation record, not one of the 18 implementation tasks).
- **Owner:** User / Руслан; authoring agent Codex desktop.
- **Related issue / PR / commit:** None created or committed.
- **Related spec:** `output/specifications/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md` / PDF; initial v1.0 preserved.
- **Related exec plan:** `docs/exec-plans/completed/MS7-MIG-spec-preparation-20261007.md`.
- **Related ADR:** ADR-0001..0005 as inputs; replacement platform ADR remains proposed.
- **Human review status:** User accepted with three corrections, applied in v1.1. This is not evidence of completed migration gates.

## 1. Task

Create detailed migration ТЗ in Russian for 07–13 October 2026, three owners, current-version React/FastAPI port without redesign, explicit branches and adaptation of completed main-spec tasks. Inspect GitHub and PostgreSQL; preserve local work.

## 2. Inputs used

User pasted request/discussion; AGENTS/PRODUCT/ARCHITECTURE/README; ADRs, API/exercise/progress specs, UX/Harness/current plans/traces; Content/Users code, tests and migrations; verification skill. Original main spec: `C:/Users/Tramsey/Desktop/MathStart_Technical_Specification_v7.1_SECTION20_PARALLEL_DEADLINES_2026-10-01.pdf`, 114 pages, SHA256 `e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd`. PDF and document authoring skills were consulted.

## 3. Initial repository state

Local `fix/topics-catalog`, HEAD `a378ab2f01bd76b514833bf692cb4c7425e90ace`; 235 modified tracked files, eight untracked entries, diff 7206 additions / 10068 deletions. Existing output/tmp entries include generated artifacts. No checkout/reset/clean occurred. Live main SHA `4df7403208312d73adaa34f00f10b025db686fe4`; open PR count zero. Main CI run 37470970648 SUCCESS on that SHA.

PostgreSQL 16.15: local Content has only `0001_initial` applied; users tables and Grade.created_at absent. 281 ContentPage / 279 published / 282 redirects; 263 published topic pages. These are read-only audit facts, not migration success.

## 4. Files changed

Added generated PDF, editable Markdown, structured 18-task JSON and sanitized GitHub snapshot under `output/specifications/`. Added this trace and preparation plan. Added generation/render QA files under `tmp/pdfs/ms7-mig/`. No pre-existing tracked code/content/specification was edited; no files deleted.

## 5. Commands / tools executed

Repository rg/Git/read operations; GitHub connector reads for main, Issues, PRs, review submissions, file contents and Actions; primary official technical documentation reads. PostgreSQL via project Python/psycopg: read-only connection, `BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY`, `SHOW transaction_read_only`, schema/aggregate SELECTs, `ROLLBACK`.

Artifact generation: bundled Python `tmp/pdfs/ms7-mig/build_spec.py`; Poppler `pdftoppm -r 95 -png`; pypdf/pdfplumber/Pillow metadata, text geometry, contact-sheet/render review. Project interpreter Python 3.12.10; artifact interpreter Python 3.12.14; ReportLab 4.4.9; pypdf 6.10.0; Pillow 12.3.0.

## 6. Implementation summary

Standalone proposed migration addendum: 20 sections, six tasks each for Руслан/Владимир/Илья, snapshot/integration/18 feature branches, daily gates, schema/auth/content/staff/CLI/security/CI/rollback requirements, preserved design and historical acceptance. Main-spec v7.2 production is a future R05 deliverable, not silently applied now. Future product domains remain planned.

## 7. Observable failures / incidents

Initial sandbox PostgreSQL connection failed; approved read-only escalation succeeded. Public web GitHub snapshot was stale; live authenticated API was used. LibreOffice and fitz were unavailable; no DOCX was promised and ReportLab/Poppler/Pillow produced the PDF. No data mutation or implementation failure occurred.

## 8. Root cause summary

Environment/tooling limitations above do not indicate target-runtime verification. Stale local schema and GitHub document status mismatches pre-exist this preparation.

## 9. Corrections made

Added live approval/status reconciliation, explicit local-data upgrade profiles, independent release acceptance, non-default-branch Issue closure rules, all current staff operations and publisher recovery. Added PDF TOC/bookmarks and clarified full migration IDs. Fixed R01 inputs so the baseline it creates is not presented as an existing prerequisite.

## 10. Verification results

| Check | Result |
| --- | --- |
| 18 IDs / unique branches / dependency existence / acyclic graph / deadline ordering | PASS, authoring script assertions |
| PDF Cyrillic extraction, text within page margins, TOC/bookmarks and page rendering | PASS; 59 pages rendered and visually reviewed; zero margin violations/replacement characters; final changed pages 14,15,18,19 reviewed again |
| PostgreSQL read-only inventory | PASS; transaction explicitly read-only, rolled back |
| Live main CI on audited SHA | SUCCESS, https://github.com/Tramsey00/MathStart-Python/actions/runs/37470970648; external baseline evidence |
| Local `python scripts/verify_repo.py`, Django/content/Harness tests | NOT RUN in document preparation; no runtime change or local PASS claimed |
| Fresh/upgrade migrations, bootstrap, restore, target React/FastAPI E2E | NOT RUN; future migration acceptance requirements |
| Live Product LLM | N/A; no LLM behavior change |

## 11. Final diff summary

Only new planning/delivery/QA artifacts. Pre-existing dirty tracked code remains unchanged by this task. No GitHub branch, Issue, PR, review or comment was created.

Final PDF SHA256: `e066ff5940912a07d9c38551c37d68bd26a1a590576b0f950756b344b0acaac7`. Machine QA: `tmp/pdfs/ms7-mig/final_qa.json`.

## 12. Acceptance criteria result

| Criterion | Result | Evidence |
| --- | --- | --- |
| Full current-version scope without redesign | Draft delivered | Sections 1,4–9,12,18 |
| Detailed cards for three people and exact branches | PASS drafting | Sections 10–16; 18 validated cards |
| 07–13.10 calendar/dependencies/independent reviews | PASS drafting | Sections 10–11 and cards |
| Completed-task adaptation and main-spec update plan | PASS drafting | Section 17 and R05 |
| Live GitHub / PostgreSQL distinguished from claims | PASS audit | Sections 2,20; sanitized snapshot |
| Human architectural acceptance | Pending | MIG-G0, no acceptance fabricated |

## 13. Remaining risks / follow-ups

Human baseline/ADR/admin scope/auth cutover decisions, approval reconciliation and verified target implementation belong to MIG-G0 and subsequent tasks. The seven-day forecast is conditional; account limits do not guarantee throughput. Artifact readiness is not runtime completion.

## 14. Harness improvement

No Harness code change. Proposed migration check-registry update is MS7-MIG-R03, with historical check identities retained.

## 15. Human review

Initial v1.0 review was pending. User subsequently wrote: remove branch prefix, make §17 explicit in tasks, add parallel queues table; otherwise accepted. These corrections were applied to v1.1. No separate signatures for the other participants or implementation acceptance dates are asserted.

## 16. Final status

`COMPLETE` for specification preparation and requested corrections. MIG-G0 checks and migration implementation have not been completed by this authoring task.

## 17. Revision v1.1

Removed branch prefix throughout the deliverables. Added §11.1 with six numbered rows, three owner columns, exact task IDs/deadlines and parallel-queue semantics. All 18 cards now include explicit historical-task adaptation fields, Detailed Scope steps, deliverables, acceptance and evidence-link checks for §17; R05 owns full main-spec/index update, other owners perform their actual platform adaptations. Deadlines, dependencies and other requirements are unchanged.

Assertions: no branch prefix remains in Markdown; 18 historical adaptation records and unique branches; acyclic/deadline-consistent dependency graph. PDF rendered and reviewed (60 pages); no text margin violations or replacement characters. Queue header contrast and heading/table pagination corrected during QA. Final PDF SHA256 `a0c72fda223f86622d01665eaa7ec9d854c7b0b3014de38174f9ad4c582eb66e`. No application/GitHub/DB mutation.
