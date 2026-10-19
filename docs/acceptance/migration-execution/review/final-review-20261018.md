# Independent technical migration review

Status: **REVIEWED — no unresolved actionable technical findings**.
Reviewer: independent `migration_review` agent, one reviewer for the unified task.
This is technical candidate/command review, not human Task Approval or deployment approval.

- Base: `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
- Reviewed HEAD: `8612d84a7d968115475ba7ce1e2009f2600746f8`.
- Runtime: `42f6249d7b49f4a5ee44eaa1ee7353f50141abdb`; subsequent commits contain docs/evidence.
- Also inspected the narrow working-tree correction to `docs/target-runtime.md`.
- Full CI39157581728 and public CI39157536179 succeeded at the runtime SHA before review.

The reviewer traced schema/adoption/sequence handling; session/CSRF/password
adapters, receipts and cutover barriers; staff authorization, combined create
permissions, mutation serialization and guarded deletion; immutable artifact
verification, publication participant, lease fencing and recovery; public/private
serving, integer transport and frontend mutations; and launch/install/recovery
paths. Current MIGRATION.md and adjacent contracts were used. Historical personal
queues and cosmetic preferences were not revived as blockers.

## Finding and resolution

**P3, resolved:** `docs/target-runtime.md:164` still described four of29 media in
the current manifest. The corrected paragraph states that all29 reviewed media,
including files without direct HTML links, are retained. Backup must cover the
entire mutable media root, including files outside the reviewed seed. The reviewer
inspected the correction. The previous backup instruction already required all29;
this was stale prose, not an observed runtime data-loss defect.

No unresolved correctness, data-preservation, security or reproducible-launch
blocker was identified within the review scope.

## Command-contract decision

All ten backend handoffs are complete semantic checks: actual routes/security;
physical PostgreSQL/Alembic equivalence; full source/filesystem/HTTP inventories;
isolated marked-database suites; two real fresh installations with React artifacts
and bootstrap preservation; and populated A/B/C CLI upgrades with retained data,
history, epoch and sequences. The four frontend interfaces invoke actual type,
unit, immutable build and browser checks. Wrappers reject missing, invalid, empty,
skipped, failing, flaky or incomplete-project receipts and fail closed on timeout.

The reviewer explicitly approved changing `runtime-commands.json` technical status
to `REVIEWED` after recording this review. Normal mandatory target/combined CI must
then pass with this state. It must not be inferred from an ordinary skipped job.

The transitional legacy default is not a technical release blocker: current
MIGRATION.md requires explicit target verification, while target itself excludes
Django/DRF and keeps the legacy oracle separate. Default switching at final cutover
requires reviewed operational intake. This review does not authorize cutover.

## Independent checks and limits

- Frozen accepted-input preservation: PASS1370 files.
- All40 ledger `source_row` objects equal the frozen matrix.
- All12 acceptance scenarios and139 named negatives retained.
- Backend test references resolve, including inherited PostgreSQL assertions.

The reviewer did not repeat whole QA, manually inspect every frozen content byte,
or perform new cosmetic/visual research. The parent separately verified the full
artifact SHA/provenance, source/cleanup guards and exact executed IDs:320 backend,
181 frontend unit,1269 browser across all9 projects with zero skips. The mapping
audit resolves251 backend,378 browser,49 frontend unit,15 pure and109 document
references with no missing IDs. Current pure CI has224 successful cases; all151
previously indexed pure IDs are now linked to current execution. These parent
checks remain separate from the independent review.

Human acceptance, source-spec approval, default/operated cutover, main merge,
Issue closure and production deployment remain separate decisions.
