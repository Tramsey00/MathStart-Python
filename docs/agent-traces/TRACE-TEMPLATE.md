# TRACE <TASK-ID>: <Task name>

- **Date:** YYYY-MM-DD
- **Task ID:** <ID>
- **Owner:** <name>
- **Coding agent / surface:** <Codex / other>
- **Related issue:** <link>
- **Related spec:** <path>
- **Related exec plan:** <path or none>
- **Related ADR:** <path or none>
- **PR / commit:** <link/hash>
- **Human review status:** Pending | Accepted | Changes requested

---

## 1. Task

State what the coding agent was asked to accomplish.

Keep this concise and testable.

---

## 2. Inputs used

List repository sources the agent relied on.

Examples:

- `AGENTS.md`
- `PRODUCT.md`
- `ARCHITECTURE.md`
- `docs/adr/ADR-....md`
- `specs/...`
- `docs/exec-plans/active/...`
- relevant code/tests/migrations

Also record the original task prompt or a concise stable summary of it.

Do **not** store hidden chain-of-thought.

---

## 3. Initial repository state

Record only observable facts relevant to reproducibility.

Examples:

- branch;
- starting commit;
- working tree state;
- relevant existing apps/files;
- migration state if important.

Example:

```text
Branch: feature/...
Start commit: abc1234
Working tree: clean
```

---

## 4. Files changed

### Added

- ...

### Modified

- ...

### Deleted

- ...

If a file was changed only for generated output, note that.

---

## 5. Commands / tools executed

Record important observable commands, not every trivial shell command.

Example:

```bash
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
```

For a schema task, also include fresh PostgreSQL migration/bootstrap commands.

For frontend/LLM work, include the relevant checks/eval commands.

---

## 6. Implementation summary

Describe what changed at an engineering level.

Examples:

- added a new Django model and migration;
- split public exercise serializer from server validation model;
- added graph cycle validation;
- added fake LLM provider;
- added regression test for answer-key leakage.

Do not include private reasoning.

---

## 7. Observable failures / incidents

Record failures encountered during implementation.

| Failure | Detection | Impact |
| --- | --- | --- |
| ... | ... | ... |

Examples:

- migration failed on fresh PostgreSQL;
- public DTO leaked `answer_key`;
- graph validation found a cycle;
- analyzer output failed Pydantic validation;
- test exposed duplicate `ProgressEvent` records.

If there were none:

`No material implementation failure was observed.`

---

## 8. Root cause summary

For material failures, describe the engineering cause in concise observable terms.

Example:

`Public and server-only exercise fields were serialized by the same DTO, so answer_key appeared in the public payload.`

Do not record hidden chain-of-thought.

If there was no material failure:

`Not applicable.`

---

## 9. Corrections made

List fixes resulting from failures/review.

- ...
- ...
- ...

If a failure revealed a weakness in the coding-agent harness, record the guardrail improvement.

Possible harness improvements:

- `AGENTS.md` rule;
- skill workflow;
- regression test;
- linter/architecture check;
- prompt change;
- ADR;
- spec clarification.

---

## 10. Verification results

Use the current verification matrix in `skills/verification/SKILL.md`.
Record actual command results. Ruff, mypy, pytest, PostgreSQL smoke, and
intelligent-domain checks are not configured in R01; mark them NOT CONFIGURED
when relevant, never PASS. Use N/A only for checks outside the task's scope.

### Backend

| Check | Result |
| --- | --- |
| `python manage.py check` | PASS / FAIL / N/A |
| `python manage.py test` | PASS / FAIL / N/A |

### Database

| Check | Result |
| --- | --- |
| `python manage.py makemigrations --check --dry-run` | PASS / FAIL / N/A |
| Fresh PostgreSQL migrate | PASS / FAIL / N/A |
| Migration smoke | PASS / FAIL / N/A |

### Content

| Check | Result |
| --- | --- |
| `python manage.py check_content_quality` | PASS / FAIL / N/A |
| `python manage.py check_lesson_sources --all` | PASS / FAIL / N/A |
| `python manage.py check_site_integrity` | PASS / FAIL / N/A |

### Domain-specific

| Check | Result |
| --- | --- |
| Knowledge graph validation | PASS / FAIL / N/A |
| Exercise contract validation | PASS / FAIL / N/A |
| Public DTO secret-leak regression | PASS / FAIL / N/A |
| LLM structured-output validation | PASS / FAIL / N/A |
| Golden eval subset | PASS / FAIL / N/A |
| Frontend checks | PASS / FAIL / N/A |
| Playwright critical flow | PASS / FAIL / N/A |

Add exact command/result details where useful.

---

## 11. Final diff summary

Summarize the resulting repository change in a few bullets.

- ...
- ...
- ...

---

## 12. Acceptance criteria result

| Acceptance criterion | Result | Evidence |
| --- | --- | --- |
| ... | PASS / FAIL | test/check/demo |
| ... | PASS / FAIL | test/check/demo |

A task must not be marked complete if a blocking acceptance criterion fails.

---

## 13. Remaining risks / follow-ups

- ...
- ...
- ...

If none:

`No known blocking follow-up remains.`

---

## 14. Harness improvement

Did this task reveal a harness weakness?

- **Yes / No**

If yes:

### Problem

...

### Improvement made

- [ ] `AGENTS.md`
- [ ] skill workflow
- [ ] spec template
- [ ] ADR
- [ ] architecture check
- [ ] regression test
- [ ] prompt
- [ ] other: ...

### Result

...

---

## 15. Human review

**Reviewer:** <name>

**Status:** Pending | Accepted | Changes requested

**Date:** YYYY-MM-DD

**Feedback:**

...

If changes were requested, link the follow-up commit/trace.

---

## 16. Final status

`COMPLETE` | `INCOMPLETE` | `BLOCKED`

Reason:

...
