# Independent I02/I03 medium review checkpoint

Scope: I02/I03 and necessary immutable-input/read-runtime/initial synthetic
activation and reproducible handoff dependencies only. This is not full R04,
V03, V04, I04, I05, migration acceptance or production execution.

Reviewer: fresh independent GPT-6.1 Sol / medium context. Application source
was read-only; own detached checkouts, ignored var/ and this evidence subtree
were used. No main merge, Issue closure, deployment or colleague messages.

## Immutable source dispositions

| Source | Commit / tree | Result |
| --- | --- | --- |
| Read runtime + CSRF + activation preflight | 5b7f3be20598e1117408fd23df5ecb34b3550280 / a751cc3681c998b378ef5e44f0d68b307de1d796 | READRT-01 CLOSED; predecessor delta inspected and independently exercised in ef7 composition |
| Bounded parsed cache + async auxiliary offload | ef7a2b2a0c13e41b67f5bb21af9607c69e1331de / 71eb7f8590479eae894e001df262301c3d409e41 | VERIFIED_IN_SCOPE for read-serving dependency |
| Backend documentation/evidence head | 0fdce4e1376e6958f0b3eb2518fd986c390a5ff1 / c960edacf3dc24a4ecdc898d614ede134a9d7835 | Evidence-only delta from ef7; source disposition preserved |
| Frontend implementation | 5308ae1e355edbf0296c6c6aa09db0d9dd21e832 / ff908320637986f4753e925d8387cda14fec160e | VERIFIED_IN_SCOPE for inspected source and independently run unit/type/build boundaries; full task verification pending |
| Read-only legacy comparator | 27079677b18b198b80bb6519f3f45b0528fd8659 / 1c038951daf0086d5944f11ce526386e17bf19a4 | VERIFIED_IN_SCOPE source; actual matched visual run remains pending |
| Frontend report head | a6a14c012c449ce6fb90b89b1cc8b3ad2b02d40f / 204ab282ae4652ccf2d66a0937c8a9a33a50232d | Report-only delta from2707967; source disposition preserved |
| Root lifecycle / portable verifier / CI | 702bcd88d6cde31540fe4c787380a64be5a278d9 / 5f2d4078503c4c7c380da685677f2d75d47491b6 | CHANGES_REQUIRED: PROCESS-01; replacement fix pending |
| Root owned-process lifetime correction | 7bdda73675ce92db554eb0f662fb08c9ab94c1d8 / 01d2d24c162a0d349bf4643ec46efc60461daff1 | VERIFIED_IN_SCOPE; PROCESS-01 CLOSED, combined run remains pending |

## Independent observed checks

Own Python3.12.14, Node24.19.0/npm11.17.0. Own target interpreter has neither
Django nor DRF. Accepted locks were retained. The initial pip index failure for
certifi2026.7.22 was preserved; exact primary-PyPI wheel was downloaded and its
SHA256 independently matched
62f22742b58a1a33014a2b6b706588a8d7e2a88ae7bd1a6ebe8c992928483775.
The complete read-runtime lock then installed and pip check passed.

Initial npm invocation used a nonexistent bundled npm-cli path; retry used the
installed npm11.17.0. Sandbox EACCES and two owner-context ECONNRESET outcomes
remain retained as environment failures. An author package-tarball cache was
copied read-only to the own cache; independent npm ci --offline verified the
accepted package-lock integrity and installed217 packages. No author's
node_modules or environment was adopted.

| Check | Actual result |
| --- | --- |
| Python artifact boundary suite at5308 | 4 PASS,0 skips,0.062s |
| Locked frontend typecheck | Four actual stages PASS |
| Full frontend Vitest | 139 PASS,14 files,0 skips,59.97s |
| Own fresh reserved PostgreSQL prepare at5b7 | 279 pages,263 topics,123 assets; bootstrap twice; no activation yet at this stage |
| Own React Router framework build at5308 using those exact inputs | PASS703 measured assertions;279 pages,280 HTML URLs plus robots/sitemap;422 files including manifest |
| Initial CSRF/session/nine-resource read tests at5b7 | 8 PASS,0 skips,1.551s; unsafe activated wiring deferred to next row |
| All13 cache/offload/read/CSRF tests at ef7 | 13 PASS,0 skips,10.634s against own activated PostgreSQL release |
| Initial activation negatives | Wrong receipt, missing URL, private export, changed redirect, missing authored body all refused; gate/journal/active counts remained0 after every rejection |
| Actual initial activation ef7 runtime +5308 artifact | PASS279 pages |
| Real ASGI key serving probes, no mocks | PASS10 cases: home/alias/catalogue/escaped query/private shell/unknown/debug-private404/current permission revocation403/same-size+mtime HTML tamper503; restored successful home200 |

Own input manifest:
890f5adac2b373b0219e253a6a7d0c92cb578d1168fe1c8f910b21bd8f63d623.
Own trusted input receipt:
c149e9386caa4b52e6386b9990e67f194ed308a3270a99966eb68312f5506287.
Own output manifest:
d8e14b7d60d79aa5b0bae661c1b759138d9faaaf472b3c3856c3087d3ad3f1f7.
Input source commit5b7, frontend build5308 and runtime ef7 are distinct facts;
this is not a run on a future combined commit.

Database retained: test_ms7_mig_v01_ms7exec_review_read_medium_20261016 on the
existing disposable backend container, loopback55432. No shared DB or server
was modified/stopped. Private signing fixture and cookie remain ignored ownvar
and are absent from committed evidence. No reviewer-owned server remains.

## Finding PROCESS-01 — P1 CLOSED at7bdda736

At702bcd8 scripts/public_block_process.py:_stop only invokes Windows taskkill/T
when the original wrapper still runs. A completed wrapper may leave its own
browser descendants alive. Independent real-process reproduction started an
owned child http.server, waited1s and exited0. run_browser_check returned
startupPASS/browser_exit0/cleanupPASS while that child listener survived.
The reviewer explicitly killed the child's recorded own PID afterward.
Raw result is retained in raw/lifecycle-orphan-probe.json.

Fix7bdda73675ce92db554eb0f662fb08c9ab94c1d8,
tree01d2d24c162a0d349bf4643ec46efc60461daff1 installs the Windows Job Object
before resuming a suspended process. The source uses kill-on-close, explicit job
termination and an ActiveProcesses==0 check, with API refusal failing closed.
There are no breakaway flags or changes to enclosing sandbox protections.
The stage driver also uses the owned process factory. POSIX process groups
retain their previous ownership behavior.

Independent repetition of the original reproduction now returned
owned_browser_child_listener_survived:false. Independent full lifecycle suite:
10 PASS,0 skips,22.843s, including normal0 and failed7 wrapper exit with a child,
browser timeout and child timeout, startup failure, occupied listener refusal
and two separately owned origins. Fix source is VERIFIED_IN_SCOPE; a full
combined portable run is still a distinct pending criterion.

## Preliminary visual observation — Chrome360 only

Manually viewed author-owned live smoke07 captures, including all four target
contents panels, all twelve power presets, the table showing0,0625 at x=0,25,
and ordinary-scale circle lab plus8/12-part diagrams. All four contents target
captures and the three circle target captures were compared with their live
Django counterparts. Labels, fraction
values, axes and controls are visible without clipping/overlap; contents are
readable and the F02/F03 values fit their cells. No new defect observed in this
width. This is manual inspection of existing live browser captures, not an
independently executed browser matrix. Source capture directory:
frontend/var/playwright-smoke-07/parity-matched-live-Django-cf202--captures-at-ordinary-scale-chrome-360.
Other browsers/widths and final combined artifact remain pending.

The frontend owner subsequently confirmed smoke07 served committed frontend5308
artifact b44ab4d4cafec31410e09cdb4a99ffe3a4008f17bc13c56c6fe34f118014581e,
release ms7exec-i02-public-20261016, input manifest
3d9a389bba5adcb6c097526fa440ad72b1efdd167536a661155b08e4e6dd435f,
input receipt db059ce5e13fe0bd12904254348122ee15c6f7acd199c0e04f05969ec7db6eab,
on backend ef7. The18 inspected public PNGs are retained with SHA256 index under
visual-chrome360/. This provenance is an author report, separately identified
from the reviewer's own fresh build and runtime.

The same author subsequently observed an actual private-shell React418 hydration
failure during full private navigation. A correction and next immutable frontend
candidate are pending. The preceding unit/build results do not accept that
private runtime behavior; final I02 readiness remains incomplete. The owner is
also splitting the nine-resource staff browser loop to retain the existing
60-second bound per independent resource test rather than hiding a timeout.

## Remaining acceptance

Final combined exact-SHA runtime/browser run, all nine browser/width projects,
manual matched F01–F04 and all style/script-family captures, portable verifier
composition on the combined artifact, publication/CI provenance and final
handoff remain pending. I02/I03 remain IN_PROGRESS; formal human gates remain
HUMAN_PENDING. Partial green checks above are not TECHNICALLY_VERIFIED tasks.

## Later deltas pending final combined run

Root source-provenance correction
db15b8c763c5a4dab28b448a08f552b62254b040,
treef904f51dc508b2c112dea8bab509f76b6568db7a: independently read source guard
before/after every stage and before final PASS. HEAD/tree, binary tracked diff
and untracked file contents are bound; ignored generated runtime/cache stay
excluded. Four independent real temporary-Git tests PASS,0 skips,4.245s. The
previous source guard observation is CLOSED; this root slice is VERIFIED_IN_SCOPE.
It adds actual npm/PostgreSQL version output and the new cache tests to the
combined command, with a bounded7200s browser workload and150-minute CI job.
No required assertions were removed. Full combined execution remains distinct.

PRIVATE-01 P1 was independently reproduced on5308 in real Chrome155.0.8059.82,
width360, against the reviewer's own ef7 ASGI runtime: private GET200 and the
correct anonymous denial message accompanied pageerror Minified React418.
The run's owned server/browser cleanup passed. This is a measured defect,
separate from the successful HTTP API and unit/build checks above.

Fix candidate48fadcce82b19bb6e5b2dc6f722602e56c746287,
treec16bc39d08bbdf69fc0a9f256aae37c7d91b9ed2: source delta inspected. The
public loader returns no home view only for the framework SPA-build header,
initial route discovery avoids a new manifest fetch requirement, and packaging
requires a hydration shell without public-view markers. The browser resource
loop is split into all nine resources at the existing60s bound; it now asserts
zero page errors. Complete inventory retains every URL with a per-request5s
bound and a separate volume bound; it has not been replaced by sampling.
Independent typecheck4 stages and focused private-shell2 tests passed. Own
complete build PASS703 assertions,279pages,422files, output manifest
0ceb78d148d7d4c376333376308848c2e9dd79de60f6f4a92c8c476227efb612 from the
same immutable reviewer inputs.

PRIVATE-01 is now CLOSED independently at48fadcc. Own real
Chrome155.0.8059.82/360 against the ef7 ASGI app passed the anonymous private
shell and all nine authenticated staff resource list/detail/history flows through
full browser navigation. Every private document returned200/private,no-store;
page_errors was empty. The owned Windows Job server/browser lifecycle returned
startupPASS/browser_exit0/cleanupPASS. This regression used the newly trusted
frontend artifact from the same immutable input release with the existing own
synthetic descriptor; it was not a second activation or production replacement.
The final combined fresh build/activation/browser matrix remains pending.

Test-only strengthening05dd3626847182a6fad9af2714f41988d8a6aef8,
tree721f78891b238712d17ea462b9e6f2e0e384072b, is VERIFIED_IN_SCOPE by independent
source review. All nine resources require at least one fixture link; the empty
conditional branch was removed. Each resource unconditionally requests
list/detail/history and requires at least three captured API responses, all200
with no-store, and zero page errors. No application source changed in this delta.
No additional full matrix was started by the reviewer; the coordinator owns the
authoritative combined run. Prior independent positive navigation of all nine
resources at48fadcc remains applicable to the unchanged application code.

## Windows npm argv correction after combined01

Coordinator combined01 at340eba98581271e05b4fea21958875fef31a567d failed at
npm-version before PostgreSQL setup. The custom cmd /s /c quoting did not survive
Windows list2cmdline handling for Program Files. That failed run remains FAIL;
the narrow correction and tests do not relabel it as successful.

Independently inspected the correction in scripts/verify_public_block.py,
file SHA2567ce4830c83a4130d49c2ac41cc572cc6e96b1f376f48b13a96183ebdb008ddef,
as an uncommitted delta on340eba9. Windows now invokes the resolved Node
executable with the installed npm-cli.js path and separate fixed argv items;
there is no cmd.exe quoting layer. The existing command whitelist remains,
missing Node/npm CLI fails closed, and POSIX argv is unchanged.

Independent actual invocation resolved both paths under C:/Program Files/nodejs
and returned npm11.17.0/exit0. Unknown commands and missing CLI were refused.
After the coordinator's typecheck ended, the reviewer ran the real integration
typecheck sequentially using that exact adapter, with its own log and receipt
under review/var. Node24.19.0; all four actual stages PASS,0 skips,9.704s:
frozen contract generation, frozen staff generation, React Router typegen and
TypeScript noEmit. Owned Windows Job cleanup PASS. Only ignored framework/check
caches were generated; no application source was edited. The adapter file hash
was identical before and after the probe.

Disposition: VERIFIED_IN_SCOPE for the reviewed correction bytes and actual
Windows invocations. The coordinator must bind those bytes to its next committed
candidate and run combined02 afresh. No full matrix was run by the reviewer.
New raw version/typecheck logs and structured receipts are retained under raw/.
