# TRACE MS7-MIG-R03: PR50 frontend CI follow-up

- Date: 2026-10-11 Europe/Moscow; owner Ruslan / Tramsey00.
- Request: add and execute a separate locked frontend job for PR50 candidate
  `150279e6ca7f1c82a6f23d8899e50992cf358f55`; record separate head/checkout SHA,
  raw results/run; preserve historical captures/frozen baseline; no I01 acceptance.
- Issue30; PR49 owns R03 delivery; PR50 is the independently reviewed consumer.
- Starting R03 SHA379411422d7ec7096dd03c98730f3fb52d77ec6a, clean worktree;
  accepted integration8d958ae; immutable MIG_BASE60b341f.
- Human gate: I01 hover and Ruslan UX/integration approval remain pending.

## Inspection and changes

Read updated AGENTS, PRODUCT/ARCHITECTURE, ADR0001/0006, migration R03/I01,
R02 frozen contract pins, R03 and I01 active plans, README/content architecture,
verification skill, workflows, generator/validator/build/verification scripts
and relevant tests. Fresh fetch confirmed PR50 head150279e6, base8d958ae,
observed merge-refbc2063a0; live review5483318464 is Vladimir approval on150279e6
and owner comment6110165810 closes publication corrections without I01 approval.

Original checkout retains user-modified AGENTS and untracked recovery/output/tmp.
Reuse existing R03 worktree/branch; create a detached candidate test checkout
under tmp/ms7-mig-r03/frontend-candidate. No I01 branch modification.
Added separate frontend workflow, fixed candidate pins, stdlib evidence adapter,
eight negative regression tests and scoped handoff. Updated own active R03 plan.
No baseline workflow edit, historical recorder, source/lock/frontend edit, DB
write, other task, deployment, merge or Issue closure.

## Verification and publication

Local interpreter/tooling and exact observable results are appended after checks.
The old R03 Python3.12 venv no longer starts: its referenced interpreter is absent;
`py -0p` reports no installed Pythons. Current PATH Node24.19.0/npm11.17.0
differs from candidate pins. These observations are environment limitations,
not execution or PASS of the requested pinned frontend suite. A bundled Python
may verify the stdlib adapter locally; CI explicitly sets Python3.12 and pinned
Node24.21.0/npm11.19.0. Current pinned suite results require actual CI execution.

Raw CI evidence is uploaded under a new artifact with run ID/attempt. Final
workflow SHA, separate candidate checkout SHA and run URL are external
exact-commit PR49 records; PR50 HEAD/approval/captures remain unchanged.
No current implementation acceptance or inherited approval is claimed.

Local stdlib verification used bundled Python3.12.14 (outside the missing old
venv): eight adapter negative tests PASS. Initial candidate Git snapshot hit
sandbox safe.directory ownership rejection; repeated read-only verification
under the normal repository owner passed without changing global Git config.
Snapshot confirmed clean150279e6/treea8b1b645,84 historical captures and both
baseline workflow blobs equal accepted input. R03 preservation check1370/1370
PASS; frozen pins unchanged, both existing R03 workflows have zero diff.
The adapter also accepted the already published owner raw clean report as112+5,
ten successful commands; this checks parsing, not re-execution or new CI evidence.
Local git diff whitespace check PASS. Pinned frontend execution is still pending
the new workflow run at publication, never claimed from current PATH tooling.
