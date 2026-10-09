# CHECK canonicalization investigation v1

Input `8d958aeeb17da46839722441425ccbb5889e2ab7`; PostgreSQL16.15.
This is an implementation repair, separate from the approved three-column B01.
[Reproducible observations](check-canonicalization-v1.json) were obtained in a
new marked disposable V01 database, with two connection-local TEMP tables.

`users_consistent_onboarding` in the frozen physical catalog contains an ANY
comparison with a varchar-array-to-text-array cast. Re-emitting that deparsed
CHECK reparses the array into per-element text casts, so PostgreSQL prints a
different definition. Neither the CHECK condition nor its truth table changed,
but the previous target builder could not reproduce the exact physical baseline.

The original Django `Q(onboarding_mode__in=...)` corresponds to the IN expression
already represented in `users/migrations/0001_initial.py`. Emitting this expression
produces `pg_get_constraintdef` exactly equal to the frozen catalog string. All
42 combinations of complete={false,true,NULL}, seven mode values and
grade={NULL,1} yield the same PostgreSQL CHECK acceptance (`IS NOT FALSE`) as the
frozen expression. These diagnostic NULL cases do not override column NOT NULL.

The builder now emits that original IN expression for this one named CHECK,
retaining NOT NULL conditions and selected-grade requirement. Other CHECKs are
unchanged. The strict constraint comparator has no normalization, ignore rule
or equivalent-expression exception. Regression tests also replace the baseline
onboarding CHECK with CHECK(true) in a synthetic DB and require rejection before
stamp, proving that a real schema difference remains visible.

Frozen R02, Django migrations, historical investigation and application semantics
are unchanged. SQLAlchemy/Alembic revision v01_0001 consumes the repaired metadata
on fresh/A disposable rehearsal only; there are no deployed/applied target heads.
