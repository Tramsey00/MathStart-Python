# MathStart repository map

Work from this primary Git root on main for the current user task. Historical
migration worktrees and personal queues are retired; do not bootstrap them.
See docs/maintenance.md for accepted history and docs/local-development.md for local start.

MathStart runs on FastAPI/Pydantic, SQLAlchemy/Alembic, PostgreSQL and React/SSG.
Start with [README.md](README.md), [current runtime](docs/target-runtime.md),
[release](deploy/RELEASE.md) and [recovery](deploy/RECOVERY.md). Read PRODUCT.md,
ARCHITECTURE.md and the relevant accepted contracts before changing behavior.
The intelligent learning domains remain future scope, not implemented features.

## Critical invariants

- Preserve the modular monolith and domain ownership in `ARCHITECTURE.md`.
  Content owns topic-to-skill mappings and depends on Knowledge for them.
- Only Progress changes long-term knowledge state, through validated
  `ProgressEvent` evidence. Reading a topic never increases mastery.
  Tutor, Analyzer, frontend, and LLM providers must not directly mutate it.
- Prefer deterministic mathematical validation. Preserve raw input separately
  from normalized data; unsupported parsing is not a misconception.
- Schema-validate LLM outputs that affect domain decisions. Malformed or
  low-confidence output must not produce strong negative misconception
  evidence. Keep provider SDKs in infrastructure and prompts versioned.
- Keep exercise answers and validation secrets server-side until explicit
  reveal. A wrong final answer alone does not identify a misconception; full
  reveal prevents `CORRECT_FIRST_TRY`. Record evidence-relevant hints/reveals.
  See the architecture's current-baseline section for legacy self-checks.
- Preserve the four exercise modes and typed ordered solution steps. New modes
  or changed semantics need a spec, validation/tests, and architectural review.
- Skill codes are stable; topics and skills differ. Prerequisites point from
  prerequisite to dependent and have no self-edges or cycles.
- Bootstrap must not overwrite historical user evidence. Never commit or log
  secrets; normal automated tests must not require a live LLM.

## Working rules

Inspect Git state and real imports/build inputs before editing. Preserve dirty
fixes, data, authored content, media, deterministic mathematics and contracts.
Use scoped changes and meaningful verification; never weaken checks for PASS.
Schema changes use reviewed Alembic migrations and fresh/upgrade verification;
never edit applied history. No automatic DDL or content/operator seed at startup.
Never commit/log secrets. Normal tests do not call live LLM providers.

Default verification is target: `python scripts/verify_repo.py`. The portable
subset is `--profile pure`; it cannot establish runtime readiness. The complete
managed run with owned disposable PostgreSQL/browser prerequisites is described
in docs/target-runtime.md. Empty, skipped, missing and timed-out checks fail.
Use [verification skill](skills/verification/SKILL.md) for staged checks and
honest evidence tied to the actual SHA. Full CI includes install/recovery and
the combined gate; old results never establish readiness for a new candidate.

Historical Django is only a separate pinned checkout and interpreter prepared
on explicit comparison runs: [oracle](docs/legacy-oracle.md). Never install
Django/DRF in target environments or copy the old platform back into HEAD.
Preservation dispositions are explicit; unknown deletions/changes fail.

For substantial work keep a scoped execution record, actual verification and
review findings in the repository. Human acceptance, main merge, production
changes and provider/security decisions require the appropriate human decision.
Accepted migration PR54 and consolidation PR55 are recorded in
[maintenance](docs/maintenance.md); neither is a pending migration assignment.
Do not operate the protected acceptance stack or original Django DB as tests.
