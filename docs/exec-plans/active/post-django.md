# Remove the historical Django platform from current source

Source: 1a87b044e8c5a7519b0ab57e22d2a35d57b4a986, branch ms7-mig-react-fastapi,
draft PR54. User authorization explicitly replaces the former requirement to
retain Django files in HEAD. Scope is platform retirement/oracle isolation only;
no appearance, mathematics, schema, future product features or dependency upgrades.
Human acceptance and main merge remain pending. Protected acceptance stack,
private files, original Django DB, other worktrees/images/volumes are untouched.

## Dependency map and implementation

- Django-only: config/settings/urls/asgi/wsgi, content/users models/views/admin/
  management/migrations/tests, page/component templates, manage.py and old root
  Docker/startup. These are restored only from the pinned historical Git commit.
- Shared target code: content/quality.py -> backend/content/quality.py;
  content/ui_foundation.py -> frontend/ui_foundation.py, both exact bytes.
  Target imports and Docker COPY updated; quality is still used by API/CLI.
- Current content: curriculum/, site_content/, reviewed29 media and all static
  assets remain current actual files; authored HTML is not a Django template.
- Oracle-only probes/fixtures: A/B/C real migrations, timestamp, index, golden
  template rendering, Django admin/search/signing, discovery and legacy return.
  Historical sources/requirements/settings/templates are executed as subprocesses
  in a pristine detached clone of source1a87b044. No target Django installation.
- Root/current docs, dependencies and default verification use FastAPI/React.
  deploy/Dockerfile is canonical; root Compose includes canonical deploy Compose.
  All16 registry checks and mandatory combined assertions are retained.

The [disposition manifest](../../../specs/migration/post-django-preservation.json)
records exact removed/moved/updated paths, original sizes/SHA256 and approved
current adapter hashes. Old approvals/digests remain unchanged. Preservation
compares all retained baseline files against actual current bytes, separately
checks historical blobs, refuses unknown edits/deletions and reintroduced sources.
Protocol source assertions and R04 historical manifest now use original source;
the generic current Harness manifest validator is unchanged and remains strict.

## Verification and continuation

Completed scoped development: 73 tests PASS (32 protocols, Harness manifest,
platform negatives, actual legacy discovery/golden/search/signing and UI contract
checks). Initial pure failures reading deleted users/views.py and original R04
instructions were corrected without changing assertions/expected digests.
Oracle preparation exercised Windows ownership separation and long-path handling;
the separate local checkout is pinned/pristine. No acceptance Docker operation.

Additional scoped checks PASS: 57 quality/contracts/adapters; all181 frontend
unit tests (20 files, zero skipped); pure six checks PASS (232 cases). Changed
Python parses, relative links resolve, diff check passes. Git diff confirms
curriculum/site_content/static/React UI/CSS/e2e, old manifests and registry unchanged.
Local PostgreSQL rehearsal could not start: Docker Linux daemon pipe unavailable;
no container was created. This is NOT a PostgreSQL/installation PASS and no
acceptance resource was inspected, stopped or rebuilt. Use real CI services.

Checkpoint9c8d936 CI: Harness39258254322 SUCCESS; main39258254154 passed verify,
pure, readiness, deployment-images and release-operations (including genuine
independent clean clone and physical legacy return), but backend-install and
target failed RuntimeError. Their bounded stdout lost the eventual failing case;
safe failure-case receipt diagnostics were added without reducing assertions.
Oracle now supplies its ignored var/ used by historical asset temporary probes;
this suspected backend cause still requires the real PostgreSQL rerun.
Public39258254217 failed at actual frontend-typecheck: generate-api read the
authorized changed test_r02a_contract.py as a frozen HEAD pin. Its source read
now follows explicit dispositions while separately checking current adapters;
old expected digests remain untouched. Actual typecheck/generation PASS(4),
three new JS preservation negatives PASS, four safe diagnostic tests PASS.

[One limited independent review](../../acceptance/migration-execution/review/post-django-20261019.md)
completed; its Compose identity and resolution-override findings were corrected.
Client-only config confirms root/canonical equivalence for all four services.
New mandatory CI after these fixes must establish target/backend/public/recovery/
combined success on that candidate; old successes remain evidence only for9c.
No successful jobs were rerun on9c, and no human acceptance/merge/production done.
