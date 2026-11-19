"""Opt-in private bank rehearsal. Evidence contains identifiers and statuses only."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from hashlib import sha256
from io import StringIO
import json
import os
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from backend import release_migrate
from backend.assessment import cli
from backend.assessment.analysis import ExerciseValidation, analyze_submission
from backend.assessment.attempt_models import action, attempt, event, exposure, step
from backend.assessment.attempts import AttemptService
from backend.assessment.models import exercise, exercise_skill, validation, version
from backend.assessment.package import read_package, validate_row
from backend.assessment.reads import project, public_rows
from backend.infrastructure.http.app import create_app
from backend.infrastructure.http.signing import Signer
from backend.knowledge.graph import graph_from_package
from backend.math_validation.model import LinearEquation, ParseInput
from backend.math_validation.parser import parse_batch
from backend.math_validation.validators import Check, Form, compare
from backend.migrations.runtime_privileges import grant_runtime_privileges
from backend.models.baseline import User, utc_now
from backend.solution_analyzer.model import SubmittedSolution, SubmittedStep, Verdict
from backend.tests.test_assessment_bank import KEY, ORIGIN, seed, stored
from backend.users.security import Security, SessionIdentity
from backend.users.service import IdentityService


ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / "var" / "private" / "ms-n008"
MODES = {
    **{f"g6_balance_{index:02d}": "TRANSFORMED_EQUATION" for index in range(1, 5)},
    "g6_linear_one_04": "SOLUTION",
    "g6_linear_paren_04": "SOLUTION",
}
PROFILE = "algebra_linear_v1"
MATH_RUN = re.compile(r"[0-9xXхХ.,+\-−–*/^×·÷:=[\](){} \t]+")
MARKER = "MS-N011 private-bank disposable PostgreSQL server"
INPUTS = ("MATHSTART_N011_TEST_ADMIN_URL", "MATHSTART_N011_SOURCE_SHA256")
PRIVATE_FIELDS = {
    "answer_key", "accepted_variants", "canonical_solution", "validation_spec",
    "initial_state", "equation_answer_mode", "checker_version", "checker_type",
}


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def parsed(texts):
    result = parse_batch(tuple(ParseInput(text, PROFILE) for text in texts))
    require(result.rejection is None, "Private parse batch refused")
    return result.results


def authored_equations(text):
    runs = tuple(dict.fromkeys(
        match.group().strip(" \t.,:[]{}") for match in MATH_RUN.finditer(text)
        if "=" in match.group()
    ))
    return [item for item in parsed(runs) if isinstance(item.value, LinearEquation)]


def private_keys(value):
    if isinstance(value, dict):
        return bool(PRIVATE_FIELDS.intersection(value)) or any(map(private_keys, value.values()))
    return isinstance(value, list) and any(map(private_keys, value))


def invoke(engine, verb, path, sha, *, refusal=None):
    args = [verb, "--package", str(path)]
    if verb != "preview":
        args += ["--reviewed-sha256", sha]
    out, err = StringIO(), StringIO()
    with patch.dict(os.environ, {"MATHSTART_DB_BACKEND": "postgresql",
                                "MATHSTART_DATABASE_URL": engine.url.render_as_string(hide_password=False)}), \
            redirect_stdout(out), redirect_stderr(err):
        status = cli.main(args)
    if refusal:
        require(status == 1 and not out.getvalue().strip()
                and err.getvalue().strip() == f"ASSESSMENT_BANK_REFUSED: {refusal}", f"{verb}: expected refusal")
        return None
    require(status == 0 and not err.getvalue().strip(), f"{verb}: unexpected CLI failure")
    receipt = json.loads(out.getvalue())
    allowed = {"action", "coverage", "package_sha256", "archive"}
    require(set(receipt) == (allowed if verb == "preview" else allowed | {"changed"})
            and not private_keys(receipt)
            and receipt["package_sha256"] == sha, f"{verb}: private output or wrong digest")
    return receipt


def content_bytes(package):
    return (json.dumps(package, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def prepare(engine, rows, output):
    with engine.connect() as conn:
        history = conn.execute(sa.select(exercise.c.code, version.c.version, version.c.status)
                               .select_from(exercise.join(version))).all()
    current = {row.code: row.version for row in history if row.status == "PUBLISHED"}
    require(current == {row["code"]: row["version"] for row in rows}, "Baseline publication differs")
    replacement = deepcopy(rows)
    outgoing = []
    for row in replacement:
        code = row["code"]
        if code not in MODES:
            continue
        anchors = authored_equations(row["statement"])
        require(len(anchors) == 1, f"{code}: ambiguous authored anchor")
        row["checker"] = {
            "version": 2, "equation_answer_mode": MODES[code],
            "initial_state": {"schema_version": 1, "kind": "EQUATION",
                              "parser_profile": PROFILE, "text": anchors[0].raw},
        }
        outgoing.append({"code": code, "version": current[code]})
        row["version"] = 1 + max(item.version for item in history if item.code == code)
        try:
            validate_row(row)
        except ValueError:
            raise AssertionError(f"{code}: reference conflicts with checker contract") from None
    require(len(outgoing) == 6, "Incomplete replacement")
    package = {"bank_version": "pilot-v1", "exercises": replacement, "archive": outgoing}
    raw = content_bytes(package)
    if output.exists():
        require(output.read_bytes() == raw, "Private output already exists with different bytes")
    else:
        with output.open("xb") as file:
            file.write(raw)
    return package, sha256(raw).hexdigest()


def state(engine, tables):
    with engine.connect() as conn:
        return tuple(stored(conn, table) for table in tables)


def session_for(engine):
    security = Security(engine, KEY, ORIGIN)
    with Session(engine) as session, session.begin():
        user = User(username="n011_test_" + uuid4().hex[:12])
        session.add(user)
        session.flush()
        row, token, _ = security.issue(session, user, utc_now())
        owner = SessionIdentity(user.id, row.id, row.lineage_id, row.revocation_epoch)
    return security, owner, token


def attempt_call(service, owner, operation, body, pk=None):
    suffix = {"update_draft": "draft", "submit_attempt": "submit", "reveal_attempt": "reveal"}
    route = f"/api/v1/attempts/{pk}/{suffix[operation]}/" if pk else "/api/v1/attempts/"
    return service.mutate(owner, operation, route, body, str(uuid4()), str(uuid4()), pk)[0]["data"]


def old_attempts(engine, topics, row):
    security, owner, _ = session_for(engine)
    service = AttemptService(IdentityService(security), Signer(KEY),
                             public_release=lambda uow: SimpleNamespace(page=lambda slug: topics[slug]))
    with engine.connect() as conn:
        identity = conn.execute(sa.select(exercise.c.id, version.c.id.label("old_id"))
                                .select_from(exercise.join(version))
                                .where(exercise.c.code == row["code"], version.c.status == "PUBLISHED")).one()
    payload = {"exercise_id": str(identity.id), "version": row["version"], "contract_version": row["version"]}
    opened, filled = [attempt_call(service, owner, "create_attempt", payload) for _ in range(2)]
    anchor = authored_equations(row["statement"])[0].raw
    draft = {"payload": {}, "steps": [
        {"step_no": 1, "step_type": "EQUATION_STATE", "payload": {"expression": anchor}, "raw_text": None},
        {"step_no": 2, "step_type": "FINAL_STATEMENT", "payload": {"answer": row["answer"]}, "raw_text": None},
    ]}
    saved = attempt_call(service, owner, "update_draft",
                         {"expected_revision": 1, "contract_version": row["version"], "draft": draft}, filled["id"])
    sent = attempt_call(service, owner, "submit_attempt",
                        {"expected_revision": saved["revision"], "contract_version": row["version"]}, filled["id"])
    reveal = attempt_call(service, owner, "reveal_attempt",
                          {"contract_version": row["version"], "confirm": True}, filled["id"])
    require(opened["state"] == "STARTED" and sent["state"] == "SUBMITTED" and sent["snapshot_digest"],
            "Prior attempt history incomplete")
    require(reveal["exposure"]["revealed_at"], "Historical exposure was not recorded")
    return service, owner, identity, opened["id"], sent["id"], sent["snapshot_digest"]


def verify_http(engine, topics, published):
    security, _, token = session_for(engine)
    app = create_app(engine, Signer(KEY), authenticate=security.identity, public_origin=ORIGIN)
    with patch("backend.infrastructure.http.app.active_release",
               return_value=SimpleNamespace(page=lambda slug: topics[slug])), TestClient(app, base_url=ORIGIN) as client:
        client.cookies.set("sessionid", token)
        listing = client.get("/api/v1/topics/reshenie-linejnyh-uravnenij/exercises/")
        require(listing.status_code == 200 and not private_keys(listing.json()), "List private boundary")
        for dto in published:
            if dto["code"] not in MODES:
                continue
            response = client.get(f"/api/v1/exercises/{dto['id']}/")
            require(response.status_code == 200 and not private_keys(response.json())
                    and response.headers.get("cache-control") == "private, no-store", "Exercise private boundary")


def verify_math(row, config, graph):
    code = row["code"]
    mode = MODES[code]
    target = row["answer"]
    require(config.initial_state is not None, f"{code}: missing projected anchor")
    anchor, key = parsed((config.initial_state, target))
    root = anchor.value.unique_solution
    require(root is not None, f"{code}: expected unique root")
    stages = []
    if row["schema"] == "equation-steps-v1":
        for line in row["solution"]:
            candidates = authored_equations(line)
            if candidates:
                require(all(compare(candidate, anchor, Form.EQUATION) == Check.VALID for candidate in candidates),
                        f"{code}: non-equivalent authored step")
                matched = next((candidate for candidate in candidates if mode == "TRANSFORMED_EQUATION"
                                and compare(candidate, key, Form.EQUATION_STATE) == Check.VALID), None)
                stages.append((matched or candidates[0]).raw)
                if matched is not None:
                    break
        require(stages, f"{code}: no authored equation steps")

    def resolve(answer, equations=stages):
        payload, steps = {"answer": answer}, ()
        if row["schema"] == "equation-steps-v1":
            payload = {}
            steps = tuple(SubmittedStep(UUID(int=index), index, "EQUATION_STATE", {"expression": text})
                          for index, text in enumerate(equations, 1))
            last = len(steps) + 1
            steps += (SubmittedStep(UUID(int=last), last, "FINAL_STATEMENT", {"answer": answer}),)
        return analyze_submission(config, SubmittedSolution(uuid4(), config.version_id, payload, steps), graph=graph)

    if mode == "TRANSFORMED_EQUATION":
        left, right = target.split("=")
        equivalent = f"{right}={left}"
        other_state = f"({left})+1=({right})+1"
        alternative, = parsed((other_state,))
        require(compare(alternative, anchor, Form.EQUATION) == Check.VALID
                and compare(alternative, key, Form.EQUATION_STATE) == Check.WRONG, f"{code}: alternate-stage probe")
        for text in (config.initial_state, other_state):
            result = resolve(text)
            require(result.verdict != Verdict.CORRECT and result.misconception_code is None,
                    f"{code}: unchanged or different stage credited")
    else:
        equivalent = f"{2 * root.numerator}/{2 * root.denominator}"
    good = (target, equivalent, *row["variants"])
    for text in good:
        result = resolve(text)
        require(result.verdict == Verdict.CORRECT and result.misconception_code is None, f"{code}: correct case")
    wrong = resolve(f"x={root + 1}")
    require(wrong.verdict == Verdict.WRONG and wrong.first_error_step_id is None
            and wrong.misconception_code is None, f"{code}: wrong final evidence")
    for text, verdict in (("x=", Verdict.INDETERMINATE), ("x=1/x", Verdict.UNSUPPORTED)):
        result = resolve(text)
        require(result.verdict == verdict and not result.evidence_refs and result.misconception_code is None,
                f"{code}: unsupported or malformed answer")
    if stages:
        previous = stages[0]
        left, right = previous.split("=")
        broken = f"({left})+1={right}"
        result = resolve(target, [previous, broken, *stages[1:]])
        require(result.verdict == Verdict.WRONG and result.final_verdict == Verdict.CORRECT
                and result.first_error_step_id == UUID(int=2) and len(result.evidence_refs) == 1
                and result.misconception_code in (None, "EQUATION_BALANCE"), f"{code}: first wrong transition")
        gap = resolve(target, [previous, "x=1/x", broken])
        require(gap.verdict == Verdict.UNSUPPORTED and gap.final_verdict == Verdict.CORRECT
                and gap.blocking_step_id == UUID(int=2) and not gap.evidence_refs
                and gap.misconception_code is None, f"{code}: unsupported gap")
    print(f"{code} {row['schema']} positive=PASS alternate=PASS negative=PASS safety=PASS "
          f"transform={'PASS' if mode == 'TRANSFORMED_EQUATION' else 'N/A'} "
          f"steps={'PASS' if stages else 'N/A'}")


@unittest.skipUnless(all(os.getenv(key) for key in INPUTS), "Requires explicit private disposable inputs")
class RealBankV2Tests(unittest.TestCase):
    def test_fresh_replay_and_upgrade_preserve_history(self):
        source = PRIVATE / "pilot-bank-v1.json"
        output = PRIVATE / "pilot-bank-n011-v2.json"
        private = PRIVATE.resolve()
        require(private.is_relative_to(ROOT) and all(path.resolve().parent == private for path in (source, output)),
                "Private package path escaped")
        sha = os.environ[INPUTS[1]]
        url = make_url(os.environ[INPUTS[0]])
        require((url.drivername, url.host, url.database) == ("postgresql+psycopg", "127.0.0.1", "postgres")
                and url.port, "Requires explicitly owned loopback PostgreSQL")
        admin = sa.create_engine(url, isolation_level="AUTOCOMMIT", hide_parameters=True,
                                 connect_args={"connect_timeout": 5})
        self.addCleanup(admin.dispose)
        try:
            with admin.connect() as conn:
                marker = conn.scalar(sa.text("select shobj_description(oid, 'pg_database') from pg_database "
                                             "where datname = current_database()"))
                require(marker == MARKER, "Missing private rehearsal server marker")
                conn.execute(sa.text("DO $$ BEGIN CREATE ROLE local_runtime; "
                                     "EXCEPTION WHEN duplicate_object THEN NULL; END $$"))
            rows, coverage, actual, archive = read_package(source)
            require(actual == sha and len(rows) == 43 and not archive and coverage["assessed"] == 40,
                    "Unexpected original package SHA or shape")
            source_rows = {row["code"]: row for row in rows}
            require(MODES.keys() <= source_rows.keys(), "Missing approved target")
            for label in ("fresh", "upgrade"):
                with self.subTest(lane=label):
                    try:
                        self.check_lane(admin, url, label, source, sha, output, rows)
                    except AssertionError:
                        raise
                    except Exception as error:
                        raise AssertionError(f"Private verification refused: {type(error).__name__}") from None
        except AssertionError:
            raise
        except Exception as error:
            raise AssertionError(f"Private verification refused: {type(error).__name__}") from None

    def check_lane(self, admin, url, label, source, sha, output, rows):
        name = f"test_n011_{label}_{uuid4().hex}"
        with admin.connect() as conn:
            conn.execute(sa.text("CREATE DATABASE " + name))
        engine = sa.create_engine(url.set(database=name), hide_parameters=True, connect_args={"connect_timeout": 5})
        try:
            plan = release_migrate.preview(engine, KEY, "FRESH")
            release_migrate.apply(engine, KEY, plan, release_migrate.plan_digest(plan), maintenance=True)
            topics = seed(engine)
            with engine.begin() as conn:
                grant_runtime_privileges(conn.connection.driver_connection)
            invoke(engine, "preview", source, sha)
            require(invoke(engine, "import", source, sha)["changed"] == 43, "Baseline import count")
            require(invoke(engine, "publish", source, sha)["changed"] == 43, "Baseline publish count")
            old_versions, old_checkers, old_links = state(engine, (version, validation, exercise_skill))
            if label == "upgrade":
                source_step = next(row for row in rows if row["code"] == "g6_balance_03")
                service, owner, identity, opened, sent, snapshot = old_attempts(engine, topics, source_step)
            history_tables = (attempt, exposure, step, action, event)
            history = state(engine, history_tables)
            package, new_sha = prepare(engine, rows, output)
            invoke(engine, "preview", output, new_sha)
            invoke(engine, "import", output, "0" * 64, refusal="Reviewed package SHA-256 does not match")
            require(invoke(engine, "import", output, new_sha)["changed"] == 6, "Replacement draft count")
            require(invoke(engine, "import", output, new_sha)["changed"] == 0, "Import replay")
            before = state(engine, (version, validation, exercise_skill, *history_tables))
            require(sum(row.status == "DRAFT" for row in before[0]) == 6, "Expected six drafts")
            with TemporaryDirectory(dir=PRIVATE, prefix="n011-conflict-") as directory:
                bad = deepcopy(package)
                bad["exercises"][-1]["solution"].append("Temporary rollback probe")
                data = content_bytes(bad)
                bad_path = Path(directory) / "conflict.json"
                bad_path.write_bytes(data)
                invoke(engine, "publish", bad_path, sha256(data).hexdigest(),
                       refusal="Version already exists with different data; create a new version")
            require(state(engine, (version, validation, exercise_skill, *history_tables)) == before,
                    "Publish rollback changed stored state")
            require(invoke(engine, "publish", output, new_sha)["changed"] == 6, "Replacement publish count")
            require(invoke(engine, "publish", output, new_sha)["changed"] == 0, "Publish replay")
            require(state(engine, history_tables) == history, "Attempt history changed")
            self.check_published(engine, topics, package, old_versions, old_checkers, old_links)
            if label == "upgrade":
                historical = service.get(owner, sent)
                require(service.get(owner, opened)["state"] == "STARTED"
                        and historical["state"] == "SUBMITTED" and historical["snapshot_digest"] == snapshot
                        and historical["exercise_version"]["id"] == str(identity.old_id)
                        and historical["exercise_version"]["status"] == "ARCHIVED"
                        and len(historical["steps"]) == 2, "Historical step snapshot unavailable")
                number = next(row["version"] for row in package["exercises"] if row["code"] == "g6_balance_03")
                new = attempt_call(service, owner, "create_attempt",
                                   {"exercise_id": str(identity.id), "version": number, "contract_version": number})
                require(new["exercise_version"]["id"] != str(identity.old_id), "New attempt bound to old version")
            require(sha256(source.read_bytes()).hexdigest() == sha, "Source bytes changed")
            print(f"{label} PASS new_package_sha256={new_sha}")
        finally:
            engine.dispose()
            with admin.connect() as conn:
                conn.execute(sa.text("DROP DATABASE " + name + " WITH (FORCE)"))

    def check_published(self, engine, topics, package, old_versions, old_checkers, old_links):
        with engine.connect() as conn:
            published = project(conn, conn.execute(public_rows()).all())
            archived = conn.execute(sa.select(exercise.c.code, version.c.version)
                                    .select_from(exercise.join(version)).where(version.c.status == "ARCHIVED")).all()
            versions = {row.id: row for row in stored(conn, version)}
            checkers = {row.version_id: row for row in stored(conn, validation)}
            links = set(stored(conn, exercise_skill))
            private = conn.execute(sa.select(exercise.c.code, version.c.schema_code, validation)
                                   .select_from(exercise.join(version).join(validation))
                                   .where(version.c.status == "PUBLISHED", validation.c.checker_version == 2)
                                   .order_by(exercise.c.code)).mappings().all()
            require(not conn.scalar(sa.text("select has_column_privilege('local_runtime', "
                                           "'assessment_exercise_validation', 'validation_spec', 'SELECT')")),
                    "Public runtime gained private checker access")
        require(len(published) == 43 and not private_keys(published) and len(private) == 6, "Published DTO scope")
        require(set(archived) == {(row["code"], row["version"]) for row in package["archive"]},
                "Archived versions differ from the reviewed list")
        require(all(checkers[row.version_id] == row for row in old_checkers) and set(old_links) <= links,
                "Legacy checker or skill history changed")
        require(sum(versions[row.id].status == "ARCHIVED" for row in old_versions) == 6
                and all(versions[row.id]._mapping.keys() == row._mapping.keys()
                        and all(value == versions[row.id]._mapping[key]
                                for key, value in row._mapping.items() if key != "status")
                        for row in old_versions), "Legacy version content or archive count")
        require({row["code"]: row["version"] for row in published}
                == {row["code"]: row["version"] for row in package["exercises"]}, "Published version map")
        with self.assertRaises(sa.exc.IntegrityError), engine.begin() as conn:
            conn.execute(validation.update().where(validation.c.version_id == old_checkers[0].version_id)
                         .values(digest="0" * 64))
        verify_http(engine, topics, published)
        graph = graph_from_package(*(
            json.loads((ROOT / "specs/knowledge/fixtures" / f"pilot-{name}-v1.json").read_text(encoding="utf-8"))
            for name in ("skills", "dependencies")
        ))
        assignments = {row["code"]: row for row in package["exercises"] if row["code"] in MODES}
        for stored_row in private:
            row = assignments[stored_row["code"]]
            config = ExerciseValidation.from_storage(
                **{field: stored_row[field] for field in (
                    "version_id", "schema_code", "checker_type", "checker_version", "validation_spec",
                    "answer_key", "accepted_variants",
                )}, skill_codes=frozenset((row["primary"], *row["secondary"])),
            )
            verify_math(row, config, graph)
