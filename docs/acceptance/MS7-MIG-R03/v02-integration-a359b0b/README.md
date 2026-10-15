# V02 ACCEPTED_INTEGRATION — verified squash a359b0b

R03 status: **INCOMPLETE**. V02 status: **ACCEPTED_INTEGRATION**.
[Structured receipt](receipt.json) and retained GitHub API responses establish:

| Fact | Verified value |
| --- | --- |
| PR53 | Merged by VladimirFrolov777 at2026-10-15T19:42:03Z |
| Human Task Approval | [5538854677](https://github.com/Tramsey00/MathStart-Python/pull/53#pullrequestreview-5538854677), APPROVED by Tramsey00 on exact8256cbf |
| Approved implementation | `8256cbf4b38e97fc1169fea85f2d558950543be8` |
| Actual squash / new accepted input | `a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6` |
| Squash only parent / previous input | `0c03197e23f69a233c0fcf8bdffa336feca20b92` |
| Approved and merged tree | `74c3014516ec3a2110d2cfec13c8e7afb8ae5024`, exactly equal |
| Observed integration ref | ms7-mig-react-fastapi points to a359b0b |
| Issue35 | OPEN, not closed by this task |

GitHub PR metadata, Git commit objects, approved review and live integration ref
were independently fetched and compared. Local Git fetch confirms exact parent
and tree. R03 synced the already accepted input into its own branch in
`a4954ed563eb67a8c5dcbfa9c90c6880059ceb53`; this is separate from the owner's
actual squash and does not merge a PR. V02 implementation/locks/tests remain
byte-identical to the accepted tree. No original pin is automatically recalculated.

Consumer review remains **source compatibility only**, producer8256cbf and consumer
`47baaa9f79da00c9d96fd880117a0dd064dcfa46`, confirmed directly by the user and
corroborated by human review5538854677. Full I02/no-JS/SSG/runtime/browser pipeline
is **not accepted**. No independent Ilya GitHub review URL is invented.

## Evidence classes remain separate

- [Post-merge baseline38796031561](https://github.com/Tramsey00/MathStart-Python/actions/runs/38796031561): SUCCESS, actual head a359b0b, workflow `.github/workflows/migration-ci.yml`, only job116632540917 verify. Steps establish the legacy baseline, disposable PostgreSQL smoke, repository verification and R02A/R03A checks. **Not V02 task-suite evidence**.
- [Successor gate/task38784183591](https://github.com/Tramsey00/MathStart-Python/actions/runs/38784183591): existing exact8256cbf evidence,118 V02/all50 PG and34 V01/all23 PG, no skips. It was **not run on a359b0b**. Tree equivalence relates approved source to accepted squash; it does not relabel execution.
- Candidate baseline38760171595 remains8256cbf baseline-only. Original staged38596739924, published38637910883/task38642117604 at76d8eac, original controls1b75c6e/anchor5a9a, successor control0effadc/scope04a47175 and raw archive digests remain unchanged.
- Prior stale-HEAD refusals, incomplete uploads, late FAILURE/NOT_RUN and global target failures remain historical records. They are not current V02 acceptance gates.

The previous [20261012 acceptance config](../../../../specs/migration/r03-v1/accepted-integration-20261012.json)
and [pre-merge approval receipt](../v02-approval-8256cbf/README.md) remain unchanged.
Historical input8d958 and immutable MIG_BASE60b341f remain explicit provenance.

## Current guard and command intake

[Current acceptance config](../../../../specs/migration/r03-v1/accepted-integration-20261015.json)
pins a359b0b and all three human approval/merge receipts. Frontend/V01 CI checkouts
now pin a359b0b and explicitly fetch exact approved source objects, including
squashed8256cbf, independently of branch retention. Historical candidate workflows,
published/successor guards and their old tree-bound configs are unchanged.

The accepted-input guard distinguishes V02 approver Tramsey00 from merger
VladimirFrolov777. It requires live accepted ref, exact clean checkout/tree,
pinned one-parent squash ancestry, approved-tree=merge-tree, and independently
checks both local Git objects and GitHub Git commit API objects. Each prior
approved domain is checked against its own merge; current candidate/R03 domain
trees are checked against the complete newly accepted input. This admits exactly
the accepted V02 additions while rejecting any later unapproved backend delta.
All1876 non-adapter input files and frozen historical manifests are checked byte
for byte. No blanket backend-addition exemption was introduced.

The CLI/receipt checklist now marks V02 accepted, while operational
runtime-commands remains **PENDING**, with no invented commands and no REVIEWED
status. Accepted services and test locks are available; review of root adapters
and the composed target interface is separate from task acceptance.

Local supplemental checks:12 accepted-provenance negative/positive tests,
8 frontend adapter tests,11 PostgreSQL adapter tests PASS; pure verification
6 groups PASS (18/30/41/32/21/73 cases); actual detached a359b0b checkout guard
PASS,1876 preserved files. Python actually used locally is **3.10.11**, so these
results do not establish Python3.12 target acceptance. Exact argv/version/exits
and byte-preserved stdout/stderr are retained in [results](local-checks/results.json),
[raw ZIP](local-checks-raw.zip) and [member inventory](local-checks-members.json).
Adapted Linux/Python3.12 CI is now [independently reconciled](ci-results.md):
frontend38801486277 SUCCESS112+5/10 commands, actual workflow2935a86 (PR headb541bf0);
V0138801476734 SUCCESS34/all23 PG/0 skips, actual workflowb541bf0. Both actual
suite checkouts are a359b0b/tree74c30145. V01 fresh2/A/B/C,57 DBs cleaned,
22-package lock,Python3.12.15/PG16.15 and owned-service cleanup PASS.
Two initial V01 historical-backend guard refusals are retained as NOT_RUN and
resolved in the R03 accepted-input adapter; original helper/owner files unchanged.
Global R0338801476735 verify/pure PASS, target prerequisite FAIL/NOT_RUN remains
separate. No V02 suite was rerun on the squash. Original raw artifact ZIPs and
their hashes/member inventories are retained in this folder.

## Next steps and ownership

1. R03/Руслан: review adapters from accepted V02 service/locks/case inventory and
   V01 isolated schema/rehearsal environment into the strict CLI/receipt interface.
   Preserve distinct legacy comparator and no-Django target runtime environments.
2. Илья/I02: deliver accepted exact-SHA public/staff pages, SSG, SEO, asset/lifecycle
   and terminating browser/API pipeline. Руслан owns UX/integration review;
   Владимир owns API/security review. Source compatibility at47baaa9 is not this gate.
3. Владимир/V04, with Илья as consumer where applicable: deliver prescribed seven
   content CLI operations, immutable publication/manifest/journal and recovery/env
   handoff with receipts. This is the existing semantic dependency, not a new V02
   acceptance prerequisite.
4. R03: after required accepted inputs and reviewed10 backend/4 frontend commands,
   pin the exact combined input and execute full target/PG/browser/Harness pipeline;
   obtain independent Владимир/Илья R03 approvals. Do not mark R03 complete early.

Issue35 remains open; Issues34/40 remain open until final main integration.
No merge, Issue closure, draft promotion, new human approval or V02 modification
is performed by this R03 increment.
