# React frontend

Current runtime: React/TypeScript, immutable public SSG and authenticated
account/staff forms served through the FastAPI publication gateway. The primary
checkout is the root; each task uses its own branch from current main. Node runs at build/development time; API/edge do
not run a Node server. No future product domains are implemented by this frontend.

## Existing locked tooling

Use the existing Node24.21.0/npm11.19.0 configuration and package-lock.json.
Do not regenerate locks to complete maintenance.

```powershell
npm --prefix frontend ci
npm --prefix frontend run typecheck
npm --prefix frontend test
npm --prefix frontend run build
```

API generation keeps canonical OpenAPI/DTO and old expected manifest digests.
Only explicitly retired historical pins are read from their exact Git commits;
retained contracts and reviewed current adapters still check actual current
HEAD/working bytes. Full Git history is required for verification.

The normal published site is built using `python -m frontend.build_public`
with exact immutable input/receipt digests, release ID, output directory and
public origin from the [release runbook](../deploy/RELEASE.md). A generic Vite
build or development server is not an installed public release.

For the prepared persistent local site use [local start](../docs/local-development.md).
Account/staff APIs enforce session, CSRF, permissions and mutation contracts;
React visibility is not authorization. Only anonymous shells are public artifacts.

## Verification

Type/unit checks are scoped evidence. The complete managed target runs actual
Chrome/Edge/Firefox at360/768/1440 and retains functional, mathematical,
accessibility, authorization and security assertions. It rejects missing,
skipped, flaky or incomplete-project receipts. See [target verification](../docs/target-runtime.md).
No new pixel-perfect/spacing criteria are introduced in maintenance.

`verify:foundation` creates a new ignored verification-run receipt, preserving
source/checkout provenance and refusing overwritten or historical evidence paths.
Old checkpoint recorders require their original pinned task checkout/branch and
are historical audit tools, not current verification entry points. Their original
sources and captured approvals are recoverable at Git3a290a46d991e22269a17dde41e39f0637576071.
