# TRACE R01: Harness v1 audit

- **Date:** 2026-09-24
- **Task ID:** R01
- **Owner:** Ruslan
- **Coding agent / surface:** Codex desktop
- **Related issue:** [R01 — Baseline repo knowledge + Harness v1](https://github.com/Tramsey00/MathStart-Python/issues/1)
- **Related spec:** `PRODUCT.md`, `ARCHITECTURE.md`
- **Related exec plan:** `docs/exec-plans/completed/R01-harness-v1.md`
- **Related ADR:** `docs/adr/ADR-0001-preserve-django.md`
- **PR / commit:** No PR or commit created by this audit
- **Human review status:** Accepted

## 1. Task

Audit Harness v1 against the actual Django repository and active R01 plan.
Check consistency, artifacts, paths, commands, templates, tooling claims, and
new-session context recovery. Make minimal supported documentation corrections,
run `python scripts/verify_repo.py`, and record observable evidence.
Do not change product behavior, content, dependencies, schema, or database data.
Do not commit, push, or merge.

Review round 2 addressed Ruslan's explicit R01 documentation corrections.
User-facing communication is in Russian; repository documentation remains
in English. Ruslan subsequently supplied the exact Progress Algorithm v1
baseline values, which are transcribed unchanged in `specs/progress/BASELINE-v1.md`.

## 2. Inputs used

- `AGENTS.md`, `PRODUCT.md`, `ARCHITECTURE.md`, and ADR-0001.
- Active R01 plan and every repository ADR/spec/exec-plan/trace/issue/PR template.
- `skills/verification/SKILL.md` and `scripts/verify_repo.py`.
- `README.md`, `docs/architecture.md`, and relevant content-editing/theme documentation.
- `requirements.txt`, `.gitignore`, `.venv/pyvenv.cfg`, and `config/settings.py`.
- Content models, views, URLs, admin restrictions, publication/bootstrap services,
  lesson component renderer, exercise template, and verification management commands.
- `content/tests.py`, `content/test_curriculum.py`, `content/test_bootstrap.py`,
  and the migration file inventory.
- The user's task scope and required final report, summarized in section 1.
- Ruslan's human review: Changes requested, with the eight correction groups
  recorded in section 15.

## 3. Initial repository state

```text
Branch: R01-harness-v1
Start commit: e532e4dc965a6a7acf13d4063cb9c6e48f508b43
Local baseline tag: v3.1-pre-harness-baseline
Annotated tag object: d36a78cadd8238874910f44f0fbe5fed5d6c2cff
Tag target commit: e532e4dc965a6a7acf13d4063cb9c6e48f508b43
```

The working tree was not clean: `scripts/verify_repo.py` was already staged as
an addition. Root Harness documents, `.github/`, `docs/adr/`,
`docs/agent-traces/`, `docs/exec-plans/`, `skills/`, and `specs/` were already
untracked. These files were supplied before this audit; this agent did not
author their entire contents. Existing tracked product files had no diff.

This paragraph describes the first audit's starting state only. At the start
of review round 2, `git status --short` showed all 15 Harness files as ` A`
(working-tree additions with intent-to-add entries), and
`git diff --cached --name-only` was empty. `git ls-files --stage` showed empty
blob entries for AGENTS.md and the verification script. The agent did not
perform staging operations in either round; these observed states are not
descriptions of one simultaneous index state.

The completed-plan directory existed but was empty, so Git would not preserve
it in a fresh checkout. The first R01 trace did not exist.

The configured application uses SQLite, Django templates, the `content` app,
Django ORM/migrations, and five pinned dependencies including Django 5.2.16.
The existing virtual environment uses Python 3.10.11, below the accepted 3.12+
target. No Ruff/mypy/pytest configuration, GitHub Actions workflow, Docker path,
PostgreSQL driver, or intelligent-domain implementation was present.
The interpreter mismatch is a pre-existing follow-up, not an R01-introduced
blocker; review round 2 does not change the environment.

## 4. Files changed

### Added by this audit

- `docs/agent-traces/R01-harness-v1.md` — this trace.
- `docs/exec-plans/completed/README.md` — preserve the directory and state the
  human-acceptance requirement for moving plans.
- `specs/progress/BASELINE-v1.md` — review-round addition recording the exact
  Progress Algorithm v1 baseline supplied by Ruslan.

### Modified from supplied Harness files

- `AGENTS.md` — review round 2 reduces the guide to a short repository map.
- `PRODUCT.md` — review round 2 retracts the initial future-algorithm claim,
  links the existing-baseline record, and states R03's refinement/test role.
- `ARCHITECTURE.md` — review round 2 restores Content-owned topic mappings,
  baseline dependencies and NFRs, defers Topic persistence to R02/V02, and
  removes the premature target-deployment selection of WhiteNoise.
- `docs/adr/ADR-0001-preserve-django.md` — fully qualify the spec-template path.
- `docs/adr/ADR-TEMPLATE.md` — link the real verification matrix.
- `docs/exec-plans/active/EXEC-PLAN-TEMPLATE.md` — current checks and future-tool limits.
- `docs/exec-plans/completed/R01-harness-v1.md` — completed R01 plan with
  accepted human gate and completion summary.
- `docs/agent-traces/TRACE-TEMPLATE.md` — actual checks and unconfigured-tool reporting.
- `specs/SPEC-TEMPLATE.md` — current checks and future-tool limits.
- `.github/PULL_REQUEST_TEMPLATE.md` — explicit pending human-review option.
- `skills/verification/SKILL.md` — runtime prerequisites and verification limits.

### Deleted

None. `scripts/verify_repo.py` and the issue template were inspected and left
unchanged. Ignored local snapshots/logs and normal check reports were written
under `var/reports/`; they are not required repository artifacts.

## 5. Commands / tools executed

Important commands, including unsuccessful attempts:

```powershell
git status --short
git status --short --untracked-files=all
git branch --show-current
git rev-parse HEAD
git tag --list v3.1-pre-harness-baseline
git rev-parse v3.1-pre-harness-baseline
git cat-file -t v3.1-pre-harness-baseline
git rev-parse 'v3.1-pre-harness-baseline^{commit}'
git ls-files --stage -- AGENTS.md scripts/verify_repo.py
python scripts/verify_repo.py
.\.venv\Scripts\python.exe -c 'import sys, django; print(sys.version); print(sys.executable); print(django.get_version())'
.\.venv\Scripts\python.exe scripts/verify_repo.py
python --version
python scripts/verify_repo.py
git diff --check
git diff --cached --check
git diff --name-only
git diff --cached --name-only
Get-FileHash db.sqlite3 -Algorithm SHA256
```

Used `rg`, `Get-Content`, `Get-ChildItem`, and `Test-Path` to inspect repository
files and classify path references. Used local pre-edit snapshots to compare
untracked Harness files; ordinary `git diff` does not show their modifications.
Read available workspace-runtime metadata during interpreter diagnosis; no
replacement runtime or dependency installation was performed.

The qualified verification command ran outside the sandbox after the existing
virtual environment could not launch inside it. For the final exact entry-point
run, prepended `.venv/Scripts` to process PATH and set process-only
`PYTHONIOENCODING=utf-8`. Output is in ignored `var/reports/r01-verification.log`.
No repository settings or environment files were edited.

## 6. Implementation summary

| Audit area | Finding and disposition |
| --- | --- |
| Root document consistency | Initial audit incorrectly treated the existing progress algorithm as unspecified future work. Review round 2 retracts that claim; exact v3.1 numeric transcription awaits source text. |
| ADR-0001 alignment | Django, ORM, migrations, SQLite transition, PostgreSQL target, templates, and progressive JS agree. No replacement architecture introduced. |
| Dependency rules | Initial audit incorrectly inverted Content -> Knowledge. Human review confirms Content owns topic-to-skill mappings. Review round 2 restores that direction and Analyzer -> Progress service use, retaining Progress-only state mutation. |
| Repository paths | Required current paths inspected; spec-template basename qualified. Target app/seed/API examples and template placeholders are not missing R01 artifacts. |
| R01 artifacts | Supplied required files present; added first trace and a Git-preserved completed-plan directory. |
| Real commands | All six script commands map to existing Django built-ins or content management commands; `--all` is implemented for lesson verification. |
| Stale stack assumptions | FastAPI/SQLAlchemy/Alembic/Next.js references are rejected alternatives, historical context, or prohibitions, not authoritative requirements to adopt them. |
| Existing code compatibility | Legacy self-check solutions are embedded in HTML; documented this current state alongside target Assessment secrecy rules. No lesson conversion or weakening of the target contract. |
| GitHub templates | Issue template covers ID/owner/goal/scope/acceptance/spec/ADR/tests/labels. PR template covers all plan-required sections; added pending-review state. |
| Verification truthfulness | Spec/plan templates incorrectly listed unconfigured tools as baseline commands; replaced with real Django checks. Trace template now distinguishes NOT CONFIGURED from PASS/N/A. |
| Context recovery | Entry documents now point to setup, the real verification workflow, current code, target boundaries, plan, and trace. Enough repository context exists to execute this R01 audit without old chats. |

No new ADR was created. Review corrections restore the v3.1 baseline specified
by Ruslan; the earlier audit's ownership inversion was not an accepted decision.
R02/V02 will fix Topic persistence/reference contracts without duplicate sources
of truth. R03 will formalize and test the existing Progress Algorithm v1.

## 7. Observable failures / incidents

| Failure | Classification / detection | Impact |
| --- | --- | --- |
| `python` not found on initial shell PATH | Environment; command exit 1 | First requested verification attempt did not start. |
| Virtual-environment interpreter could not launch inside sandbox | Environment/execution restriction; diagnostic command exit 1 | Retried verification outside sandbox successfully. |
| Python 3.10.11 versus accepted 3.12+ target | Pre-existing environment mismatch; pyvenv.cfg and final `python --version` | Passing run does not establish target-version compatibility. |
| Initial broad reads truncated output; two guessed search paths did not exist | Audit command errors | Re-read required sections and used discovered `content/test*.py` and renderer/template paths. |
| Initial multi-file patch reported a context failure after partial edits | Harness editing incident | Inspected actual files, removed duplicate AGENTS additions using the pre-edit snapshot, and applied remaining scoped corrections. |

No Django/content check failed in either complete verification run.

Human review identified documentation defects: an overlong AGENTS.md; missing
baseline algorithm values mislabeled as future design; reversed mapping
ownership; premature Topic persistence constraints; omitted numeric NFRs and
operational requirements; premature WhiteNoise selection; inaccurate annotated-
tag labeling; and inconsistent descriptions of staging and follow-up status.
These are documentation findings, not failures of the Django checks.

## 8. Root cause summary

The shell did not expose Python on PATH, and sandboxed execution could not
launch the existing virtual environment's base interpreter. The same virtual
environment ran successfully outside the sandbox. Its older Python version
was pre-existing and was not upgraded in this documentation-only task.

Some templates described the future verification matrix as current tooling.
The initial audit resolved a documentation inconsistency in the wrong direction
instead of preserving baseline Content ownership, and treated unavailable
algorithm source text as evidence that the algorithm was not specified.
Human review corrected both assumptions. The partial patch incident was
corrected after inspecting the resulting files; duplicate text was not retained.

## 9. Corrections made

### First audit (historical)

- Made verification templates use Django checks/tests and explicitly defer
  unconfigured tools. Linked the verification skill as the matrix source.
- Documented setup, database/media prerequisites, ignored report outputs,
  interpreter recording, and the lack of automated Harness path validation.
- Distinguished the existing content runtime from accepted future technology,
  server-side exercise contracts. The initial progress-spec interpretation
  was rejected and superseded by the review-round correction below.
- Changed the architecture diagram in the first audit; the rejected ownership
  inversion is restored in review round 2 below.
- Preserved completed-plan storage in Git, qualified the template path, and
  made pending PR review representable.
- Updated observed plan checkboxes while retaining Active status and Pending
  human gate. Recorded remote issue/tag verification limits.

### Review round 2 corrections

- Reduced AGENTS.md from 631 to 107 lines, retaining the required map,
  invariants, workflow, gates, migration rule, verification, and Done criteria.
- Restored Content ownership of `TopicSkill` and `Content -> Knowledge` in
  the diagram, ownership table, domain descriptions, and dependency rules.
  The illustrative seed location follows Content ownership. Restored
  Analyzer -> Progress service dependency without direct state mutation.
- Documented current `ContentPage` use without permanently forbidding a Topic
  model; final persistence/reference decisions belong to R02/V02 spec/ADR.
- Restored normal API p95 < 500 ms and AI p95 < 15 s in the demo environment,
  required AI timeout/retry, structured logs with request/trace id, and AI
  endpoint rate limiting before public deployment. No achieved NFR claim.
- Replaced the target deployment diagram's WhiteNoise selection with neutral
  static asset delivery; left existing runtime dependencies unchanged.
- Corrected annotated-tag object versus target commit, separated per-round
  index observations, and retained the Python-version gap as a pre-existing
  follow-up rather than an R01-introduced blocker.
- Updated plan/review status and stale references after shortening AGENTS.md.
- Added the Progress Algorithm v1 record and corrected PRODUCT.md's R03 role.
  Ruslan supplied exact weights, formula, coefficients, status thresholds, and
  related rules after review. They were transcribed unchanged; no values or
  thresholds were invented or changed. This review finding is resolved.

## 10. Verification results

The first audit's two complete entry-point runs exited 0 with all six groups
passing. The following table records that first audit's final run:

| Check | Result / evidence |
| --- | --- |
| `python manage.py check` | PASS; no issues, 0 silenced |
| `python manage.py makemigrations --check --dry-run` | PASS; no changes detected |
| `python manage.py check_lesson_sources --all` | PASS; 263 lessons match the database |
| `python manage.py check_content_quality` | PASS; 281 pages, 840 SVGs, 0 issues |
| `python manage.py check_site_integrity` | PASS; 281 pages, 263 topics, 29 media assets, 1,685 references; all reported problem counts 0 |
| `python manage.py test` | PASS; 15 tests, 38.953 seconds; separate test database created and destroyed |
| `python scripts/verify_repo.py` | PASS; 6 of 6 checks, exit 0, Python 3.10.11 |
| Local SQLite SHA-256 comparison | PASS; unchanged from the audit snapshot, including across the final full run |
| First-audit product diff / staged state | PASS at that time; no tracked product changes; the verification script was already staged at the start, and other Harness files remained untracked |
| `git diff --check` and `git diff --cached --check` | PASS; these commands exclude untracked files |
| Harness artifacts, references, templates, and scope inspection | PASS; all 15 required files exist, including the completed-directory marker; future examples/placeholders classified separately |
| Untracked Harness whitespace and duplicate-correction checks | PASS; no trailing whitespace or duplicate AGENTS additions |
| Ruff / mypy / pytest / PostgreSQL smoke / Actions / future domain checks | NOT CONFIGURED; no pass claimed |
| Python 3.12+ execution | NOT RUN; environment follow-up |

The source/quality/integrity commands read the existing site without running
bootstrap or modifying its data. No migration, publication, dependency, or
product implementation command was used. No new product tests were needed for
these documentation changes; the existing full suite was executed.

### Review round 2 verification

Ran the same entry point through the existing interpreter using
`.\.venv\Scripts\python.exe scripts/verify_repo.py` outside the sandbox.
No PATH, environment file, dependency, or runtime setting was changed in this
round. All six checks passed, exit 0:

| Check | Review-round result |
| --- | --- |
| Django system check | PASS; no issues |
| Migration consistency | PASS; no changes detected |
| Lesson sources | PASS; 263 lessons match |
| Content quality | PASS; 281 pages, 840 SVGs, 0 issues |
| Site integrity | PASS; 1,685 references, all problem counts 0 |
| Django tests | PASS; 15 tests in 37.353 seconds |
| Protected product paths versus HEAD | PASS; no diff |
| Local SQLite hash | PASS; unchanged from the start of review round 2 |
| Cached diff | Empty at round start and after corrections; no staging by agent |
| `git diff --check` | PASS |
| Exact numeric baseline transcription | RESOLVED; Ruslan supplied values and they are recorded unchanged in `specs/progress/BASELINE-v1.md` |

Successful runtime checks do not imply human acceptance. The Python 3.10.11
environment is unchanged; target-version verification remains a pre-existing
follow-up.

### Review round 3 — baseline transcription and verification

Ruslan supplied the exact MathStart v3.1 Progress Algorithm v1 values after
the second review round. The event effects, formula, difficulty coefficients,
repeat coefficient, statuses, topic aggregation, and additional rules were
transcribed unchanged into `specs/progress/BASELINE-v1.md`. No numeric value,
threshold, or additional rule was invented.

Ran `.\.venv\Scripts\python.exe scripts/verify_repo.py` after the
transcription. The command exited 0 with all six groups passing:

| Check | Result |
| --- | --- |
| Django system check | PASS; no issues |
| Migration consistency | PASS; no changes detected |
| Lesson sources | PASS; 263 lessons match |
| Content quality | PASS; 281 pages, 840 SVGs, 0 issues |
| Site integrity | PASS; 1,685 references, all problem counts 0 |
| Django tests | PASS; 15 tests in 34.904 seconds |
| `python scripts/verify_repo.py` | PASS; 6 of 6 checks, exit 0 |

At the end of review round 3, the exact-baseline transcription finding was
resolved. Human review was Pending for the second review; R01 was Active and
incomplete until that review accepted it.

## 11. Final diff summary

First audit: two documentation files added and eleven supplied
Harness documents modified. No product files deleted or changed. The issue
template and verification script remain as supplied. Nothing was staged,
committed, pushed, or merged by this audit.

Review round 2 modifies AGENTS.md, PRODUCT.md, ARCHITECTURE.md, this trace,
the active R01 plan, and the completed-plan README, and adds the progress
baseline transcription file. Review full Harness additions with `git diff`
in the current intent-to-add state; the cached diff was empty at round start.
Local snapshots distinguish review corrections from the earlier file contents.

## 12. Acceptance criteria result

| Acceptance criterion | Result | Evidence |
| --- | --- | --- |
| Branch convention | PASS | `R01-harness-v1` |
| Root docs and accepted ADR | PASS | Review corrections applied; exact Progress Algorithm v1 baseline transcribed unchanged |
| Required templates/skill/entry point/plan/trace | PASS | File inventory and structural inspection |
| Existing application checks and migration consistency | PASS on current environment | Six groups above |
| Bounded first Harness exercise and trace | PASS | This audit and trace |
| Product/data/dependency scope preserved | PASS | Diff inspection and database hash |
| GitHub Issue R01 exists | PASS | [R01 GitHub Issue #1](https://github.com/Tramsey00/MathStart-Python/issues/1) |
| Python 3.12+ target verification | PRE-EXISTING FOLLOW-UP | Current environment is 3.10.11; not an R01-introduced blocker |
| Human architecture gate | PASS | Accepted by Ruslan on 2026-09-24 |
| R01 fully Done / final acceptance | PASS | Final human gate accepted; R01 is complete |

## 13. Remaining risks / follow-ups

- Verify on Python 3.12+ in a separately scoped environment task; do not treat
  the Python 3.10.11 pass as compliance with the accepted target. This is a
  pre-existing follow-up, not a blocker introduced by R01.
- Progress Algorithm v1 is transcribed from `MathStart Technical Specification
  v3.1, section 12 — Progress Engine`; the numeric-baseline finding is resolved.
- Runtime verification does not automatically lint Harness links, dependency
  diagrams, or secret boundaries. Those were manually audited here; future
  domain checks must be introduced with their implementations.
- Root/template rules describe future intelligent exercises; current legacy
  self-check content still does not provide server-side reveal/evidence semantics.

## 14. Harness improvement

**Yes.** This audit found future-tool claims, incomplete discovery links,
current-versus-target ambiguity, and an empty directory that would disappear
from a fresh checkout.

Improvements made: AGENTS discovery, verification skill, spec/ADR/plan/trace
templates, architecture/product clarifications, completed-directory marker,
and PR review state. The result is a more accurate starting point for a new
agent session without expanding R01 into product implementation.

## 15. Human review

**Reviewer:** Ruslan

**Status:** Accepted

**Date:** 2026-09-24

**Feedback:** Ruslan requested: (1) shorten AGENTS.md to a repository map;
(2) record the existing Progress Algorithm v1 unchanged and make R03's role
refinement/formalization/testing; (3) restore Content-owned topic mappings and
Content -> Knowledge; (4) leave Topic persistence/reference to R02/V02;
(5) restore explicit latency, logging, timeout/retry, and rate-limiting NFRs;
(6) avoid selecting WhiteNoise architecturally in R01; (7) correct trace review,
tag, staging, and Python follow-up statements; (8) preserve product code,
models, migrations, content, templates, dependencies, data, and environment.

The first review requested changes. All requested changes were completed,
including the exact Progress Algorithm v1 baseline transcription. Ruslan
accepted the final human gate on 2026-09-24.

## 16. Final status

`COMPLETE`

R01 Harness v1 is complete and accepted. All requested changes from the first
review were completed; the Progress Algorithm v1 baseline is fixed and the
finding is resolved. Python 3.12+ verification remains a pre-existing follow-up
and did not block R01 acceptance.
