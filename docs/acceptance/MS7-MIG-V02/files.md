# MS7-MIG-V02 current publication files

All files remain untracked task-owned files. No tracked baseline edits.
Ignored var runtimes/venvs/intermediates are excluded. Original47 snapshot and
original46-entry manifest are retained byte-for-byte under history/initial/.

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
| `backend/tests/v02/check_evidence.py` | Read-only workspace/frozen/ownership evidence drift checker; no pin refresh |
| `backend/tests/v02/fixtures.py` | Synthetic fixture data/release artifacts, no runtime writer |
| `backend/tests/v02/legacy_comparator.py` | Actual Django Admin/SEO/catalogue independent comparator |
| `backend/tests/v02/public_baseline_projection.py` | Full279-page/263-topic target vs actual Django read projection check |
| `backend/tests/v02/requirements.lock` | Task-scoped pinned dependency declaration/lock; V01/root locks preserved |
| `backend/tests/v02/test_asset_regressions.py` | 45 named F01/F02 real ASGI, PostgreSQL and Django comparator regressions |
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
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/F01-runtime.patch` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/F02-runtime.patch` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/before-fix-command.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/compile-command.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/django-http-probes.json` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/findings.json` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/frozen-ownership.json` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/full_content-command.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/content/__init__.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/content/grades.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/content/projection.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/content/releases.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/infrastructure/http/README.md` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/infrastructure/http/__init__.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/infrastructure/http/app.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/infrastructure/http/contracts.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/infrastructure/http/requirements.lock` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/infrastructure/http/requirements.txt` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/infrastructure/http/runtime.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/infrastructure/http/signing.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/infrastructure/http/transport.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/staff/__init__.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/staff/authorization.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/staff/publication.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/staff/reads.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/tests/v02/__init__.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/tests/v02/baseline.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/tests/v02/check_evidence.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/tests/v02/fixtures.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/tests/v02/legacy_comparator.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/tests/v02/public_baseline_projection.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/tests/v02/requirements.lock` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/tests/v02/test_http.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/tests/v02/test_postgres.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/backend/tests/v02/test_unit.py` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/acceptance-draft.md` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/files.md` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/frozen-ownership.json` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/full_content-command.txt` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/legacy-fresh-smoke-command.txt` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/legacy-version-report-command.txt` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/old-to-new-evidence.json` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/r02-command.txt` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/r02a-command.txt` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/r03a-command.txt` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/report.md` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/routes.json` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/test-matrix.json` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/v01-command.txt` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/v02-command.txt` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/verification.json` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/verify-repo-command.txt` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/acceptance/MS7-MIG-V02/workspace-manifest.json` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/agent-traces/MS7-MIG-V02.md` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/docs/exec-plans/active/MS7-MIG-V02.md` | Immutable byte copy of audited initial47 snapshot |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/intake.json` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/intermediate-v02-84-command.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/legacy-fresh-smoke-command.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/legacy-version-report-command.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/original-audit/Independent-Audit-Report.md` | Immutable external negative audit/source snapshot copy |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/original-audit/independent-source-snapshot.json` | Immutable external negative audit/source snapshot copy |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/r02-command.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/r02a-command.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/r03a-command.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/report.md` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/runtime-check-source.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/runtime-command.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/runtime-pip-command.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/test-matrix.json` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/test-pip-command.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/v01-command.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/v02-command.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/verification.json` | F01/F02 current remediation record, patch, actual log or verification provenance |
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/verify-repo-command.txt` | F01/F02 current remediation record, patch, actual log or verification provenance |
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
| `docs/acceptance/MS7-MIG-V02/remediation-f01-f02/scope-recheck.json` | Final observed branch, tracked/frozen/history/ownership rechecks |
