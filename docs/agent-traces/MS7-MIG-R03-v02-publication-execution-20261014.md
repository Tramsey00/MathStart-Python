# MS7-MIG-R03: original V02 snapshot and external gate

User supplied the full original ZIP and explicitly authorized R03 scripts,
controls, records and a separate Linux CI run in existing PR49. V02 source,
frozen workflows, Task Approval, publication and merge remain outside this step.

Input R03 HEAD: `dfbe760b34e20cf41783f2b6ef467603f84a158c`.
Live integration ref remains `0c03197e23f69a233c0fcf8bdffa336feca20b92`.
MIG_BASE remains `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.

## Observed local results

- ZIP SHA256 matches user pin; all234 members and233 inventory rows verified.
- Prior151 records and three exact original handoff documents match. Auditor
  report digest/five control tuples/40 exception blob tuples remain independent
  prior inputs; no candidate pin regeneration.
- Isolated baseline.pack objects2092, BASE tree1672,151 additions and full1823
  entries verified. Git reconstructed approved tree
  `dbad1e853dff354c5d3255755afb5cc32e0ad279` from actual objects.
- Real byte/OID/size/mode,13/full attributes and checkout bytes PASS;73 raw kept.
- Original whitespace raw outputs reproduced exactly: full FAIL/2 twice,
  scoped PASS/0 twice. No new diagnostics in the positive snapshot.
- External exact-source verifier with real owner anchor exit0.17 real-package
  negative scenarios rejected for their expected reasons; restored positive0.
- Historical preservation checker PASS1370 files and strict manifest pins.
- First local restoration failed on Windows path length. Adding `core.longpaths`
  to the isolated R03 environment resolved it; source/pins were unchanged.
- First pure verification had Windows sandbox Temp PermissionError. Original
  failure retained; retry/result and Linux evidence will be appended below.

The package inventory now contains the corrected tree field. Older transmission
inventory/REPORT with the typo remain untouched in their historical archive.
No package script, historical synthetic anchor or auditor executable was run.

## Current review state

Concrete owner anchor records the previously approved exact40 policy, SHA256
`5a9a7a65dab43afe4e353b51523d86f3a15de2e371d19efacc8127ae6d0dbfd7`.
See [controls and commands](../../specs/migration/r03-v1/v02-publication/README.md).
Final control revision `1b75c6e58ecdcb4bb172d4df979e9b9efa7dde68`; workflow/event
revision `21a82d43cd8219338fe83bf6ff73a57c046e4297`. Actual Linux owner checkout
matches control revision; snapshot HEAD remains BASE, staged/tree is the approved
tree, implementation SHA remains null. Run38596739924 SUCCESS,17 expected negative
rejections and restored positive0. Earlier run38596554853 SUCCESS retained separately.

Ubuntu24.04.5/Python3.12.15/Git2.55.0. Downloaded raw artifact11909044256 SHA256
`f52fcb18f4a4ecd4343fcf2efe363c23ec7f856b2995f4666b3fdd3717ca3de2` matches GitHub.
Independently checked408 original members,397 evidence rows and192 command
receipts. Repository compact raw archive preserves all bytes with a digest map
to the already committed source ZIP for the single duplicate55MB stdout.
Full whitespace3887/6 remains FAIL/2 with exact original streams; both scoped0.
Frozen60 and original139 verification PASS; V02-owned paths untouched.

Workspace-Temp pure retry PASS6 groups/215 tests; original PermissionError failure
retained. Companion accepted-I01/V01 runs38596750664/38596750682 SUCCESS.
Migration run38596740077 verify/pure SUCCESS, target FAILURE at the unchanged
owner-handoff prerequisite: expected REVIEWED/all10 commands, actual
PENDING_OWNER_IMPLEMENTATIONS_AND_REVIEW/commands={}. Later target stages NOT_RUN;
PR run38596750672 also FAILURE. This is a pre-existing dependency, not a gate PASS.

Current status **READY_FOR_OWNER_REVIEW**. R03 remains INCOMPLETE; concrete anchor
and gate-readiness confirmation, V02 publication authorization and Task Approval
are separate human gates. No V02 commit/push/PR/merge or Issue closure occurred.
Current [review packet](../acceptance/MS7-MIG-R03/v02-publication-20261014/review-packet.md)
and [machine intake](../acceptance/MS7-MIG-R03/v02-publication-20261014/readiness.json)
contain raw evidence links and subsequent exact implementation-SHA verification.
