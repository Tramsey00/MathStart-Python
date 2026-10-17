# Target image commands

Build from this Git root. The retained root Dockerfile/compose files still serve
the historical Django development workflow. These separate targets contain the
new runtime and locked dependencies:

```text
docker build -f deploy/Dockerfile --target api -t mathstart-api:<candidate> .
docker build -f deploy/Dockerfile --target frontend-builder -t mathstart-frontend-builder:<candidate> .
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

These image build/import checks are scoped packaging evidence. The full staged
edge/proxy setup, separate reviewed release migration command, clean-clone
startup, backup/restore and release rollback rehearsal remain part of the
unified migration and are not established by an image import test.
