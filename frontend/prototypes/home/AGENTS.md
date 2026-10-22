# Approved visual baseline

The user approved Professional Theme colors and QraftHive typography on
2026-10-22. Preserve that baseline for cosmetic/component work. See
`../../../docs/ux/theme-baseline.md` for sources and exact font stacks.

Do not replace the palette, font families, theme tokens, or reintroduce theme
comparison pages unless the user explicitly requests another style experiment.
Changes to spacing, responsive layout and component density may use this
baseline. Keep the page's existing hero, catalogue, search and dialogs.

The user approved the catalogue on 2026-10-22 and requested a separate homepage.
`index.html` / `landing.tsx` own that homepage; `materials.html` / `main.tsx`
retain the approved navigation catalogue. Shared navigation/footer live in
`site-shell.tsx`. Homepage materials links must open the real catalogue;
actual authentication stays on the existing local site's account route. Do not invent future
tutor, progress, mastery, exercise or authentication features.

Latest homepage revision: the user explicitly authorized one additional muted
green accent on the homepage only; keep it scoped to `.landing-page`, never
replace the shared theme tokens. The repeated class/subject selector and square
demo were rejected. Use a simple transition to materials instead. The user
approved an email/password form PREVIEW now and email-auth integration later.
Do not submit, persist or log credentials, simulate a signed-in session, add
OAuth providers, or change identity/security contracts in this design task.

Section rows show a number, complete section title and topic count. Do not
restore topic preview descriptions, repeated action labels, or decorative
arrows. Preserve keyboard focus, accessible controls and content-driven height.
