# TRACE VISUAL-PROMPT-20261005: Word defect analysis and scoped Codex prompt

- Date: 2026-10-05
- Owner: user
- Agent/surface: Codex desktop, local Windows
- Related issue/spec: user's request to prepare a prompt from `ошибки mathstart.docx`; no implementation spec introduced
- Related exec plan: none for this preparatory audit; implementation plan required by the generated prompt
- Related ADR: accepted ADR-0001-preserve-django
- PR/commit: no new PR or commit
- Human review status: Pending review of prompt artifacts; lesson repair not performed

## Task and scope

Read the attached Word descriptions and screenshots, inspect current lesson sources and local pages, identify the defect families and strongly similar repetitions, and deliver a precise prompt plus commands preserving the current version. Latest steering: repair the same defect type using the same structure and style. This task prepares instructions; it does not execute the future visual repair or backup.

## Inputs and initial state

Consulted AGENTS.md, PRODUCT.md, relevant ARCHITECTURE.md baseline/ownership sections, ADR-0001, README, editing-lessons, lesson-theme, content pipeline documentation, relevant active UI plans/contracts, and verification skill. Read the attached Word XML and all 197 unique embedded screenshot images. Official Codex prompting guide consulted at https://learn.chatgpt.com/docs/prompting .

Branch: `fix/topics-catalog`.
HEAD: `9ef93f90767b6639a0ebf3c23aa7bc9d288456d3`.
The working tree already contains tracked changes and untracked materials from prior work; preserved. Local lesson runtime: http://127.0.0.1:8000/ . PostgreSQL engine configured for database `mathstart`, host 127.0.0.1, port 5432. Runtime media and collected static reside inside the project.

## Observable analysis and results

- Extracted 586 nonempty text paragraphs and 197 PNG screenshots; viewed all images in 17 contact sheets and inspected selected originals.
- Mapped each image reference D001..D197 to a candidate lesson directory; 118 distinct directories, all corresponding body.html files present. Mapping is navigation, not automatic confirmation of the defect.
- Inspected all 263 lesson sources and loaded their actual HTTP pages at 1440 and 360 px after fonts.ready: 526 states, all HTTP 200, zero Playwright pageerror events in that pass. This does not establish full interaction/visual correctness.
- Scanned card structures in a separate browser pass: 92 lesson / 640 card candidates; 30 candidate lesson pages outside the Word set. Candidates require semantic/visual confirmation.
- Raw source search: 82 lessons / 1864 double-br matches; 7 lessons / 112 C/A/P adjacent-index matches. A broad browser sub+sup search covers 11 lessons and includes indices of different bases. Counts are search candidates, not confirmed defect totals.
- Visually confirmed another glued number/description card at `chislovye-nabory-srednee-arifmeticheskoe` and the same horizontally offset C indices in the Bernoulli series formula outside the Word cases.
- Investigated D169: x=1..6 and y=52,57,63,70,76,82 agree with actual SVG coordinates. The text describes scatter with positive association, not exact collinearity. Prompt prevents moving observations onto a line or modifying data for appearance.
- Linear and square-root targets already have interactive code; prompt requires adaptation to the theme-6.6 quadratic lab, preserving supported behavior.
- Prompt includes a single repair pattern per component type, subtype-aware SVG arrows, full D/R registry and evidence, scoped shared CSS, unchanged educational semantics, selected-slug local publication, actual static delivery checks, and future full repository verification.
- No lesson, shared runtime stylesheet/script, database, Git branch, index, or existing task record changed by this preparatory work. This trace is the sole new repository document from this task.

## Delivered artifacts

Files at `C:\Users\Tramsey\Desktop\MathStart-visual-fixes-20261005`:

- codex-prompt.md: executable user prompt and full D001..D197 appendix.
- defects.json: structured startup registry.
- backup-current-version.ps1: save project files, dirty/staged patches, Git history bundle and PostgreSQL custom dump outside the repository.
- analysis.md: evidence, families, repeats, limitations and command validation.
- checksums.json: hashes of the four delivered artifacts.

Detailed extracted materials, screenshots, source scans and browser JSON at `C:\Users\Tramsey\AppData\Local\Temp\mathstart-visual-prompt-20261005`.

## Verification and limitations

| Check | Result |
| --- | --- |
| Markdown/JSON registry IDs and candidate source existence | PASS, 197/197 |
| Backup script parse in Windows PowerShell 5.1.26100.9444 | PASS |
| Argument construction and native handling of paths with spaces | PASS |
| Container `sh -n` check for the dump command | PASS; pg_dump not executed |
| Full project backup or test restoration | Not performed; commands requested for user execution |
| Whole DOCX page rendering | Unavailable: LibreOffice absent; text + embedded screenshots inspected instead |
| scripts/verify_repo.py for this prompt-only task | Not run; mandatory for future implementation, no past result claimed as new evidence |

Project runtime Python 3.12.10 / Django 5.2.16. Bundled Python/Pillow used for document extraction and contact sheets. Playwright 1.62.1 / Edge 154.0.4258.53 used for HTTP/UI inspection. pg_dump/pg_restore 16.15 available inside the existing PostgreSQL 16 container; no host pg_dump installation performed.

The backup script was syntax/argument validated only. Success markers and archive checks happen when the user runs it. Local backup contains .env and database contents and is not a repository artifact. Future implementation and visual human acceptance remain separate work.

## User clarification: Git commit only

User clarified that saving the current version means an ordinary commit. Updated codex-prompt.md to remove mandatory project/database copies and backup-dependent publication gates, and to record the starting commit while preserving any pre-existing dirty changes. Supplied git-commit-commands.txt for user execution, scoped to current source/document directories; output/ and tmp/ are not selected. Rechecked git status and index: prior changes remain, no staging or commit was executed. Earlier backup script is superseded for the clarified request. The D001..D197 registry remains intact.
