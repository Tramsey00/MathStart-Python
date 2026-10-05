# SPEC: Bounded public-site polish

- Status: Applied locally; automated checks passed; human acceptance pending
- Date: 2026-10-04
- Owner/reviewer: repository owner
- Plan: `docs/exec-plans/active/site-polish.md`
- Compatibility: ADR-0001, MS7-I02, `topics-catalogue.md`

## Contract and scope

Preserve Django, Content ownership, lesson/class/subject content and styles,
catalogue GET search/filter/grouping, home hero and class selector behavior.
Polish only the catalogue introduction, shared brand/footer, About, Contacts,
and two home information sections. No schema, dependencies, API, account,
exercise, evidence or deployment changes. No branch, agents, commit or push.
This feature does not create or mutate knowledge evidence.

Catalogue has one compact «Все темы» heading and short search guidance. The
header brand links to `/`, with a decorative hidden math symbol and visible
focus. Footer links to catalogue/About/Contacts with one concise purpose line.
About describes actual reading/examples/available self-checks and the partial
grade-10 algebra coverage; remove the whole illustrative gallery, retain media.
Contacts preserves `mailto:rr06@mail.ru` and explains what to report/include.
Home benefits become concise columns; lesson structure becomes a distinct
sequence. Remove the final class-selection note; retain hero/classes verbatim.
All new styles must stay inside shell/page/block roots.

## Publication contract

The user explicitly authorizes updating the existing local PostgreSQL site.
Use a scoped source-driven update of `glavnaya`, `karta-sajta`, `o-proekte`,
`kontakty`, the existing powers lesson/PDF relationship, exactly four retired
URL redirects, and the two static-page publication flags. Retain retired rows.
Full bootstrap must not recreate their deleted sources. Do not sweep missing
sources or overwrite other lessons/catalogue/media/users. Keep conflict-safe
lesson publication; a conflict prevents the update. Snapshot affected records,
verify on isolated PostgreSQL first, collect static and verify actual port 8000.
No production/remote update is authorized.

## Acceptance and verification

Meaningful tests cover scoped upgrade/repeat/dry-run/conflict rollback,
unrelated/user/media preservation, rendered links/text/metadata, direct 301s,
fresh bootstrap, catalogue behavior, and manifest storage. Required verification:
`.venv312/Scripts/python.exe scripts/verify_repo.py`, `git diff --check`, disposable
PostgreSQL fresh smoke, browser 360/768/1440 on six representative pages.
Compare lesson/class component markup and dimensions and home protected areas.
Report unused gallery media honestly; never weaken integrity checks. Keep
plan active and implementation uncommitted until the owner's human review.

Local media limitation: the unchanged DEBUG=False runserver does not serve
`/media/`. The PDF is preserved and linked correctly but live PDF HTTP is 404;
no claim of successful media delivery or deployment configuration change.
