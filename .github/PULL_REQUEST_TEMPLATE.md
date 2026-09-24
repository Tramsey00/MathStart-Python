## Goal

What does this PR achieve?

...

## Task / issue

- Task ID: `Rxx / Vxx / Ixx`
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
- Exec plan: `<path or none>`

## Acceptance

- [ ] acceptance criteria from the issue/spec are satisfied
- [ ] change stays within declared scope
- [ ] architecture/domain boundaries are preserved
- [ ] no unrelated files were changed without reason

## Tests and verification

### Backend

- [ ] `python manage.py check`
- [ ] relevant tests
- [ ] broader test suite where applicable

### Database

- [ ] No DB schema change
- [ ] Migration added and reviewed
- [ ] `python manage.py makemigrations --check --dry-run`
- [ ] fresh PostgreSQL migration/bootstrap verified when required

### Existing content

- [ ] N/A
- [ ] `python manage.py check_lesson_sources --all`
- [ ] `python manage.py check_content_quality`
- [ ] `python manage.py check_site_integrity`

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

## Agent trace

Trace:

`docs/agent-traces/<task>.md`

If no trace is required, explain why.

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
- [ ] trace updated when required
- [ ] main remains deployable
