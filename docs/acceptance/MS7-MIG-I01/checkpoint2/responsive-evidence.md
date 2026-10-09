# Current responsive / keyboard evidence

Source input8d958aeeb17da46839722441425ccbb5889e2ab7; current uncommitted bytes
bound by content-manifest.json. Appearance baseline8c11edadc8debc81432d1db1145feac504f09061.
Browser: Codex In-app Browser, Chromium/Google Chrome155.0.8059.27 from current
UA Client Hints exposed by owned dev-only diagnostics. Separate Codex IAB version
unavailable/unconfirmed. This is a new Stage2 run, not reused browser metadata.

[screenshot index](screenshot-index.md), [raw browser evidence](browser-evidence.json),
[shell comparison](shell-comparison.json).

|Viewport|React shell|Source-derived shell|Gallery full page|
|---|---|---|---|
|360×800|[React](screenshots/react-shell-360.jpg)|[Reference](screenshots/source-shell-360.jpg)|[Gallery](screenshots/gallery-360-full.jpg)|
|768×1024|[React](screenshots/react-shell-768.jpg)|[Reference](screenshots/source-shell-768.jpg)|[Gallery](screenshots/gallery-768-full.jpg)|
|1440×1000|[React](screenshots/react-shell-1440.jpg)|[Reference](screenshots/source-shell-1440.jpg)|[Gallery](screenshots/gallery-1440-full.jpg)|

All three shell pairs are byte-identical JPEGs, with exact geometry/computed CSS/
leaf text equality. Aggregate Django indentation whitespace differs in textContent
only; raw data retained. This is a controlled source-derived empty shell, not
live Django/full-page parity. Live R01 Django remains unavailable.

Gallery has no horizontal overflow at all three widths; one-column cards at360,
two-column cards at768/1440. Source CSS/tokens remain unchanged; no design/reset
or font change. Reviewed full-page360/1440 and the mobile field-error/focus capture;
no in-scope clipping/layout defect found in these checks.

Real browser checks:
- Tab: skip link → brand → catalogue → account → input, visible3px focus outline.
- Skip Enter focuses foundation-main, then Tab reaches input at all widths.
- Loading updates aria-busy/status; error exposes retry/alert.
- Retry by Tab+Enter focuses selector before hiding itself, at all widths.
- Field-error Space focuses input; pointer click clears error and preserves raw
  text including surrounding spaces. No mathematical normalization.
- Four modes select the expected slots; unknown shows controlled unsupported;
  still one demo input and no form.
- Console errors/warnings: none recorded.

[Retry focus](screenshots/gallery-error-keyboard-360.jpg),
[field error/focus](screenshots/gallery-field-error-360.jpg),
[unsupported](screenshots/gallery-unsupported-360.jpg).
Dedicated hover simulation is unavailable in the documented browser API; pointer
activation passes, but the hover color transition is NOT independently verified.
No deployment, real API/session/bridge, lesson/math, concurrency or recovery claim.

Earlier browser attempts reported ERR_BLOCKED_BY_CLIENT. On resumed inspection the
old dev process was absent; a separate hidden I01 dev process was restored at the
same localhost5171 URL. Current browser checks then succeeded, without changing
security settings or trying alternate origins. Initial limitation retained as
RESOLVED history in browser-limitation.json.

Checkpoint1 remains unchanged and retains its original screenshots/metadata.
Its partial gallery screenshot is not used as evidence for the completed gallery.
