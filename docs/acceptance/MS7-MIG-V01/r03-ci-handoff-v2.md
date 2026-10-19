# V01 -> R03 owner handoff v2: dependencies and explicit target PG verification

Owner for root CI/verification: Руслан. This task did not edit root workflows,
README, root locks, verification skill or scripts. The adjacent
[proposed exact CI diff](r03-ci-handoff-v2.patch) is for owner review/application;
it is not a CI run, approval or permission to create a PR.

## Concrete integration requirement

The unchanged root lock does not install SQLAlchemy/Alembic. Django's default
test discovery finds the new backend unit modules, so a root-lock-only CI job
would fail their import. Install the reviewed `backend/requirements.lock` alongside
the root baseline lock. The isolated local test environment has both and pip
check/verify_repo pass; the separate target-only venv has no Django and passes
fresh twice/A/B/C CLI checks.

Add the explicit target test command to the owning migration workflow. Baseline
verify_repo intentionally runs without the target admin URL: its 129-test suite
has 11 explicit target-PG skips, while the separate V01 invocation runs all 22
target methods with zero skips. Do not treat those baseline skips as target proof.
The proposed patch uses a step-scoped administration URL and an additional
localhost55441 mapping on the existing disposable CI PostgreSQL service, retaining
the old5432 baseline path. V01 test fixtures derive administrator user/password
from that URL and keep their new UUID database naming/marker/cleanup guards.

## Scope and limits of the patch

The exact diff adds backend runtime dependencies in `ci.yml` and
`migration-ci.yml`, and the reserved service port/explicit V01 command only in
the migration workflow. Its password is the workflow's existing synthetic
disposable CI value, not a production credential. Linux execution and CI status
are **NOT VERIFIED** locally; only Python3.12.10/Windows/PostgreSQL16.15 results
are claimed. R03 may adapt its final pipeline while preserving the explicit
target check and safe disposable environment. No target claim is inferred from
previous baseline CI or from the existence of this patch.

The patch uses LF repository format. Against the current checkout's CRLF
workflow bytes, plain `git apply --check` reported context mismatch; the read-only
`git apply --check --ignore-space-change r03-ci-handoff-v2.patch` succeeded.
No workflow patch was applied and no whitespace conversion was made to root files.
