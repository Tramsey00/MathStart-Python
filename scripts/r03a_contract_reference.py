"""Pure R03A boundary DTO/mirror oracle. No ORM, HTTP, providers or persistence.

The frozen R03 reducer is the sole numerical implementation. Authority contexts
are explicitly supplied synthetic domain records, not client authentication.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Iterable, Mapping
from uuid import UUID

from scripts import r03_contract_reference as frozen

ContractError = frozen.ContractError
IdentityConflict = frozen.IdentityConflict
COMPLETION_POLICY = "progress-v1.1"
OUTCOMES = frozenset({"CORRECT", "WRONG", "UNSUPPORTED", "INDETERMINATE"})
FIELDS = frozenset({"completion_id", "user_id", "skill_id", "attempt_id",
                    "outcome", "independent_correct", "completed_at", "policy_version"})
AUTHORITY_VERSIONS = frozenset({"assessment-completion-v1", "legacy-completion-v1"})


def validate_completion_fact(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Validate/copy shape and canonical content; this alone grants no authority."""
    if not isinstance(raw, Mapping) or set(raw) != FIELDS:
        raise ContractError("CompletionFact requires exactly the eight DTO fields")
    fact = dict(raw)
    for field in FIELDS - {"independent_correct"}:
        if not isinstance(fact[field], str) or not fact[field]:
            raise ContractError(f"{field} must be a nonempty string")
    try:
        if str(UUID(fact["completion_id"])) != fact["completion_id"]:
            raise ValueError("noncanonical UUID")
    except ValueError as exc:
        raise ContractError("completion_id must be a canonical lowercase UUID") from exc
    if fact["skill_id"] not in frozen.PILOT_CODES:
        raise ContractError("unknown pilot skill")
    if fact["policy_version"] != COMPLETION_POLICY:
        raise ContractError("unsupported CompletionFact policy_version")
    if fact["outcome"] not in OUTCOMES:
        raise ContractError("unknown assessed completion outcome")
    if type(fact["independent_correct"]) is not bool:
        raise ContractError("independent_correct must be boolean")
    if fact["independent_correct"] and fact["outcome"] != "CORRECT":
        raise ContractError("independent_correct requires CORRECT outcome")
    if not re.search(r"(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])$", fact["completed_at"]):
        raise ContractError("completed_at must have a valid RFC 3339 timezone offset")
    try:
        fact["completed_at"] = frozen.utc_instant(fact["completed_at"], "completed_at")
    except OverflowError as exc:
        raise ContractError("completed_at UTC instant is outside representable range") from exc
    return fact


def completion_identity(fact: Mapping[str, Any]) -> str:
    return fact["completion_id"]


def completion_source_identity(fact: Mapping[str, Any]) -> tuple[str, str]:
    return fact["attempt_id"], fact["skill_id"]


def _unique_facts(raw_facts: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Check both identities globally, before selecting a projection scope."""
    by_id: dict[str, dict[str, Any]] = {}
    by_source: dict[tuple[str, str], dict[str, Any]] = {}
    attempts: dict[str, tuple[str, str]] = {}
    for raw in raw_facts:
        fact = validate_completion_fact(raw)
        key, source = completion_identity(fact), completion_source_identity(fact)
        for old in (by_id.get(key), by_source.get(source)):
            if old is not None and old != fact:
                raise IdentityConflict("CompletionFact identity/source reused with different immutable payload")
        binding = (fact["user_id"], fact["completed_at"])
        if fact["attempt_id"] in attempts and attempts[fact["attempt_id"]] != binding:
            raise ContractError("inconsistent attempt owner or cross-skill completion instant")
        attempts[fact["attempt_id"]] = binding
        by_id[key] = fact
        by_source[source] = fact
    return sorted(by_id.values(), key=completion_identity)


def _authority_records(authority: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if (not isinstance(authority, Mapping)
            or set(authority) != {"context_version", "records"}
            or not isinstance(authority["context_version"], str)
            or authority["context_version"] not in AUTHORITY_VERSIONS
            or not isinstance(authority["records"], list)):
        raise ContractError("explicit trusted completion authority context required")
    facts = []
    for record in authority["records"]:
        if not isinstance(record, Mapping) or set(record) != {"fact", "attempt_state", "mapped_skill_ids"}:
            raise ContractError("invalid trusted completion record")
        fact = validate_completion_fact(record["fact"])
        expected_state = ("COMPLETED" if authority["context_version"] == "assessment-completion-v1"
                          else "LEGACY_COMPLETION")
        if record["attempt_state"] != expected_state:
            raise ContractError("authority record is not a finalized completion")
        mapped = record["mapped_skill_ids"]
        if (not isinstance(mapped, list) or not mapped
                or any(not isinstance(skill, str) or skill not in frozen.PILOT_CODES for skill in mapped)
                or len(set(mapped)) != len(mapped) or fact["skill_id"] not in mapped):
            raise ContractError("authoritative bound-version skill mapping mismatch")
        facts.append(fact)
    return _unique_facts(facts)


def _validated_mirror(facts, authority) -> list[dict[str, Any]]:
    mirror = _unique_facts(facts)
    if not mirror:
        return mirror
    source = {completion_identity(f): f for f in _authority_records(authority)}
    for fact in mirror:
        if source.get(completion_identity(fact)) != fact:
            raise ContractError("DTO disagrees with trusted immutable completion authority")
    return mirror


@dataclass(frozen=True, init=False)
class NumericalReplay:
    """Immutable reusable frozen-event result; fact ingestion never reapplies it.

    JSON strings detach both inputs and output. Properties return fresh copies,
    preventing a caller's mutable result/DTO from changing this cached evidence.
    """
    user_id: str
    skill_id: str
    _events_json: str
    _result_json: str

    def __init__(self, events: Iterable[Mapping[str, Any]], user_id: str, skill_id: str):
        if (not isinstance(user_id, str) or not user_id or not isinstance(skill_id, str)
                or skill_id not in frozen.PILOT_CODES):
            raise ContractError("invalid user/skill projection scope")
        canonical = [frozen.validate_event(event) for event in events]
        result = frozen.replay(canonical, user_id, skill_id)
        object.__setattr__(self, "user_id", user_id)
        object.__setattr__(self, "skill_id", skill_id)
        object.__setattr__(self, "_events_json", json.dumps(canonical, sort_keys=True))
        object.__setattr__(self, "_result_json", json.dumps(result, sort_keys=True))

    @property
    def events(self):
        return json.loads(self._events_json)

    @property
    def result(self):
        return json.loads(self._result_json)


def _coexistence(events, mirror):
    by_source = {completion_source_identity(f): f for f in mirror}
    owners = {f["attempt_id"]: f["user_id"] for f in mirror}
    for event in events:
        attempt = event.get("attempt_id")
        if attempt in owners and event["user_id"] != owners[attempt]:
            raise ContractError("event/fact attempt owner mismatch")
        fact = by_source.get((attempt, event["skill_id"]))
        if fact is None:
            continue
        if event.get("completed_at") is not None and event["completed_at"] != fact["completed_at"]:
            raise ContractError("conflicting inline event/fact completion time")
        kind = event["event_kind"]
        if kind in frozen.POSITIVE_KINDS:
            independent = kind in frozen.INDEPENDENT_KINDS and not event["hint_used"] and not event["reveal_used"]
            if fact["outcome"] != "CORRECT" or fact["independent_correct"] != independent:
                raise ContractError("final-result eligibility/outcome contradiction")
        elif kind == "DIAGNOSTIC_WRONG":
            if fact["outcome"] != "WRONG" or fact["independent_correct"]:
                raise ContractError("final-result eligibility/outcome contradiction")
        # Wrong steps and a later reveal cannot determine/rewrite final outcome.


def replay_completion_facts(
    numerical: NumericalReplay, facts: Iterable[Mapping[str, Any]], *, authority=None,
) -> dict[str, Any]:
    """Replay the full mirror using cached numbers, without numerical application."""
    if not isinstance(numerical, NumericalReplay):
        raise ContractError("validated NumericalReplay required")
    mirror = _validated_mirror(facts, authority)
    events = numerical.events
    _coexistence(events, mirror)
    selected = [f for f in mirror if f["user_id"] == numerical.user_id and f["skill_id"] == numerical.skill_id]
    recent = sorted(selected, key=lambda f: (f["completed_at"], f["attempt_id"]))[-10:]
    count = sum(f["independent_correct"] for f in recent)
    baseline = numerical.result
    state = dict(baseline["state"])
    state["status"] = frozen.status_for(Decimal(state["mastery"]), Decimal(state["confidence"]),
                                        state["evidence_count"], count)
    state["reducer_version"] = COMPLETION_POLICY
    delivered = {f["attempt_id"] for f in selected}
    gaps = sorted({e["attempt_id"] for e in events
                   if e["user_id"] == numerical.user_id and e["skill_id"] == numerical.skill_id
                   and e.get("completed_at") is not None and e["attempt_id"] not in delivered})
    return {
        "state": state,
        "recent_window": {"attempt_ids": [f["attempt_id"] for f in recent],
                          "independent_correct_count": count},
        "ordered_event_ids": baseline["ordered_event_ids"],
        "applied_event_ids": baseline["applied_event_ids"],
        "nonprojecting_event_ids": baseline["nonprojecting_event_ids"],
        "legacy_snapshots": baseline["snapshots"],
        "completion_gaps": gaps,
    }


def replay_v1_1(events, facts, user_id, skill_id, *, authority=None):
    """Full replay; event delivery constructs a new numerical cache explicitly."""
    return replay_completion_facts(NumericalReplay(events, user_id, skill_id), facts, authority=authority)


def ingest_completion_fact(existing, incoming, numerical: NumericalReplay, *, authority=None):
    """Return a proposed detached mirror/result/retry flag; rejection is atomic."""
    old = _validated_mirror(existing, authority)
    candidate = validate_completion_fact(incoming)
    proposed = _unique_facts(old + [candidate])
    if candidate["user_id"] != numerical.user_id or candidate["skill_id"] != numerical.skill_id:
        raise ContractError("incoming fact must match target user/skill scope")
    duplicate = candidate in old
    result = replay_completion_facts(numerical, proposed, authority=authority)
    return proposed, result, duplicate


def import_progress_v1_completions(events, user_id, skill_id, *, authority):
    """Explicit legacy import; IDs/outcomes come only from supplied source DTOs."""
    numerical = NumericalReplay(events, user_id, skill_id)
    if not isinstance(authority, Mapping) or authority.get("context_version") != "legacy-completion-v1":
        raise ContractError("explicit versioned legacy completion context required")
    context = _authority_records(authority)
    sources = {completion_source_identity(f): f for f in context}
    completed = {}
    independent = set()
    for event in sorted(numerical.events, key=frozen.event_order):
        if event["user_id"] != user_id or event["skill_id"] != skill_id:
            continue
        attempt = event.get("attempt_id")
        if event.get("completed_at") is not None:
            completed[attempt] = event["completed_at"]
        if (event["event_kind"] in frozen.INDEPENDENT_KINDS
                and not event["hint_used"] and not event["reveal_used"]):
            independent.add(attempt)
    imported = []
    for attempt, stamp in completed.items():
        fact = sources.get((attempt, skill_id))
        if (fact is None or fact["user_id"] != user_id or fact["completed_at"] != stamp
                or fact["independent_correct"] != (attempt in independent)):
            raise ContractError("legacy completion source context missing or inconsistent")
        imported.append(fact)
    result = replay_completion_facts(numerical, imported, authority=authority)
    legacy = numerical.result
    for field in ("mastery", "confidence", "evidence_count", "status", "last_updated"):
        if result["state"][field] != legacy["state"][field]:
            raise ContractError("legacy state parity mismatch")
    if result["recent_window"] != legacy["recent_window"]:
        raise ContractError("legacy recent-window parity mismatch")
    return _unique_facts(imported), result
