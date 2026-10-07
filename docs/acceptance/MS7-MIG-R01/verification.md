# R01 candidate verification вЂ” 2026-10-07

**R01 INCOMPLETE; independent acceptance and snapshot merge PENDING.** Tested
application input is `8c11edadc8debc81432d1db1145feac504f09061`; application,
dependencies, migrations, Harness and CI remain unchanged. Candidate commit and
current CI/tested merge-ref are recorded in the external snapshot PR, so this
document does not attempt to embed its own containing commit SHA.

[Draft PR46](https://github.com/Tramsey00/MathStart-Python/pull/46) initially
published head31d629f; no head workflow/check runs present in first live search.
Initial merge-ref existed but was not yet proven tested. Final current head/CI
must be read in PR body; [receipt](snapshot-review.json) records this distinction.

## Isolation and actual tooling

Existing interpreter: `C:/Projects/MathStart-Python/.venv312/Scripts/python.exe`,
Python 3.12.10, pip 26.2.1; `python -m pip check` exit 0. Locked installed
packages reported in [version evidence](evidence/verification-1.txt), including
Django 5.2.16, DRF 3.18.1 and psycopg / psycopg-binary 3.3.6. No new dependency
was installed. PostgreSQL 16.15 (`server_version_num=160015`); Docker 29.8.1,
Compose v5.5.1; Git 2.47.0.windows.1; Node v24.19.0 (inventory only).

Snapshot worktree: `C:/Projects/MathStart-Python/tmp/ms7-mig-r01/snapshot`.
Private QA/runtime: sibling `qa/`, `qa/runtime`. Disposable container
`ms7-mig-r01-pg-20261007`, image `postgres:16-bookworm`, port 127.0.0.1:55437;
runtime DB `ms6_v01_smoke_ms7_mig_r01_20261007`, Django test DB
`test_ms7_mig_r01_20261007`. The separate HTTP process on 127.0.0.1:8017 was
terminated by its audit's finally block. Existing working runtime/5432/8000
was not used for writes. Only disposable smoke ran migrations/bootstrap/static.
Synthetic credentials are restricted to disposable task utilities; working
credentials, session keys, raw user rows and DB dumps are absent from records.

## Executed checks

All commands use the interpreter above, candidate cwd and explicitly isolated
PostgreSQL/runtime environment. [Command results](evidence/commands.json) and
selected plaintext logs retain exact verification output.

| Command/check | Exit | Result / evidence |
| --- | --- | --- |
| `python scripts/version_report.py` | 0 | PASS; [versions](evidence/verification-1.txt) |
| `python scripts/check_database.py` | 0 | PASS; [connection](evidence/verification-2.txt) |
| `python scripts/fresh_install_smoke.py --disposable` | 0 | PASS; empty PostgreSQL, 22 migrations, bootstrap twice, sentinel identity preserved, media/static/source integrity; [log](evidence/verification-3.txt) |
| `python scripts/verify_repo.py` | 0 | PASS **8/8**, no skip flags; [full log](evidence/verification-4.txt) |
| в†і `python manage.py check` | 0 | PASS |
| в†і `python manage.py makemigrations --check --dry-run` | 0 | PASS; no new migration |
| в†і `python manage.py check_lesson_sources --all` | 0 | PASS; 263 lessons |
| в†і `python manage.py check_content_quality` | 0 | PASS; 279 published pages, 1137 SVG, zero problems |
| в†і `python manage.py check_site_integrity` | 0 | PASS; 25 informational unused-media references in fresh disposable runtime |
| в†і `python manage.py test` | 0 | PASS; 107 tests, actual PostgreSQL connection/transaction tests included |
| в†і R03 pure reference suite | 0 | PASS; 18 tests; reference behavior, not runtime Knowledge persistence |
| в†і Harness unit suite | 0 | PASS; 73 tests, deterministic/mock providers |
| `python -m unittest discover -s tests -p test_r02a_contract.py -v` | 0 | PASS; 30; [log](evidence/verification-5.txt) |
| `python -m unittest discover -s tests -p test_r03a_contract.py -v` | 0 | PASS; 41; [log](evidence/verification-6.txt) |
| `python -m unittest discover -s tests -p test_i02_*.py -v` | 0 | PASS; 7; [log](evidence/verification-7.txt) |
| R01 HTTP audit (`tools/route_smoke.py`, same script rerun from private QA) | 0 | PASS; 572 requests: 279 canonical public URLs, 282 redirect rules, 11 public/account/API/admin/static/negative cases; [results](route-smoke.json) |
| Working DB `tools/runtime_readonly.py --original C:/Projects/MathStart-Python` | 0 | PASS; explicit REPEATABLE READ READ ONLY, SHOW verifies read-only/isolation, final ROLLBACK; [schema/aggregates](runtime-data-manifest.json) |
| Metadata audit | 0 | PASS; 16 models, 9 admin registrations, 77 non-DEBUG patterns, 39 installed commands |
| Source/frozen pins/local preservation/doc links/record safety | See [validation](validation.json) | Exact source hashes; all unchanged input contracts/code retained; 18,568 original output/tmp files verified without overwrite |
| `git diff --check` | 0 | PASS for unstaged tracked preparation |
| `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --cached --check` | See trace / PR | Recognizes required unchanged external CRLF input; does not suppress trailing-space checks |
| Existing GitHub workflow at candidate head/tested merge-ref | See snapshot PR | Current run required; input main's old green run is not candidate acceptance |

Working runtime differs from canonical renderer only by 13 structural HTML
LF/CRLF variants after normalization; all 263 topic/source/publication outputs
match. Two retired unpublished records retained. Separate raw, normalized and
original-checkout comparisons are in [rendered digests](rendered-runtime-digests.json).
No bootstrap/repair ran against the original DB. Informational unused media
counts from different runtimes are not silently equated.

## Observed failures and corrections

Initial non-escalated local PostgreSQL/Docker access was sandbox restricted;
authorized isolated/read-only execution succeeded. No credentials were printed.
The first Issue transfer had incorrect Cyrillic decoding through shell stdout;
the existing Issue was repaired, not duplicated. All 18 live titles/bodies/
assignments were then independently compared with canonical input.

First HTTP QA execution exited 1 because urllib received a Unicode legacy URL;
R01 utility now uses `iri_to_uri`. Second execution exited 1 for `/glavnaya/`:
the expectation omitted the published home slug alias. Inspection confirmed
`content.views.page_detail` serves it with 200 and `RedirectFallbackMiddleware`
uses rules only after 404. Audit expectations now include explicit slug routes;
the final run exits 0, preserving the application's actual precedence and
checking all rules. No application validation was weakened or changed.

Initial record validation exited 1 because the two Markdown links to its own
not-yet-created report were checked before writing that report. The utility now
establishes its output path first; preservation and source checks were already
passing. Final source/link/safety result is recorded in validation.json.

The input checkout's CRLF transformations are separately recorded from exact
Git blob hashes. Canonical external specification is pinned `-text` to retain
its exact bytes; manifests do not include their own digest. Historical output
references are checked for real on-disk existence, including missing/pattern
entries. Source/runtime mismatches remain decisions, not automatic overwrites.

Ruff/mypy/target React/FastAPI/Alembic checks and target CI are **NOT RUN / NOT
CONFIGURED for this R01 baseline**. No live LLM was required. New platform
implementation, human approval and public deployment were not performed.

Initial staged default whitespace check exited 1 because imported exact CRLF input and captured Windows stdout contain CR. Exported log line endings were normalized without changing original private logs; raw/export hashes are recorded. The final staged check explicitly recognizes CR-at-EOL for exact external input while retaining other whitespace checks. The original specification bytes remain unchanged.

## Initial candidate CI failure and in-scope correction

[Run37602901512](https://github.com/Tramsey00/MathStart-Python/actions/runs/37602901512), head31d629f, actually checked out merge-ref fab0ea1cb3bc8b6970a7b86867e1068d0697465b. Python3.12.15/PG16.15. Verification exit1,7/8 pass; Harness73 tests/1 error because new current-status paragraphs changed frozen MS6-R04 PRODUCT/ARCHITECTURE digests. This was introduced by R01, not pre-existing. Initial local8/8 predates these document edits and did not prove the first commit. Both files restored to exact input bytes; pins/Harness unchanged. Validator now requires exact input for those documents. [Sanitized first CI evidence](ci-first-head.json). A non-escalated narrow rerun encountered sandbox temp cleanup permissions; repeat in authorized isolated QA environment. Final corrected local baseline and current-head CI follow below/in PR.

## Corrected isolated candidate verification

Both pin-restored checks completed with exit0: [Harness73/73](evidence/harness-after-pin-restore.txt) and [full baseline8/8](evidence/baseline-after-pin-restore.txt), including Django107/R0318/Harness73. [Exact commands/log hashes](evidence/corrected-commands.json). Source/frozen pin/preservation/link/safety validation PASS:1023 unchanged input files, only .gitattributes/AGENTS/README changed; all18568 original QA files retained. Final current-head CI is separately required and externally recorded in PR46; the first failed run remains visible.

## D08 follow-up verification — 2026-10-07

Live GitHub comment author/explicit acceptance/exact reviewed head/merge metadata comparison PASS for both supplied records. Historical head CI36876278599 and36999556028 still SUCCESS. Participant test claims remain attributed to their own records; this follow-up performs no source/schema/DB change. Original_result objects and frozen source/audit/runtime snapshots preserved. R01 source/preservation/link/safety validation and regenerated record Git blob manifest checked before commit; current new head CI/tested merge-ref required and recorded externally in PR46. D08 CLOSED; other decisions/gates PENDING.
