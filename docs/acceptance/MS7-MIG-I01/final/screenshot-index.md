# Final screenshot index

Input:8d958aeeb17da46839722441425ccbb5889e2ab7. Canonical appearance:8c11edadc8debc81432d1db1145feac504f09061. Implementation:uncommitted; [exact bytes](content-manifest.json).

Browser:Chromium/Google Chrome155.0.8059.27 from current UA Client Hints; separate Codex IAB version unavailable/unconfirmed. Capture:2026-10-09T13:04:05.214Z.

Live fresh task-local Django SQLite gallery comparison, not R01 PostgreSQL or whole-site/target runtime parity. [Hashes/metadata](screenshot-index.json), [keyboard/CSS observations](browser-evidence.json). CSS viewport differs from full-page raster.3/3 gallery JPEG pairs byte-identical.

|Screenshot|Exact URL|Viewport CSS px|Raster px|Full-page|State|
|---|---|---|---|---|---|
|[react-gallery-360.jpg](screenshots/react-gallery-360.jpg)|http://127.0.0.1:5171/__ui__/foundation/|360×800|345×3579|true|ordinary; empty input; SELF_CHECK|
|[django-sqlite-gallery-360.jpg](screenshots/django-sqlite-gallery-360.jpg)|http://127.0.0.1:8003/__ui__/foundation/|360×800|345×3579|true|ordinary; empty input; SELF_CHECK|
|[react-gallery-768.jpg](screenshots/react-gallery-768.jpg)|http://127.0.0.1:5171/__ui__/foundation/|768×1024|753×2484|true|ordinary; empty input; SELF_CHECK|
|[django-sqlite-gallery-768.jpg](screenshots/django-sqlite-gallery-768.jpg)|http://127.0.0.1:8003/__ui__/foundation/|768×1024|753×2484|true|ordinary; empty input; SELF_CHECK|
|[react-gallery-1440.jpg](screenshots/react-gallery-1440.jpg)|http://127.0.0.1:5171/__ui__/foundation/|1440×1000|1425×2292|true|ordinary; empty input; SELF_CHECK|
|[django-sqlite-gallery-1440.jpg](screenshots/django-sqlite-gallery-1440.jpg)|http://127.0.0.1:8003/__ui__/foundation/|1440×1000|1425×2292|true|ordinary; empty input; SELF_CHECK|
|[react-field-error-360.jpg](screenshots/react-field-error-360.jpg)|http://127.0.0.1:5171/__ui__/foundation/#foundation-main|360×800|345×767|false|field error; input focused after Space; raw synthetic input preserved|
|[react-unsupported-360.jpg](screenshots/react-unsupported-360.jpg)|http://127.0.0.1:5171/__ui__/foundation/#foundation-main|360×800|345×767|false|controlled unsupported; no form|
|[react-retry-focus-360.jpg](screenshots/react-retry-focus-360.jpg)|http://127.0.0.1:5171/__ui__/foundation/|360×800|345×767|false|error; retry focused by Tab from state selector|
|[react-gallery-final-1440-viewport.jpg](screenshots/react-gallery-final-1440-viewport.jpg)|http://127.0.0.1:5171/__ui__/foundation/|1440×1000|1425×990|false|ordinary; empty input; SELF_CHECK; final clean-install build/dev run|

[Checkpoint2 source-derived shell comparison](../checkpoint2/screenshot-index.md) preserved separately.
