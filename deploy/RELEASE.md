# Explicit release and maintenance commands

These commands are operator tools for the target runtime. They do not grant
production approval. Rehearse on owned disposable data first. API startup never
performs DDL, seeds users/content, or adopts legacy history.

Use a candidate API/edge image built from the same checkout and locked builder
output. Keep the retained root Django Docker/Compose files as historical inputs.
Use `deploy/compose.yaml` for the target stack. It requires an explicit unique
project name, existing named PostgreSQL/public volumes, a dedicated unused IPv4
subnet and exact edge IP, and private env/plan paths. It never exposes PostgreSQL
or API to the host. Only the edge binds a specified loopback port. Do not attach
legacy and target writers to the same tables.

The PostgreSQL bootstrap env contains `POSTGRES_USER`, `POSTGRES_PASSWORD` and
`POSTGRES_DB`. The runtime env contains the configuration from
`backend/READ_RUNTIME.md`, using host `db` for its database URL. Configure a
separate target runtime role; do not use an application superuser in an operated
stack. The schema env supplies a separate `MATHSTART_SCHEMA_SIGNING_KEY` of at
least32 random characters and a migration-role `MATHSTART_DATABASE_URL`,
overriding the runtime URL only in the release service. Keys/DSNs stay outside
Git, command-line argv and logs. Keep both existing verifier keys and cutover
binding when restoring identity state.

Set these Compose interpolation variables in your local shell or a private
Compose env file; they are paths/image/volume/network identifiers, not passwords:

```text
MATHSTART_STACK
MATHSTART_API_IMAGE
MATHSTART_EDGE_IMAGE
MATHSTART_POSTGRES_ENV_FILE
MATHSTART_RUNTIME_ENV_FILE
MATHSTART_SCHEMA_ENV_FILE
MATHSTART_PLAN_DIRECTORY
MATHSTART_DATABASE_VOLUME
MATHSTART_PUBLIC_VOLUME
MATHSTART_INTERNAL_SUBNET
MATHSTART_EDGE_IP
MATHSTART_HTTP_PORT
```

The plan directory must be writable by UID10001. Serving volume paths are
`releases/<release>` and `frontend/<release>`, readable by UID10001; the API
mounts them read-only. The publisher writes through a separate explicit mount,
never through API startup. Preserve the input receipt, input/output manifests,
digest map and DB authority as one release tuple. The edge forwards all public
static/media and private requests through that authority, with no static alias
that bypasses publication fences.

Start only PostgreSQL before schema installation. Stop API, edge, all publishers
and every other database client for maintenance. For legacy adoption, disable
and drain the sole legacy writer role and remove incoming role memberships;
`NOLOGIN` alone does not drain existing sessions. Retain the pre-cutover schema,
data and role snapshot. The CLI checks the role fact, all physical baseline
objects, applied history and input data/sequence HMAC. It does not alter roles.

```text
docker compose -f deploy/compose.yaml up -d db
docker compose -f deploy/compose.yaml run --rm --no-deps release preview --profile FRESH --plan-file /plans/schema.json
```

For an existing supported legacy schema use `--profile A`, `B` or `C` plus
`--legacy-role <drained sole legacy writer>`. Preview is a read-only repeatable
snapshot. It creates a private signed plan, refuses to overwrite an existing
file, and prints its SHA256. Review the actual candidate code, baseline/profile,
database/role identity, backup/drain and plan before applying its exact digest:

```text
docker compose -f deploy/compose.yaml run --rm --no-deps release apply --plan-file /plans/schema.json --maintenance --reviewed-plan-sha256 <reviewed digest>
docker compose -f deploy/compose.yaml run --rm --no-deps release check
```

Plans expire after30 minutes and bind the code/revision bytes, DB/role OIDs,
drained legacy writer and full schema/data/sequence input. A wrong key, changed
input, unknown history, different DB/role, expired plan or other connected
database client refuses before DDL. Fresh creates the checked target chain and
auth permission metadata. A/B/C adoption preserves original Django history,
IDs, existing data and Grade epoch; it adds the target protocol chain and fills
missing profiles. Existing public disposable schema wrappers keep their guards.

An uncertain COMMIT is `SCHEMA_REFUSED_OR_UNCERTAIN`, never success. Do not retry
blindly, stamp, downgrade, rewind sequences or restore an older DB over target
writes. Keep maintenance and reconcile schema/head, retained rows, sequences,
role/cutover provenance and the before snapshot. The read-only `check` proves
physical schema compatibility only; it does not prove the result of a lost
prior COMMIT. Sequence gaps after a failed transaction are allowed.

For a fresh unused target identity database, create its first operator explicitly
before starting API/publishers. This is the retained staff/superuser capability,
not an automatic seed account. Supply credentials with non-echoing prompts:

```text
python -m backend.users.operator --maintenance
```

For automation, set private `MATHSTART_OPERATOR_USERNAME`,
`MATHSTART_OPERATOR_PASSWORD` and optional `MATHSTART_OPERATOR_EMAIL` in the
process environment and add `--from-environment`. They are not accepted as argv
values and are never printed. The command uses the retained password validators
and hasher, creates the profile, and refuses any existing user, legacy history,
session, pending receipt, cutover state or other connected client. It cannot
reset or adopt an imported user. After uncertain COMMIT, reconcile privately;
existing identity blocks replay instead of overwriting it.

After installation/adoption, complete identity import and the fenced content
publication using the documented `backend.users.cutover_cli` / `backend.content.publish`
commands and reviewed immutable inputs. The isolated pre-admission legacy-cluster return procedure now has scoped
real evidence in deploy/RECOVERY.md; operated return still requires independent
fencing/admission review. Do not mistake a compatible empty
schema for an installed site. Readiness must remain UNREADY until matching content/frontend
publication is installed and reconciled.

```text
docker compose -f deploy/compose.yaml up -d api edge
```

The edge starts when API is running and may serve503 until a matching release
is installed. It must be reachable for initial publication's actual HTTP probes;
waiting for API readiness before starting the edge would create an initial
publication dependency cycle. The ordinary authority gateway and readiness
continue to refuse an incomplete publication.

For isolated HTTPS rehearsal, Compose2.24.4+ can apply
`-f deploy/compose.tls.yaml`. Set `MATHSTART_HTTPS_PORT` and a private
`MATHSTART_TLS_DIRECTORY` containing `tls.crt` and `tls.key`, readable by UID101.
Set the actual HTTPS public origin before building the release and configuring
the API. The override replaces the HTTP port with a loopback TLS8443 listener,
supports TLS1.2/1.3, disables session tickets and mounts certificates read-only.
It trusts no forwarded header from the external client. Certificate renewal,
external ingress/firewall and production exposure require operator review.
Actual isolated HTTPS/cookie rehearsal has passed with an explicitly trusted
loopback test certificate, default-client rejection and full CA/hostname checks.
This is not evidence of public-domain deployment or certificate ownership.
See `deploy/RECOVERY.md` for the real physical backup/restore/application-switch
rehearsal and its remaining legacy-cluster return boundary.

The reproducible empty-stack check creates a unique project and labelled
volumes, runs actual container preview/apply/check, verifies no startup data
writes and UNREADY without publication, checks Nginx config, then removes its
own resources. It uses no legacy DB, existing volumes or host PostgreSQL port:

```text
python scripts/verify_deployment.py --disposable --runtime-root var/deployment-<run> --api-image mathstart-api:<candidate> --edge-image mathstart-edge:<candidate>
```

`scripts/verify_images.py` separately checks a fully installed synthetic release
and real auth through the edge. Both receipts are scoped evidence, not final
QA or human acceptance.

## Independent clean-clone rehearsal

From a target Python3.12+ environment, run this disposable check with Docker
available and unused loopback ports55443/18125 (or explicit `--pg-port`/`--port`):

```text
python scripts/verify_installation.py --disposable --runtime-root var/install-<new-run>
```

The verifier clones the committed HEAD without hardlinks, creates a new locked
Python environment, and builds API/edge/Node-builder images from that exact clean
clone. It uses the ordinary reviewed schema CLI, initial operator CLI,
`prepare-bootstrap`, real locked Node build, publication plan/publish, readiness,
network login/private admin shell and lesson-source checks. It requires initial503,
COMPLETE publication with every public HTTP assertion, zero-change repeat bootstrap,
clean clone source and cleanup. It never installs a synthetic fixture in place of
the ordinary installation path. Only new owned labelled Docker resources are used.

API and publisher share a named public volume; API mounts it read-only, publisher
read-write. The builder writes a separate immutable output. For this disposable
loopback origin only, the publisher process resolves its exact public-origin socket
to the actual edge container; URL/Host, response bytes, cache assertions and the5s
HTTP timeout remain unchanged. Real deployments use their reachable public DNS.

The c205ef1 rehearsal on18 October2026 passed:279 pages/282 public URLs/424 files,
813 real HTTP probes (maximum1.165s), normal initial operator login,263 lesson
sources, repeat preview with no changes, source guard and cleanup PASS. Receipts:
`docs/acceptance/migration-execution/i02-verification/clean-install-03-20261018.json`
and the adjacent public-probes log. This is scoped c205ef1 installation evidence,
not final combined migration QA. The preceding install-02 failure is retained;
the original bind-mount explanation remains a hypothesis rather than a proven cause.
