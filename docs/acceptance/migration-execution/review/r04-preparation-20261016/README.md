# R04 source ledger preparation

Status: **SOURCE_PREPARATION_ONLY**. This is not an R04 audit or runtime result.

`source-ledger.json` preserves every original frozen matrix row verbatim and adds
pending fields for implementation paths, task/slice, exact candidate/tree, test
IDs, raw results, negative-case dispositions, review findings, and limitations.
All statuses are **NOT_REVIEWED**. The source bytes are identical to accepted
`a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6`; SHA256:
`141cdf1e53dd6729549ec4674a798adb8d00b7f64254852ecec5b7e5df5a3aa9`.

The exact required set of **40 parity IDs** was checked, along with all **139
explicit negative cases** in 36 rows. The four F01–F04 rows use source reproduction
steps and positive visual criteria instead of a `negative_cases` field; those
were copied separately without inventing extra frozen assertions. Their complete
historical row remains available under `original_contract_row`, including source
context and original pending evidence. Historical personal names/deadlines are
preserved only as source provenance and are not new execution assignments.

The ledger also prepares **AT-M01–AT-M12** from the activated execution package.
AT-M12 splits `technical_release_ready: NOT_REVIEWED` from
`human_merge_closeout: HUMAN_PENDING`. It does not require R06/main merge as a
prerequisite to the earlier combined R04 technical audit. Runtime implementation,
security/recovery/data tests, exact combined-candidate review, final rehearsal,
and release-delta review remain required at their respective stages.

No frozen contract or application file was edited. Candidate fields intentionally
remain empty until the relevant implementation candidate and real results arrive.
