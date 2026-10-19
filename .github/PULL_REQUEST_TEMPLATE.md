## Goal

What does this PR achieve?

...

## Task / issue

- Current user task / optional task ID:
- Issue: #
- Owner: <name>

## Scope

### In scope

- ...
- ...

### Out of scope

- ...
- ...

## Related specs / ADRs / plans

- Spec: `<path or none>`
- ADR: `<path or none>`
- Scoped execution record: `<path or PR description>`

## Acceptance

- [ ] acceptance criteria from the issue/spec are satisfied
- [ ] change stays within declared scope
- [ ] architecture/domain boundaries are preserved
- [ ] no unrelated files were changed without reason

## Tests and verification

### Backend

- [ ] affected FastAPI/service checks from `docs/target-runtime.md`
- [ ] relevant tests
- [ ] broader test suite where applicable

### Database

- [ ] No DB schema change
- [ ] Migration added and reviewed
- [ ] reviewed Alembic/metadata consistency checks when schema is affected
- [ ] fresh PostgreSQL migration/bootstrap verified when required

### Existing content

- [ ] N/A
- [ ] current lesson-sources, content-quality and site-integrity target commands
- [ ] `python scripts/check_migration_preservation.py`

Use `python scripts/verify_repo.py` for the full target registry with the
prerequisites in `docs/target-runtime.md`. `--profile pure` is a portable subset.
Record actual candidate SHA, commands/results and required CI links; skipped or
missing checks do not establish readiness. Legacy comparisons use the separate
pinned oracle, never Django in the target environment.

### Domain-specific

- [ ] N/A
- [ ] knowledge graph validation
- [ ] exercise contract validation
- [ ] public DTO secret-leak regression
- [ ] LLM structured-output validation
- [ ] golden eval subset
- [ ] frontend checks
- [ ] E2E / Playwright flow

## DB migration

Describe migration impact.

`None` if no schema change.

...

## API / schema impact

Describe:

- endpoints;
- public DTOs;
- input schemas;
- step schemas;
- server-only fields;
- reveal/hint semantics.

`None` if unchanged.

...

## Screenshots / demo

Attach screenshots or a short demo when UI behavior changes.

N/A if this PR has no UI change.

## Execution and review record

Record actual changes, checks and review findings in this PR or a scoped document:

`<link>`

## Risks

- ...
- ...

## Security / privacy

- [ ] no secrets committed
- [ ] server-only validation data is not leaked
- [ ] auth/ownership boundaries preserved
- [ ] logs do not contain passwords/tokens/API keys
- [ ] AI endpoint limits/rate controls considered when applicable

## Human gate

- [ ] Not required
- [ ] Required; review pending
- [ ] Required and approved

Reviewer:

...

## Final review checklist

- [ ] `AGENTS.md` followed
- [ ] relevant docs/specs updated
- [ ] migrations included when required
- [ ] required verification passed
- [ ] known failures are documented
- [ ] execution/review record updated
- [ ] main remains deployable
