# MS6-I01: UX-spec — карта и предметная область

- **Status:** Draft for review
- **Task:** MS6-I01, MathStart ТЗ v6.0 (2026-09-25)
- **Scope:** student MVP UX; low-fidelity information architecture only
- **Companion artifacts:** [states matrix](MS6-I01-states-matrix.md), [screen map](MS6-I01-screen-map.md), [wireframes](MS6-I01-wireframes.md), [source notes](MS6-I01-source-notes.md), [API-needs handoff](MS6-I01-api-needs.md)

## 1. Product boundary

MathStart is a Russian-language web application for school mathematics. The MVP loop is: topic -> exercise -> validated result/evidence -> progress feedback -> help or targeted practice -> return to the topic. A guest can read published catalogue and theory; attempts, history, progress, diagnostic, practice, and Tutor are student-scoped. Internal content administration is not a public UX flow.

The pilot covers linked clusters around integers and sign rules; distributive property, parentheses, and like terms; and one-variable linear equations. It uses `SELF_CHECK`, `FINAL_ANSWER`, `STEP_BY_STEP`, and `STRUCTURED_SOLUTION`. Teacher/parent accounts, dashboards, and cross-student views are deliberately absent.

## 2. UX rules

1. Reading a topic is activity, not evidence of mastery. Do not display a progress increase after page view or refresh.
2. A final-answer verdict is not a diagnosis. Only a validated transition/field may be shown as a confirmed misconception. A recoverable transport failure may retry the same submission identity while preserving the raw input; once mathematical evaluation has completed, correction starts a new `Attempt` and does not mutate the evaluated one.
3. Raw mathematical input remains visible to the student; preview/normalization never silently replaces it.
4. `UNSUPPORTED` means the current input cannot be reliably assessed. It is distinct from `wrong` and from a knowledge error.
5. Hint and reveal are separate actions. After a hint, the learner may continue solving or separately choose reveal. Reveal requires explicit confirmation and is displayed only after server confirmation. Exposure is remembered for the user and immutable `exercise_version` across attempts: creating another `Attempt` does not restore eligibility for new independent positive evidence on that revealed version.
6. Deterministic exercise feedback remains usable when Tutor/model service is unavailable. Tutor outage is not exercise-validation outage.
7. Each write state has pending, successful, recoverable-error, and retry behavior. Retry must preserve input and must not promise a new progress event.
8. The UI renders public exercise data only. Correct answers, canonical solutions, validation rules, and accepted variants are not preloaded into DOM, JavaScript, or local storage.

## 3. Information architecture

| Area | Principal student purpose | Included routes / screens |
| --- | --- | --- |
| Entry and account | Authenticate and set learning context | sign in, registration, profile, grade, onboarding choice |
| Catalogue and topic | Read theory and select an available activity | grade, subject, section, topic, exercise entry |
| Exercise | Submit mode-specific work and receive safe feedback | self-check, final answer, step editor, structured form, result/help/reveal states |
| Progress and history | Inspect own evidence-backed state | skills, topic aggregate, history, explanation of empty/low-coverage state |
| Diagnostic and practice | Establish evidence or practise a weak prerequisite | diagnostic start/next/finish; practice start/item/finish/return |
| Tutor | Request bounded help | hint request, pending, answer, rate/outage/retry; never bypasses reveal |

The existing Content page remains the topic/theory host. Future exercise and progress widgets must be additive and preserve stable content URLs.

## 4. Mathematical input and presentation

The primary input is plain, editable math text with an optional non-authoritative preview. Examples in low-fidelity sheets use `-8 * (-4)`, `2(x+3)=10`, and `2x+3=10`. The UI must state the expected form where a schema provides it, preserve the exact raw string, and offer keyboard-reachable labels and errors.

For ordered work, the initial condition is a separate read-only reference; each line has a visible one-based order number and type. For structured work, labels, required status, field-specific error, and order are public-schema-driven. An unknown public mode, schema version, or field type blocks submission with a clear explanation; it does not guess a form.

## 5. User-message glossary

| State | Candidate message | Meaning / prohibited implication |
| --- | --- | --- |
| Correct | «Ответ принят. Результат сохранён.» | Does not claim mastery by itself. |
| Wrong final | «Ответ пока не совпадает. Чтобы исправить решение, начните новую попытку или запросите подсказку.» | Does not name a misconception and does not imply editing an evaluated attempt. |
| Confirmed step issue | «Первый проблемный переход — строка 1: раскрытие скобок.» | Shown only with validated confirmed evidence. |
| Uncertain | «В этом переходе есть повод проверить решение, но система не подтверждает тип ошибки.» | Does not diagnose. |
| Unsupported | «Мы пока не можем надёжно разобрать этот ввод. Сохраните запись и попробуйте поддерживаемый формат.» | Not an error of knowledge. |
| Hint | «Подсказка уровня 2 из 3» | Distinct from a complete solution. |
| Reveal confirmation | «Показать полный ответ? Раскрытие сохранится в вашем профиле для этой версии задания, включая новые попытки. Повтор этой версии больше не даст нового самостоятельного подтверждения освоения.» | No answer is exposed yet. |
| Revealed | «Решение раскрыто для этой версии задания. Повтор этой версии не будет новым самостоятельным подтверждением.» | Applies across attempts for the same user and exercise version; does not shame or claim failure. |
| Validation pending | «Проверяем ответ…» | Input remains visible and protected from duplicate submission. |
| Recoverable request failure | «Не удалось подтвердить результат. Проверьте соединение и повторите запрос — введённые данные сохранены.» | No inferred result or extra event. |
| Tutor outage | «Проверка задания доступна. Помощник временно недоступен; используйте подготовленную подсказку.» | Distinguishes model failure from validation. |
| No access | «Эта попытка недоступна.» | Does not disclose another user’s existence or data. |

## 6. Accessibility and responsive baseline

Implementation must be checked at 360, 768, and 1440 px. Desktop sheets use a two-column reading/work layout where it helps; mobile sheets collapse to one column while keeping the task reference reachable. Every actionable element has a text label and visible focus; state is not communicated by colour alone; errors are programmatically associated with their field/line; and focus lands on a server-identified field/step error. Loading, result, validation, help, reveal, and degraded-service updates use appropriate live regions without repeatedly announcing static content. Keyboard flow proceeds from context to input to feedback to the next safe action.

## 7. Explicit non-goals

This artifact does not select a design system, create final visual design, introduce a SPA, define API endpoints, calculate progress on the client, or convert existing lesson content. It also does not introduce teacher/parent scope.
