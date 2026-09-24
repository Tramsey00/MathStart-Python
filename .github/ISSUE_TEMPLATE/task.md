---
name: MathStart task
about: Backlog task for MathStart development
title: "[ID] "
labels: ""
assignees: ""
---

## Task ID

`Rxx / Vxx / Ixx`

## Owner

<name>

## Goal

Describe the concrete result that must be achieved.

## Scope

### In scope

- ...
- ...
- ...

### Out of scope

- ...
- ...
- ...

## Related repository sources

- `AGENTS.md`
- `PRODUCT.md`
- `ARCHITECTURE.md`
- Spec: `<path or none>`
- ADR: `<path or none>`
- Exec plan: `<path or none>`

## Acceptance criteria

- [ ] ...
- [ ] ...
- [ ] ...

## Expected verification

- [ ] `python manage.py check`
- [ ] relevant automated tests
- [ ] `python manage.py makemigrations --check --dry-run` when schema may be affected
- [ ] domain-specific verification where applicable
- [ ] trace summary for a significant agent task

## DB migration impact

- [ ] No schema change
- [ ] Schema change expected
- [ ] Data migration expected

Details:

...

## API / schema impact

- [ ] None
- [ ] Public API contract changes
- [ ] Internal contract changes
- [ ] Exercise interaction/input/step schema changes

Details:

...

## Human gate

Human review is required if the task changes:

- architecture/data ownership;
- breaking DB migration;
- exercise mode semantics;
- public/server validation boundary;
- reveal policy;
- mastery/confidence algorithm or thresholds;
- taxonomy historical meaning;
- prompt policy affecting learning strategy;
- security/auth/deployment;
- external dependency/provider.

- [ ] Human gate required
- [ ] Human gate not required

## Risks

- ...
- ...

## Priority / module labels

Recommended labels:

- `priority:P0` or `priority:P1`
- one or more `module:*`
- `type:feature` / `type:bug`
- `harness` when applicable

## Notes

...
