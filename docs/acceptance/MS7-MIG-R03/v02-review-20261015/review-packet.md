# V02 published candidate: technical packet for Independent Task Approval

**Current status: TECHNICAL_CHECKS_PASS / INDEPENDENT_TASK_APPROVAL_PENDING.**
PR53 remains open/draft; no approval, draft promotion, merge or Issue closure
was performed. R03 remains **INCOMPLETE**. This packet is R03-owned evidence;
V02 implementation, owner locks/tests, original reports and frozen baseline
workflow were not changed. Gate/anchor/40-path policy/publication permission
were already confirmed by the user and were not requested again.

## Exact candidate and separate execution revisions

| Fact | Recorded value |
| --- | --- |
| PR / owner | [PR53](https://github.com/Tramsey00/MathStart-Python/pull/53), VladimirFrolov777 |
| Base repository / ref | Tramsey00/MathStart-Python / ms7-mig-react-fastapi |
| Base / only parent | `0c03197e23f69a233c0fcf8bdffa336feca20b92` |
| Implementation / actual Linux candidate checkout | `76d8eac6387a5fde5432a0e8130a881cb6d7ba82` |
| Actual candidate tree | `dbad1e853dff354c5d3255755afb5cc32e0ad279` |
| Fixed publication controls / actual owner checkout | `1b75c6e58ecdcb4bb172d4df979e9b9efa7dde68` |
| Approved owner anchor SHA256 | `5a9a7a65dab43afe4e353b51523d86f3a15de2e371d19efacc8127ae6d0dbfd7` |
| Separate human decision SHA256 | `0a872e5f2c15fd6e6e031c87c97e6ca41323db4bdfa84da60383978319e3a8f4` |
| Published workflow/event/orchestrator SHA | `a743323a32e256399cb293beee2822eb4e63e555` |
| Final task workflow/event/orchestrator SHA | `aefba6a25400a2eecb8c861a58b9637c070a12ac` |
| First task workflow SHA (incomplete artifact packaging) | `31d29212d94ddc569341838c52ad5d7ca2aec86b` |
| Immutable MIG_BASE_SHA | `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7` |

Each job used fresh Linux candidate checkout at implementation SHA, not a PR
synthetic merge ref or the R03 workflow checkout. Live PR HEAD was checked before
and after both gates and remained76d8eac. Publication checks require exact owner,
repository/base, one accepted parent, tree and clean HEAD/index. Current candidate
input is [canonical R03 input](../../../../specs/migration/r03-v1/v02-published-candidate.json).
Task controls field references the approved publication controls; the task job
executes R03 observers at its separately recorded workflow SHA, not a new owner
control revision. Actual owner checkout1b75c6e is recorded by the published job.

## Actual checks and applicability

| Evidence | Result and precise coverage |
| --- | --- |
| [Published gate38637910883](https://github.com/Tramsey00/MathStart-Python/actions/runs/38637910883) | SUCCESS; `published` mode on actual commit; mandatory isolated external v3 verifier exit0. Approved151 paths/bytes/OIDs/sizes/modes/attributes;40 exceptions,73 raw paths, original139 and frozen60 unchanged. |
| [Final task CI38642117604](https://github.com/Tramsey00/MathStart-Python/actions/runs/38642117604) | SUCCESS; three separate exact owner-lock environments; all20 phases PASS. Complete downloaded artifact reconciliation PASS,1050 manifest rows and36 command receipts checked. |
| V02 owner suite at exact SHA | **86 PASS / all40 PostgreSQL /0 skips**. Exact IDs match remediation named_tests. Classes9 unit +15 SQLite HTTP +17 PG HTTP +22 SQLite asset +23 PG asset.0 failures/errors/expected failures/unexpected successes; every recorded subcase PASS. |
| F01/F02 regressions |45 asset cases included above; shared identity versus per-page CSS/JS order, incompatible identity/digest/storage/lifecycle fail closed. Missing404 redirects preserve GET/HEAD/status/Location; other failures/private/CSRF/integrity errors never redirect. Native PostgreSQL Django-versus-FastAPI comparator **8/8 exact matches** retained. |
| Content / Grades / routing / staff / security | V02 unit/HTTP/native PG tests cover DTO/content-type/methods, PK versus number, signing/keyring/keyset edits/delete/insert, bounds, Unicode/catalogue/SEO, redirect/media precedence, nine staff DTO families/history/selectors, DB flags/permissions before private lookup, revision cursors, read-only transactions and no profile/evidence/DML. Invalid cursor/raw JSON/traversal/unsupported row/DB/internal failures are safe. |
| V01 separate regression at exact candidate | **34 PASS / all23 PostgreSQL /0 skips**, exact accepted inventory; separate locked venv and PG16 port55441. Fresh install×2, profiles A/B/C, schema/history/data/sequences, review/stamp/rollback/connection negatives and real concurrency/timestamp remediations. Accepted V01 files/locks verified unchanged; added V02 files are not mistaken for V01 mutations. |
| Historical contract regressions at exact candidate | R0263, R02A30 and R03A41 PASS,0 skips. Native comparators remain in isolated legacy-containing test env, separate from target runtime. |
| Content projection parity | Fresh disposable legacy Content profile, **279 pages /263 topics**; source identities, SEO and catalogue PostgreSQL order agree with native Django; SQL reads only. This projection check does not establish full asset-family/browser rendering or candidate activation. |
| Separate target runtime | Runtime owner lock installed alone, exact package pins and pip check PASS; Django/DRF unavailable and no Django imports,32 implemented operations. Actual localhost8202 service returns grades200/staff401/default public503, safe private,no-store JSON; PID stopped. Public503 is expected with absent reviewed renderer/release ports. |
| PostgreSQL ownership/cleanup | Two new PG16.15 tmpfs services on15441/55441, checked IDs/image/ports; no prior DBs. Both suite DB inventories empty before/after; Content profile explicitly created/marked/dropped; final empty, services stopped and removed. |
| §17 | All three original_result→migration_follow_up→target_evidence records resolve. Current exact-SHA/CI overlay preserves complete original history/approvals, plus existing frozen/source checks; [current overlay](section17-current-overlay.json). |
| [Candidate baseline38635496099](https://github.com/Tramsey00/MathStart-Python/actions/runs/38635496099) | SUCCESS on76d8eac; fresh legacy PG smoke and8 verify_repo checks,109 Django +18 R03 contract +73 Harness tests; R02A30/R03A41. **Does not execute V02 suite.** Decoded GitHub job log retained separately. |

Exact per-case results: [V02](38642117604-v02-tests.json),
[V01](38642117604-v01-tests.json), [task summary](task-summary.json).
CI Python3.12.15; Git2.55.0; PostgreSQL16.15. Full installed distribution/lock
receipts and actual argv/stdout/stderr/exits are retained, not inferred from a
green workflow badge. No live Product LLM or production database was used.

## Whitespace policy and evidence preservation

The unchanged confirmed bootstrap extracts trusted controls from1b75c6e and checks
script digests before execution. It invokes the mandatory command in published mode:

```text
python -I -B OWNER_CONTROLLED/verify_publication_v3.py --root CLEAN_CHECKOUT --ref 76d8eac6387a5fde5432a0e8130a881cb6d7ba82 --owner-anchor OWNER_CONTROLLED_APPROVAL_JSON --owner-anchor-sha256 5a9a7a65dab43afe4e353b51523d86f3a15de2e371d19efacc8127ae6d0dbfd7
```

Actual absolute argv is in `gate/gate-raw/commands.json`. Exit0, exact approved
source/metadata and **both scoped whitespace checks PASS/0**. Full checks remain
**FAIL/2**, with3887 ordinary and6 cr-at-eol diagnostics. Raw stream SHA256s are
`c1b69b199ac5cd41c665d656a72587d36ff0d13dc04a82c0a4c3d75086da20fb` and
`5837278beb0d2ef638db564512c6913f9ae02346d204ba7b75c059aaef373f63`.
No new diagnostics outside40 exceptions, no repinned candidate values,
`--local-proposal` or synthetic publication approval anchors. Approved earlier
generic authorization=false/pending fields are unchanged source history; current
publication authority is the separate human decision and current published receipt.

Confirmed staged/tree run38596739924 (positive/17 real negative rejections/restored
positive) remains earlier source evidence. It is not relabelled as commit evidence.
Current published run also passed12 synthetic orchestration guard regressions;
those are guard tests, not owner approvals.

| Raw artifact | Original GitHub ZIP SHA256 |
| --- | --- |
| [Published11928258444](https://github.com/Tramsey00/MathStart-Python/actions/runs/38637910883/artifacts/11928258444) | `8612c147dbe88a113e257b7ad355ffaa9c5b2b0f6668ee1d3b676d09c1c05300` |
| [Final task11930482101](https://github.com/Tramsey00/MathStart-Python/actions/runs/38642117604/artifacts/11930482101) | `bc5ad6c40b4095a0f8ea2f1f2a350d4bcf5af1b388d49da27581932139f520b8` |
| [First task11930332405](https://github.com/Tramsey00/MathStart-Python/actions/runs/38641371932/artifacts/11930332405) | `5df3e77ccf75acc01395386e7a8817c9c46bddcded89f7ff1b623d5d9f1245a1` |

Downloaded ZIPs matched GitHub SHA256. Publication artifact:114 members,
65+113 manifest rows and47 command receipts independently checked. All bytes
preserved in [compact raw ZIP](linux-38637910883-raw.zip), SHA256
`b24a669eeb69665803cdb678b018141e78a4d3201da6c4143485ef80718ced94`;
one55MB duplicate stream maps byte-for-byte to the already committed approved
source ZIP via duplicate-byte-map.json. Final task:1058 members,1050 manifest rows,
36 command receipts,0 missing; [retained raw ZIP](linux-38642117604-raw.zip)
SHA256 `6e3bcf92dde8ba11c99b3efb3090a8e600d31c2436b97db655063dca6a6ec63a`.
Service logs added after the manifest are covered by every-member inventory.
Decoded GitHub logs are labelled as decoded API output, not claimed original
GitHub log archive bytes. [Review artifact inventory](review-artifact-digests.json)
and reconciliation receipts identify each original/retained class separately.

## Findings and remaining human gates

No failing V02 task-specific case or source/provenance discrepancy was observed
on this HEAD. Earlier named F01/F02 findings have passing actual regressions;
this is technical verification, not a declaration of human acceptance.

R03 packaging finding: first task run38641371932 passed its suites, but221 hidden
pip cache/selfcheck files (28,612,619 bytes) declared in manifest were absent from
upload (default hidden-file policy). Expected hashes/sizes and actual absence
are retained in its **INCOMPLETE** reconciliation. R03-only include-hidden-files
correction in aefba6a, rerun38642117604 and strict reconciliation close that
packaging finding; the first run is retained separately. It is not used as the
final complete artifact. GitHub's automatic final service cleanup reports
already-removed containers; explicit owned cleanup step succeeded and its
State.Running=false/removed-ID receipts are independently checked.

Remaining V02 review actions:

1. Руслан reviews this technical packet and gives or withholds final **Independent
   Task Approval on76d8eac**. Publication exception/gate confirmation is already
   received but is not Task Approval. Recheck live HEAD if review occurs later.
2. Илья records applicable Content/Grades/manifest/transport consumer handoff
   acknowledgement or concrete expected/actual incompatibilities on the exact
   producer and consumer SHAs; see [service/CLI/consumer checklist](service-cli-consumer-handoff.md).
   Full I02 browser/SSG integration is not claimed here and is not an extra V02
   prerequisite where the task card has no INTEGRATION dependency.
3. Record the human disposition and accepted exact input after those applicable
   reviews. Draft promotion, merge and closure remain separate authorized actions.

No additional owner command/lock/env input is missing for the V02 checks executed
here. The concrete service/test/receipt handoff is prepared. V03 session/CSRF,
V04 activation/immutable publisher/content CLI and I02 full renderer/browser
pipeline remain their own work; no V02 implementation extension was made.

## R03 dependencies and next available step

V02 card: HARD V01, CONTRACT R02, HANDOFF -, INTEGRATION -. Existing accepted
V01/R02 dependencies are retained. Global R03 target is independently incomplete:
runtime-commands status PENDING/commands{}, reviewed10 backend +4 frontend map,
accepted V02/I02 inputs and applicable V04 content CLI, combined exact-SHA
fresh/upgrade/content/frontend/browser/PG pipeline and independent Владимир/Илья
R03 approvals remain outstanding. Latest automatic R03 target failure and later
stages NOT_RUN are retained separately, not attributed to V02 suite.

Next available step is the human exact-HEAD V02/consumer review using this packet;
then R03 can intake accepted inputs and concrete owner command receipts under
the existing [CLI checklist](../cli-receipt-handoff-checklist.md). Keep MIG_BASE,
historical8d958/0c03197 provenance and old successes/failures. Issues30/34/35/40
remain open;34/40 stay open until final main integration. No acceptance/merge
or Issue closure is performed by this packet.
