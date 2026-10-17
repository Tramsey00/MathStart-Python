# Independent H-BUILD-INPUTS interface review

Result: **CHANGES_REQUIRED** at commit
`2b3a60da04346ed8c747ec35c3fe751bbbb9f9cd`, tree
`e1277d318fa0eb0763f6009a541d0d949e063189`, compared with input
`24d06112bcd6abcd1abad9b052de14a0a7b49e8e`.

Scope: immutable source ingestion/component rendering, disposable bootstrap,
public index/pages/assets writer, trusted receipt verifier, and narrow CLI
handoff. Eleven added code/test/plan/trace files were read from the exact detached
candidate. Existing V02 ReleaseStore/projection, public-build/delivery/content
contracts, source themes/templates, and reviewer/package rules were read as inputs.
This is not full V04 publication/activation/recovery review or combined R04.

## Independent execution

Own disposable PostgreSQL database:
`test_ms7_mig_v01_ms7exec_review_hbuild_20261016`, on the existing synthetic
container at loopback port 55432. The V01 name/reservation comment was checked;
fresh Alembic and two bootstraps ran on this database only. PostgreSQL 16.15,
Python 3.12.14; separate `var/hbuild-env` uses accepted persistence, HTTP, and R03
verification locks, with no Django. No author environment or working database
was used for the independent execution.

Seven independently executed tests passed, zero skips, **57.518 seconds**:
five BuildTests plus complete source/asset inventory and strict source/path/JSON
negatives. Coverage includes the valid complete 279-page/263-topic/123-asset
input, immutable existing release rejection, metadata/receipt tampering,
unlisted private export, missing/corrupt assets/pages, and body-edit refusal.
See `independent-tests.log` and `independent-probes.json`.

The author's separate committed-candidate eight-case log/result was read:
8 PASS, zero skips, unittest runtime 56.650 seconds; wrapper elapsed 58.261 seconds.
That run includes the separate Django golden oracle for all 263 rendered topics.
The independent seven-case run did not rerun that legacy oracle; it remains
observed author evidence, not an independent golden claim.

## Blocking findings

| ID | Priority | Path:line | Observed defect | Contract | Reproduction / regression | Fix SHA / recheck | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HBUILD-01 | P1 | `backend/content/build.py:123` | Source/DB comparison omits grade/subject/section identity. Valid alternative hierarchy is exported under unchanged reviewed source metadata. | Package section 5 source/content identity preservation; V04 source identity/conflict semantics; content/public build contract requires coherent reviewed inputs. | In a transaction on own PG DB, topic `10-klass-naturalnye-chisla-povtorenie` changed from IDs `[6,12,61]` to coherent existing `[1,1,1]`, source bytes unchanged. Both writer and trusted receipt verifier accepted/exported `[1,1,1]`. Require regression rejecting changed grade/subject/section mapping before finalization, retaining DB/source state. | Pending | OPEN |
| HBUILD-02 | P1 | `backend/cli.py:50` and `backend/content/build.py:119` | READ ONLY retains default READ COMMITTED; delivery/index/catalogue reads can observe different committed DB editions, and accepted output contains that mixture. | Public-build `consistency`, content B02 coherent complete manifest/page/catalogue, package coherent immutable build input. | Under CLI-equivalent READ ONLY, hook only schedules a real second-connection commit after deliveries and before index: Grade 1 title changes to `REVIEW-CONCURRENT-GRADE-EDITION`. Writer/verifier accept index label from new edition while `/5-klass/` SEO description uses previous `5 класс`. Require two-connection regression proving one coherent snapshot or fail-closed refusal for CLI and direct writer consumers. | Pending | OPEN |

HBUILD-01 raw result is `independent-probes.json`; HBUILD-02 uses
`snapshot-probe.json`, including isolation, exact changed label, old metadata,
start/end and cleanup. The hierarchy mutation rolled back; the concurrent label
was restored after the probe. Temporary artifacts were removed. The exclusively
reserved review database remains for fix verification. Candidate code was not
modified and the detached code checkout is clean.

## Additional scope observations

The artifact contains four of the 29 seed-media objects. The omitted 25 have no
references in current curriculum/site_content HTML/CSS, and current static shared
CSS/JS did not reveal nested local network dependencies. The narrow public-build
contract specifies the union of per-page assets, so this fact alone is not a
finding against this handoff. Full V04 must still preserve all seed/media storage
keys and applicable direct serving/restore behavior; this interface does not
establish that broader result.

The receipt's source commit is operator-supplied. Trust is external: a consumer
must receive the separately reviewed exact receipt digest, not infer review from
the receipt's source-SHA text or accept a caller-supplied DTO trust flag. No claim
is made that the writer independently authenticates Git provenance. Source file
digests, public closed DTO schemas, exact artifact sizes/hashes, and finalized
inventory checks are present. Full release evidence must bind the reviewed source
identity and receipt digest to the actual candidate/artifact.

Initial independent setup failed on sandbox network access and then on missing
accepted schema/HTTP dependency groups; those logs are retained under `var/`.
Scoped installs from the accepted locks repaired the own environment without
installing Django. These setup failures are not passes; later tests ran after
dependency checks succeeded. Git worktree creation and synthetic Docker/PG access
used authorized owner context after sandbox restrictions; no Git safety policy,
source tree, historical acceptance, or production setting was changed.

Next: review the author's additive fix at its exact SHA and rerun the two failing
probes plus affected interface tests. Neither this candidate nor the positive
seven/eight-case suites establishes full V04 completion or human acceptance.
