# Accepted migration and consolidation

PR [54](https://github.com/Tramsey00/MathStart-Python/pull/54) was accepted and
merged as 3a290a46d991e22269a17dde41e39f0637576071 using a merge commit.
[Main Migration](https://github.com/Tramsey00/MathStart-Python/actions/runs/39276711652)
and [Harness](https://github.com/Tramsey00/MathStart-Python/actions/runs/39276711485)
completed successfully. This does not claim production deployment or completion
of future product gates.

The primary checkout and normal platform are main, FastAPI/SQLAlchemy/Alembic,
PostgreSQL and React. [Local start](local-development.md), [release](../deploy/RELEASE.md),
[recovery](../deploy/RECOVERY.md), [testing](target-runtime.md),
[oracle](legacy-oracle.md) and the complete [product specification](specifications/technical-spec-v7.2-draft.md)
are the active entry points. The future product program remains specified, not implemented.

Historical plans, traces, approvals, raw evidence and original specification PDF
are restored by exact SHA/path from the main history, primarily
3a290a46d991e22269a17dde41e39f0637576071. Old hashes/results are not rewritten.
The explicit [preservation manifest](../specs/migration/post-django-preservation.json)
records each retired or moved file; retained current content/contracts/assets
still use actual current bytes, with unknown edits/deletions rejected.
Active inventory, 40 parity rows and 12-scenario/negative mapping audit remain
in specs/migration; the complete 52-card future product disposition is in specs/product.

The consolidation maintenance PR records its actual candidate checks and diff
review separately from the accepted migration's CI. It retires exactly1477
user-approved historical originals (60,801,077 canonical blob bytes); six active
inputs/verifiers move to scripts/specs. Historical helper checks require explicit
separate sources, while current contracts/content keep actual-file assertions.
Relative documentation links now resolve locally or to verified historical blobs.

Local consolidation retired24 registered worktrees and16 old local branches
after Git/patch/unique-source checks. Unique work, private settings, verified
SQLite backups, five physically restored PostgreSQL backups and a verified Git
bundle are in the one restricted external backup recorded in var/local/README.md.
Reproducible working copies, environments and logs were not archived.
Old Docker resources were removed by exact identity; the two target data volumes
remain in use by mathstart-local. Two anonymous volumes with unconfirmed purpose
and shared base images/build cache remain untouched. Physical disk reclamation
was not measured; logical file bytes and Docker accounting are not that measure.

The persistent local site, existing operator and published content are retained;
see [local start](local-development.md). Migration Issues28–45 can be closed
against PR54, its actual review and successful main CI after scope reconciliation.
Cosmetic UX issue52 remains a deferred follow-up; production and future features
are outside this maintenance task.
