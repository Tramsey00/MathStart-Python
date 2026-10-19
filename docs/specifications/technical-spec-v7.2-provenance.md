# Product v7.2 provenance

The complete current [v7.2 specification](technical-spec-v7.2-draft.md) retains
all32 chapters,52 canonical cards,115 typed dependencies and47 planned future
product equivalents. Product draft approval remains separate. Migration of the
existing site was accepted in PR54; main3a290a46d991e22269a17dde41e39f0637576071
passed mandatory CI. Consolidation PR55 merged as
12450dfd39b51166aa5a40955ce78e40169a1cb4 with successful post-merge CI.
The user accepted the platform adaptation of v7.2, not the whole product draft,
future gates or production rollout. See [maintenance](../maintenance.md).

| Input | SHA256 |
| --- | --- |
| Current complete v7.2 | `1160bcdd0d690e968273aa0de48c50227bd6a87eb2c048fb569cb694654ee7dc` |
| [Current52-card source registry](../../specs/product/task-dispositions-v7.2.json) | `dc25307bfb1b7f143ff565b1bb474e8a74faef3b2dfaa88f9d889f80ba404c0e` |
| Historical114-page v7.1 PDF | `e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd` |
| Historical v7.2 before status-only introduction update | `c6be84b2932f1e79821c11f18fd5fa1463507793ace30ecbc47804d45478c6f8` |

Historical inputs are read from literal main3a290a46d991e22269a17dde41e39f0637576071,
paths docs/specifications/sources/technical-spec-v7.1.pdf and
 docs/acceptance/migration-execution/product-source-audit.json. The explicit
preservation manifest checks original bytes/size/SHA256; no old digest is refreshed.
The prior consolidated v7.2 at Git12450dfd39b51166aa5a40955ce78e40169a1cb4
had SHA256 `aac2ba4f43a3c20b6315d38400263e7f4d1160ebba9866d417465e57d6de3cde`. This guidance-only revision updates completion/status
paragraphs in chapters1/2/17/20/32 and the current registry/source pointers;
it removes obsolete execution assignments. All32 chapters, future requirements,
card bodies, historical approvals, numerical values and dependency edges remain
preserved. Historical source digests above are unchanged.

The233-assertion source reconciliation still checks PDF SHA256,32 chapters,
52 IDs and complete card-excerpt hashes, all115 typed edges (HARD60/CONTRACT24/
HANDOFF6/INTEGRATION25), historical result/acceptance/disposition objects against
953fe979742784a196efab203ab987c0cfefd3b3, and68 glyph-position-only corrections.
The47 future equivalents remain PLANNED without invented runtime evidence.
The geometric source audit and old approvals are historical evidence; they do
not replace actual current specification/registry or runtime verification.

```powershell
python scripts/check_product_source.py
```

Full Git history is required. The checker reads the actual current v7.2 and
registry, and obtains only explicitly retired PDF/audit inputs from pinned Git.
See [maintenance](../maintenance.md), [runtime/testing](../target-runtime.md),
[release](../../deploy/RELEASE.md) and [recovery](../../deploy/RECOVERY.md).
