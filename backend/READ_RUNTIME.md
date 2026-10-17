# Target public and identity runtime (migration candidate)

The normal ASGI factory composes public releases, `frontend.rendering.PublicRenderer`,
PostgreSQL identity/session services and React account/staff forms. The explicit
`create_public_app` test factory retains its read-only default unless an identity
service is supplied. Full publication/recovery and production cutover remain
unfinished; these commands describe a disposable demonstration candidate.

Install `backend/infrastructure/http/requirements.lock` in the target environment.
For tests also install `backend/tests/v04/requirements.lock`. Neither requires
Django. The legacy golden oracle remains a separate environment.

Run from the combined repository root. Set these environment variables without
printing their values:

- `MATHSTART_DATABASE_URL`: PostgreSQL/psycopg connection to a newly created empty
  synthetic DB named `test_ms7_mig_v01_<unique suffix>`.
- `MATHSTART_DISPOSABLE=1`.
- `MATHSTART_HTTP_SIGNING_KEY`: disposable private signing key, retained for the
  synthetic session lifetime; optional JSON-array `MATHSTART_HTTP_SIGNING_FALLBACK_KEYS`.
- `MATHSTART_PUBLIC_ORIGIN`: exact HTTP origin, e.g. local port8121.

```text
python -m backend.content.synthetic_setup prepare --disposable --runtime-root var/i02-runtime --release-id i02-public-<unique suffix> --source-sha <reviewed commit>
```

The command checks the DB name and emptiness before reserving the accepted V01
marker, applies unchanged Alembic fresh migrations, bootstraps twice and compares
the preserved source edition, creates only synthetic staff/group/media/session
fixtures, then builds immutable public inputs under `var/i02-runtime/releases/`.
Its `prepare-result.json` contains release/input/receipt digests and paths.
`private-staff-cookie.json` contains a synthetic opaque cookie: keep it ignored,
do not print or attach its contents. This is a test fixture, not a login endpoint.

Build React output from those exact fresh inputs using `frontend.build_public`.
Use the exact `MATHSTART_PUBLIC_ORIGIN`; capture the trusted output manifest digest.
Then:

```text
python -m backend.content.synthetic_setup activate-initial --disposable --runtime-root var/i02-runtime --release-id <release> --receipt-digest <trusted input receipt digest> --artifact-root <new frontend output> --artifact-digest <trusted output manifest digest>
```

This one-time synthetic setup verifies the complete input/output inventory and
DB edition before installing the initial descriptor in one SQL transaction.
It refuses existing publication authority. It is not publish/retry/takeover,
does not replace an active release and is not production cutover evidence.

For the read server set:

- `MATHSTART_RELEASE_ROOT` to `var/i02-runtime/releases`.
- `MATHSTART_PUBLIC_ARTIFACT_ROOT` to the frontend output root, or a parent with
  per-release subdirectories.
- `MATHSTART_PUBLIC_ARTIFACT_DIGESTS` to the trusted JSON mapping from release ID
  to output manifest SHA256.

```text
python -m uvicorn backend.content.public_runtime:application --factory --host 127.0.0.1 --port 8121 --no-access-log --no-proxy-headers
```

Public documents/API/assets pin the authoritative DB release. Explicit native
account/staff URLs serve only the verified anonymous shell with private/no-store;
their API reads and mutations authenticate the opaque session, expiry/revocation/
auth-hash and current DB permissions. Mutations enforce CSRF and validators.
Compiled UI files check the pinned committed descriptor, trusted output manifest
and requested file hash; public content still checks the full source release.
Proxy headers are disabled until an explicit edge trust policy is implemented.
Private staff documents receive a boolean-only presentation snapshot from the
current DB permissions. It hides unavailable actions, preserves combined User
creation permissions and Content read-only controls; each API still authorizes
independently. The snapshot contains no user IDs, PII or credentials and is never
written to the public artifact. Unknown
staff URLs remain404. Generated frontend assets must be in the trusted output
manifest. Corrupt/missing files fail closed. There is no constant Node server.

The staff publication-state observer reports the immutable active release, the
committed DB edition and the durable pending operation, including takeover
eligibility and recovery. Authority is sampled around the representation;
conflicting data or corrupt artifacts fail closed. Reads never claim/renew a
publisher lease. Unpublished pages retain their DB identities and report a
null public page digest/path.

For browser tests set `MATHSTART_STAFF_COOKIE_FILE` to the ignored private cookie
file. For the focused PG session tests use the same DB/signing/cookie environment:

```text
python -m unittest backend.tests.v04.test_read_runtime -v
```

Stop the owned Uvicorn process after checks. Retain or drop only the newly named
reserved synthetic DB and its own var subtree according to the run ledger.
Root portable verification/CI owns combined lifecycle and final exact-SHA runs.

Existing content inspection commands now have target adapters:

```text
python -m backend.cli check-lesson-sources --source-root . --all
python -m backend.cli check-lesson-sources --source-root . --slug <existing lesson slug>
python -m backend.cli check-site-integrity --static-root static --media-root site_content/media --report-root var/inspection-reports
python -m backend.cli check-content-quality --origin http://127.0.0.1:8121 --report-root var/inspection-reports
```

They use the explicitly configured target DB. Lesson verification compares all
lesson metadata, HTML, CSS, JS and catalogue identities with the DB; `check-sources`
alone only validates source files. Integrity checks current DB pages, redirects,
references and registered media against the supplied storage roots. Quality
checks actual HTTP responses and uses the preserved authoring/SVG/anchor checker;
it refuses redirects and empty published inventories. It requires the running
target origin; the fixture HTTP tests are command wiring evidence, not public
rendering acceptance. Storage roots must match the actual deployment; the media
path above is for the synthetic seed.

PostgreSQL inspections use a repeatable read-only transaction. Quality/integrity
also create or replace their JSON report in the explicit report root, including
when issues produce a nonzero exit. They do not offer a misleading dry-run flag.
Missing tools, storage, source mismatch, non-200 HTTP and invalid HTML fail;
unused registered media is reported without becoming a critical error, preserving
the existing command policy. Files are confined to the configured storage roots.
These inspection adapters do not perform publication, index writes or cutover.

Identity cleanup records natural session expiry as `DETACHED`, and replay-window
expiry as `EXPIRED`, without deleting receipt identity or response. Revocation is
terminal, including auth-hash invalidation of independent sessions. Registration
replay accepts the existing bound owner session or the original bootstrap proof;
after an explicit same-owner login, that original proof may rebind a detached
receipt without issuing another session. A receipt key or owner login alone
cannot select an anonymous scope. Old-epoch concurrent rebinds fail closed.
Verified legacy cutover checkpoint/import/F-proof recovery remains unfinished;
the current identity checks do not establish production cutover readiness.

The internal `backend.content.publication.PublisherAuthority` now implements the
PostgreSQL P1 pending slot, owner/generation lease, takeover, domain-commit fact,
descriptor activation, reconciliation and acknowledgement. Its participant must
provide reviewed content/artifact staging, short DB edition checks/updates and
public probes; a fixture participant is not a production content publisher.
Staging/probes run outside row locks. Their receipts bind operation, owner, fence,
plan and release identity, and are accepted only under the same current lease.
Final conditional SQL guards use DB time and roll back flushed domain changes
on expiry. Only COMPLETE or proven FAILED_PRECOMMIT releases pending. There is
no filesystem active pointer and no cleanup of unowned paths.

`backend.content.editions` supplies exact fingerprints of the seven content
tables and guarded prepared before/after updates, preserving IDs and timestamps.
It rejects auth tables, primary-key changes, duplicate patches and stale rows;
it does not allocate IDs or delete content. These internal layers are covered
by real PostgreSQL crash/race/rollback tests. The concrete prepared content/SSG
participant and operator CLI are now integrated. Initial synthetic activation
remains a separate fixture. New source registration/ID allocation, general
bootstrap/index operations, production cutover and final publication acceptance
remain unfinished.

Prepare and publish existing sources from a reviewed Git commit:

```text
python -m backend.content.publish prepare-sources --source-root . --source-sha <full reviewed SHA> --release-id <unique release> --all --input-root var/publication-inputs --changes var/prepared-edition.json
python -m frontend.build_public --input-root var/publication-inputs --release-id <unique release> --manifest-digest <input manifest digest> --receipt-digest <input receipt digest> --output var/publication-output/<unique release> --origin http://127.0.0.1:8121
python -m backend.content.publish plan --changes var/prepared-edition.json --plan var/publication-plan.json --input-root var/publication-inputs --output-root var/publication-output/<unique release> --output-digest <trusted output manifest SHA256> --release-root var/serving/releases --artifact-root var/serving/frontend --origin http://127.0.0.1:8121
python -m backend.content.publish publish --plan var/publication-plan.json --key <stable unique operation key> --owner <stable owner UUID> --input-root var/publication-inputs --output-root var/publication-output/<unique release> --release-root var/serving/releases --artifact-root var/serving/frontend
python -m backend.content.publish status
```

The target DB must already contain its checked schema and existing content.
Source preparation reads one repeatable snapshot and preserves PK/FK/created_at.
Only changed rows get the captured updated_at; source ownership/digests refuse
runtime edits. All published sources/assets must agree with the candidate.
PostgreSQL orders a VALUES projection of the captured catalogue, retaining its
real collation without writing rows or allocating sequences. The command creates
immutable input files and an exclusive prepared-edition file; it does not claim
or activate a publication. `--dry-run` performs source/selection/conflict checks
without creating those files. New IDs/source registrations fail explicitly.

Build output is independently verified before `plan` writes its exclusive plan
file. The bound edition file rejects drift between preparation and planning.
`publish` claims the durable gate, stages in operation/owner/generation paths,
installs only absent or byte-identical files, commits domain updates once, and
switches the descriptor only after complete installed-byte verification. A lease
worker uses its own sessions while staging/probing. Actual HTTP verifies current
release identity, every public document/alias and reviewed asset, asset ETags,
sitemap/robots, redirects and removed URLs. Failed probes retain pending recovery
and return nonzero. No filesystem active pointer or Node serving process exists.

Use per-release subdirectories in the serving frontend root. Retain the initial
artifact under its release ID there as well; do not mix an old single-output
manifest with the parent directory of future releases. New output pins are read
from the matching committed/applied journal plan, including its plan digest;
rendering a previously selected release never resolves latest again. The env pin
map is retained for explicitly trusted older initial artifacts and may be `{}`
when all releases use the prepared publisher.

To unpublish an existing page, replace `--all` with `--slug <slug>` and add
`--kind unpublish` to both `prepare-sources` and `plan`; invoke `unpublish` instead
of `publish`. The next build excludes its HTML/catalogue/sitemap entry and leaves
the DB row and historical releases intact. Explicit redirects keep their usual
precedence. No cache purge success is invented; public documents revalidate at
the Python gateway and public assets use content ETags.

Recovery/control commands use the operation UUID and observed/current generation
from `status`; all errors are sanitized and nonzero:

```text
python -m backend.content.publish resume --operation-id <operation> --owner <current owner> --generation <current generation> --input-root var/publication-inputs --output-root var/publication-output/<release> --release-root var/serving/releases --artifact-root var/serving/frontend
python -m backend.content.publish recover --operation-id <operation> --owner <new recovery owner> --generation <observed expired generation> --input-root var/serving/releases --output-root var/serving/frontend/<release> --release-root var/serving/releases --artifact-root var/serving/frontend
python -m backend.content.publish renew --operation-id <operation> --owner <current owner> --generation <generation>
python -m backend.content.publish surrender --operation-id <operation> --owner <current owner> --generation <generation>
python -m backend.content.publish abort --operation-id <operation> --owner <current owner> --generation <generation> --release-root var/serving/releases
```

Takeover requires an expired/surrendered lease and the exact observed generation.
After commit, recovery always moves forward and reconciles the actual descriptor;
it never reapplies the domain patch. Before commit, abort proves the unchanged DB
and previous release even if the candidate files are lost. Lease controls and
terminal resume do not require candidate files. For recovery before successful
staging, supply the original reviewed input/output handoffs instead of the
installed roots shown above. Keep operation-owned staging paths for diagnosis;
automatic garbage collection is not implemented and no other paths are deleted.
