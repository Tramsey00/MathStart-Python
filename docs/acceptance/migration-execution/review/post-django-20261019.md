# Limited independent post-Django review

One independent reviewer examined source `1a87b044e8c5a7519b0ab57e22d2a35d57b4a986`
to checkpoint `9c8d93698b1407696c4198479b1b6bbcf9e5e97c`, then only the resolution
delta. Scope: deletions, shared-code extraction, oracle isolation, preservation.
This is technical review, not human acceptance or production/merge approval.

The reviewer confirmed byte-identical quality/UI helper moves; unchanged
authored content/static/schema/contracts/React runtime; no target Django/DRF
dependency closure; real golden/auth/session/upgrade/legacy-return subprocesses
from a literal pinned checkout; current retained-byte checks plus historical
provenance without rewriting old digests. Independent preservation PASS:
1270 retained original files,119 explicit dispositions,100 baseline dispositions.

## Findings and resolution

P2: root Compose include did not inherit the canonical project's name. Added
the same required MATHSTART_STACK name to root. Real client-only Compose config
comparison with synthetic empty env files and tools profile PASS: both project
names, services(api/db/edge/release), networks and volumes identical. No daemon,
container, acceptance runtime/private setting or database was used.

During resolution review the reviewer caught a P2 in the added CI assertion:
the canonical POSIX group_add override must not be merged into the parent
include model, where it conflicts with imported release. The assertion now
compares base configurations without that override; actual release operations
continue to use the existing canonical override. Full deployment CI must confirm
the Linux lifecycle; no local daemon-based PASS is claimed.

The same reviewer checked the subsequent preservation adapter for the actual
frontend generator failure: original Git hashes remain original; explicit
updated adapters require current HEAD and working bytes at their recorded hash,
while retained contracts use actual current HEAD/working files. Removed/moved
paths and shared destination hashes stay checked. No additional P1/P2 found.

Safe backend failure diagnostics retain case identities, excluding exception
messages/subtest parameter values; four unit tests PASS. Three new JS negative
tests PASS and actual frontend typecheck/generation PASS(4 measured assertions).
Oracle ignored var/ creation supports the historical temporary asset probe;
full real PostgreSQL suites still determine its runtime result.

No reviewer edits or full-QA reruns. The main executor applied the findings and
tested affected areas. Mandatory candidate CI is recorded in PR54 and MIGRATION;
this document does not substitute its results.
