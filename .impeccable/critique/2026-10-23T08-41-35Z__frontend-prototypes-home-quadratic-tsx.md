---
target: frontend/prototypes/home/quadratic.tsx
total_score: 32
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 0
target_identity: "file:C:\\Projects\\MathStart-Python\\frontend\\prototypes\\home\\quadratic.tsx"
target_fingerprint: "sha256:112a2def4c46553aa3f17146fe786504a62b3c0faceb42f176aca7865d10c5d8"
target_path: "C:\\Projects\\MathStart-Python\\frontend\\prototypes\\home\\quadratic.tsx"
timestamp: 2026-10-23T08-41-35Z
slug: frontend-prototypes-home-quadratic-tsx
closed: true
---
⚠️ DEGRADED: single-context (sub-agents declined by user)

Target: frontend/prototypes/home/quadratic.tsx; Read with an interactive math lab.
Design specificity: MathStart identity is coherent: approved typography and blue accent, authored mathematical diagrams, flat article, inline self-checks. Preserve it.

Nielsen scores before changes: status 3; real-world match 4; control 4; consistency 3; prevention 3; recognition 3; efficiency 3; minimalist design 3; recovery 3; help 3. Total 32/40, all ten apply. No P0/P1.

Strengths: linear reading path; graph and computed results grouped on desktop; keyboard-operable self-checks and contents modal.
Cognitive load: eight contents links are justified article navigation, not eight competing actions. The article leads to graph exploration and self-check. No extra recap/CTA needed.
Emotional journey: calm reading and experimentation; friction occurs in the small graph annotations and phone controls.

P2 readability: graph caption/legend use 11px; coefficient labels and property names 12px; reset on mobile 11px. Raise supporting text to 12–13px and property values to 15px while retaining desktop co-visibility. layout/polish.
P2 encoding: roots are primary-blue rings on the graph but muted rings in the legend; curve and dashed symmetry use circle swatches. Match legend markers to plotted marks with CSS. polish.
P2 touch: phone contents trigger has 36px target and close button 40px. Raise to 44px and account for sticky rail height in scroll offsets. layout.

Personas: Casey needs larger phone targets; Jordan needs legend symbols matching the math visualization; Sam needs visible focus and unclipped anchor destinations. Existing keyboard behavior is sound and must remain.
Minor observations: long formulas tested at a=4,b=-10,c=10 wrap within the mobile toolbar without horizontal overflow. Retain two-column desktop and stacked phone layouts.
Deterministic source scan: [] across entry TSX and lesson directory. No false positives. URL scan failed launching its bundled Chromium (crashpad named-pipe error), so this is not a clean runtime detector result. Browser inspection via CUA succeeded for wide/light and phone/dark, contents, graph extremes and disclosure.
Questions skipped: user specified autonomous refinement and unchanged style/content.
