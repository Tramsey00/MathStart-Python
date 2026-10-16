# Independent review: frontend receipt enforcement

Result: **VERIFIED_IN_SCOPE**. **R03-INTAKE-01 is CLOSED** at exact fix
`916d16da9378a71fae6bde5cc79e7e34ed6bcd68`, tree
`3eec5974d076f2e8e4c55c2c73369a54508655e1`, compared with intake merge
`f5c05588ee68dfe21f9676a2ab79535f2a6de9c8`.

The independently read delta changes only `scripts/target_check.py`, its R03
README contract, and the new frontend-receipt regression suite among code/spec
paths. The same commit also imports historical intake evidence; this review does
not relabel that earlier evidence or treat it as a fresh run. The isolated detached
fix checkout had no tracked or untracked changes after verification. Application
code was read-only; the original review evidence was preserved.

The dispatcher now creates a unique result destination and supplies the exact
check ID for every one of the fourteen interfaces. Successful process exit always
passes through result validation. Nonobject JSON results fail validation explicitly.
This removes the frontend-only branch which previously accepted an empty success.

Independent command, using Python 3.12.14 and the existing locked no-Django review
environment, from `var/review-fix-916d16d`:

```text
review/var/review-env/Scripts/python.exe -m unittest tests.test_migration_r03_frontend_receipts tests.test_migration_r03_verification -v
```

Actual result: **26 tests PASS, zero skips, exit 0, 27.701 seconds**. The five new
tests use real child processes for all four empty-success frontend interfaces,
unique destinations/exact check IDs, malformed/empty/nonobject receipts, and failed
children which write a nominal PASS receipt. Count/type/check-ID/status/evidence
class mutations are also rejected. The existing 21 verification tests continue
to pass, retaining timeout, missing-tool, nonrecursive selection, preservation,
PostgreSQL evidence requirements, redaction, and CI-linkage coverage.

Raw output: `independent-tests.log`; exact provenance, command, versions, log hash,
and finding disposition: `review.json`. Temporary child test directories were
managed by `TemporaryDirectory`; the detached checkout and ignored diagnostic
outputs remain available for follow-up. Creating the detached checkout initially
hit sandbox denial on Git administration metadata; the authorized owner-context
retry succeeded, without changing Git safety policy or original code checkout.

This is dispatcher verification with synthetic children, not frontend runtime,
browser, publication, or PostgreSQL acceptance. **R03-INTAKE-02 remains OPEN**:
the command map is still pending/empty and the complete target pipeline requires
implementation and exact-candidate evidence. No historical human approval,
R03 task completion, main merge, or cutover is implied.
