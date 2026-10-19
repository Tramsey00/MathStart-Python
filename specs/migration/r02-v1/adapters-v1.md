# §17 framework adapter contracts v1.0.0

PROPOSED; original_result, historical task IDs, scopes, approvals, original PRs,
frozen manifests/pins/tests and bytes are preserved. New framework references
are here only. [Old-to-new index](../../../docs/acceptance/MS7-MIG-R02/old-to-new-evidence.json)
binds source input to R02 evidence and future implementation obligations.
Historical pending R02A/R03A wording is not current rejection: R01 D08 receipt
verified Vladimir's07.10 comments; no approval is backdated/transferred to R02.

| Original | Framework-facing contract | Preserved authority / required future proof |
| --- | --- | --- |
| R02 | public DTO -> React mode dispatcher; server validation -> isolated Python service, HTTP controller only orchestration; no Django serializer/model assumption | Four exact modes and typed ordered steps; input_schema UI vs step_schema representation, raw/normalized separation, hint/reveal/secret split, immutable bound version. I01 dispatcher remains fixture-only; no assessed runtime claim. |
| R03 | Content topic read/reference adapter uses existing ContentPage ID; future Knowledge repository, Progress evidence/replay service |10 skills/13 prerequisite->dependent edges, external basic_arithmetic, Decimal ROUND_HALF_UP after each event, global identities/replay ordering and single penalty. No future ORM tables created. Content owns TopicSkill -> Knowledge, Knowledge never imports Content. |
| MS7-R02A | strict raw-body FastAPI boundary plus cookie/session/CSRF bridge; separate content/staff delivery addendum; explicit route registration | canonical37 operations, DTO/status limits, owner404, revisions, receipts/exposure/permanent source identity; only8 API operations currently implemented. No generated OAS takeover/default422/307/coercion. |
| MS7-R03A | Assessment authoritative CompletionFact -> immutable internal DTO -> Progress mirror/replay; future SQLAlchemy units of work | Dual global completion_id and attempt+skill uniqueness, immutable owner/outcome/time/independent flag, server trusted context, neutral history doesn't alter numbers; no public write API or invented runtime. |

Future dependencies: content -> knowledge for Content-owned mapping; knowledge
has no content dependency; math_validation pure; progress -> users/knowledge;
assessment -> users/content/knowledge/math_validation/solution_analyzer/progress;
solution_analyzer -> math_validation/knowledge/llm/progress service;
adaptive_practice -> progress/knowledge/assessment reads;
ai_tutor -> content/knowledge/progress/assessment/llm reads; llm -> infrastructure.
Dependency DAG and negative-cycle check are in the package verifier. This is
accepted domain direction represented as a contract, not imports of absent apps.

Future assessed acquisition: owner/version exposure before attempt; exact replay
before revision/state; immutable draft snapshot/version/step ordering; finalized
positive-credit guard permanent; help committed before finalization disqualifies
independence, later help doesn't revoke completed decisions. R03A dual identities
checked before scope filtering; facts require server Assessment authority and
COMPLETED lifecycle, never client independent_correct. Neutral outcome remains
history; only validated ProgressEvent affects numbers. Use frozen pure oracles
directly for synthetic comparison; implementing a copied formula here is forbidden.

Raw input bytes/Unicode/array order survive transport before normalization;
unsupported syntax -> UNSUPPORTED, not WRONG/misconception. A final wrong answer
alone cannot identify misconception. Synthetic exchanges do not execute target
HTTP, database locks, renderer or LLM. Current migration real identity/content
tests and later V/I API/PG/browser tests are independent additional evidence.

Old verification IDs map to future adapters in the matrix: Django check ->
config/startup/routes; migration check -> metadata/Alembic drift/one head/reviewed
SQL; source/quality/integrity keep full semantics; fresh smoke -> target
fresh+bootstrap twice+assets/SSG; current Node semantic tests -> React lifecycle/
browser evidence. This is an R03 handoff only, not a Harness/CI rewrite in R02.
