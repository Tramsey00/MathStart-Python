# PostgreSQL development and verification

Use the current [README](../../README.md), [release runbook](../../deploy/RELEASE.md)
and [target verification](../target-runtime.md). The runtime is FastAPI/SQLAlchemy;
the canonical Compose is deploy/compose.yaml. Select new owned resources for QA,
never an existing acceptance/legacy database or volume.

The former MS6-V01 Django runbook is historical:
1a87b044e8c5a7519b0ab57e22d2a35d57b4a986:docs/runbooks/postgres-dev-test.md.
Its commands run only through the [pinned oracle](../legacy-oracle.md).
