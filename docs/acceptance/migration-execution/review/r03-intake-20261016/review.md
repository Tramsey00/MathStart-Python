# Independent R03 continuation intake

Result: **VERIFIED_WITH_LIMITATIONS** for controlled intake as an explicitly
**INCOMPLETE** continuation. This is not R03 task acceptance, target acceptance,
R04 acceptance, a historical human approval, or approval to merge main/cut over.

Reviewed commit: `fb39647beb983a4f488ad82d4984d3f96e87b9a8`.
Actual tree: `08f0181373b2bc3458bf1c6bc012117d36f254fd`.
Accepted comparison input: `a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6`.
Code checkout: `C:/Projects/MathStart-Python/migration-execution/review`, detached.
Application code remained read-only. Dirty paths at review were the untracked
review evidence directory only; local environment/probe outputs are ignored `var/`.
Reviewer is a separate execution context from the implementation coordinator.

Authority: activated migration package, ADR-0006, R02 frozen contracts,
R03 README/command registry/checklist, verification skill, and reviewer profile.
The new execution process allows verified candidates and independent technical
review to support continuation; historical approvals remain scoped to their
recorded commits. No old personal approval fields were synthesized.

## Preservation and checks

| Observation | Result | Raw evidence |
| --- | --- | --- |
| Python 3.12.14, locked R03 tooling, pip dependency check | PASS | `pip-freeze.log`, `pip-check.log` |
| Django and DRF absent from independent environment | PASS | `no-django.log`, `recheck-provenance.json` |
| Pure six-check profile: 18 + 30 + 41 + 32 + 21 + 73 = 215 tests | PASS, zero skips, exit 0 | `pure-locked.log`, `pure-locked-exit.txt` |
| Additional frontend/PostgreSQL/accepted-input/published/successor guard suites | PASS, 61 tests, zero skips, exit 0 | `guard-suites.log`, `guard-suites-exit.txt` |
| Original R02 preservation guard | PASS, 1,370 files outside explicit adapter allowlist | `preservation.log` |
| Additional accepted a359b0b preservation | PASS, 1,876 files outside same allowlist | `recheck-provenance.json` |
| Accepted backend/frontend/content/users/curriculum/site_content/R02 and R01/R02 acceptance scope diff | Empty | `recheck-provenance.json` |
| Missing system handoff | Correct nonzero exit 1 | `system-missing-handoff.log`, `system-missing-handoff-exit.txt` |
| Empty successful frontend child, real subprocess with only command resolution patched | Defect reproduced: exit 0 without receipt/cases | `independent-probes.json`, `recheck-provenance.json` |

Initial `pure.log`/`pure-exit.txt` retain the missing-tooling failure; installed
accepted tooling repaired the disposable environment before `pure-locked.log`.
Neither the original failure nor later passing evidence was overwritten.
The additional probe was rerun during this review resumption; previous complete
suite logs were read and retained, rather than claiming a second suite execution.

## Findings and required continuation work

| ID | Priority | Path/line | Observed defect | Contract and reproduction | Required regression | Fix SHA | Recheck | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R03-INTAKE-01 | P1 | `scripts/target_check.py:101` and `:119` | Only backend checks receive and validate `MATHSTART_CHECK_RESULT`; all four frontend commands can pass solely from process exit 0. | MIGRATION_VERIFICATION section 2 requires each of 14 interfaces to supply nonempty structured results and positive/negative evidence. Patching only command resolution to an actual `python -c pass` subprocess returns 0 for frontend-e2e without receipt/cases. | Each frontend interface rejects missing, empty, malformed, wrong-ID, skipped, or nonpassing receipt; accepts meaningful independently reviewed result. Keep real child exit and timeout failures. | Pending | Reproduced twice | OPEN; required before full R03 acceptance |
| R03-INTAKE-02 | P1 completion gap | `specs/migration/r03-v1/runtime-commands.json:6` | Command map is empty and explicitly pending. | Target correctly fails at absent system handoff. No complete backend startup/content/fresh/upgrade pipeline is present in this intake. | Ten executable backend interfaces plus four reviewed frontend interfaces, real side effects/cleanup, complete target/fresh/upgrades and final CI at actual reviewed SHA. | Pending | Correct fail-closed behavior observed | OPEN; expected continuation work, not an intake prohibition |

The default verification profile remains legacy and the final migration package
requires a reviewed switch/aligned entry points. Current target CI setup installs
only Chromium; this does not establish the later Chrome/Edge/Firefox matrix.
These are explicit completion conditions, not evidence that historical accepted
V01/V02/I01 scopes should be reopened or that pure success proves runtime parity.

## Provenance correction and limits

The coordinator's initially supplied tree `46ac5f...` is not the reviewed HEAD
tree. An unquoted PowerShell `HEAD^{tree}` command produced extra encoded-command
arguments and an ambiguity error. Literal Python subprocess argv and
`git log -1 --format='%H %T'` both verify `08f0181373b2bc3458bf1c6bc012117d36f254fd`.
The original `independent-probes.json` tree was correct; `recheck-provenance.json`
records the repeated observation and explanation.

This review reads the changed verification framework and accepted preservation
boundary, independently reproduces narrow guards, and checks retained suite logs.
It does not independently rerun PostgreSQL runtime, fresh/upgrades, publication,
browser parity, deployment/restore, or final CI. Those require subsequent exact
candidate inputs. Existing recorded CI artifacts remain historical observations,
not new executions on this review's commit. The new V03/V04/I02/I03 implementation
and the combined 40-row/AT-M01–12 R04 audit remain separate pending reviews.

Recommendation: integrate useful R03 work with provenance preserved and explicit
INCOMPLETE status, fix R03-INTAKE-01, implement remaining concrete interfaces,
then submit the changed exact candidate and real results for delta review.
