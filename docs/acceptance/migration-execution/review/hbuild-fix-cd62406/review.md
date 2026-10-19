# H-BUILD parent-identity fix: independent disposition

Result: **VERIFIED_IN_SCOPE** for the immutable H-BUILD-INPUTS dependency needed
by the current I02/I03 block. **HBUILD-01 CLOSED** at
`cd62406c6e0ff029c6e4445e8f015243731fd194`, tree
`03991ef93a98e65e8425b2d5c0a3b9a7e3976378`, compared with
`74745c72ae58d4cd4f5dd04344ad2ad3e82dea75`.

**HBUILD-02 remains CLOSED**: the independently verified REPEATABLE READ guard
and CLI snapshot fix from 74745c7 are unchanged in this delta. Its nine-test,
72.319-second independent result is retained in the separate intermediate review.
Neither closure is full V04, publication activation/recovery, I02/I03 completion,
combined R04, human acceptance, deployment, or main-merge approval.

Read delta: the writer explicitly checks that a page's subject belongs to its
grade and its section belongs to its subject, in addition to matching source
slugs. A new real PostgreSQL regression covers the previously accepted same-slug
cross-grade substitution. No identity/auth WIP is present in the reviewed delta.

Independent retest on the exclusively reserved synthetic PostgreSQL review DB,
Python 3.12.14, own accepted-lock no-Django environment:

| Scenario | Actual result |
| --- | --- |
| Complete immutable 279-page/263-topic public manifest/private exclusion | PASS |
| Coherent alternate grade/subject/section triple conflicts with unchanged source | PASS: refused before finalized artifact |
| Same `algebra` slug but subject from another grade | PASS: refused before finalized artifact |
| Preserved reviewer reproduction, using independently selected foreign same-slug subject | REFUSED with SourceError |

Three tests PASS, zero failures/errors/skips, **24.959 seconds**. The separate
reviewer reproduction also refused the formerly accepted change. Exact reviewed
SHA/tree, start/end, Python/no-Django facts, counts, and cleanup are recorded in
`review-probes.json`; raw test output is `independent-tests.log`.

The first attempt after interruption failed before collection because the own
review database no longer existed. That environment failure is preserved as
`environment-failure-tests.log` and `environment-failure-wrapper.log`, not counted
as a pass. The absent, exclusively reserved DB was recreated with its V01 marker,
migrated fresh, and bootstrapped twice to 279 pages; recovery output is retained
as `environment-recovery.log`. The successful retry is a distinct execution.

The source checkout remained read-only. Synthetic identity mutations rolled back,
temporary artifacts were removed, and the reserved DB is retained for combined
I02/I03 integration checks. Only this dependency slice is cleared for technical
integration; the coordinator must bind the actual combined frontend/backend
candidate, input receipt, output artifact, real serving/browser evidence and
publish/handoff records separately. No historical human approval is synthesized.
