# MS7-MIG-V02 created files

All files below are NEW; no existing tracked file was modified or deleted. Ignored var runtime/venvs/intermediates are not publication artifacts.

| Path | Purpose |
| --- | --- |
| `backend/content/__init__.py` | Content read package; no writer |
| `backend/content/grades.py` | Real PK/number and signed created_at/id Grade keysets |
| `backend/content/projection.py` | Read-only SQLAlchemy delivery/catalogue/build candidate and native SEO |
| `backend/content/releases.py` | Authoritative immutable release/safe asset validation and catalogue context |
| `backend/infrastructure/http/README.md` | V02 documentation/report/human review draft |
| `backend/infrastructure/http/__init__.py` | Scoped package initialization |
| `backend/infrastructure/http/app.py` | FastAPI explicit route/method/error/staff/public adapters |
| `backend/infrastructure/http/contracts.py` | Frozen offline closed JSON schema validation |
| `backend/infrastructure/http/requirements.lock` | Task-scoped pinned dependency declaration/lock; V01/root locks preserved |
| `backend/infrastructure/http/requirements.txt` | Task-scoped pinned dependency declaration/lock; V01/root locks preserved |
| `backend/infrastructure/http/runtime.py` | Explicit read-only startup/configuration; downstream ports deny by default |
| `backend/infrastructure/http/signing.py` | Independent legacy-compatible TimestampSigner and keyring |
| `backend/infrastructure/http/transport.py` | Strict wire envelopes/raw parser/query/types/request ID |
| `backend/staff/__init__.py` | Scoped package initialization |
| `backend/staff/authorization.py` | Server-only identity and current DB flags/effective permissions |
| `backend/staff/publication.py` | Three-sample coherent read guard and V04 observer port |
| `backend/staff/reads.py` | Closed staff DTOs/search/filter/native order/signed keysets/history |
| `backend/tests/v02/__init__.py` | Scoped package initialization |
| `backend/tests/v02/baseline.py` | Safe new disposable Django smoke/full verification driver |
| `backend/tests/v02/fixtures.py` | Synthetic fixture data/release artifacts, no runtime writer |
| `backend/tests/v02/legacy_comparator.py` | Actual Django Admin/SEO/catalogue independent comparator |
| `backend/tests/v02/public_baseline_projection.py` | Full279-page/263-topic target vs actual Django read projection check |
| `backend/tests/v02/requirements.lock` | Task-scoped pinned dependency declaration/lock; V01/root locks preserved |
| `backend/tests/v02/test_http.py` | Fifteen HTTP/security assertions in explicit SQLite compatibility |
| `backend/tests/v02/test_postgres.py` | Seventeen disposable PG HTTP/parity tests; unchanged V01 guards |
| `backend/tests/v02/test_unit.py` | Nine unit/contract/negative/tokenizer/raw/observer tests |
| `docs/acceptance/MS7-MIG-V02/acceptance-draft.md` | V02 documentation/report/human review draft |
| `docs/acceptance/MS7-MIG-V02/files.md` | V02 documentation/report/human review draft |
| `docs/acceptance/MS7-MIG-V02/frozen-ownership.json` | V02 acceptance/provenance/test/route/hash evidence |
| `docs/acceptance/MS7-MIG-V02/full_content-command.txt` | Retained actual command output, safe synthetic verification |
| `docs/acceptance/MS7-MIG-V02/legacy-fresh-smoke-command.txt` | Retained actual command output, safe synthetic verification |
| `docs/acceptance/MS7-MIG-V02/legacy-version-report-command.txt` | Retained actual command output, safe synthetic verification |
| `docs/acceptance/MS7-MIG-V02/old-to-new-evidence.json` | V02 acceptance/provenance/test/route/hash evidence |
| `docs/acceptance/MS7-MIG-V02/r02-command.txt` | Retained actual command output, safe synthetic verification |
| `docs/acceptance/MS7-MIG-V02/r02a-command.txt` | Retained actual command output, safe synthetic verification |
| `docs/acceptance/MS7-MIG-V02/r03a-command.txt` | Retained actual command output, safe synthetic verification |
| `docs/acceptance/MS7-MIG-V02/report.md` | V02 documentation/report/human review draft |
| `docs/acceptance/MS7-MIG-V02/routes.json` | V02 acceptance/provenance/test/route/hash evidence |
| `docs/acceptance/MS7-MIG-V02/test-matrix.json` | V02 acceptance/provenance/test/route/hash evidence |
| `docs/acceptance/MS7-MIG-V02/v01-command.txt` | Retained actual command output, safe synthetic verification |
| `docs/acceptance/MS7-MIG-V02/v02-command.txt` | Retained actual command output, safe synthetic verification |
| `docs/acceptance/MS7-MIG-V02/verification.json` | V02 acceptance/provenance/test/route/hash evidence |
| `docs/acceptance/MS7-MIG-V02/verify-repo-command.txt` | Retained actual command output, safe synthetic verification |
| `docs/acceptance/MS7-MIG-V02/workspace-manifest.json` | V02 acceptance/provenance/test/route/hash evidence |
| `docs/agent-traces/MS7-MIG-V02.md` | Observable actions/incidents/checks and pending human gate |
| `docs/exec-plans/active/MS7-MIG-V02.md` | Scoped active execution plan and ownership/handoffs |
| `backend/tests/v02/check_evidence.py` | Read-only workspace/frozen/ownership evidence drift checker; no pin refresh |
