# Repository cleanup before PR 54 merge

Source: `1d9e4d39aa103ccc049dd9569c2354893af30a75`, branch
`ms7-mig-react-fastapi`. The checkout was clean and the remote branch and draft
PR 54 had that exact HEAD. Main remains unmerged; human acceptance is pending.
This is maintenance of the completed migration, not another implementation phase.

## Removed scope and dependency review

65 explicitly enumerated files were removed. There was no recursive deletion,
Git clean/reset, history rewrite, Docker cleanup or change to another checkout.
The [restoration index](restoration-index.json) records every removed path,
its canonical Git blob byte size and SHA256 at the source SHA; it contains no
file copies. Where Windows CRLF checkout bytes differed, `checkout_*` fields
retain those observed values too. Binary ZIP digests are identical.

- `backend/IDENTITY-WIP-CHECKPOINT.md`: deferred-work advice superseded by the
  implemented/reviewed identity and staff runtime; no executable consumer.
- `docs/archive/migration-process-20261017/`: duplicate historical instructions,
  role queues and obsolete drafts, including their old manifests. They are not
  frozen root originals or inputs of the current preservation check. Their
  provenance remains recoverable in Git, without a replacement archive.
- The preparation/backend/frontend plans named in the cleanup request: inactive
  instructions/stubs with no current verification consumer. Historical trace and
  package-import references remain historical; they resolve through the source
  SHA and restoration index instead of implying future assignments.
- Seven retired workflows and the scripts/tests below: exact fixed-candidate
  controllers for PR 50/51/53 and the former verification branch. They do not
  execute the current ordinary runtime or current combined candidate gate.
- Two historical artifact collectors beside the V02 publication/review packets:
  they only recreated historical raw ZIPs and read the retired source snapshot.
  They are retired with that snapshot; existing receipts/results are unchanged.

Actual call chains traced before deletion:

| Retired workflow | Controller/dependencies | Controls/fixtures and dedicated tests |
| --- | --- | --- |
| `frontend-ci.yml` | `frontend_ci.py` → `accepted_integration_ci.py` | `frontend-ci-pr50.json`, accepted-integration config; `test_frontend_ci.py`, `test_accepted_integration_ci.py` |
| `postgres-ci.yml` | `postgres_ci.py` → frontend/accepted helpers and `v01_ci_observer.py` | `postgres-ci-pr51.json`, accepted-integration config, old V01 case inventory; `test_postgres_ci.py` and accepted tests |
| `published-v02-ci.yml` | `published_v02_ci.py` → pinned original publication gate/intake | old owner confirmation, published-candidate config, approved controls; `test_published_v02_ci.py` |
| `v02-publication-gate.yml` | `v02_publication_gate.py` → `v02_publication_intake.py` | approved-pins/trusted-controls and source snapshot; original positive/negative replay |
| `v02-task-ci.yml` | `v02_task_ci.py` → publication/intake → `v02_task_worker.py` | source snapshot, pinned V02 and V01 locks/matrices; exact historical candidate suites |
| `v02-successor-ci.yml` | `v02_successor_gate.py` → published controller, then task controller/worker | reviewed successor config, predecessor/source snapshot; `test_v02_successor_gate.py` and published tests |
| `v02-successor-guards.yml` | successor and published guard tests | preparation-only version of the preceding chain |

The five deleted test modules exclusively tested these deleted orchestration
tools. They were selected by dependency analysis before running checks, not
removed to hide failing tests. Current runtime/backend/frontend/Harness tests,
oracles, required case sets, timeouts and registry commands are unchanged.

## Raw archives and restoration

The three raw log ZIPs have no current code/CI/test or baseline/preservation
consumer. Their summaries, complete member inventories, reconciliation receipts,
artifact digests, review packets and Git provenance remain. The retained ZIP
size/hash in each original reconciliation receipt was verified before deletion.
The source snapshot was an input only of the retired gate/task chain and the two
retired collectors; it is not an input of current target or preservation checks.

| Removed archive (under `docs/acceptance/MS7-MIG-R03/`) | Bytes | SHA256 |
| --- | ---: | --- |
| `v02-successor-review-8256cbf/task/linux-38784183591-raw.zip` | 52083573 | `bf6a66f664b67c71f30d21e3384527c453aa2d830127ead4cc24500ed3d1a010` |
| `v02-review-20261015/linux-38642117604-raw.zip` | 52055122 | `6e3bcf92dde8ba11c99b3efb3090a8e600d31c2436b97db655063dca6a6ec63a` |
| `v02-review-20261015/linux-38641371932-raw.zip` | 24499338 | `c641b95cf72a427381f8d1795fe7ce0c9c60e69697eff462f89f9fdbbdf56ca4` |
| `v02-source-snapshot-20261014.zip` | 55278004 | `57cad8b19e75bda674ce1ac9ddcf9c92a6b57daa2a3b4bd1f39e528c1a77cd0a` |

Historical packet links and `retained_zip`/dedup locations describe the original
tree, not an assertion that those raw bytes still exist in today's checkout.
They were deliberately not rewritten as new results. To recover an exact file,
use its full path from the index with
`git restore --source=1d9e4d39aa103ccc049dd9569c2354893af30a75 --worktree -- <path>`
and verify its SHA256. This command is recovery guidance, not a cleanup step.
Deletion reduces only the current tree; Git history and clone history size remain.

## Deliberately retained

| Retained material | Current consumer/reason |
| --- | --- |
| `migration-ci.yml`, `public-migration-ci.yml`, Harness `ci.yml` | ordinary latest-candidate verification, target/install/recovery and mandatory combined gate; bytes unchanged |
| `check_migration_preservation.py` | `tests/test_migration_r03_verification.py` in target/pure; preserves 1370 original files and historical manifest pins |
| `ci_provenance.py` | current migration/public jobs and R03 verification tests |
| Current backend/frontend suites and shared reference libraries/fixtures | target command map, managed suite, installation, recovery, pure and Harness checks |
| Historical configs/approved pins/controls and frozen acceptance matrices | unchanged contract/provenance records; retiring a workflow does not rewrite its approval or digest. Full historical replay requires restoring its removed tools/snapshot from Git |
| Frozen root AGENTS/PRODUCT/ARCHITECTURE/README and old frozen active plans | preserved accepted input checked by `check_migration_preservation.py`; current guidance is AGENTS.override/MIGRATION/target-runtime |
| Original product PDF, v7.2 draft/provenance, 52-card disposition | `check_product_source.py` and source reconciliation; future product scope remains future |
| Final review, exact-SHA CI receipts, 40 parity / 12 acceptance / 139 negatives | current parity ledger, mappings, audit and human acceptance evidence |
| Other historical raw evidence, including successor gate raw ZIP | outside the four evaluated archive removals; no indiscriminate archive purge |

`MIGRATION.md` now gives the completed result, evidence and pending human
acceptance. AGENTS.override and target-runtime no longer instruct a restart or
report an old full run as still pending. Frozen originals were not changed.

## Runtime preservation

The persistent local acceptance environment still serves source candidate
`1d9e4d3` from its already built images and separate named PostgreSQL/public
volumes. Its ignored `var/acceptance-1d9e4d3` directory, private envs/settings,
source volume and images were neither edited, rebuilt nor removed. No test
cleanup is applied to it. Original Django resources, all other local environments
and worktrees, parent checkout, main and production are outside the mutation scope.

## Size and verification

Size scope is Git-tracked regular files in this checkout, excluding `.git`,
ignored runtime/cache/venvs and other worktrees. Byte totals refer to the physical
current-tree file contents, not compressed Git storage.

| Current tracked tree | Files | Bytes | MiB |
| --- | ---: | ---: | ---: |
| Before cleanup | 2847 | 289670421 | 276.251 |
| After cleanup | 2784 | 104965004 | 100.102 |
| Reduction | 63 | 184705417 | 176.149 |

- `python scripts/check_migration_preservation.py`: PASS, all 1370 originals and manifest pins.
- `python docs/acceptance/migration-execution/check_product_source.py --output var/cleanup-20261019/product-source-check.json`: PASS, 233 assertions.
- `python scripts/verify_repo.py --profile pure`: PASS, six checks / 224 tests
  (18 + 30 + 41 + 32 + 30 + 73), including Harness. No skipped success is claimed.
- Cleanup dependency/delta inspection: PASS. All 65 restoration entries match
  original Git blobs. Remaining tracked Python modules parse, no imports of
  retired controllers remain, active workflow command paths and edited Markdown
  links resolve. Active workflow Git blobs/combined conditions are unchanged.
  Runtime/schema/locks/contracts/preservation manifests/historical results have
  no edits. Local inspection receipts are under ignored `var/cleanup-20261019`;
  no artificial removed-file-list test was added to the repository.
- `git diff --check`: PASS.
- Existing acceptance home: HTTP 200 with complete HTML; API and PostgreSQL
  healthy, edge still bound to 127.0.0.1:8121. Read-only observation only, with
  no restart, rebuild, login mutation, private-file edit or cleanup.
- Review scope: audited deletions, their consumers and the three edited guidance
  files. This does not replace or relabel the completed independent migration
  review, nor claim a new full local runtime/visual QA run.

The cleanup commit needs its own mandatory CI, including actual target,
image-recovery and combined SUCCESS; source-candidate CI is historical evidence
only. Exact cleanup SHA, run links and final conclusions are recorded in PR 54.
If normal paths do not start the full gate, use the existing explicit full-target
dispatch; do not change the reviewed command map or combined conditions.
The acceptance environment is left running for the user's outstanding review.
