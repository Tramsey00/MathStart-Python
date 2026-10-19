# Verification

Use the current user task, contracts and docs/target-runtime.md. Work from the primary Git root.
Run affected checks first, then the mandatory coherent-candidate gate when required.
Default: python scripts/verify_repo.py; portable subset: --profile pure.
Pure, --list, missing, skipped, flaky or timed-out checks do not prove runtime readiness.
Use owned disposable databases and runtimes. Real legacy comparisons use the pinned
separate oracle from docs/legacy-oracle.md. Tie results to exact SHA/tree and preserve
actual assertions, data, content and old approvals. Never print secrets/cookies/PII.
Review the delta without duplicating successful unchanged QA.
