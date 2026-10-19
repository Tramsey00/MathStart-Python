# V02 producer8256cbf: service / CLI / I02 consumer handoff

Producer: PR53 exact8256cbf4b38e97fc1169fea85f2d558950543be8; parent76d8eac,
tree74c3014516ec3a2110d2cfec13c8e7afb8ae5024. Technical matrix PASS under
[current packet](review-packet.md); renewed human Task Approval remains pending.
Владимир owns backend; Руслан owns R03 wiring/review; Илья owns renderer consumer.

Runtime/test locks are unchanged. From exact candidate root, use separate venvs:

```text
RUNTIME_PYTHON -I -m pip install --no-deps -r backend/infrastructure/http/requirements.lock
RUNTIME_PYTHON -I -m pip check
RUNTIME_PYTHON -B -m backend.infrastructure.http.runtime
TEST_PYTHON -I -m pip install --no-deps -r backend/tests/v02/requirements.lock
TEST_PYTHON -I -m pip check
TEST_PYTHON -B -m unittest backend.tests.v02.test_unit backend.tests.v02.test_http backend.tests.v02.test_postgres backend.tests.v02.test_asset_regressions -v
```

Runtime requires explicit MATHSTART_DATABASE_URL, MATHSTART_HTTP_SIGNING_KEY and
MATHSTART_PUBLIC_ORIGIN; optional verifier-keyring/release-root inputs as in
[exact owner README copy](renderer-contract-owner-copy.md). Do not log real
credentials. Tests require new owned PG16 on localhost15441 with matching owner
synthetic fixture credentials. V01 uses a distinct environment/PG service55441.
Current locked R03 observer checks118/all50 PG, exact IDs, old86 inclusion and0
skips; the 63 new acceptance files are required source dependencies, including
verify_helper_sources.py and its JSON inputs. Helper fixtures reconstruct retained
bytes into owned temporary paths; no ignored developer scripts need installation.

Internal callback remains `render_page(page, context, canonical_url)`. Every
public HTML context has `pinned_release = {release_id, manifest_digest}` from the
selected Release, not a Git SHA. Only karta-sajta adds `catalogue_full` containing
complete grades/subjects/sections/topics references with names and relationships,
alongside unchanged seven filtered catalogue fields. Page and complete context
are deep copies; no active-descriptor/DB catalogue reread during callback. IDs
remain exact Python positive int64; public JSON DTOs are unchanged.

Current HOME profile requires its actual-slug alias200 with same page_id and
canonical `/`. No additional HOME aliases are authorized; redirects remain a
separate fallback mechanism. Invalid active release fails503 without using old
valid R1 or redirect to conceal invalid R2. No policy reapproval is requested.

Илья's applicable receipt should identify producer8256cbf, exact consumer SHA and
checked context/filter/canonical/alias behavior, producer/consumer pinned identity
and safe error behavior. For a JS bridge agree lossless IDs above2**53-1; this
handoff does not authorize public DTO conversion. Actual renderer/escaping/XSS,
group labels/no-JS/SSG/browser and gateway wiring stay I02/V05. The runtime smoke
uses default absent renderer503 and is not their browser evidence. V03 sessions/
CSRF and V04 activation/immutable publisher/content CLI stay their own tasks.

R03 retains workflow/control/implementation/checkout/tree, before/after live
HEAD, lock/package/case/raw command/cleanup receipts and artifact digests. All
current backend checks PASS; only explicit human review records can confer Task
Approval. No message or approval is sent on behalf of another owner here.
