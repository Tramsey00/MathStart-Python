"""R02A contract artifact/reference tests, deliberately independent of runtime."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import unittest
from pathlib import Path
from urllib.parse import quote, urlsplit

from jsonschema import ValidationError

from scripts.r02a_contract_reference import (
    API, ROOT, ContractOracle, assert_public, digest, load, request_digest,
    resolve_ref, validate_artifacts, validate_draft, validate_exercise, validator, walk,
)

# Independent transcription of canonical TS v7.1 §11, not derived from OpenAPI.
EXPECTED_ROUTES = {
    ("get", "auth/csrf/"), ("post", "auth/register/"),
    ("post", "auth/login/"), ("post", "auth/logout/"),
    ("get", "users/me/"), ("patch", "users/me/"),
    ("post", "onboarding/complete/"), ("get", "grades/"),
    ("get", "topics/"), ("get", "topics/{slug}/"),
    ("get", "topics/{slug}/exercises/"), ("get", "exercises/{id}/"),
    ("post", "attempts/"), ("get", "attempts/"), ("get", "attempts/{id}/"),
    ("put", "attempts/{id}/draft/"), ("post", "attempts/{id}/submit/"),
    ("post", "attempts/{id}/hints/"), ("post", "attempts/{id}/reveal/"),
    ("post", "attempts/{id}/abandon/"),
    ("post", "diagnostics/sessions/"), ("get", "diagnostics/sessions/{id}/"),
    ("post", "diagnostics/sessions/{id}/next/"),
    ("post", "diagnostics/sessions/{id}/finish/"),
    ("get", "progress/skills/"), ("get", "progress/topics/"),
    ("get", "progress/events/"), ("post", "progress/self-reports/"),
    ("post", "practice/sessions/"), ("get", "practice/sessions/{id}/"),
    ("post", "practice/sessions/{id}/next/"), ("post", "practice/sessions/{id}/finish/"),
    ("post", "ai/conversations/"), ("get", "ai/conversations/{id}/messages/"),
    ("post", "ai/conversations/{id}/messages/"),
    ("get", "health/live/"), ("get", "health/ready/"),
}
IDEMPOTENT = {
    "register", "complete_onboarding", "create_attempt", "submit_attempt",
    "request_hint", "reveal_attempt", "abandon_attempt", "create_diagnostics_session",
    "next_diagnostics_session", "finish_diagnostics_session", "create_self_report",
    "create_practice_session", "next_practice_session", "finish_practice_session",
    "create_conversation", "create_message",
}
FIELDS = {"id", "code", "topic", "statement", "interaction_mode", "input_schema",
          "step_schema", "parser_profile", "difficulty", "reveal_policy", "contract_version"}


class HTTPArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oas = validate_artifacts()
        cls.policy = load(API / "http-policy-v1.json")
        cls.defs = load(API / "schemas/dto-v1.schema.json")["$defs"]

    def test_official_openapi_structure_all_routes_and_offline_refs(self):
        actual = {(method, path.removeprefix("/api/v1/"))
                  for path, item in self.oas["paths"].items() for method in item}
        self.assertEqual(actual, EXPECTED_ROUTES)
        ids = [op["operationId"] for item in self.oas["paths"].values() for op in item.values()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {x["operation_id"] for x in self.policy["operations"]})
        self.assertEqual(len(list(API.glob("openapi*"))), 1)

    def test_candidate_package_pins_external_schemas_and_artifacts(self):
        manifest = load(API / 'candidate-manifest-v1.json')
        self.assertEqual(manifest['human_acceptance'], 'PENDING')
        self.assertIn('specs/api/schemas/dto-v1.schema.json', manifest['artifacts'])
        self.assertIn('specs/api/http-policy-v1.json', manifest['artifacts'])
        for relative, expected in manifest['artifacts'].items():
            target = (ROOT / relative).resolve()
            self.assertTrue(target.is_relative_to(ROOT))
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), expected, relative)

    def test_auth_csrf_idempotency_revision_and_owner_isolation(self):
        for p in self.policy["operations"]:
            with self.subTest(operation=p["operation_id"]):
                op = self.oas["paths"][p["path"]][p["method"]]
                params = [resolve_ref(x["$ref"], API / "openapi-v1.json")[0] for x in op["parameters"]]
                headers = {x["name"]: x for x in params if x["in"] == "header"}
                self.assertEqual("X-CSRFToken" in headers, p["method"] != "get")
                self.assertEqual("Idempotency-Key" in headers, p["operation_id"] in IDEMPOTENT)
                self.assertEqual(op["security"], [] if p["access"] == "anonymous" else [{"SessionAuth": []}])
                for header in headers.values():
                    self.assertTrue(header["required"])
                path_params = {x["name"] for x in params if x["in"] == "path" and x["required"]}
                if "{id}" in p["path"]:
                    self.assertIn("id", path_params)
                if "{slug}" in p["path"]:
                    self.assertIn("slug", path_params)
                if p["owner_scoped"]:
                    self.assertIn("404", op["responses"])
                    self.assertTrue(op["x-owner-scoped"])
                if p["method"] == "get":
                    self.assertTrue(op["x-read-only"])
                    self.assertNotIn("requestBody", op)
                if p["request"] in {"DraftUpdateRequest", "SubmitRequest", "AbandonRequest"}:
                    self.assertIn("expected_revision", self.defs[p["request"]]["required"])

    def test_all_operation_examples_and_negative_shapes_validate(self):
        policies = {x["operation_id"]: x for x in self.policy["operations"]}
        examples = load(API / "fixtures/http-exchanges-v1.json")
        self.assertEqual({x["operation_id"] for x in examples}, set(policies))
        for ex in examples:
            with self.subTest(operation=ex["operation_id"]):
                op = policies[ex["operation_id"]]
                self.assertEqual(ex['method'], op['method'].upper())
                self.assertEqual('X-CSRFToken' in ex['headers'], op['method'] != 'get')
                self.assertEqual('Idempotency-Key' in ex['headers'], op['idempotency'])
                if op["request"]:
                    validator(op["request"]).validate(ex["request"])
                else:
                    self.assertIsNone(ex["request"])
                validator(op["response"]).validate(ex["response"])
                self.assertEqual(ex["status"], op["status"])
                assert_public(ex["response"])
                data = ex["response"]["data"]
                if ex['operation_id'] == 'request_hint':
                    self.assertGreaterEqual(data['exposure']['max_help_level'], data['level'])
                if ex['operation_id'] == 'reveal_attempt':
                    self.assertEqual(data['exposure']['revealed_at'], data['reveal_recorded_at'])
                    self.assertEqual(data['attempt']['exposure'], data['exposure'])
                if ex['operation_id'] == 'submit_attempt':
                    self.assertEqual(data['state'], 'COMPLETED')
                    self.assertIsNotNone(data['result'])
                if ex['operation_id'] == 'update_draft':
                    self.assertEqual(data['draft'], ex['request']['draft'])
                    self.assertEqual(data['revision'], ex['request']['expected_revision'] + 1)
                if ex['operation_id'] == 'abandon_attempt':
                    self.assertEqual(data['state'], 'ABANDONED')
                if ex['operation_id'].startswith('finish_'):
                    self.assertEqual(data['exit_reason'], ex['request']['reason'])
        for bad in load(API / "fixtures/invalid-v1.json"):
            with self.subTest(reason=bad["reason"]), self.assertRaises(ValidationError):
                validator(bad["schema"]).validate(bad["value"])

    def fixture_relationships(self, examples):
        """Index only immutable relationships declared by the source fixtures.

        The exchange under test is never added to this index. Mutable state,
        exposure levels and session policy examples are not identity bindings.
        """
        relations = {name: {} for name in (
            "topics", "topic_slugs", "exercises", "versions", "exercise_versions",
            "attempt_versions", "attempt_modes", "previous_attempts", "items",
            "practice_origins", "conversations", "messages")}

        def bind(name, key, value):
            if key in relations[name]:
                self.assertEqual(relations[name][key], value, ("canonical relation", name, key))
            relations[name][key] = value

        def version_identity(version):
            return {field: version[field] for field in ("id", "exercise_id", "version", "contract_version")}

        sources = load(API / "fixtures/public-exercises-v1.json") + examples
        for source in sources:
            for node in walk(source):
                if not isinstance(node, dict):
                    continue
                if {"id", "slug"} <= node.keys():
                    topic = {field: node[field] for field in ("id", "slug")}
                    bind("topics", topic["id"], topic)
                    bind("topic_slugs", topic["slug"], topic)
                if "exercise_version" in node:
                    version = version_identity(node["exercise_version"])
                    bind("versions", version["id"], version)
                    bind("exercise_versions", (version["exercise_id"], version["contract_version"]), version)
                    if "statement" in node:
                        bind("exercises", (node["id"], node["contract_version"]),
                             {"version": version, "topic": node["topic"], "mode": node["interaction_mode"]})
                    if "draft" in node:
                        bind("attempt_versions", node["id"], version)
                        bind("attempt_modes", node["id"], node["interaction_mode"])
                        bind("previous_attempts", node["id"], node["previous_attempt_id"])
        for example in examples:
            operation = example["operation_id"]
            data = example["response"]["data"]
            request = example["request"] or {}
            if isinstance(data, dict) and "current_item" in data and data["current_item"] is not None:
                item = data["current_item"]
                version = version_identity(item["exercise"]["exercise_version"])
                bind("attempt_versions", item["attempt_id"], version)
                domain = "diagnostics" if "diagnostics" in operation else "practice"
                bind("items", (domain, item["id"]),
                     {"session_id": data["id"], "attempt_id": item["attempt_id"], "version": version})
            if operation == "create_practice_session":
                bind("practice_origins", data["id"],
                     {"target_skill_code": data["target_skill_code"], "origin_topic": data["origin_topic"]})
            if operation == "create_conversation":
                bind("conversations", data["id"],
                     {"topic": data["topic"], "exercise_version_id": data["exercise_version_id"],
                      "attempt_id": request["attempt_id"]})
            if operation in {"create_message", "list_messages"}:
                for message in data if isinstance(data, list) else [data]:
                    bind("messages", message["id"], message["conversation_id"])
        return relations

    def assert_exchange_identity(self, exchange, examples):
        """Check wire relationships that JSON Schema cannot express."""
        operation = exchange["operation_id"]
        policy = next(p for p in self.policy["operations"] if p["operation_id"] == operation)
        pattern = re.escape(policy["path"])
        for name in ("id", "slug"):
            pattern = pattern.replace(re.escape("{" + name + "}"), f"(?P<{name}>[^/]+)")
        match = re.fullmatch(pattern, exchange["path"])
        self.assertIsNotNone(match, (operation, "path does not match canonical route"))
        params = match.groupdict()
        request = exchange["request"] or {}
        data = exchange["response"]["data"]
        relations = self.fixture_relationships(examples)

        def same_version(left, right):
            for field in ("id", "exercise_id", "version", "contract_version"):
                self.assertEqual(left[field], right[field], (operation, field))

        def nested(value):
            if isinstance(value, list):
                for item in value:
                    nested(item)
            elif isinstance(value, dict):
                if {"id", "slug"} <= value.keys():
                    topic = {field: value[field] for field in ("id", "slug")}
                    for known in (relations["topics"].get(topic["id"]),
                                  relations["topic_slugs"].get(topic["slug"])):
                        if known is not None:
                            self.assertEqual(topic, known, (operation, "topic identity"))
                if "exercise_version" in value:
                    version = value["exercise_version"]
                    self.assertEqual(version["version"], version["contract_version"])
                    # Check both directions: changing exercise_id must not turn
                    # a known version ID into an unchecked unknown tuple.
                    for known in (relations["versions"].get(version["id"]),
                                  relations["exercise_versions"].get((version["exercise_id"], version["contract_version"]))):
                        if known is not None:
                            same_version(version, known)
                    if "statement" in value:
                        self.assertEqual(value["id"], version["exercise_id"])
                        self.assertEqual(value["version"], version["version"])
                        self.assertEqual(value["contract_version"], version["contract_version"])
                        known = relations["exercises"].get((value["id"], value["contract_version"]))
                        if known is not None:
                            same_version(version, known["version"])
                            self.assertEqual(value["topic"], known["topic"], (operation, "exercise topic"))
                            self.assertEqual(value["interaction_mode"], known["mode"])
                    if "exposure" in value:
                        self.assertEqual(value["exposure"]["exercise_version_id"], version["id"])
                        if value["id"] in relations["attempt_versions"]:
                            same_version(version, relations["attempt_versions"][value["id"]])
                        if value["id"] in relations["attempt_modes"]:
                            self.assertEqual(value["interaction_mode"], relations["attempt_modes"][value["id"]])
                        previous = value["previous_attempt_id"]
                        if value["id"] in relations["previous_attempts"]:
                            self.assertEqual(previous, relations["previous_attempts"][value["id"]])
                        if previous is not None:
                            self.assertNotEqual(previous, value["id"])
                            if previous in relations["attempt_versions"]:
                                same_version(version, relations["attempt_versions"][previous])
                        error_step = (value["result"] or {}).get("first_error_step_id")
                        if error_step is not None:
                            self.assertIn(error_step, {step["step_id"] for step in value["steps"]})
                if {"attempt_id", "exercise", "position"} <= value.keys():
                    if value["attempt_id"] in relations["attempt_versions"]:
                        same_version(value["exercise"]["exercise_version"],
                                     relations["attempt_versions"][value["attempt_id"]])
                    domain = "diagnostics" if "diagnostics" in operation else "practice"
                    known = relations["items"].get((domain, value["id"]))
                    if known is not None:
                        self.assertEqual(value["attempt_id"], known["attempt_id"])
                        self.assertEqual(data["id"], known["session_id"])
                        same_version(value["exercise"]["exercise_version"], known["version"])
                if {"conversation_id", "role", "text"} <= value.keys():
                    if value["id"] in relations["messages"]:
                        self.assertEqual(value["conversation_id"], relations["messages"][value["id"]])
                for child in value.values():
                    nested(child)

        nested(data)
        nested(request)
        if operation == "get_topic":
            self.assertEqual(data["slug"], params["slug"])
        elif operation == "list_topic_exercises":
            for exercise in data:
                self.assertEqual(exercise["topic"]["slug"], params["slug"])
        elif operation == "get_exercise":
            self.assertEqual(data["id"], params["id"])
        elif operation == "create_attempt":
            self.assertEqual(request["exercise_id"], data["exercise_version"]["exercise_id"])
            self.assertEqual(request["version"], data["exercise_version"]["version"])
            self.assertEqual(request.get("previous_attempt_id"), data["previous_attempt_id"])
        elif operation in {"get_attempt", "update_draft", "submit_attempt", "abandon_attempt"}:
            self.assertEqual(data["id"], params["id"])
        elif operation == "request_hint":
            version = relations["attempt_versions"].get(params["id"])
            if version is not None:
                self.assertEqual(data["exposure"]["exercise_version_id"], version["id"])
                self.assertEqual(request["contract_version"], version["contract_version"])
        elif operation == "reveal_attempt":
            self.assertEqual(data["attempt"]["id"], params["id"])
            self.assertEqual(data["exposure"], data["attempt"]["exposure"])
        elif operation in {"get_diagnostics_session", "next_diagnostics_session",
                           "finish_diagnostics_session", "get_practice_session",
                           "next_practice_session", "finish_practice_session"}:
            self.assertEqual(data["id"], params["id"])
        elif operation == "create_practice_session":
            self.assertEqual(request["target_skill_code"], data["target_skill_code"])
            self.assertEqual(request["origin_topic"], data["origin_topic"])
        elif operation == "create_conversation":
            self.assertEqual(request["topic"], data["topic"])
            self.assertEqual(request["exercise_version_id"], data["exercise_version_id"])
            if request["attempt_id"] is not None:
                version = relations["attempt_versions"].get(request["attempt_id"])
                if version is not None:
                    self.assertEqual(request["exercise_version_id"], version["id"])
            version = relations["versions"].get(request["exercise_version_id"])
            if version is not None:
                exercise = relations["exercises"].get((version["exercise_id"], version["contract_version"]))
                if exercise is not None:
                    self.assertEqual(request["topic"], exercise["topic"])
            known = relations["conversations"].get(data["id"])
            if known is not None:
                self.assertEqual(data["topic"], known["topic"])
                self.assertEqual(data["exercise_version_id"], known["exercise_version_id"])
                self.assertEqual(request["attempt_id"], known["attempt_id"])
        elif operation in {"list_messages", "create_message"}:
            for message in data if isinstance(data, list) else [data]:
                self.assertEqual(message["conversation_id"], params["id"])
        elif operation in {"update_me", "complete_onboarding"}:
            self.assertEqual(request["selected_grade_id"], data["selected_grade_id"])
            if operation == "complete_onboarding" and 200 <= exchange["status"] < 300:
                self.assertEqual(request["mode"], data["onboarding_mode"])
                self.assertTrue(data["onboarding_complete"])
        elif operation == "create_self_report":
            accepted = set(data["accepted_skill_codes"])
            reported = set(data["already_reported_skill_codes"])
            self.assertFalse(accepted & reported)
            self.assertEqual(accepted | reported, set(request["skill_codes"]))

        attempt = data.get("attempt", data) if isinstance(data, dict) else {}
        if "exercise_version" in attempt and "contract_version" in request:
            self.assertEqual(request["contract_version"], attempt["exercise_version"]["contract_version"])
        if isinstance(data, dict) and "return_route" in data:
            known = relations["practice_origins"].get(data["id"])
            if known is not None:
                self.assertEqual(data["origin_topic"], known["origin_topic"])
                self.assertEqual(data["target_skill_code"], known["target_skill_code"])
            route = data["return_route"]
            if route["reason"] == "ORIGIN":
                self.assertEqual(route["topic"], data["origin_topic"])
                url = urlsplit(route["url"])
                self.assertFalse(url.scheme or url.netloc)
                self.assertTrue(url.path.endswith("/" + quote(data["origin_topic"]["slug"], safe="") + "/"))

    def test_semantic_identity_for_all_37_http_exchanges(self):
        examples = load(API / "fixtures/http-exchanges-v1.json")
        self.assertEqual(len(examples), 37)
        self.assertEqual({ex["operation_id"] for ex in examples},
                         {p["operation_id"] for p in self.policy["operations"]})
        for exchange in examples:
            with self.subTest(operation=exchange["operation_id"]):
                self.assert_exchange_identity(exchange, examples)

    def assert_schema_valid_identity_rejected(self, operation, path, value):
        examples = load(API / "fixtures/http-exchanges-v1.json")
        exchange = copy.deepcopy(next(ex for ex in examples if ex["operation_id"] == operation))
        parent = exchange
        for key in path[:-1]:
            parent = parent[key]
        parent[path[-1]] = value
        policy = next(p for p in self.policy["operations"] if p["operation_id"] == operation)
        if policy["request"]:
            validator(policy["request"]).validate(exchange["request"])
        validator(policy["response"]).validate(exchange["response"])
        with self.assertRaises(AssertionError):
            self.assert_exchange_identity(exchange, examples)

    def test_get_attempt_rejects_changed_nested_exercise_id(self):
        self.assert_schema_valid_identity_rejected(
            "get_attempt", ("response", "data", "exercise_version", "exercise_id"),
            "00000000-0000-4000-8000-999999999999")

    def test_get_exercise_rejects_changed_nested_topic_id(self):
        self.assert_schema_valid_identity_rejected(
            "get_exercise", ("response", "data", "topic", "id"), "another-topic")

    def test_successful_onboarding_preserves_mode_and_completion(self):
        examples = load(API / "fixtures/http-exchanges-v1.json")
        exchange = next(ex for ex in examples if ex["operation_id"] == "complete_onboarding")
        self.assertEqual(exchange["response"]["data"]["onboarding_mode"], exchange["request"]["mode"])
        self.assertTrue(exchange["response"]["data"]["onboarding_complete"])
        for field, value in [("onboarding_mode", None), ("onboarding_mode", "SELF_REPORT"),
                             ("onboarding_complete", False)]:
            with self.subTest(field=field, value=value):
                self.assert_schema_valid_identity_rejected(
                    "complete_onboarding", ("response", "data", field), value)

    def test_other_known_nested_relations_reject_schema_valid_substitutions(self):
        wrong_id = "00000000-0000-4000-8000-999999999999"
        for operation, path, value in [
            ("get_attempt", ("response", "data", "exercise_version", "id"), wrong_id),
            ("get_topic", ("response", "data", "id"), "another-topic"),
            ("next_diagnostics_session", ("response", "data", "current_item", "attempt_id"), wrong_id),
            ("next_practice_session", ("response", "data", "current_item", "attempt_id"), wrong_id),
            ("next_diagnostics_session", ("response", "data", "current_item", "exercise", "exercise_version", "exercise_id"), wrong_id),
            ("next_practice_session", ("response", "data", "current_item", "exercise", "topic", "id"), "another-topic"),
            ("get_practice_session", ("response", "data", "target_skill_code"), "another-skill"),
            ("create_conversation", ("request", "attempt_id"), wrong_id),
        ]:
            with self.subTest(operation=operation, field=path):
                self.assert_schema_valid_identity_rejected(operation, path, value)

        examples = load(API / "fixtures/http-exchanges-v1.json")
        by_operation = {ex["operation_id"]: ex for ex in examples}
        other_exercise = load(API / "fixtures/public-exercises-v1.json")[1]
        bad_attempt = copy.deepcopy(by_operation["get_attempt"])
        # A locally consistent version/exposure substitution still violates the
        # original binding of this known attempt ID.
        bad_attempt["response"]["data"]["exercise_version"] = copy.deepcopy(other_exercise["exercise_version"])
        bad_attempt["response"]["data"]["exposure"]["exercise_version_id"] = other_exercise["exercise_version"]["id"]
        bad_conversation = copy.deepcopy(by_operation["create_conversation"])
        bound_version = by_operation["get_exercise"]["response"]["data"]["exercise_version"]["id"]
        bad_conversation["request"]["exercise_version_id"] = bound_version
        bad_conversation["response"]["data"]["exercise_version_id"] = bound_version
        bad_message = copy.deepcopy(by_operation["create_message"])
        bad_message["path"] = bad_message["path"].replace(bad_message["response"]["data"]["conversation_id"], wrong_id)
        bad_message["response"]["data"]["conversation_id"] = wrong_id
        for exchange in (bad_attempt, bad_conversation, bad_message):
            with self.subTest(operation=exchange["operation_id"], coherent_substitution=True):
                policy = next(p for p in self.policy["operations"] if p["operation_id"] == exchange["operation_id"])
                if policy["request"]:
                    validator(policy["request"]).validate(exchange["request"])
                validator(policy["response"]).validate(exchange["response"])
                with self.assertRaises(AssertionError):
                    self.assert_exchange_identity(exchange, examples)

    def test_unshown_resource_bindings_are_not_invented(self):
        examples = load(API / "fixtures/http-exchanges-v1.json")
        by_operation = {ex["operation_id"]: ex for ex in examples}
        unknown = "00000000-0000-4000-8000-999999999999"
        attempt = copy.deepcopy(by_operation["create_attempt"])
        attempt["request"]["exercise_id"] = unknown
        data = attempt["response"]["data"]
        data["id"] = unknown
        data["exercise_version"]["id"] = unknown
        data["exercise_version"]["exercise_id"] = unknown
        data["exposure"]["exercise_version_id"] = unknown
        conversation = copy.deepcopy(by_operation["create_conversation"])
        conversation["response"]["data"]["id"] = unknown
        for value in (conversation["request"], conversation["response"]["data"]):
            value["topic"] = {"id": "unshown-topic", "slug": "unshown-topic"}
            value["exercise_version_id"] = unknown
        conversation["request"]["attempt_id"] = unknown
        for exchange in (attempt, conversation):
            policy = next(p for p in self.policy["operations"] if p["operation_id"] == exchange["operation_id"])
            validator(policy["request"]).validate(exchange["request"])
            validator(policy["response"]).validate(exchange["response"])
            self.assert_exchange_identity(exchange, examples)

    def test_schema_valid_identity_mismatches_are_rejected(self):
        examples = load(API / "fixtures/http-exchanges-v1.json")
        by_operation = {ex["operation_id"]: ex for ex in examples}
        wrong_id = "00000000-0000-4000-8000-999999999999"
        mutations = [
            ("get_exercise", ("response", "data", "id"), wrong_id),
            ("create_attempt", ("request", "exercise_id"), wrong_id),
            ("create_attempt", ("request", "version"), 2),
            ("create_attempt", ("request", "previous_attempt_id"), wrong_id),
            ("reveal_attempt", ("response", "data", "attempt", "id"), wrong_id),
            ("get_topic", ("response", "data", "slug"), "another-topic"),
            ("request_hint", ("response", "data", "exposure", "exercise_version_id"), wrong_id),
            ("get_attempt", ("response", "data", "exposure", "exercise_version_id"), wrong_id),
            ("create_conversation", ("response", "data", "topic", "id"), "another-topic"),
            ("update_me", ("response", "data", "selected_grade_id"), 9),
            ("complete_onboarding", ("response", "data", "selected_grade_id"), 9),
            ("create_self_report", ("response", "data", "accepted_skill_codes"), ["another-skill"]),
            ("next_diagnostics_session", ("response", "data", "current_item", "exercise", "exercise_version", "id"), wrong_id),
            ("next_practice_session", ("response", "data", "current_item", "attempt_id"),
             by_operation["reveal_attempt"]["response"]["data"]["attempt"]["id"]),
            ("create_practice_session", ("response", "data", "origin_topic", "id"), "another-topic"),
            ("get_practice_session", ("response", "data", "return_route", "topic", "id"), "another-topic"),
        ]
        for operation in ("get_diagnostics_session", "next_diagnostics_session", "finish_diagnostics_session",
                          "get_practice_session", "next_practice_session", "finish_practice_session"):
            mutations.append((operation, ("response", "data", "id"), wrong_id))
        mutations.append(("create_message", ("response", "data", "conversation_id"), wrong_id))
        for operation, path, value in mutations:
            with self.subTest(operation=operation, field=path):
                bad = copy.deepcopy(by_operation[operation])
                parent = bad
                for key in path[:-1]:
                    parent = parent[key]
                parent[path[-1]] = value
                policy = next(p for p in self.policy["operations"] if p["operation_id"] == operation)
                if policy["request"]:
                    validator(policy["request"]).validate(bad["request"])
                validator(policy["response"]).validate(bad["response"])
                with self.assertRaises(AssertionError):
                    self.assert_exchange_identity(bad, examples)

    def test_list_items_and_conversation_context_preserve_identity(self):
        examples = load(API / "fixtures/http-exchanges-v1.json")
        by_operation = {ex["operation_id"]: ex for ex in examples}
        exercise = by_operation["get_exercise"]["response"]["data"]
        for operation, item in [
            ("list_topic_exercises", exercise),
            ("list_messages", by_operation["create_message"]["response"]["data"]),
        ]:
            populated = copy.deepcopy(by_operation[operation])
            populated["response"]["data"] = [copy.deepcopy(item)]
            self.assert_exchange_identity(populated, examples)
            if operation == "list_topic_exercises":
                populated["response"]["data"][0]["topic"]["slug"] = "another-topic"
            else:
                populated["response"]["data"][0]["conversation_id"] = "00000000-0000-4000-8000-999999999999"
            policy = next(p for p in self.policy["operations"] if p["operation_id"] == operation)
            validator(policy["response"]).validate(populated["response"])
            with self.assertRaises(AssertionError):
                self.assert_exchange_identity(populated, examples)
        context = copy.deepcopy(by_operation["create_conversation"])
        attempt = by_operation["create_attempt"]["response"]["data"]
        context["request"]["attempt_id"] = attempt["id"]
        context["request"]["exercise_version_id"] = attempt["exercise_version"]["id"]
        context["request"]["topic"] = copy.deepcopy(exercise["topic"])
        context["response"]["data"]["exercise_version_id"] = attempt["exercise_version"]["id"]
        context["response"]["data"]["topic"] = copy.deepcopy(exercise["topic"])
        # This constructed positive case declares a distinct context from the
        # topic-only canonical example; keep that source separate from mutations.
        context_examples = [ex for ex in examples if ex["operation_id"] != "create_conversation"] + [copy.deepcopy(context)]
        self.assert_exchange_identity(context, context_examples)
        wrong_version = "00000000-0000-4000-8000-999999999999"
        context["request"]["exercise_version_id"] = wrong_version
        context["response"]["data"]["exercise_version_id"] = wrong_version
        validator("ConversationRequest").validate(context["request"])
        validator("ConversationResponse").validate(context["response"])
        with self.assertRaises(AssertionError):
            self.assert_exchange_identity(context, context_examples)

    def test_pending_unsupported_and_degraded_are_typed_business_results(self):
        for fixture in load(API / 'fixtures/business-results-v1.json'):
            validator(fixture['schema']).validate(fixture['response'])
            op = next(x for x in self.policy['operations'] if x['operation_id'] == fixture['operation_id'])
            self.assertIn(str(fixture['status']), self.oas['paths'][op['path']][op['method']]['responses'])
            if fixture['status'] == 202:
                bad = copy.deepcopy(fixture['response']); bad['data']['operation_id'] = None
                with self.assertRaises(ValidationError): validator('PendingAttemptResponse').validate(bad)
            elif fixture['operation_id'] == 'submit_attempt':
                self.assertEqual(fixture['response']['data']['result']['outcome'], 'UNSUPPORTED')
                self.assertFalse(fixture['response']['data']['result']['positive_credit_awarded'])
            else:
                self.assertEqual(fixture['response']['data']['service_state'], 'DEGRADED')

    def test_status_specific_error_envelopes(self):
        for fixture in load(API / 'fixtures/errors-v1.json'):
            with self.subTest(status=fixture['status'], schema=fixture['schema']):
                validator(fixture['schema']).validate(fixture['response'])
                if fixture['status'] != 409:
                    bad = copy.deepcopy(fixture['response'])
                    bad['error']['code'] = 'REVISION_CONFLICT'
                    with self.assertRaises(ValidationError): validator(fixture['schema']).validate(bad)
        login = self.oas['paths']['/api/v1/auth/login/']['post']
        self.assertIn('401', login['responses'])

    def test_r02_public_fields_and_all_frozen_examples_preserved(self):
        self.assertTrue(FIELDS <= set(self.defs["PublicExerciseDTO"]["required"]))
        new = {x["code"]: x for x in load(API / "fixtures/public-exercises-v1.json")}
        frozen = ROOT / "specs/exercises/fixtures"
        self.assertEqual(len(list(frozen.glob("*.json"))), 7)
        for path in frozen.glob("*.exercise-v1.json"):
            old = load(path)
            ex = new[old["code"]]
            validate_exercise(ex)
            for key in old.keys() - {"fixture_type", "id"}:
                self.assertEqual(ex[key], old[key])
        final = load(frozen / "final-answer-submission.exchange-v1.json")
        self.assertEqual(final["request"]["contract_version"], 1)
        self.assertIsNone(final["response"]["specific_misconception"])
        steps = load(frozen / "step-submission.exchange-v1.json")
        validator("SolutionStepSubmission").validate(steps["request"]["submitted_step"])
        self.assertEqual(set(steps["response"]["step"]), {"step_no", "step_type", "payload", "raw_text", "normalized_repr", "parse_status"})
        reveal = load(frozen / "reveal.exchange-v1.json")
        self.assertFalse(reveal["response"]["attempt_rules"]["independent_correct_eligible"])

    def test_public_schema_secrets_and_health_allowlist(self):
        # Only raw client payload is open: its fields remain untrusted student data.
        for name in ["PublicExerciseDTO", "InputField", "InputSchema", "StepSchema", "ExerciseVersionIdentity", "HealthLive", "HealthReady"]:
            assert_public(self.defs[name])
        for ex in load(API / "fixtures/public-exercises-v1.json"):
            for secret in ["answer_key", "checker", "reference_solution", "correct_value"]:
                bad = copy.deepcopy(ex)
                bad['interaction_mode'] = 'FINAL_ANSWER'
                bad["input_schema"] = {"type": "object", "fields": [{"name": secret, "input_type": "text", "required": True}]}
                with self.assertRaises(ValueError):
                    validate_exercise(bad)
        self.assertEqual(set(self.defs["HealthReady"]["properties"]), {"status", "database", "configuration", "provider"})
        self.assertFalse(self.defs["HealthReady"]["additionalProperties"])
        self.assertNotIn("normalized_repr", self.defs["SolutionStepSubmission"]["properties"])
        self.assertNotIn("parse_status", self.defs["SolutionStepSubmission"]["properties"])

    def test_version_alias_difficulty_and_order_are_checked(self):
        ex = load(API / "fixtures/public-exercises-v1.json")[0]
        for field, value in [("version", 2), ("difficulty_level", 4)]:
            bad = copy.deepcopy(ex); bad[field] = value
            with self.assertRaises(ValueError):
                validate_exercise(bad)
        attempt = copy.deepcopy(next(x['response'] for x in load(API / 'fixtures/http-exchanges-v1.json') if x['operation_id'] == 'create_attempt'))
        for stamp in ['2026-02-30T09:00:00Z', '2026-09-30T09:00:00', '2026-09-30T09:00:00.1234567Z']:
            attempt['data']['created_at'] = stamp
            with self.assertRaises(ValidationError): validator('AttemptResponse').validate(attempt)
        step = {"step_no": 1, "step_type": "EQUATION_STATE", "payload": {"expression": "x+1"}, "raw_text": "x+1"}
        for numbers in [[1, 1], [2, 1], [2], [1, 3]]:
            with self.assertRaises(ValueError):
                validate_draft({"payload": {}, "steps": [{**step, "step_no": n} for n in numbers]})
        validate_draft({"payload": {}, "steps": [step]})
        for count in [40, 41]:
            payload = {"payload": {}, "steps": [{**step, "step_no": n+1} for n in range(count)]}
            if count == 40:
                validate_draft(payload)
            else:
                with self.assertRaises(ValidationError): validate_draft(payload)

    def test_envelopes_pagination_and_pending_status_contract(self):
        self.assertEqual(self.policy["pagination"]["order"], ["created_at", "id"])
        p = self.oas["components"]["parameters"]["PageSize"]["schema"]
        self.assertEqual((p["default"], p["maximum"]), (20, 100))
        self.assertTrue(self.oas["components"]["responses"]["429"]["headers"]["Retry-After"]["required"])
        submit = self.oas["paths"]["/api/v1/attempts/{id}/submit/"]["post"]
        self.assertIn("202", submit["responses"])
        self.assertEqual(submit["x-status-route"], "/api/v1/attempts/{id}/")
        self.assertIn("get", self.oas["paths"][submit["x-status-route"]])
        self.assertEqual(set(self.defs["ErrorEnvelope"]["properties"]["error"]["required"]), {"code", "message", "field_errors", "retryable", "request_id"})

    def test_digest_scope_and_permanent_uniqueness(self):
        body = {"expected_revision": 1, "contract_version": 1}
        base = request_digest("owner-a", "submit", "/attempts/a/submit/", body)
        self.assertEqual(base, request_digest("owner-a", "submit", "/attempts/a/submit/", dict(reversed(list(body.items())))))
        for args in [("owner-b", "submit", "/attempts/a/submit/", body),
                     ("owner-a", "reveal", "/attempts/a/submit/", body),
                     ("owner-a", "submit", "/attempts/b/submit/", body),
                     ("owner-a", "submit", "/attempts/a/submit/", {**body, "expected_revision": 2})]:
            self.assertNotEqual(base, request_digest(*args))
        self.assertNotEqual(digest([1, 2]), digest([2, 1]))
        self.assertNotEqual(digest("2,5"), digest("2.5"))
        self.assertGreaterEqual(self.policy["idempotency"]["retention_seconds_min"], 7*86400)
        self.assertTrue(self.policy["idempotency"]["permanent_source_uniqueness"])


class TransactionFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {c["case_id"]: c for c in load(API / "fixtures/concurrency-v1.json")["cases"]}

    def check_case(self, name):
        case = self.cases[name]
        validator("ConcurrencyScenario").validate(case)
        oracle = ContractOracle(case["initial"])
        results = []
        for action in case["actions"]:
            result = oracle.apply(action)
            results.append(result)
            self.assertEqual(result["status"], action["expected"]["status"], (name, action))
            data = result["body"].get("data", result["body"].get("error"))
            for key, value in action["expected"].items():
                if key != "status": self.assertEqual(data[key], value, (name, action, result))
            if result["status"] >= 400:
                validator("ConflictEnvelope" if result["status"] == 409 else "ErrorEnvelope").validate(result["body"])
            else:
                validator("SuccessEnvelope").validate(result["body"])
        self.assertEqual({"positive": oracle.positive, "completions": oracle.completions,
                          "help_actions": oracle.help_actions, "submit_actions": len(oracle.action_ids)}, case["expected_totals"])
        self.assertLessEqual(oracle.positive, 1)
        return oracle, results

    def test_all_serial_concurrency_fixtures(self):
        for name in self.cases:
            with self.subTest(case=name): self.check_case(name)

    def test_repeat_submit(self):
        _, results = self.check_case("repeat-submit")
        self.assertEqual(results[1], results[3])

    def check_help_retry_after_expiry(self, name):
        oracle, results = self.check_case(name)
        self.assertEqual(results[1], results[3])
        self.assertEqual(oracle.help_actions, 1)
        case = self.cases[name]
        oracle = ContractOracle(case["initial"])
        oracle.apply(case["actions"][0])
        original = oracle.apply(case["actions"][1])
        self.assertTrue(oracle.receipts)
        oracle.apply({"action": "expire_receipts"})
        self.assertFalse(oracle.receipts)
        exposure = copy.deepcopy(oracle.exposure)
        # Repeated expiry/retry cycles cannot recreate the domain action.
        for _ in range(2):
            self.assertEqual(oracle.apply(case["actions"][1]), original)
            self.assertEqual(oracle.help_actions, 1)
            self.assertEqual(oracle.exposure, exposure)
            oracle.apply({"action": "expire_receipts"})
        foreign = {**case["actions"][1], "owner": "00000000-0000-4000-8000-000000000099"}
        self.assertEqual(oracle.apply(foreign)["status"], 404)
        changed = copy.deepcopy(case["actions"][1])
        changed["body"]["contract_version"] += 1
        conflict = oracle.apply(changed)
        self.assertEqual(conflict["status"], 409)
        self.assertEqual(conflict["body"]["error"]["code"], "IDEMPOTENCY_CONFLICT")
        self.assertEqual(oracle.help_actions, 1)
        new_action = {**case["actions"][1], "key": "new-help-action"}
        self.assertEqual(oracle.apply(new_action)["status"], 200)
        self.assertEqual(oracle.help_actions, 2)

    def test_hint_retry_after_receipt_expiry(self):
        self.check_help_retry_after_expiry("hint-retry-after-receipt-expiry")

    def test_reveal_retry_after_receipt_expiry(self):
        self.check_help_retry_after_expiry("reveal-retry-after-receipt-expiry")

    def test_hint_retry_after_expiry_keeps_original_level_and_route_scope(self):
        case = self.cases["hint-retry-after-escalation"]
        oracle = ContractOracle(case["initial"])
        results = [oracle.apply(action) for action in case["actions"][:3]]
        oracle.apply({"action": "expire_receipts"})
        self.assertEqual(oracle.apply(case["actions"][1]), results[1])
        self.assertEqual(oracle.exposure["max_help_level"], 2)
        self.assertEqual(oracle.help_actions, 2)
        other = copy.deepcopy(case["actions"][0])
        other["attempt_id"] = "00000000-0000-4000-8000-000000000101"
        oracle.apply(other)
        retry = {**case["actions"][1], "attempt_id": other["attempt_id"]}
        conflict = oracle.apply(retry)
        self.assertEqual(conflict["status"], 409)
        self.assertEqual(conflict["body"]["error"]["code"], "IDEMPOTENCY_CONFLICT")
        self.assertEqual(oracle.help_actions, 2)

    def test_stale_revision(self):
        _, results = self.check_case("stale-revision")
        error = results[-1]["body"]["error"]
        self.assertEqual(error["current_revision"], 2)
        self.assertTrue(error["reload_url"].endswith("/"))

    def test_help_submit_race(self):
        for name in ["hint-submit-help-wins", "submit-pending-before-help", "submit-completed-before-help",
                     "reveal-submit-reveal-wins", "submit-pending-before-reveal", "submit-completed-before-reveal"]:
            with self.subTest(case=name): self.check_case(name)

    def test_second_positive_eligibility(self):
        oracle, _ = self.check_case("second-positive-eligibility")
        self.assertEqual(oracle.completions, 2)
        self.assertEqual(oracle.positive, 1)
        self.check_case("receipt-expiry-permanent-credit")

    def test_submit_and_positive_credit_guards_survive_receipt_expiry(self):
        oracle, results = self.check_case("receipt-expiry-original-submit")
        self.assertEqual(results[-1]["status"], 409)
        self.assertEqual(len(oracle.action_ids), 1)
        self.assertEqual(oracle.completions, 1)
        oracle, _ = self.check_case("receipt-expiry-permanent-credit")
        self.assertEqual(oracle.completions, 2)
        self.assertEqual(oracle.positive, 1)

    def test_no_foreign_existence_or_revision_disclosure(self):
        _, results = self.check_case("foreign-owner")
        self.assertEqual(results[1], results[2])
        self.assertNotIn("current_revision", results[1]["body"]["error"])

    def test_snapshot_order_raw_data_and_get_are_immutable(self):
        case = self.cases["repeat-submit"]
        oracle = ContractOracle(case["initial"])
        oracle.apply(case["actions"][0])
        aid = case["actions"][0]["attempt_id"]
        step = {"step_no": 1, "step_type": "EQUATION_STATE", "raw_text": "2,5", "payload": {"expression": "2,5"}}
        update = {"action": "draft", "attempt_id": aid, "body": {"expected_revision": 1, "contract_version": 1, "draft": {"payload": {}, "steps": [step]}}}
        oracle.apply(update)
        submit = copy.deepcopy(case["actions"][1]); submit["body"]["expected_revision"] = 2
        oracle.apply(submit)
        snapshot = copy.deepcopy(oracle.attempts)
        oracle.apply({"action": "read", "attempt_id": aid})
        self.assertEqual(oracle.attempts, snapshot)
        update["body"]["draft"]["steps"][0]["raw_text"] = "changed"
        self.assertEqual(oracle.apply(update)["status"], 409)
        self.assertEqual(oracle.attempts, snapshot)


if __name__ == "__main__":
    unittest.main()
