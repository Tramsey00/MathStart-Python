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

After installation/adoption, complete identity import and the fenced content
publication using the documented `backend.users.cutover_cli` / `backend.content.publish`
commands and reviewed immutable inputs. Provisioning the first fresh operator,
clean-clone release installation and full cutover/backup/rollback runbooks are
still pending migration work. Do not mistake a compatible empty schema for an
installed site. Readiness must remain UNREADY until matching content/frontend
publication is installed and reconciled.

```text
docker compose -f deploy/compose.yaml up -d api edge
```

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
