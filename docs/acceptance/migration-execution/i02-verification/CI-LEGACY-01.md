# CI-LEGACY-01 — fixed public candidate verified

Independent review of public GitHub Actions run38951840140, push event and actual
checkout b8a93821eccf37eebaebe744460a9f9c6b002cc2, tree
c9310049bbf0b8c4e5204ee926497a0d4ccb64b9.

The run completed FAILURE. Dependency locks, provenance, browser installation
and real lifecycle regressions passed. The combined driver passed prepare,
frontend typecheck/unit/build and initial activation, then failed its28-test
source/read stage:27 PASS,1 ERROR,0 skips,28.147s. No browser matrix ran in CI.

The failing case is test_legacy_template_golden_all_lessons. Its actual child
command in the preserved traceback is
/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3.12 -m backend.tests.v04.golden_oracle,
which is the base interpreter, not var/public-legacy-env/bin/python. The child
stderr is captured by the test and not included in that traceback, so a specific
missing-module exception has not been directly observed.

The source cause is nevertheless concrete: Path.resolve dereferences normal
POSIX virtualenv interpreter symlinks, changing interpreter identity. At the
tested commit scripts/verify_public_block.py:104 and167 resolve the supplied
legacy executable before exporting/calling it. frontend/legacy_comparator.py:56
and58 resolve it again for the actual Django probe and server. This escapes the
separately installed legacy environment. The target/base interpreter correctly
has no Django; installing Django into it would violate the environment boundary.

Required fix: preserve the absolute executable path without resolving its final
symlink in both driver and comparator. Cover a real symlink-based virtualenv;
the invoked executable must retain its venv identity. Keep every golden/browser
assertion and the separate target no-Django check. Review a new immutable SHA
and run the public CI again. Windows local success does not establish the POSIX
symlink case because its virtualenv executable layout differs.

Raw evidence retained in this directory:

- Timestamped public REST run/job responses and summaries. Public log download
  initially returned403; that limitation was retained and subsequently overcome
  by the authenticated GitHub connector.
- Authenticated public-job-117144876332.log and
  generalized-target-job-117144879640.log.
- public-block-38951840140-1.zip, downloaded through the authorized connector;
  published/independently checked SHA256
  011471a5a3729169bd4e956caa33d44d2b7c14837c2dcb6c820f9f25110a56da.
- Extracted artifact-source-render-and-read-runtime.log, artifact-result.json,
  artifact-public-provenance.json and artifact-prepare-result.json. Only selected
  named files were read from the ZIP; arbitrary archive paths were not extracted.

Generalized run38951840175 at the same push/checkout completed FAILURE:
pure SUCCESS, verify SUCCESS, target failed the unchanged runtime-command
handoff prerequisite assertion; later target checks were skipped. This is the
existing incomplete full R03 command-map scope, not a new green target result or
authorization to weaken the prerequisite. The commit-workflow connector returns
only PR-triggered runs, explaining its empty list for these push-triggered runs.

Neither run needs unchanged-state polling now that both are terminal. Follow
the next actual run after the owner fixes the defect. The local authoritative
Windows matrix is a distinct run and was not stopped or modified by this review.

## Continuation 2026-10-17

Public push CI [39022103101](https://github.com/Tramsey00/MathStart-Python/actions/runs/39022103101) completed SUCCESS at exact checkout `360e75bdbad6d199a037ebeb0a9c79ade7ed74dd`. This run executes the retained real POSIX invocation regression, separate target/legacy environments, golden stage and the 14-case I02 Chrome scope. General workflow [39022103093](https://github.com/Tramsey00/MathStart-Python/actions/runs/39022103093) completed SUCCESS with the full target job gated PENDING by its still-empty command map. Neither workflow is full migration acceptance. Later identity/staff changes require their own candidate evidence.
