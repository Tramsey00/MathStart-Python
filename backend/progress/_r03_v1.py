"""Pure Python R03 contract reference. No Django, database, or provider calls.

This is a reviewable oracle for specification fixtures, not runtime Progress or
Knowledge persistence. Numerical authority remains specs/progress/BASELINE-v1.md.
"""

from __future__ import annotations

import heapq
import re
from collections import defaultdict, deque
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Iterable, Mapping


class ContractError(ValueError):
    """A candidate graph or progress event violates the R03 contract."""


class IdentityConflict(ContractError):
    """An existing event identity was reused with conflicting content."""


PILOT_CODES = frozenset(
    {
        "integer_number_line",
        "negative_numbers",
        "sign_rules_add_sub",
        "sign_rules_mul_div",
        "distributive_property",
        "expand_parentheses",
        "combine_like_terms",
        "equation_balance",
        "linear_one_step",
        "linear_parentheses",
    }
)

PILOT_EDGES = frozenset(
    {
        ("integer_number_line", "negative_numbers"),
        ("negative_numbers", "sign_rules_add_sub"),
        ("negative_numbers", "sign_rules_mul_div"),
        ("sign_rules_add_sub", "distributive_property"),
        ("sign_rules_mul_div", "distributive_property"),
        ("distributive_property", "expand_parentheses"),
        ("sign_rules_add_sub", "combine_like_terms"),
        ("expand_parentheses", "combine_like_terms"),
        ("combine_like_terms", "equation_balance"),
        ("equation_balance", "linear_one_step"),
        ("linear_one_step", "linear_parentheses"),
        ("expand_parentheses", "linear_parentheses"),
        ("combine_like_terms", "linear_parentheses"),
    }
)

EXTERNAL_PREREQUISITE = {
    "code": "basic_arithmetic",
    "scope": "pilot_entry",
    "representation": "outside_skill_dependency",
}


def decimal_value(value: Any, label: str) -> Decimal:
    if isinstance(value, bool):
        raise ContractError(f"{label} must be a finite decimal")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ContractError(f"{label} must be a finite decimal") from exc
    if not result.is_finite():
        raise ContractError(f"{label} must be a finite decimal")
    return result


def clamp_round(value: Any) -> Decimal:
    """Clamp first, then ROUND_HALF_UP to two places, using Decimal."""
    amount = decimal_value(value, "projection value")
    amount = max(Decimal("0"), min(Decimal("100"), amount))
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def validate_graph(skill_codes: Iterable[str], edges: Iterable[Mapping[str, Any]]) -> tuple[str, ...]:
    """Validate a generic directed skill graph and return deterministic DAG order."""
    codes = list(skill_codes)
    if not codes or any(not isinstance(code, str) or not code for code in codes):
        raise ContractError("skill codes must be nonempty strings")
    if len(set(codes)) != len(codes):
        raise ContractError("duplicate skill code")
    known = set(codes)
    adjacency: dict[str, set[str]] = {code: set() for code in codes}
    indegree = {code: 0 for code in codes}
    seen: set[tuple[str, str]] = set()
    for edge in edges:
        if not isinstance(edge, Mapping):
            raise ContractError("edge must be an object")
        prerequisite = edge.get("prerequisite")
        dependent = edge.get("dependent")
        if not isinstance(prerequisite, str) or not isinstance(dependent, str):
            raise ContractError("edge endpoints must be skill codes")
        if prerequisite not in known or dependent not in known:
            raise ContractError("edge references unknown skill")
        if prerequisite == dependent:
            raise ContractError("self-edge is forbidden")
        pair = (prerequisite, dependent)
        if pair in seen:
            raise ContractError("duplicate edge")
        seen.add(pair)
        weight = decimal_value(edge.get("weight"), "edge weight")
        if not Decimal("0") < weight <= Decimal("1"):
            raise ContractError("edge weight must be in (0, 1]")
        adjacency[prerequisite].add(dependent)
        indegree[dependent] += 1
    ready = [code for code, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    order: list[str] = []
    while ready:
        code = heapq.heappop(ready)
        order.append(code)
        for dependent in sorted(adjacency[code]):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                heapq.heappush(ready, dependent)
    if len(order) != len(codes):
        raise ContractError("cycle detected")
    return tuple(order)


def validate_pilot_graph(skills: Mapping[str, Any], dependencies: Mapping[str, Any]) -> tuple[str, ...]:
    if skills.get("graph_version") != "pilot-v1" or dependencies.get("graph_version") != "pilot-v1":
        raise ContractError("graph_version must be pilot-v1 in both fixtures")
    if skills.get("external_prerequisite") != EXTERNAL_PREREQUISITE:
        raise ContractError("basic_arithmetic must be an external pilot-entry prerequisite")
    skill_rows = skills.get("skills")
    edge_rows = dependencies.get("edges")
    if not isinstance(skill_rows, list) or not isinstance(edge_rows, list):
        raise ContractError("skills and edges must be arrays")
    if any(not isinstance(row, Mapping) for row in skill_rows):
        raise ContractError("skill row must be an object")
    codes = [row.get("code") for row in skill_rows]
    if any(not isinstance(code, str) for code in codes):
        raise ContractError("skill code must be a string")
    if len(codes) != 10 or set(codes) != PILOT_CODES or len(set(codes)) != 10:
        raise ContractError("pilot-v1 requires exactly the ten approved skill codes")
    if "basic_arithmetic" in codes:
        raise ContractError("basic_arithmetic cannot be a pilot node")
    order = validate_graph(codes, edge_rows)
    pairs = [(row["prerequisite"], row["dependent"]) for row in edge_rows]
    if len(pairs) != 13 or set(pairs) != PILOT_EDGES:
        raise ContractError("pilot-v1 requires exactly the thirteen approved edges")
    if any(decimal_value(row["weight"], "edge weight") != Decimal("1.0") for row in edge_rows):
        raise ContractError("pilot-v1 edge weights must all be 1.0")
    return order


def ancestors(skill_id: str, max_depth: int = 2) -> tuple[tuple[str, int], ...]:
    """Return pilot prerequisites as (skill code, minimum depth), then code."""
    if not isinstance(skill_id, str) or skill_id not in PILOT_CODES:
        raise ContractError("unknown pilot skill")
    if type(max_depth) is not int or not 0 <= max_depth <= 2:
        raise ContractError("pilot ancestor max_depth must be 0, 1, or 2")
    parents: dict[str, set[str]] = {code: set() for code in PILOT_CODES}
    for prerequisite, dependent in PILOT_EDGES:
        parents[dependent].add(prerequisite)
    found: dict[str, int] = {}
    queue = deque([(skill_id, 0)])
    while queue:
        dependent, depth = queue.popleft()
        if depth == max_depth:
            continue
        for prerequisite in sorted(parents[dependent]):
            next_depth = depth + 1
            if prerequisite not in found:
                found[prerequisite] = next_depth
                queue.append((prerequisite, next_depth))
    return tuple(sorted(found.items(), key=lambda item: (item[1], item[0])))


EVENT_KINDS = frozenset(
    {
        "SELF_REPORTED_KNOWN",
        "CORRECT_FIRST_TRY",
        "CORRECT_AFTER_HINT",
        "WRONG_ATTEMPT",
        "MISCONCEPTION_DETECTED",
        "ANSWER_REVEALED",
        "DIAGNOSTIC_CORRECT",
        "DIAGNOSTIC_WRONG",
    }
)
ASSESSED_KINDS = EVENT_KINDS - {"SELF_REPORTED_KNOWN", "ANSWER_REVEALED"}
INDEPENDENT_KINDS = frozenset({"CORRECT_FIRST_TRY", "DIAGNOSTIC_CORRECT"})
POSITIVE_KINDS = frozenset({"CORRECT_FIRST_TRY", "CORRECT_AFTER_HINT", "DIAGNOSTIC_CORRECT"})

BASE_DELTAS = {
    "CORRECT_FIRST_TRY": (Decimal("6"), Decimal("5")),
    "CORRECT_AFTER_HINT": (Decimal("3"), Decimal("4")),
    "WRONG_ATTEMPT": (Decimal("-2"), Decimal("3")),
    "MISCONCEPTION_DETECTED": (Decimal("-5"), Decimal("5")),
    "DIAGNOSTIC_CORRECT": (Decimal("8"), Decimal("8")),
    "DIAGNOSTIC_WRONG": (Decimal("-6"), Decimal("8")),
}
DIFFICULTY_BANDS = {
    "easy": ("EASY", Decimal("0.8")),
    "medium": ("MEDIUM", Decimal("1.0")),
    "hard": ("HARD", Decimal("1.2")),
}
SUPPORTED_POLICIES = frozenset({"progress-v1"})


def normalize_difficulty(value: Any) -> tuple[str, Decimal]:
    if type(value) is int:
        value = {1: "easy", 2: "easy", 3: "medium", 4: "hard"}.get(value)
    if isinstance(value, str):
        band = DIFFICULTY_BANDS.get(value.lower())
        if band is not None:
            return band
    raise ContractError("missing or invalid assessed difficulty")


def utc_instant(value: Any, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})",
        value,
    ):
        raise ContractError(f"{label} must be a timezone-aware RFC 3339 string")
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"{label} must be a timezone-aware RFC 3339 string") from exc
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ContractError(f"{label} must include a timezone")
    return instant.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _required_string(event: Mapping[str, Any], field: str) -> str:
    value = event.get(field)
    if not isinstance(value, str) or not value:
        raise ContractError(f"{field} must be a nonempty string")
    return value


def validate_event(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Return an immutable-content canonical envelope suitable for comparison."""
    if not isinstance(raw, Mapping):
        raise ContractError("ProgressEvent must be an object")
    event = dict(raw)
    for field in ("event_id", "user_id", "skill_id", "event_kind", "policy_version"):
        _required_string(event, field)
    kind = event["event_kind"]
    if kind not in EVENT_KINDS:
        raise ContractError("unknown ProgressEvent kind")
    if event["policy_version"] not in SUPPORTED_POLICIES:
        raise ContractError("unsupported recorded policy_version")
    event["occurred_at"] = utc_instant(event.get("occurred_at"), "occurred_at")
    for field in ("hint_used", "reveal_used"):
        if field in event and type(event[field]) is not bool:
            raise ContractError(f"{field} must be boolean")
        event.setdefault(field, False)
    if kind == "SELF_REPORTED_KNOWN":
        if event.get("attempt_id") is not None or event.get("difficulty") is not None:
            raise ContractError("self-report has no attempt or difficulty")
        if event.get("completed_at") is not None:
            raise ContractError("self-report has no attempt completion")
        if event["hint_used"] or event["reveal_used"]:
            raise ContractError("self-report cannot use hint or reveal")
    else:
        _required_string(event, "attempt_id")
        _required_string(event, "evidence_ref")
        if kind in ASSESSED_KINDS:
            normalize_difficulty(event.get("difficulty"))
        elif event.get("difficulty") is not None:
            raise ContractError("reveal has no assessed difficulty")
    if event.get("completed_at") is not None:
        event["completed_at"] = utc_instant(event["completed_at"], "completed_at")
    if kind in ("CORRECT_FIRST_TRY", "CORRECT_AFTER_HINT", "DIAGNOSTIC_CORRECT", "DIAGNOSTIC_WRONG"):
        if event.get("completed_at") is None:
            raise ContractError("correct and diagnostic results require a completed attempt")
    if kind == "MISCONCEPTION_DETECTED":
        _required_string(event, "misconception_code")
        if event.get("confirmed") is not True:
            raise ContractError("misconception must be confirmed")
        if event.get("source_kind") not in ("STEP", "DOMAIN_VALIDATION", "STRUCTURED_FIELD"):
            raise ContractError("wrong final answer alone cannot confirm a misconception")
        if event["reveal_used"]:
            raise ContractError("revealed work cannot confirm a misconception")
    elif event.get("misconception_code") is not None:
        raise ContractError("misconception_code is only for confirmed misconception")
    if event.get("independent_evidence_rule") is not None:
        if kind not in ("WRONG_ATTEMPT", "MISCONCEPTION_DETECTED") or event["independent_evidence_rule"] != "distinct_validated_steps":
            raise ContractError("unsupported independent evidence rule")
    if kind == "CORRECT_FIRST_TRY" and (event["hint_used"] or event["reveal_used"]):
        raise ContractError("first-try correct cannot follow hint or reveal")
    if kind == "CORRECT_AFTER_HINT" and (not event["hint_used"] or event["reveal_used"]):
        raise ContractError("after-hint correct requires hint and no reveal")
    if kind in POSITIVE_KINDS and event["reveal_used"]:
        raise ContractError("revealed solution is not positive evidence")
    if kind == "ANSWER_REVEALED" and not event["reveal_used"]:
        raise ContractError("ANSWER_REVEALED requires reveal_used")
    return event


def source_identity(event: Mapping[str, Any]) -> tuple[str, str, str, str] | None:
    if event["event_kind"] == "SELF_REPORTED_KNOWN":
        return None
    return (event["attempt_id"], event["skill_id"], event["event_kind"], event["evidence_ref"])


def evidence_unit(event: Mapping[str, Any]) -> tuple[str, str, str, str] | None:
    if event["event_kind"] == "SELF_REPORTED_KNOWN":
        return None
    return (event["user_id"], event["skill_id"], event["attempt_id"], event["evidence_ref"])


def event_order(event: Mapping[str, Any]) -> tuple[str, str, str]:
    return (event["occurred_at"], event["event_id"], event["policy_version"])


def status_for(mastery: Decimal, confidence: Decimal, evidence_count: int, independent_recent: int) -> str:
    if evidence_count == 0:
        return "NOT_STARTED"
    if mastery >= 80 and confidence >= 60 and independent_recent >= 3:
        return "MASTERED"
    if mastery < 50 and confidence >= 30:
        return "WEAK"
    return "LEARNING"


def _recent_attempts(attempts: Mapping[str, Mapping[str, Any]]) -> tuple[list[str], int]:
    completed = [
        (facts["completed_at"], attempt_id, facts["independent_correct"])
        for attempt_id, facts in attempts.items()
        if facts["completed_at"] is not None
    ]
    completed.sort(key=lambda item: (item[0], item[1]))
    recent = completed[-10:]
    return [item[1] for item in recent], sum(bool(item[2]) for item in recent)


def _state_dict(
    mastery: Decimal,
    confidence: Decimal,
    evidence_count: int,
    last_updated: str | None,
    attempts: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    _, independent_count = _recent_attempts(attempts)
    return {
        "mastery": format(mastery, ".2f"),
        "confidence": format(confidence, ".2f"),
        "evidence_count": evidence_count,
        "status": status_for(mastery, confidence, evidence_count, independent_count),
        "last_updated": last_updated,
        "reducer_version": "progress-v1",
    }


def replay(events: Iterable[Mapping[str, Any]], user_id: str, skill_id: str) -> dict[str, Any]:
    """Reproject one user/skill from the complete immutable ProgressEvent log."""
    canonical = [validate_event(raw) for raw in events]
    by_id: dict[str, dict[str, Any]] = {}
    by_source: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for event in canonical:
        if event["event_id"] in by_id:
            raise IdentityConflict("duplicate event_id in immutable log")
        by_id[event["event_id"]] = event
        identity = source_identity(event)
        if identity is not None:
            if identity in by_source:
                raise IdentityConflict("duplicate attempt/skill/kind/evidence identity")
            by_source[identity] = event
    ordered = sorted(
        (event for event in canonical if event["user_id"] == user_id and event["skill_id"] == skill_id),
        key=event_order,
    )
    negative_by_unit: dict[tuple[str, str, str, str], str] = {}
    by_attempt: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in ordered:
        if event["event_kind"] in ("WRONG_ATTEMPT", "MISCONCEPTION_DETECTED"):
            unit = evidence_unit(event)
            previous_kind = negative_by_unit.get(unit)
            if previous_kind is not None and previous_kind != event["event_kind"]:
                raise ContractError("same evidence unit cannot contain WRONG_ATTEMPT and MISCONCEPTION_DETECTED ProgressEvents")
            negative_by_unit[unit] = event["event_kind"]
            by_attempt[event["attempt_id"]].append(event)
    for attempt_events in by_attempt.values():
        for index, first in enumerate(attempt_events):
            for second in attempt_events[index + 1:]:
                if evidence_unit(first) != evidence_unit(second):
                    if any(event.get("independent_evidence_rule") != "distinct_validated_steps"
                           for event in (first, second)):
                        raise ContractError("separate penalties in one attempt require an explicit distinct-evidence rule")
    mastery = Decimal("0.00")
    confidence = Decimal("0.00")
    evidence_count = 0
    last_updated: str | None = None
    assessed_seen = False
    self_report_seen = False
    repeat_counts: dict[str, int] = defaultdict(int)
    attempts: dict[str, dict[str, Any]] = {}
    revealed_attempts: set[str] = set()
    snapshots: list[dict[str, Any]] = []
    applied_ids: list[str] = []
    nonprojecting_ids: list[str] = []

    for event in ordered:
        # This dispatch is explicit so a future policy cannot silently reinterpret
        # historical events. R03 registers exactly one policy.
        if event["policy_version"] != "progress-v1":
            raise ContractError("unsupported recorded policy_version")
        kind = event["event_kind"]
        attempt_id = event.get("attempt_id")
        if attempt_id is not None:
            facts = attempts.setdefault(attempt_id, {"completed_at": None, "independent_correct": False})
            completed_at = event.get("completed_at")
            if completed_at is not None:
                if facts["completed_at"] not in (None, completed_at):
                    raise ContractError("conflicting completion time for one attempt/skill")
                facts["completed_at"] = completed_at
        else:
            facts = None

        if kind == "SELF_REPORTED_KNOWN":
            if self_report_seen or assessed_seen:
                raise ContractError("self-report allowed once before assessed event")
            self_report_seen = True
            mastery = Decimal("60.00")
            confidence = Decimal("15.00")
            evidence_count += 1
            last_updated = event["occurred_at"]
            applied_ids.append(event["event_id"])
        elif kind == "ANSWER_REVEALED":
            revealed_attempts.add(attempt_id)
            nonprojecting_ids.append(event["event_id"])
        else:
            assessed_seen = True
            if kind in POSITIVE_KINDS and attempt_id in revealed_attempts:
                raise ContractError("positive evidence after full reveal on same attempt")
            _, difficulty_coeff = normalize_difficulty(event["difficulty"])
            base_delta, confidence_delta = BASE_DELTAS[kind]
            repeat_coeff = Decimal("1.0")
            if kind == "MISCONCEPTION_DETECTED":
                code = event["misconception_code"]
                repeat_coeff = (Decimal("1.0"), Decimal("1.25"), Decimal("1.5"))[
                    min(repeat_counts[code], 2)
                ]
                repeat_counts[code] += 1
            mastery = clamp_round(mastery + base_delta * difficulty_coeff * repeat_coeff)
            confidence = clamp_round(confidence + confidence_delta)
            evidence_count += 1
            last_updated = event["occurred_at"]
            applied_ids.append(event["event_id"])
            independent = kind in INDEPENDENT_KINDS and not event["hint_used"] and not event["reveal_used"]
            if independent and facts is not None and facts["completed_at"] is not None:
                facts["independent_correct"] = True
                repeat_counts.clear()
        snapshots.append({"event_id": event["event_id"], "state": _state_dict(
            mastery, confidence, evidence_count, last_updated, attempts
        )})

    recent_ids, independent_count = _recent_attempts(attempts)
    return {
        "state": _state_dict(mastery, confidence, evidence_count, last_updated, attempts),
        "recent_window": {
            "attempt_ids": recent_ids,
            "independent_correct_count": independent_count,
        },
        "ordered_event_ids": [event["event_id"] for event in ordered],
        "applied_event_ids": applied_ids,
        "nonprojecting_event_ids": nonprojecting_ids,
        "snapshots": snapshots,
    }


def ingest_event(
    existing: Iterable[Mapping[str, Any]], incoming: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any], bool]:
    """Append or return an exact duplicate; reproject late events atomically in memory."""
    log = [validate_event(raw) for raw in existing]
    candidate = validate_event(incoming)
    candidate_identity = source_identity(candidate)
    for old in log:
        if old["event_id"] == candidate["event_id"]:
            if old == candidate:
                return log, replay(log, candidate["user_id"], candidate["skill_id"]), True
            raise IdentityConflict("event_id reused with conflicting payload")
        if candidate_identity is not None and source_identity(old) == candidate_identity:
            raise IdentityConflict("source identity reused with conflicting payload")
    proposed = log + [candidate]
    projection = replay(proposed, candidate["user_id"], candidate["skill_id"])
    return proposed, projection, False
