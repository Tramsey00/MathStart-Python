# Recovery rehearsal and supported rollback boundary

The repeatable test below uses only newly owned synthetic containers, databases
and volumes. It neither attaches to production nor authorizes restoring it.
Keep real backups encrypted, access controlled and outside Git; define their
retention, off-host storage, key recovery and operator ownership before release.

An installed release is a tuple: PostgreSQL schema/data/history/protocol state,
the complete mutable source media root, immutable input releases, compiled
frontend, their receipts/manifests/digests, signing verifier keys and the cutover
writer binding. A copy of compiled public files alone is insufficient. The
earlier public release included only4 directly referenced media files. The
current reviewed home delivery retains all29 public seed media URLs and hashes,
including unreferenced files. Still back up the entire mutable media root,
including retained uploads outside that reviewed seed; do not infer the complete
backup set from current HTML or the immutable asset manifest.

The physical method is intentional. Cutover provenance binds database and role
OIDs as well as the drained writer fact. A logical restore into another DB/role
does not preserve that identity and must not silently become READY. Do not
invent a new digest, change the verifier key or automatically rebind a checkpoint
to make the imported DB serve. Such a recovery needs a separately reviewed
provenance procedure. The current tested procedure preserves cluster identities.

For the tested maintenance backup:

1. Fence ingress and stop API workers, publishers and legacy writers. Disable
   and drain the sole legacy role; keep role memberships and the actual role
   snapshot. Retain the current signing/verifier keys separately in the private
   operator secret store. Never log their values or put them into public volumes.
2. In the owned PostgreSQL16 container run `pg_basebackup` as its postgres OS
   user with the selected replication-capable database role, `-X stream`,
   `--checkpoint=fast` and `--manifest-checksums=SHA256`, into a new private backup
   directory/volume. The rehearsal uses its own cluster's local socket and does
   not relax network replication authentication.
3. Run `pg_verifybackup` on that completed backup. Copy the entire immutable
   input/frontend tuple and the entire source media root. Bind full file hashes,
   retained DB input HMAC, DB/role identity and cutover digest in the private
   tuple manifest. No raw private rows/password/session values enter that
   manifest. Flush it before considering the backup complete.
4. Stop the source cluster before enabling the restored writer. Restore only
   into newly created, explicitly owned empty data/public/media volumes, using
   the same pinned PostgreSQL image. Preserve ownership and private file modes.
   Keep the backup mount read-only during restoration; never boot PostgreSQL
   directly on the only retained backup copy.
5. After WAL recovery, prove physical schema/head, every row and sequence HMAC,
   DB/role OIDs, writer/checkpoint facts, every public file hash and every media
   hash. Only then start the API against the restored volume tuple and retained
   keys. Prove exact HTML/catalogue, revoked sessions staying revoked, password
   re-login, profile/opaque session, and read-only repeated checkpoint import.
   Readiness must use the ordinary authority gateway.

The automated implementation is `scripts/image_recovery.py`, invoked only by
`scripts/verify_images.py --recovery`. It makes an actual successful registration
receipt, a pending receipt, group membership, role permissions and a cutover
checkpoint before backup. It verifies all SQL rows/sequences after recovery;
the API check then exercises the retained opaque-session and re-login boundary.
All copy roots and cleanup identities belong to this test. No operator restore
command that overwrites an arbitrary existing volume is provided.

Use a verified synthetic source runtime and frontend build with the selected
loopback origin, plus local candidate API/edge images. For HTTPS supply a private
test certificate/key with the actual loopback IP in SAN; its public certificate
is the explicitly trusted CA for this test. Both the host client and an
independent TCP client verify CA and hostname. The independent container routes
the public origin to its edge peer without changing URL/Host/SNI. It never uses
`verify=False`. A default untrusted client must reject the certificate.

```text
python scripts/verify_images.py --disposable --recovery --rollback-image mathstart-api:<prior-compatible> --runtime-root var/recovery-<run> --source-runtime var/<managed-run>/runtime --artifact-root var/<https-build>/site --api-image mathstart-api:<candidate> --edge-image mathstart-edge:<candidate> --tls-cert <private-test-cert> --tls-key <private-test-key>
```

Omit TLS flags only for an artifact whose actual origin is HTTP. The command
derives the edge port from that artifact, reserves loopback PG55442 (or explicit
`--pg-port`), creates unique labelled resources and removes only those resources.
Signing keys/passwords exist in ignored private env files for the run and are
removed in `finally`. Reports contain exact image IDs, source bindings, actual
assertion IDs, public hashes/HMACs and measurements. Never hard-kill the owner;
if interrupted, reconcile only its recorded IDs/labels before another run.

Application rollback is separate from restoring a DB snapshot. With a distinct
`--rollback-image`, the rehearsal starts that prior actual API binary on the
restored target head before new target writes. It then switches to the candidate,
logs in and proves target writes occurred, switches back to the prior API, and
checks the complete persisted account/profile DTO, session and unchanged DB
HMAC. It returns to the candidate before measuring the workload. HTTP envelopes
must preserve their exact shape/version while each request gets a fresh UUID;
the test does not compare volatile request IDs as persisted data.

This proves compatibility only for the two tested image IDs on their common
schema head. A future incompatible image/schema combination is not a safe
rollback. Before any target writes, a retained pre-cutover whole-cluster snapshot
can be considered only with both writer clusters fenced and a reviewed return
to the old application/roles. Re-enabling an old writer in a target cluster and
later reusing the old cutover checkpoint is unsupported. After target writes,
do not replace current data with an older snapshot. Keep current data/WAL and
use a proved compatible application switch or forward recovery. Applied
migrations/history, receipts and sequences must not be rewritten to appear safe.
The separate legacy-cluster return rehearsal below now covers the pre-admission
whole-cluster boundary; the image test above covers compatible target API switches.

Latest scoped local evidence is `image-recovery-result-20261018.json` under
`docs/acceptance/migration-execution/i02-verification`:449 real assertions,
828 public files and29 source media hashes, physical verification and cleanup
PASS. Backup took8.797s; restoration through authenticated readiness including
application switches took36.656s. On the local Windows/Docker Desktop setup,
80 sequential HTTPS requests,20 cycles of `/`, `/_content/index.json`,
`/api/v1/grades/`, `/api/v1/users/me/`, one authenticated keep-alive client and
two API workers measured p50=70.5ms, p95=110ms and max=1157ms after restore.
These are measured synthetic local results, not production capacity or SLO.
Previous failures and partial immutable-public-only recovery remain in evidence.
Final combined QA and human operational acceptance remain pending.

## Legacy-cluster return before target admission

```text
python scripts/verify_legacy_return.py --disposable --runtime-root var/legacy-return-<new-run> --legacy-python <separate installed Django interpreter>
```

The target interpreter must remain Django-free; Docker and unused loopback ports
55444/18135/18136 are required. This creates new labelled volumes/containers only.
It runs the actual retained Django migrations, bootstrap and collectstatic; a
real HTTP registration/onboarding creates native session/profile/success receipts.
Private group/permission/admin-history/pending fixtures are retained as well.
It stops the legacy process, disables the sole legacy LOGIN role, proves sessions
are drained, and records full schema/row/sequence HMAC plus DB/role OIDs. Physical
pg_basebackup with streamed WAL and pg_verifybackup retains the pre-cutover cluster;
all29 media and the immutable legacy static build are retained separately.

The ordinary reviewed target schema and cutover CLI then execute. Target user
traffic has not been admitted: only controlled migration/import changes exist.
The target cluster is stopped and verified fenced before copying that physical
pre-snapshot to a new owned volume. Before re-enabling any legacy LOGIN role,
the restored full private HMAC/schema/history/sequences/OIDs must equal the
recorded pre-snapshot facts. The old target cluster stays stopped. The returned
Django process must serve the same public HTML and complete profile/session and
pass an actual password login. This is the narrow point at which a pre-cutover
whole-cluster return can be considered; it is not a rollback after live writes.

If migration resumes after returning to legacy, stop/drain legacy again and
create new reviewed schema and cutover plans from its current state. The old
checkpoint must not be reused. This rehearsal performs that new adoption,
requires one F-login with the retained password/native proof, preserves the
complete profile, then makes a real target profile write. Its owned procedure
refuses the old physical snapshot after target admission and proves current
private facts remain unchanged. This guard tracks its own controlled lifecycle;
it is not a production oracle for writes made by external operators. In an
operated stack, independent ingress/writer fencing and audited admission history
remain operator responsibilities. After target writes use the compatible API
switch/forward recovery procedure, preserving current data/WAL.

Scoped result18 October2026:34 measured assertion events, backup1.313s,
physical return through authenticated Django login7.860s; source unchanged and
cleanup PASS. Receipts `i02-verification/legacy-return-02-20261018.json`; the prior
CookieConflict harness failure/cleanup PASS is retained in legacy-return-01.
Cookie jars now preserve domain/path instead of flattening duplicate scoped
names. This proves the synthetic procedure, not production configuration,
operator approval, public-domain acceptance or final combined QA.

### Ordinary API concurrent workload, 2026-10-18

The later `var/image-performance-01` rehearsal retained the complete physical
recovery and distinct compatible-image rollback checks and passed455 assertions.
It additionally measured400 real HTTPS requests at10 concurrent clients against
existing `/api/v1/grades/` and authenticated `/api/v1/users/me/` (200 each), after
20 separate warmup requests. All400 succeeded with valid DTOs/no-store;400 request
correlations were unique and observed peak concurrency was10. Overall nearest-rank
p95 was203ms; Grade32ms and profile219ms, each below the existing500ms criterion.
Failures remain in the denominator and latency distribution; no automatic retries.
The complete database, sequences and private-fact HMAC were unchanged by the load.

Scope: Windows/WSL2 Docker Desktop,12 logical CPUs,7,978,807,296 bytes memory,
PostgreSQL16.15, Python3.12.15 and two API workers through the owned HTTPS edge.
Windows clock resolution quantized individual samples; these are local disposable
measurements, not a production capacity or future AI claim. The exact runtime
images were built from3116fda, with the new host recovery controller; raw timings,
cohort sizes, package versions and source hashes are retained in
`i02-verification/ordinary-api-workload-20261018.json` and the455-check result.
The full-candidate workflow now runs this ordinary workload with physical recovery
as a required seventh technical job; syntax checking alone does not prove that job.
