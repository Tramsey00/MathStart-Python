# MS7-PREG0 correction trace

Date:2026-09-29. Artifact production and QA complete; human G0 pending.

User attachment requested correction of existing v7, not v8. Plan: docs/exec-plans/active/MS7-PREG0-correction.md. Inputs: previously delivered v7 and retained v6/source audit. No new remote audit, product edits, DB operations, commits, PR, push or deployment.

Changed: calendar now explicit target windows without effort data;31fields per future card; separate Reviewer/Task Approver/Milestone; G0–G5 people/evidence/blockers; Unified DoD;22Operational Defaults rows;52plain outcomes; clarified post-G0 closeouts. NORMAL18.12/EARLY11.12, deadline before20.12.2026 retained. All52scope/negative/dependency records preserved. Protected source sections [2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 26, 27, 28, 29] compared unchanged. Frozen6tasks retained; no new implementations. Graphify assessment unchanged.

Checks:52-node DAG,115typed references including frozen, no cycles; both roadmaps0same-owner implementation overlaps; allH/C before start andD/I before acceptance.31fields/card,32TOC anchors valid, allregistries present, noeffort expressions. PDF61pages/Word export; allpages rendered85dpi and visually reviewed, finaldeltasrechecked. Noempty pages orout-of-page characters. Machine evidence: tmp/tz-v7-preg0/verification.json.

Tooling: {"python": "3.12.14", "python_docx": "1.2.0", "reportlab": "4.4.9", "pypdf": "6.10.0"}; Microsoft Word COM + Poppler. Canonical render_docx.py failed because soffice.exe absent; safe Word fallback opened only generated DOCX read-only and quit owned instance. A temporary export-preparation encoding-name typo was fixed before final export. Visual QA caught adjacent-table header merging, repaired with separating paragraph and widths; finalPASS. Earlier render-pass outputs are intermediate and not delivered.

Runtime tests not rerun: document-only edit. PreviousPASS8/8 is historical and retains its Python3.10.11/SQLite/2PGskips limitation. git diff --stat empty; additions are output/temp/plan/trace only. No secrets introduced. Finalfourfiles in output/tz-v7-preg0-2026-09-29/. HumanG0 signatures pending; plan remains active, no architectural approval claimed.
