# Target image commands

Build from this Git root. The retained root Dockerfile/compose files still serve
the historical Django development workflow. These separate targets contain the
new runtime and locked dependencies:

```text
docker build -f deploy/Dockerfile --target api -t mathstart-api:<candidate> .
docker build -f deploy/Dockerfile --target frontend-builder -t mathstart-frontend-builder:<candidate> .
docker build -f deploy/Dockerfile --target edge -t mathstart-edge:<candidate> .
```

The base digests are the actual Python and Node images resolved during the local
build checks. Python was3.12.15, Node is24.21.0 and npm11.19.0. The API image runs
as UID10001, imports the target HTTP/publisher without Django/DRF, and has no Node.
The separate builder performs the normal locked npm install and React build.
Both images exclude local runtime credentials, browser caches, test results and
host node_modules/build directories from the build context.

Use reviewed public build inputs and an empty, explicitly owned output directory:

```text
docker run --rm --network none --mount type=bind,source=<absolute inputs>,target=/inputs,readonly --mount type=bind,source=<absolute owned output parent>,target=/output mathstart-frontend-builder:<candidate> --input-root /inputs --release-id <release> --manifest-digest <input digest> --receipt-digest <receipt digest> --output /output/site --origin <public origin>
```

The output path `site` must not already exist. UID10001 must have read access to
inputs and write access to the output parent. The builder verifies immutable
inputs, includes public HTML/head, assets and the anonymous private shell, and
emits the externally pinned output manifest. No Node server runs in the API.

The API needs an installed target schema, durable publication authority and
matching installed input/frontend trees. Keep private environment files outside
Git. Required configuration is documented in `backend/READ_RUNTIME.md`; in the
container set `MATHSTART_RELEASE_ROOT=/runtime/releases` and
`MATHSTART_PUBLIC_ARTIFACT_ROOT=/runtime/frontend`. Supply an explicit PostgreSQL
URL reachable on the selected owned container network, signing keys, public
origin and initial output-pin map (`{}` for prepared publications). Existing
legacy databases also require their reviewed cutover digest and drained writer
role. The two trees must refer to the same committed release.

```text
docker run --rm --network <owned network> --read-only --tmpfs /tmp:rw,nosuid,noexec,size=32m --env-file <private runtime env> --mount type=bind,source=<absolute releases>,target=/runtime/releases,readonly --mount type=bind,source=<absolute frontend>,target=/runtime/frontend,readonly -p 127.0.0.1:18080:8000 mathstart-api:<candidate>
```

The image starts ASGI without migrations or access logs. Proxy headers are
disabled. Its readiness command reads the ordinary local public gateway with
the configured trusted Host. Missing/broken publication, redirect,503 or an
incomplete document produces UNREADY. It adds no public health API route and
does not write to the DB or filesystem. Keep serving mounts read-only; the
separately invoked publisher owns writes to them.

The edge image runs Nginx as UID101 on8080. Run it read-only with all capabilities
dropped and a writable `/tmp` tmpfs owned by101:101. All Nginx temporary paths
are under `/tmp`. Access logs are disabled. It sends every public HTML/static/
media and private API request through the authority gateway, preserving cache
and error contracts. It overwrites forwarded client/scheme headers, clears
untrusted alternatives and disables upstream retries, including unsafe POSTs.
Use a dedicated internal network with API alias `api`, expose only the edge,
and enable Uvicorn proxy headers only for that edge's exact reserved IP. An
arbitrary client must never be able to join the trusted network.

The reproducible disposable image rehearsal requires already built local API
and edge images, the pinned PostgreSQL16 image, and retained synthetic inputs
from `scripts/verify_target.py`. It derives the loopback HTTP port from the
verified frontend output. It rejects existing output directories and occupied
ports, creates unique labelled DB/volume/networks, checks actual HTTP/auth and
independent TCP client budgets, and removes only its owned resources:

```text
python scripts/verify_images.py --disposable --runtime-root var/image-check-<run> --source-runtime var/<managed-run>/runtime --artifact-root var/<managed-run>/artifact --api-image mathstart-api:<candidate> --edge-image mathstart-edge:<candidate>
```

Run it in the Django-free target environment. `--docker <executable>` supports a
CLI outside PATH; `--pg-port` selects an unused loopback port (default55442).
The receipt binds actual image IDs and before/after source snapshots. A failed
assertion, source change or cleanup is FAIL. Private temporary env files are
removed in `finally`; do not interrupt the owning process with a hard kill.

The default edge is HTTP for an isolated local rehearsal. The separate checked
release schema CLI, Compose/TLS configuration and operator commands are in
`deploy/RELEASE.md`. The actual empty Compose/schema rehearsal passed and remains
UNREADY without publication. HTTPS/cookie, physical DB/media/frontend recovery
and compatible application switches have scoped actual evidence documented in
`deploy/RECOVERY.md`. Clean-clone installation, the complete legacy-cluster return
procedure and final combined checks remain migration work. Scoped image checks
do not establish final acceptance or authorize production deployment.
