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

## Ilya evidence import — 2026-10-08 Europe/Moscow

Import reads supplied ZIP and repository records, with no DB access/setup/write.
Archive SHA256 matches supplied63d0bca0…e9313; 232 safe members/ZIP CRC verified;
231 payload manifest entries and228 export provenance entries exact SHA256/size.
All190 JPEG decoded/verified with existing bundled Pillow; no EXIF/extra metadata.
Decoded text/JSON and credential pattern review found no secrets/row-level PII;
127 imported Markdown relative links resolve within package. Atlas plus F01–F04
screenshots inspected as public anonymous content. Imported ZIP member bytes
preserved, upstream export transformations kept separate; all Git blob OIDs/SHA256
checked by [import validation](ilya-20261007/import-validation.json).

Ilya's reported application Python3.14.7 is distinct from original R01
Python3.12.10; artifact tools3.12.14/Pillow12.3.0. Imported fresh smoke/parity
exit0:279 exact pages/263 publication digests; six HTTP routes/15 static assets.
His browser review:63 functional groups PASS +1 observation; one browser
surface, limited runtime/session version linkage, resampled JPEG. Cross-browser,
touch, full accessibility and exact pixel comparison NOT RUN. Browser-only
phase did not run canonical verify_repo; current PR CI is separate evidence.

Ruslan working DB's13 LF/CRLF variants do not describe Ilya working DB:
five specifically checked payloads have substantive drift. Ilya disposable
exact-source parity is a third environment. Historical reports/frozen schemas/
source manifest preserved; no source fix or application change. Record/source/
local preservation/link/safety checks run before commit; new-head CI required
and externally recorded in PR46. D02/D03 partial; final gates PENDING.

Evidence-import verification results: source/frozen/local preservation/link/
safety validator exit0 PASS,1023 exact original input files and18568 original
output/tmp files preserved. Initial import Git check found ignored .log/two
report JSON absent from index; scoped package force-add includes all232 members.
Original long Windows revision paths made the first input-tree check exit1;
the R01 utility now compares batched Git tree/index object IDs, preserving all
checks rather than changing source/validation criteria.

New local canonical verify_repo exit1 **FAIL_ENVIRONMENT**, four checks pass
(backend,migration command,R03,Harness73), four PostgreSQL-dependent checks
fail with ConnectionTimeout at own disposable55437. Docker ps/ps-a show no
matching earlier R01 container. makemigrations exit0 includes missing migration
history warning, so does not prove local database consistency. No working DB
fallback/setup/bootstrap/migrate/recreation or skip flag used.
See [bounded result receipt](ilya-20261007/local-verification.json)
for trace, or the corresponding same-folder receipt for verification. Current
head full isolated CI remains required; previous green is not this run.

Staged whitespace audit first flagged own new blank lines and14 pre-existing
trailing spaces in imported command-05.log. Own blank lines fixed; original
log bytes preserved as required. Own/current documents use full whitespace
check excluding only exact imported package; package SHA256/Git blobs separately
validate every byte, with original whitespace findings left visible.

Final import audit: `validate_ilya_import.py --ref INDEX --archive <supplied ZIP>` exit0 PASS; all232 ZIP members equal checkout and staged Git blob bytes/OIDs,231 package hashes/228 provenance exports verified,165 relative links valid, original_result objects and D08/source/runtime/initial GitHub/first CI snapshots preserved. See [exact result](ilya-20261007/import-validation.json). Own whitespace check excludes only the unchanged external package;14 original command-05.log trailing spaces remain observed, not repaired.

## Final acceptance record amendment — 08.10.2026

Live author/body/date/head verification PASS for three supplied human records;
Vladimir API review APPROVED/commit_id=daf4e603. Reviewed-head CI37688709748
SUCCESS is historical for the new documentation commit, not its CI. New current
head full unchanged workflow/verify_repo8 required, recorded in PR46 after push.
No local DB verification rerun: prior disposable container unavailable; prior
FAIL_ENVIRONMENT preserved and no working-DB fallback/setup. Record/source/
history/package hashes, links and manifest checks run without DB access under
repository verification skill. Existing verification/CI/Harness not altered.

The prior Desktop ZIP path is absent in this session: optional original-archive
probe exits1 FileNotFoundError. No ZIP recreated or evidence overwritten.
Current audit checks all232 committed package bytes against the preserved
manifest/provenance/receipts and Git blobs without claiming a new ZIP hash probe.
Previous successful ZIP verification remains historical at reviewed daf4e603.

Final database-free checks exit0 PASS:232 exact imported files/Git blobs,231
package entries/228 provenance entries,168 relative participant evidence links;
original_result objects/source/runtime/frozen snapshots and earlier scoped/import
receipts unchanged.1023 input files and18568 original output/tmp preserved.
See [current import audit](final-acceptance-import-validation.json). Own whitespace changes checked before commit.

## Post-merge R01 verification — 08.10.2026 Europe/Moscow

MIG_BASE_SHA60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7, accepted PR46 heade510744.
PR CI37696561717 SUCCESS and separate resulting-main CI37698445057 SUCCESS;
actual main checkout confirmed in job113055830577. Resulting tree equals
PR head/tested merge-ref tree. [Merge provenance](post-merge-provenance-20261008.json).

Verification skill followed with unchanged installed lock and interpreter.
[Sanitized exact local commands/results](post-merge-local-verification.json):
Python3.12.10 (distinct from Ilya report3.14.7 and CI3.12.15),
Django5.2.16, PostgreSQL16.15 (server160015), pip26.2.1.
Dedicated R01 disposable container127.0.0.1:55438, unique runtime/test DB and
QA runtime; no connection to working5432 DB. No dependency install or changes.

| Command / check | Result / exit |
| --- | --- |
| python --version; python -m pip check; scripts/version_report.py | PASS /0 each |
| scripts/fresh_install_smoke.py --disposable | PASS /0, fresh PG migrations/bootstrap/static |
| scripts/verify_repo.py | PASS /0,8/8; Django107,R03 reference18,Harness73 |
| R02A reference suite | PASS /0,30 |
| R03A reference suite | PASS /0,41 |
| tools/validate_records.py --original C:/Projects/MathStart-Python | PASS /0,1023 unchanged input +1026 original files,18568 preserved output/tmp |
| tools/validate_ilya_import.py --ref INDEX --output post-merge-import-validation.json | PASS /0,232 exact files/Git blobs,231 package entries,228 provenance entries,169 evidence links |
| Post-merge provenance/scope/historical/relative-link audit | PASS /0; owner report distinguished from public approval;18 Issues OPEN |
| git diff --check; git diff --cached --check | PASS /0 |
| Task PR→integration GitHub Actions | NOT RUN / NOT TRIGGERED: unchanged workflow only main PR/main push |
| Original external ZIP SHA256 repeat | NOT RUN: Desktop archive absent; prior archive receipt unchanged, Git package exact |

[Current import audit](post-merge-import-validation.json) and
[post-merge audit](post-merge-validation.json) preserve all historical evidence.
New current record manifest excludes itself; exact staged Git blobs and checkout
digests are separate. Original local failing environment receipts remain history,
not rewritten by this successful fresh disposable run. Raw synthetic smoke logs
retained private; no DB rows/session/credential dumps published.

The local results do not establish a GitHub CI run on the new record task HEAD.
No failing checks skipped, tests/validation weakened, target CI added or
subsequent migration task started. Current task record amendment review/intake
remains required; merged snapshot approval is not automatically transferred.

## Current CI trigger extension — 08.10.2026

Earlier task NOT RUN entries above are historical at9fde3e5 and earlier heads.
Owner now authorizes integration branch filters for existing baseline CI; both
main triggers remain, entire jobs byte-identical. No full target verification/R03.
[Trigger audit and exact digests](ci-trigger-adjustment-20261008.json).

Local existing R02A test suite: FAIL /exit1,30 tests,1 failure due preserved
whole-file ci.yml pin in historical candidate-manifest. Pin/test remain unchanged.
This is an actual blocking failure, not a waived check. Exact new-head GitHub
workflow outcome and checkout/tested merge-ref recorded in PR47/current CI receipt.
The source manifest and old validation/import reports remain historical input
proofs; workflow is the single newly authorized source exception, recorded here.
No change to working DB, baseline/integrationSHA, dependency lock or Harness.

### Observed integration trigger CI

[Run37701885197](https://github.com/Tramsey00/MathStart-Python/actions/runs/37701885197)
on e64d9a4b2682ee5b206f9d88f11fff2867071686 completed **FAIL**;
checkout4a62032c033543ef4a282981a8d97585a579ca33 verified in job113067016184.
[Sanitized CI receipt](ci-integration-trigger-first-run.json).
Python3.12.14,Django5.2.16,PostgreSQL160015.

| Step | Observed outcome |
| --- | --- |
| Install locked dependencies / pip check / version / bounded connection failure | PASS |
| Fresh disposable PostgreSQL smoke | PASS |
| verify_repo.py | PASS8/8; Django107,R03reference18,Harness73 |
| R02A HTTP and eligibility contract | FAIL1/30,exit1; preserved whole-file ci.yml pin mismatch |
| R03A CompletionFact contract | NOT RUN; normal step skipped after prior failure, no skip flag |
| Workflow configuration parse / integration PR trigger | PASS; actual run started by pull_request integration base |

This receipt is an exact first-trigger-head observation, not final containing-head
CI. Record commit gets a new run; exact final head/run/tested merge-ref/result
recorded in PR47. No old successful run substitutes for current checks.
Pin incompatibility remains acceptance blocker, no historical manifest/test rewrite.
