# V01 -> R03 CI integration handoff v4

Input: `d5dc9a4e130d3901c26894aa01e30a935dac84b6`, branch `ms7-mig-v01-schema`,
PR [#51](https://github.com/Tramsey00/MathStart-Python/pull/51).
Supersedes the unapplied v3 proposal; original v3 remains unchanged as history.

The code fix restores default Django discovery with only `requirements.lock`.
No workflow change or target dependency installation is required to repair
the historical `Verify repository` failure. The new package discovery boundary
loads two dependency-independent regressions and retains all legacy tests.

Independent target coverage still needs an explicit CI step. The adjacent
[proposal](r03-ci-handoff-v4.patch) leaves root dependency installation unchanged,
adds the reserved localhost55441 service mapping, creates a separate venv with
the complete `backend/requirements-test.lock`, runs pip check, and invokes the
three target modules explicitly. It proposes this for both existing workflows:
root CI covers PRs to main (including PR51); migration CI covers the integration
branch. No trigger changes, secrets or production services are proposed.

Only the target step gets `MATHSTART_V01_TEST_ADMIN_URL`, using existing
synthetic CI credentials. All23 PostgreSQL tests must run without skips; the
expected collection is34 (11 unit +23 PG). Fixtures reject unreserved endpoints
and create/remove new marked databases. F1/F2 diagnostics go to a new ignored
run directory so historical evidence is retained. Legacy Verify repository
continues in the root-lock interpreter, with no SQLAlchemy/Alembic installation.

The patch is **PROPOSED / NOT APPLIED**. Руслан/R03 must review and integrate
the separate target job/steps and obtain a real green GitHub Actions run before
CI acceptance. A local applicability check is not a Linux/CI result:

```text
git apply --check --ignore-space-change docs/acceptance/MS7-MIG-V01/r03-ci-handoff-v4.patch
```
