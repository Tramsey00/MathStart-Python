# MathStart Product Specification

## 1. Product identity

**MathStart** is an intelligent educational web system for school mathematics.

Its core purpose is not only to show theory and exercises, but to understand how a student solves supported problems, identify a confirmed problematic step, connect the error to an underlying skill, update the student's knowledge state, and select an appropriate next practice activity.

The product evolves from an existing MathStart Django project that already contains educational content for grades 5-9.

This document defines the product-level source of truth for MathStart v3.1.

Detailed architecture belongs in `ARCHITECTURE.md`.
Detailed feature/domain contracts belong in `specs/`.
Significant engineering decisions belong in `docs/adr/`.

---

## 2. Product vision

MathStart should support the following learning loop:

1. a student studies a topic;
2. the student receives an exercise in an interaction mode appropriate to the task;
3. MathStart validates the answer or solution steps;
4. when supported, MathStart identifies the first confirmed problematic step;
5. the system links confirmed evidence to one or more skills;
6. Progress Engine updates the student's knowledge state using validated knowledge events;
7. if a prerequisite is weak, Adaptive Practice temporarily switches the student to targeted practice;
8. AI Tutor provides hint-first help using relevant topic and progress context;
9. after successful practice, the student returns to the original topic.

The system must remain explainable: progress changes must be traceable to concrete evidence, not opaque LLM judgments.

---

## 3. Existing product baseline

The repository already contains a working MathStart educational website.

Existing product assets include:

- curriculum content for grades 5-9;
- topic/theory pages;
- existing exercise/self-check content;
- Django-based publication/runtime infrastructure;
- current content quality and integrity checks;
- current tests and management tooling.

The existing educational content is an asset of the project and must be preserved.

MathStart v3.1 extends this baseline instead of replacing it with a full rewrite.

---

## 4. What is new in the course project

The new course-project scope is the intelligent learning layer around the existing MathStart content.

The major new product capabilities are:

- student accounts and profiles;
- selected grade and onboarding mode;
- a unified exercise model;
- four exercise interaction modes;
- attempts and typed solution steps;
- server-side answer/solution validation;
- knowledge graph of atomic skills;
- diagnostics;
- event-based progress tracking;
- `UserSkillState`;
- misconception taxonomy;
- Solution Analyzer;
- AI Tutor;
- Adaptive Practice;
- progress visualization;
- LLM observability;
- public web deployment;
- coding-agent harness and reproducible development workflow.

---

## 5. Primary user

### Student

The student is the main MVP user.

The student can:

- register and sign in;
- select a grade;
- choose an onboarding path;
- read theory;
- solve exercises;
- submit final answers;
- submit step-by-step solutions where supported;
- use hints;
- reveal an answer/solution when allowed;
- see recent attempts;
- see confirmed mistakes;
- view progress by skills/topics;
- receive adaptive practice;
- interact with AI Tutor.

---

## 6. Secondary roles

### Content administrator

A minimal content administration capability is required.

For MVP, content administration may use Django Admin, management commands, seeds, or similar internal tooling.

A polished standalone content-management frontend is not required.

The administrator must be able to manage or bootstrap, where applicable:

- grades;
- topics;
- skills;
- skill dependencies;
- exercises;
- interaction contracts;
- validation specifications;
- skill mappings;
- mistake taxonomy.

### Teacher / parent

Teacher and parent dashboards are **POST-MVP**.

They must not block delivery of the student vertical slice.

---

## 7. MVP subject scope

The MVP deliberately uses a deep vertical slice instead of attempting to make every school-mathematics topic intelligent at once.

The pilot learning chain is:

1. **negative numbers**;
2. **distributive property / expanding parentheses**;
3. **linear equations**.

Supporting atomic skills may include:

- integer number line;
- understanding negative numbers;
- addition/subtraction sign rules;
- multiplication/division sign rules;
- distributive property;
- expanding parentheses;
- combining like terms;
- equation balance;
- one-step linear equations;
- linear equations with parentheses.

The infrastructure should be extensible to additional domains later, but complete support for geometry, probability, statistics, and every task type is not required for MVP.

---

## 8. Interaction modes

Every exercise explicitly declares its interaction mode.

The baseline modes are:

### `SELF_CHECK`

Use when MathStart presents an exercise but does not require a submitted answer or does not yet have a reliable validator.

Typical behavior:

- show task;
- optionally allow answer/solution reveal;
- record activity/reveal when needed;
- do not create positive mastery evidence merely because the student viewed or revealed the answer.

This mode is suitable for much of the existing content until deeper validation is available.

### `FINAL_ANSWER`

Use when the final result is enough for the task.

Examples:

- numeric answer;
- fraction;
- algebraic expression;
- small structured final result.

The final answer is checked server-side.

A wrong final answer may create weak negative evidence, but it must not automatically create a specific misconception without additional evidence.

### `STEP_BY_STEP`

Use when the transition between mathematical states is pedagogically informative.

Examples:

- expanding parentheses;
- combining like terms;
- solving linear equations.

The student submits ordered solution steps.

This mode allows MathStart to locate a first problematic transition and, when sufficiently supported, connect it to a misconception/skill.

### `STRUCTURED_SOLUTION`

Use when a solution naturally consists of heterogeneous fields/actions rather than only equation strings.

Examples may later include:

- claim + reason;
- known values -> formula -> substitution -> answer;
- total outcomes + favorable outcomes + probability;
- sorted dataset + median.

MVP must provide the infrastructure/contract for this mode, but complete domain coverage is not required.

---

## 9. Exercise integrity

The frontend may know how an exercise should be displayed and what kind of input is expected.

The ordinary public exercise payload must not expose server-side validation secrets.

Server-only data includes, where applicable:

- `answer_key`;
- `validation_spec`;
- `canonical_solution`;
- accepted variants that effectively reveal the correct answer.

A reveal action must be explicit and recorded.

After a full reveal, the same attempt must not be treated as an independent first-try success.

---

## 10. Mathematical input

Students are not required to type LaTeX.

The baseline mathematical input is ordinary text, for example:

- `2(x+3)=10`
- `3/4`
- `x^2`
- `2*x`
- `2x`
- `2.5`
- `2,5`

The system should normalize supported syntax into a canonical representation.

Raw user input must also be preserved for audit/debug.

If input cannot be parsed reliably, MathStart must represent that state explicitly instead of inventing a mathematical mistake.

---

## 11. Onboarding

After registration, the student chooses a grade.

The product supports three knowledge-initialization paths:

### Start from the beginning

No prior knowledge is assumed.

Unverified skills remain `NOT_STARTED` with zero confidence.

### Short diagnostic

The student completes diagnostic exercises.

Diagnostic results create stronger knowledge evidence than self-reporting.

### Mark familiar topics

The student may indicate topics/skills they believe they know.

Self-report is weak evidence only.

It must not be treated as demonstrated mastery.

Opening a page or reading theory must not increase mastery.

---

## 12. Knowledge model

MathStart models knowledge at the level of atomic skills.

A **topic** and a **skill** are different concepts.

For example, the topic "Linear equations" may depend on several skills:

- expanding parentheses;
- combining like terms;
- preserving equation balance.

The knowledge graph stores objective prerequisite relations between skills.

It does not store a particular student's progress.

The pilot graph must be a directed acyclic graph.

Cycles and self-dependencies are invalid.

---

## 13. Student knowledge state

For each relevant student/skill pair, MathStart maintains a knowledge state containing at least:

- `mastery` from 0 to 100;
- `confidence` from 0 to 100;
- `evidence_count`;
- status;
- last evaluation time.

Baseline statuses:

- `NOT_STARTED`;
- `LEARNING`;
- `WEAK`;
- `MASTERED`.

The state is a projection of validated evidence.

It is not updated directly by AI Tutor or an LLM provider.

---

## 14. Knowledge events

Long-term progress changes are driven by explicit knowledge events.

Baseline event types include:

- `SELF_REPORTED_KNOWN`;
- `CORRECT_FIRST_TRY`;
- `CORRECT_AFTER_HINT`;
- `WRONG_ATTEMPT`;
- `MISCONCEPTION_DETECTED`;
- `ANSWER_REVEALED`;
- `DIAGNOSTIC_CORRECT`;
- `DIAGNOSTIC_WRONG`.

`ARCHITECTURE.md` defines progress ownership and the event/projection boundary.
MathStart v3.1 already defines Progress Algorithm v1, including event semantics,
weights, the update formula, and status thresholds. Its repository record is
[`specs/progress/BASELINE-v1.md`](specs/progress/BASELINE-v1.md).
R03 will formalize, implement, and test this existing baseline, not invent a
replacement. Changes to the formula require an ADR and unit tests.

Product-level expectations:

- correct independent work should produce stronger positive evidence than work completed after hints;
- reveal does not prove knowledge;
- a wrong final answer is weak negative evidence;
- a confirmed misconception is stronger negative evidence;
- every progress change must remain explainable from stored evidence.

---

## 15. Solution Analyzer

Solution Analyzer is a critical subsystem, but it is not used identically for every interaction mode.

### `SELF_CHECK`

No detailed solution analysis is required.

### `FINAL_ANSWER`

Normally uses deterministic answer validation.

A wrong answer alone does not reveal the exact cause.

### `STEP_BY_STEP`

Uses parser/normalizer plus transition validation.

When deterministic/domain logic finds a problematic step, Solution Analyzer may classify the error into the controlled mistake taxonomy.

LLM assistance may be used when semantic classification is useful, but it must pass structured validation and confidence gates.

### `STRUCTURED_SOLUTION`

Uses field/domain validation and may optionally use controlled LLM classification where appropriate.

The analyzer returns analysis.

It does not directly mutate long-term progress state.

---

## 16. Misconceptions

MathStart uses a controlled misconception taxonomy.

The LLM must not invent arbitrary persistent mistake codes.

A strong confirmed mistake should include:

- controlled mistake type;
- related skill;
- relevant attempt;
- relevant step when available;
- confidence;
- explanation/hint metadata as appropriate.

When evidence is insufficient, the system should return an unknown/unsupported/low-confidence outcome instead of fabricating certainty.

---

## 17. AI Tutor

AI Tutor provides contextual educational help.

Its context may include:

- current topic;
- relevant theory;
- relevant skills;
- prerequisite state;
- recent confirmed mistakes;
- current exercise/attempt context.

Tutor behavior is **hint-first**.

The first response should not automatically reveal the full solution when a smaller hint is pedagogically appropriate.

AI Tutor must not directly modify mastery/confidence.

It may explain, ask guiding questions, and generate help, but progress remains controlled by validated domain logic.

---

## 18. Adaptive Practice

When MathStart identifies a weak skill or prerequisite with sufficient evidence, it may start an adaptive practice session.

A practice session stores enough context to return the student to the original learning flow.

At minimum it should preserve:

- origin topic;
- target skill;
- return topic;
- session status;
- selected practice items/results.

The adaptive loop should:

1. identify a weak target skill/prerequisite;
2. choose suitable practice;
3. collect validated evidence;
4. finish the short targeted session after sufficient success;
5. return the student to the original topic.

The MVP must demonstrate this complete loop on the pilot domain.

---

## 19. Progress UI

The student should be able to inspect progress.

The MVP progress view should expose, in understandable form:

- skill status;
- mastery;
- confidence;
- topic-level aggregation;
- recent attempts;
- confirmed mistakes where appropriate.

The UI is a projection of backend state.

Frontend code must not become the authoritative source for mastery/confidence calculations.

---

## 20. Core MVP end-to-end scenario

The main demonstration scenario is a step-by-step linear-equation task.

Example:

`2(x+3)=10`

Possible student step:

`2x+3=10`

Expected system flow:

1. the exercise is delivered as `STEP_BY_STEP`;
2. the original problem state is stored independently from student steps;
3. the student submits the next step;
4. raw input is preserved;
5. parser/normalizer creates a normalized representation;
6. deterministic transition validation detects a non-equivalent transformation;
7. Solution Analyzer classifies the confirmed problem into a controlled mistake type, when evidence is sufficient;
8. the mistake is linked to the relevant skill;
9. structured analysis passes validation/confidence gates;
10. a validated knowledge event is created;
11. Progress Engine updates the affected skill state;
12. prerequisite state is inspected;
13. if a prerequisite is weak, Adaptive Practice starts targeted practice;
14. AI Tutor may provide hint-first support;
15. after sufficient successful practice, the student returns to the original topic.

This scenario must be demonstrable end-to-end in the final MVP.

---

## 21. Final-answer scenario

Example:

`-8 * (-4)`

Student submits:

`32`

Expected product behavior:

1. backend validates the result using server-side validation data;
2. a correct independent answer may create positive evidence;
3. an incorrect answer creates weak negative evidence;
4. the system does not infer a concrete misconception from the wrong number alone;
5. hint/reveal usage affects evidence semantics.

---

## 22. Product principles

### 22.1. Deterministic truth before LLM opinion

For supported mathematics, deterministic/domain validation is the primary source of correctness.

The LLM is used for semantic analysis, explanation, and tutoring where useful.

### 22.2. Evidence before progress

Long-term knowledge state changes only from explicit, validated evidence.

### 22.3. Explainability

The project must be able to explain why a student's progress changed.

### 22.4. Depth before breadth

A complete working vertical slice is more important than partial intelligent support across all grades and topics.

### 22.5. Existing content is preserved

The course project extends existing MathStart rather than discarding the content platform.

### 22.6. Human-controlled architecture

Coding agents may implement tasks, but architectural/product changes require repository documentation and human review.

---

## 23. MVP functional requirements

The MVP includes:

- registration/sign-in/sign-out;
- student profile and grade;
- three onboarding modes;
- browsing grades/topics/theory;
- skill mappings for pilot topics;
- four exercise interaction-mode contracts;
- `SELF_CHECK`;
- `FINAL_ANSWER`;
- `STEP_BY_STEP`;
- `STRUCTURED_SOLUTION` infrastructure;
- server-only answer/validation data;
- deterministic validation for supported pilot mathematics;
- first-problematic-step detection where supported;
- controlled mistake taxonomy;
- confirmed mistake -> skill mapping;
- knowledge events;
- user skill state;
- prerequisite graph;
- AI Tutor;
- hint-first behavior;
- adaptive practice;
- return to origin topic;
- attempt/error/hint/reveal history;
- progress map/view;
- LLM run metadata;
- public web deployment.

---

## 24. Non-goals for MVP

The following do not block MVP:

- OCR;
- handwritten-solution recognition;
- interactive geometry construction canvas;
- automatic validation of arbitrary geometric proofs;
- complete support for every school-mathematics task type;
- full structured migration of every existing grade 5-9 page before the pilot slice works;
- Neo4j or another dedicated graph database;
- microservices;
- Bayesian Knowledge Tracing;
- Item Response Theory;
- a complex ML progress model;
- unlimited LLM exercise generation in the main learning flow;
- teacher dashboards;
- parent dashboards;
- payments;
- voice mode;
- native mobile application;
- full-site RAG while relevant topic context can be supplied directly;
- a complete frontend rewrite solely for technology preference.

These items require separate post-MVP prioritization and, where architectural, an ADR.

---

## 25. Product success criteria

The MVP is successful when a reviewer can use the web application and observe a complete intelligent learning loop on the pilot topics.

At minimum, the demonstration should prove that:

1. the student can authenticate and open a pilot topic;
2. exercises use explicit interaction contracts;
3. validation data is not exposed through ordinary public exercise payloads;
4. a supported step-by-step solution can be analyzed;
5. the system can locate a problematic step or explicitly state that it cannot;
6. a confirmed error can be connected to a skill;
7. progress changes through knowledge events;
8. weak prerequisites can trigger adaptive practice;
9. AI Tutor uses relevant context without directly modifying progress;
10. the student can return to the original topic after targeted practice;
11. progress is visible;
12. the system is publicly deployable and demonstrable through a browser;
13. core behavior is covered by automated verification.

---

## 26. Product scope change policy

A change requires explicit review when it affects:

- MVP boundaries;
- primary user flows;
- interaction modes;
- progress semantics;
- knowledge-event semantics;
- onboarding behavior;
- AI Tutor trust boundaries;
- adaptive-practice behavior;
- exercise-answer secrecy;
- pilot subject scope.

Significant product decisions should be documented in a spec or ADR before or alongside implementation.

The coding agent must not silently expand product scope.

---

## 27. Relationship to other repository documents

Use this document to answer:

**What are we building and why?**

Use `ARCHITECTURE.md` to answer:

**How is the system structurally organized and which component owns what?**

Use `AGENTS.md` to answer:

**How should a coding agent work safely in this repository?**

Use `specs/` to answer:

**What exactly is the contract/behavior for a particular subsystem or feature?**

Use `docs/adr/` to answer:

**Why was a significant engineering decision accepted?**
