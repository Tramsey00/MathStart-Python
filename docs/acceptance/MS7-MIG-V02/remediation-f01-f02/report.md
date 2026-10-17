# MS7-MIG-V02 — F01/F02 Remediation Report

Owner: Vladimir. Issue #35. Independent original verdict **CHANGES REQUIRED**.
Current status: **READY FOR INDEPENDENT RE-AUDIT**; scoped fixes and required
local verification complete. Positive independent re-audit **PENDING**. No publication
or Task Approval. tested_implementation_sha=null; **PENDING_PUBLICATION**.

## 1. Initial state and 47-file snapshot

cwd C:/Projects/MathStart-Python-V02; branch ms7-mig-v02-content;
HEAD/V02_BASE_SHA/merge-base: `0c03197e23f69a233c0fcf8bdffa336feca20b92`.
All 47 audited files existed and matched independent source snapshot SHA256/size.
Tracked baseline diff empty. The three source files containing the original 41 tests remain byte-identical.
Every original file was preserved before edits under history/initial/; audit and
independent snapshot copied byte-for-byte under original-audit/, with intake.json
recording source paths/hashes. No frozen/other-owner file was changed.

## 2. F01 root cause

Original releases.py:111 compared complete descriptors for a shared public URL.
Per-page Asset.order therefore became an unintended global identity requirement.
Changing topic order0->1, with identical asset bytes/storage/hash/kind/lifecycle,
caused release-wide503. Pre-fix real ASGI regression reproduced503 instead of200.
Authority: accepted `specs/migration/r02-v1/content-v1.md` Assets/lifecycle and
`specs/migration/r02-v1/public-build-contract-v1.json` union
of ordered per-page Asset arrays; order belongs to the page.

## 3. F01 patch / regressions

[F01-runtime.patch](F01-runtime.patch): compare all descriptor fields except order,
plus exact loaded bytes; keep original per-page arrays and one first-seen union
entry per URL. Closed schema, per-page sorted unique order, asset hashing/MIME/
storage containment/private restrictions remain unchanged. Different storage,
digest/bytes, kind or valid script lifecycle fail closed.
Named ASGI tests cover same/different page order, multiple CSS/JS page sequences,
unique union, valid-but-conflicting script lifecycle, damaged/missing assets.

## 4. F02 root cause

Original app.py:217 raised terminal404 for absent static/media assets, bypassing
the fallback used by ordinary public pages. Pre-fix GET /static/old.css with an
active permanent rule returned404 instead of301. Original Django middleware
applies active exact redirects after actual404.

## 5. F02 patch / regressions

[F02-runtime.patch](F02-runtime.patch): one guarded public404 fallback reads the
already selected immutable release registry. Missing assets and missing public
pages use it; working resources retain precedence. Errors401/403/405/409/503 and
integrity failure do not enter fallback. URI serialization matches actual Django
iri_to_uri, preserving existing percent escapes; malformed raw UTF8 is rejected
before replacement-character paths can match a redirect. No route/DTO/auth/CI changes.
Named tests exercise static301/302, media301, GET/HEAD, working-resource POST405,
inactive/missing rules, unsafe target, Unicode/percent Location, traversal/private
storage, corrupt/missing release and invalid asset digest.

## 6. Actual Django comparator

PG-only comparator executes real baseline WhiteNoiseMiddleware file resolution,
Django static media serving, real Redirect ORM and RedirectFallbackMiddleware.
Rule setup is in a rollback-only transaction on that test's new UUID database;
files are synthetic, under its owned temporary directory. Eight actual pairs
compare status and Location: static permanentGET, temporaryHEAD, mediaGET,
working staticGET/POST, missing staticPOST, Unicode source and encoded/Unicode target.
Detailed actual observations retained in django-http-probes.json.

## 7. ASGI results

Both minimal pre-fix regressions FAIL as expected, preserving original reproduction.
Final V02 suite **PASS: 86 tests, 0 skips**: all unchanged original 41 plus 45 new named cases.
There are 22 new SQLite ASGI and 23 new PG cases (including actual Django comparator).
All probes use the real create_app routes, not helper-only responses.

## 8. PostgreSQL verification

Dedicated existing disposable V02 container; PostgreSQL16.15, host15441/internal55441.
New marked UUID fixture databases only, original V01 fresh guard unchanged. New
baseline smoke database/runtime, no production/working DB. V01 runs separately
with read-only checkout and tmpfs var in its network-sharing Python container.
Public/runtime reads stay SELECT/READ ONLY; no activation/publisher/auth implementation.

## 9. Full test matrix

| Check | Observed result |
| --- | --- |
| Two minimal new tests before fix | EXPECTED FAIL: F01 503vs200; F02 404vs301 |
| Original 41 + new 45 V02 ASGI/PG regressions | PASS: 86, 0 skips |
| V01 original 34, including 23 PG | PASS: 34, 0 skips |
| R02 contracts | PASS: 63 |
| Fresh disposable PostgreSQL smoke | PASS |
| Complete Content projection | PASS: 279 pages / 263 topics; actual source hash/SEO/order; read-only |
| verify_repo, R02A / R03A | PASS: 8/8; PASS: 30 / 41, 0 skips |
| Actual normal target startup without Django | PASS: disposable PG connection and unchanged 32 GET registry |
| Test/runtime pip check; compileall | PASS |
| git diff --check | PASS |
| Ruff/mypy/formatter | NOT RUN: NOT CONFIGURED |

The original rerun also includes Grade list/detail/order/cursor and native staff
ordering/search parity checks. These were not replaced by asset regressions.

Exact command/exit/log/test provenance is collected in verification.json and
test-matrix.json; historical original logs are retained in history/initial/.

## 10. Frozen / ownership

Tracked HEAD diff empty; frontend/root scripts/workflows/frozen contracts/history/
V01 schema/repositories/Alembic and Django migrations untouched. Only two runtime
files patched, one scoped comparator extended and one scoped regression module added,
plus V02 plan/trace/current evidence and historical preservation copies.
Final frozen/ownership/hash comparison is recorded separately; no pin refresh.

## 11. Workspace manifest

The recomputed current workspace manifest binds actual remediated bytes;
old 46-entry manifest and its self-hash remain in original 47-file archive. No HEAD
is misrepresented as an implementation commit; commit/CI/publication still pending.

## 12. Original negative audit provenance

Source report SHA256 `1feaa929b56e5485534fbc606184c8be9953199c1d558782a8fe6717549ddbd2`.
Source snapshot SHA256 `19349dca6f3dc9560723a8837766d01a114c6917b158c27a825fafbab0b74a30`.
Original workspace manifest self-hash `0a2a37d7141e1b1e4662a4042bb59018995bc20e4b63a1d02b586ee24c266435`.
Original auditor verdict remains CHANGES REQUIRED at that snapshot. The retained
audit was not edited or relabelled as positive. This remediation is an owner
submission; it does not replace independent review or human Task Approval.

## 13. Remaining findings

F01/F02: locally remediated and regression-proven, independent positive re-audit
PENDING. No additional confirmed P1/P2/P3 defect observed during these scoped checks;
this is not an independent security verdict.

## 14. NOT VERIFIED

Positive independent re-audit, human approval, future published candidate CI,
real V03 sessions/CSRF, V04 production snapshot/activation/recovery and full
I02/I03/V05 HTML/assets/browser/gateway deployment. Original normative PDFs were
available and hash-rechecked here; the earlier auditor's availability limitation
is preserved as its historical observation, not rewritten.

## 15. Recommendation

**READY FOR INDEPENDENT RE-AUDIT**. Positive independent re-audit and human
Task Approval remain **PENDING**; V02 is not ACCEPTED.
No commit/push/merge/rebase/reset/clean or PR performed. Independent re-audit is
the next gate for the completed local PASS/hash/ownership package.

Current evidence run: `MS7-MIG-V02-F01-F02-f5cac30e92044cb99c11b0907b931fa1`. The final 86-test matrix records each
executed case. The 409 probe injects a resolver error only to prove fallback
precedence; no ordinary V02 read 409 outcome is claimed. All 60 frozen records,
all 47 archived originals and both staged/unstaged tracked diffs were rechecked.
