# SPEC: All topics catalogue

- Status: Implemented and verified; final human acceptance pending
- Date: 2026-10-04
- Scope owner/reviewer: repository owner
- Compatibility: ADR-0001, existing Content publication, MS7-I02 UI isolation
- Plan: `docs/exec-plans/active/topics-catalogue.md`

## Contract

`/karta-sajta/` is «Все темы» in navigation, heading and SEO title.
Only published topic ContentPages appear, grouped by Grade → Subject → Section.
Empty groups and non-teaching pages are absent. A GET form accepts `q`, `grade`
(grade slug), and `subject` (subject slug, shared across grades). Unknown filter
values are treated as all; incompatible subjects reset to all on grade changes.
Subject options come from published topics of the selected grade, independently
of the query. Search trims surrounding whitespace and uses Unicode casefold
substring matching on titles in Python for identical PostgreSQL/SQLite behavior.
At the current 263-topic scale, loading lightweight title/relationship records
is acceptable; lesson bodies are deferred. No API, search dependency or JS is needed.

Search results are immediately visible with grade/subject/section context.
Ordinary browsing retains nested groups and native details/summary. The URL
retains submitted state across refresh and browser Back from an unchanged lesson
URL. Reset links to the bare catalogue URL. Labels, visible focus, wrapping and
360/768/1440 layouts are required. CSS is scoped to `.ms-catalogue` and reuses UI
tokens; existing lesson/home styles and the XML sitemap remain intact.

## Retirement and publication

Delete only sources for `materialy` and `pamyatki`. During bootstrap explicitly
unpublish these two static ContentPages, retaining identities/content and all
other records. No missing-source sweep and no migration/schema change.
Update redirects from both root and `/mathstart/` addresses directly to
`/karta-sajta/` and `/bazovye-svojstva-stepenej-s-naturalnym-pokazatelem/`.
Preserve the bytes and URL `/media/uploads/2026/07/pamyatka-stepeni.pdf`, add its
link to that lesson and update MediaAsset ownership. Update Contacts/About copy.
Existing publication conflict detection remains effective.

## Acceptance

Tests cover Unicode search, filter combinations, invalid/empty input, unpublished
topics, hierarchy, links, navigation, four 301s, upgrade/repeat/bootstrap,
content/media/user preservation and source integrity. Run verify_repo plus
available visual/browser checks; explicitly record missing evidence.
Only isolated databases may be initialized by the agent. Changes remain
uncommitted. Human review of the final UI and update procedure is pending.
