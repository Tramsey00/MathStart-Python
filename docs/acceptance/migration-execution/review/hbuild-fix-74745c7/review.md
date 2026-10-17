# H-BUILD delta review at 74745c7

Reviewed SHA `74745c72ae58d4cd4f5dd04344ad2ad3e82dea75`, tree
`3626c53597749902618d82b04711d6dccefdabce`, compared with
`2b3a60da04346ed8c747ec35c3fe751bbbb9f9cd`.

Result: **CHANGES_REQUIRED**. **HBUILD-02 CLOSED in this reviewed delta**;
**HBUILD-01 remains OPEN**. This is a historical intermediate review; a later
candidate requires its own disposition. It is not full V04 or I02/I03 acceptance.

The writer now refuses PostgreSQL READ COMMITTED for all direct consumers;
the CLI starts REPEATABLE READ READ ONLY. The independent nine-case run passed,
zero skips, 72.319 seconds, using the own PostgreSQL review DB and no-Django
environment. This includes a real second-connection catalogue update, proving
the repeatable snapshot retains the previous label. Trusted-source Git matching
and untracked source checks were also read in the delta. The author's separate
ten-case result, including the legacy oracle, was reported independently by the
author and is not relabelled as the reviewer's nine-case run.

The original alternate grade/subject/section test now refuses the changed slug
triple. However, independent `review-probes.json` reproduces a remaining hole:
topic `10-klass-naturalnye-chisla-povtorenie` keeps grade ID 6 and section ID 61,
but subject ID 12 is changed to subject ID 3. Both subjects have slug `algebra`;
subject 3 belongs to grade 3. The new independent-slug comparisons accept this
cross-grade substitution, and both writer and receipt verifier export subject 3.

HBUILD-01 required regression: resolve the source's composite catalogue identity
or verify the subject's grade and section's subject alongside the source slugs.
It must refuse this case before finalizing an artifact. The transaction-local
mutation was rolled back and temporary artifacts removed. Exact results are in
`independent-tests.log` and `review-probes.json`. Code remained read-only and the
detached candidate checkout was clean.
