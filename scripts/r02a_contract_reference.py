"""MS7-R02A artifact validation and serial transaction oracle; no product runtime.

This model checks legal linearizations supplied by fixtures. It has no ORM,
HTTP server, mathematical checker, durable receipts or Progress projection.
"""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid5

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "specs/api"
NAMESPACE = UUID("00000000-0000-4000-8000-000000000001")
SECRETS = frozenset({"answer_key", "validation_spec", "canonical_solution",
                     "accepted_variants", "checker", "reference_solution",
                     "hidden_rule", "hidden_rules", "correct_answer", "correct_value",
                     "is_correct", "expected_answer", "hidden_accepted_variants"})
FORMATS = FormatChecker()


@FORMATS.checks("date-time", raises=(ValueError, TypeError))
def valid_timestamp(value):
    """Calendar validation without optional jsonschema format dependencies."""
    if not isinstance(value, str):
        return True  # the schema's type check rejects non-strings
    return datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None


def load(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def request_digest(owner: str, operation: str, route: str, body: dict) -> str:
    return digest({"owner": owner, "operation": operation,
                   "canonical_route": route, "body": body,
                   "expected_revision": body.get("expected_revision")})


def validator(name: str) -> Draft202012Validator:
    bundle = load(API / "schemas/dto-v1.schema.json")
    registry = Registry().with_resource(bundle["$id"], Resource.from_contents(bundle))
    schema = load(API / "schemas/scenario-v1.schema.json") if name == "ConcurrencyScenario" else {"$ref": bundle["$id"] + "#/$defs/" + name}
    return Draft202012Validator(schema,
                                registry=registry, format_checker=FORMATS)


def assert_public(value: object) -> None:
    if isinstance(value, dict):
        forbidden = SECRETS.intersection(k.casefold() for k in value)
        if forbidden:
            raise ValueError(f"Private public field(s): {sorted(forbidden)}")
        # Input shape metadata must not smuggle correctness through a field name.
        if str(value.get("name", "")).casefold() in SECRETS:
            raise ValueError("Private input field name")
        for item in value.values():
            assert_public(item)
    elif isinstance(value, list):
        for item in value:
            assert_public(item)


def validate_exercise(exercise: dict) -> None:
    validator("PublicExerciseDTO").validate(exercise)
    assert_public(exercise)
    identity = exercise["exercise_version"]
    if not (exercise["contract_version"] == exercise["version"] == identity["version"]
            == identity["contract_version"] and identity["exercise_id"] == exercise["id"]):
        raise ValueError("Version aliases / exercise identity disagree")
    band = {1: "easy", 2: "easy", 3: "medium", 4: "hard"}[exercise["difficulty_level"]]
    if exercise["difficulty"] != band:
        raise ValueError("Difficulty band disagrees with level")
    mode = exercise["interaction_mode"]
    if mode in {"FINAL_ANSWER", "STRUCTURED_SOLUTION"} and exercise["input_schema"] is None:
        raise ValueError("Input mode requires public input schema")
    if mode in {"STEP_BY_STEP", "STRUCTURED_SOLUTION"} and exercise["step_schema"] is None:
        raise ValueError("Step mode requires public step schema")
    if mode == "SELF_CHECK" and (exercise["input_schema"] or exercise["step_schema"]):
        raise ValueError("SELF_CHECK has no assessed input")


def validate_draft(draft: dict) -> None:
    validator("AttemptDraft").validate(draft)
    numbers = [s["step_no"] for s in draft["steps"]]
    if numbers != list(range(1, len(numbers) + 1)):
        raise ValueError("Steps must be unique, contiguous and ordered from one")


def walk(value: object):
    yield value
    if isinstance(value, dict):
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


def resolve_ref(reference: str, document: Path) -> tuple[object, Path]:
    filename, _, fragment = reference.partition("#")
    if ":" in filename:
        raise ValueError("Remote references are not allowed in the public contract")
    target = (document.parent / filename).resolve() if filename else document
    if not target.is_relative_to(API.resolve()):
        raise ValueError("Reference escapes contract directory")
    value = load(target)
    if fragment and not fragment.startswith("/"):
        raise ValueError("Only JSON Pointer references are used")
    for part in fragment.split("/")[1:]:
        key = part.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value, target


def validate_artifacts() -> dict:
    oas = load(API / "openapi-v1.json")
    structural = load(API / "schemas/openapi-3.1-2025-09-15.schema.json")
    Draft202012Validator(structural, format_checker=FormatChecker()).validate(oas)
    bundle = load(API / "schemas/dto-v1.schema.json")
    Draft202012Validator.check_schema(bundle)
    visited = set()
    def visit(value, document):
        for node in walk(value):
            if isinstance(node, dict) and "$ref" in node:
                key = (document, node["$ref"])
                if key not in visited:
                    visited.add(key)
                    child, target = resolve_ref(node["$ref"], document)
                    assert_public(child)
                    visit(child, target)
    visit(oas, API / "openapi-v1.json")
    for name, schema in bundle["$defs"].items():
        Draft202012Validator.check_schema(schema)
        assert_public(schema)
        validator(name)  # build the offline registry as well
    Draft202012Validator.check_schema(load(API / "schemas/scenario-v1.schema.json"))
    return oas


class ContractOracle:
    """Sequential committed actions, representing one legal lock order per fixture."""

    def __init__(self, initial: dict):
        self.owner = initial["owner"]
        self.version_id = initial["exercise_version_id"]
        self.version = initial.get("version", 1)
        self.archived = initial.get("archived", False)
        self.attempts = {}
        self.exposure = {"max_help_level": 0, "revealed": False, "credited": False}
        self.receipts = {}
        # Domain help-source facts outlive temporary HTTP replay receipts.
        # Retain the original digest and observation, not a second help action.
        self.help_sources = {}
        self.action_ids = set()
        self.positive = 0
        self.completions = 0
        self.help_actions = 0

    def error(self, code, status, attempt_id=None):
        detail = {"code": code, "message": "Resource unavailable" if status == 404 else code,
                  "field_errors": {}, "retryable": status == 503,
                  "request_id": str(NAMESPACE)}
        if code == "REVISION_CONFLICT":
            detail.update(current_revision=self.attempts[attempt_id]["revision"],
                          reload_url=f"/api/v1/attempts/{attempt_id}/")
        return {"status": status, "body": {"error": detail}}

    def ok(self, **data):
        return {"status": 200, "body": {"data": data, "meta": {"request_id": str(NAMESPACE)}}}

    def apply(self, action: dict) -> dict:
        kind = action["action"]
        attempt_id = action.get("attempt_id")
        if kind == "expire_receipts":
            self.receipts.clear()
            return self.ok()
        if kind == "archive":
            self.archived = True
            return self.ok()
        if kind == "create":
            if action.get("version", self.version) != self.version:
                return self.error("VERSION_CONFLICT", 409)
            if self.archived:
                return self.error("STATE_CONFLICT", 409)
            previous = action.get("previous_attempt_id")
            if previous and previous not in self.attempts:
                return self.error("NOT_FOUND", 404)
            if attempt_id in self.attempts:
                return self.error("STATE_CONFLICT", 409)
            self.attempts[attempt_id] = {"state": "STARTED", "revision": 1,
                "draft": {"payload": {}, "steps": []}, "version": self.version,
                "mode": action.get("mode", "FINAL_ANSWER"), "independent": False,
                "snapshot_digest": None, "operation_id": None, "positive": False}
            return self.ok(state="STARTED", revision=1, version=self.version)
        attempt = self.attempts.get(attempt_id)
        # Owner check precedes receipt lookup / revision disclosure.
        if action.get("owner", self.owner) != self.owner or attempt is None:
            return self.error("NOT_FOUND", 404)
        if kind == "read":
            return self.ok(**copy.deepcopy(attempt))
        body = action.get("body", {})
        suffix = "hints" if kind == "hint" else kind
        route = f"/api/v1/attempts/{attempt_id}/{suffix}/"
        operation = {"submit": "submit_attempt", "hint": "request_hint", "reveal": "reveal_attempt", "abandon": "abandon_attempt", "draft": "update_draft"}.get(kind, kind)
        receipt_key = (self.owner, operation, action.get("key"))
        rdigest = request_digest(self.owner, operation, route, body)
        if action.get("key") and receipt_key in self.receipts:
            prior_digest, result = self.receipts[receipt_key]
            return copy.deepcopy(result) if prior_digest == rdigest else self.error("IDEMPOTENCY_CONFLICT", 409)
        if action.get("key") and kind in {"hint", "reveal"} and receipt_key in self.help_sources:
            prior_digest, observation = self.help_sources[receipt_key]
            if prior_digest != rdigest:
                return self.error("IDEMPOTENCY_CONFLICT", 409)
            return self.ok(**copy.deepcopy(observation))
        if body.get("contract_version", self.version) != attempt["version"]:
            return self.error("VERSION_CONFLICT", 409)
        result = self._mutate(kind, attempt_id, attempt, body)
        if action.get("key") and result["status"] in {200, 202}:
            self.receipts[receipt_key] = (rdigest, copy.deepcopy(result))
            if kind in {"hint", "reveal"}:
                self.help_sources[receipt_key] = (rdigest, copy.deepcopy(result["body"]["data"]))
        return result

    def _mutate(self, kind, attempt_id, attempt, body):
        if kind in {"draft", "submit", "abandon"}:
            if attempt["state"] != "STARTED":
                return self.error("STATE_CONFLICT", 409)
            if body.get("expected_revision") != attempt["revision"]:
                return self.error("REVISION_CONFLICT", 409, attempt_id)
        if kind == "draft":
            validate_draft(body["draft"])
            attempt["draft"] = copy.deepcopy(body["draft"])
            attempt["revision"] += 1
        elif kind == "submit":
            if attempt["mode"] == "SELF_CHECK":
                return self.error("STATE_CONFLICT", 409)
            attempt["revision"] += 1
            attempt["state"] = "SUBMITTED"
            attempt["snapshot_digest"] = digest({"exercise_version_id": self.version_id,
                "version": self.version, "revision": attempt["revision"], "draft": attempt["draft"]})
            attempt["operation_id"] = str(uuid5(NAMESPACE, attempt_id + attempt["snapshot_digest"]))
            self.action_ids.add(attempt["operation_id"])
            return {**self.ok(state="SUBMITTED", revision=attempt["revision"],
                             operation_id=attempt["operation_id"], snapshot_digest=attempt["snapshot_digest"]), "status": 202}
        elif kind in {"hint", "reveal"}:
            if kind == "hint":
                self.exposure["max_help_level"] = max(self.exposure["max_help_level"], body["level"])
            else:
                if not body.get("confirm"):
                    return self.error("INVALID_REQUEST", 400)
                self.exposure["revealed"] = True
                if attempt["mode"] == "SELF_CHECK" and attempt["state"] == "STARTED":
                    attempt["state"] = "REVIEWED"
            self.help_actions += 1
            return self.ok(level=body.get("level", self.exposure["max_help_level"]), revealed=self.exposure["revealed"], state=attempt["state"])
        elif kind == "finalize":
            if attempt["state"] == "COMPLETED":
                return self.ok(state="COMPLETED", outcome=attempt["outcome"], independent=attempt["independent"], positive=attempt["positive"])
            if attempt["state"] != "SUBMITTED":
                return self.error("STATE_CONFLICT", 409)
            correct = body["outcome"] == "CORRECT" and body.get("validated_supported", True)
            available = correct and not self.exposure["credited"] and not self.exposure["revealed"]
            independent = available and self.exposure["max_help_level"] == 0
            positive = available and (not body.get("diagnostic", False) or independent)
            attempt.update(state="COMPLETED", outcome=body["outcome"], independent=independent, positive=positive)
            self.completions += 1
            if positive:
                self.exposure["credited"] = True
                self.positive += 1
            return self.ok(state="COMPLETED", outcome=body["outcome"], independent=independent, positive=positive)
        elif kind == "abandon":
            attempt["state"] = "ABANDONED"
            attempt["revision"] += 1
        else:
            raise ValueError(f"Unknown oracle action {kind}")
        return self.ok(state=attempt["state"], revision=attempt["revision"], version=attempt["version"])


if __name__ == "__main__":
    validate_artifacts()
    print("PASS: official OpenAPI structural schema, DTO schemas and offline references")
