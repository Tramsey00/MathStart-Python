/* Manual regression check using an available Node runtime; no npm dependencies. */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {test} = require("node:test");

const root = path.resolve(__dirname, "..");
const sandbox = {window: {}};
vm.runInNewContext(fs.readFileSync(path.join(root, "static/mathstart/js/ui/schema-dispatch.js"), "utf8"), sandbox);
const dispatch = sandbox.window.MathStartUI.dispatchExercise;
const exercises = JSON.parse(fs.readFileSync(path.join(root, "specs/ui/fixtures/ui-states-v1.json"), "utf8")).exercises;
const clone = exercise => JSON.parse(JSON.stringify(exercise));

test("valid synthetic descriptors retain all four foundation slots", () => {
  const expected = {SELF_CHECK: "self-check", FINAL_ANSWER: "final-answer",
    STEP_BY_STEP: "ordered-steps", STRUCTURED_SOLUTION: "structured-solution"};
  assert.equal(exercises.length, 4);
  assert.deepEqual(exercises.map(item => item.interaction_mode).sort(), Object.keys(expected).sort());
  for (const exercise of exercises) {
    assert.equal(dispatch(exercise), expected[exercise.interaction_mode], exercise.interaction_mode);
  }
});

test("unknown string interaction modes fail safely", () => {
  for (const exercise of exercises) {
    for (const mode of ["UNKNOWN", "", "final_answer", " FINAL_ANSWER ", "__proto__", "toString"]) {
      assert.equal(dispatch({...clone(exercise), interaction_mode: mode}), "unsupported", mode);
    }
  }
});

test("SELF_CHECK requires both schema fields to be present and null", () => {
  const exercise = exercises.find(item => item.interaction_mode === "SELF_CHECK");
  const input = exercises.find(item => item.input_schema !== null).input_schema;
  const steps = exercises.find(item => item.step_schema !== null).step_schema;
  assert.equal(dispatch(clone(exercise)), "self-check");
  for (const [key, value] of [["input_schema", input], ["step_schema", steps]]) {
    assert.equal(dispatch({...clone(exercise), [key]: value}), "unsupported", `${key}: non-null`);
    assert.equal(dispatch({...clone(exercise), [key]: undefined}), "unsupported", `${key}: undefined`);
    const missing = clone(exercise);
    delete missing[key];
    assert.equal(dispatch(missing), "unsupported", `${key}: missing`);
  }
  assert.equal(dispatch({...clone(exercise), input_schema: input, step_schema: steps}), "unsupported", "both non-null");
});

test("non-string interaction modes fail without property-key coercion or exceptions", () => {
  for (const exercise of exercises) {
    const mode = exercise.interaction_mode;
    const cases = [
      ["FINAL_ANSWER array", ["FINAL_ANSWER"]], ["mode array", [mode]],
      ["nested mode array", [[mode]]], ["empty array", []], ["plain object", {}],
      ["number", 1], ["zero", 0], ["NaN", NaN], ["null", null], ["undefined", undefined],
      ["true", true], ["false", false], ["boxed string", new String(mode)],
      ["symbol", Symbol(mode)], ["bigint", 1n], ["function", () => mode],
      ["coercible object", {toString: () => mode}],
      ["throwing coercion", {[Symbol.toPrimitive]() { throw new Error("must not coerce mode"); }}],
    ];
    for (const [label, value] of cases) {
      assert.equal(dispatch({...clone(exercise), interaction_mode: value}), "unsupported", `${mode}: ${label}`);
    }
  }
});

test("required input and step schemas fail safely when missing, null or undefined", () => {
  const required = {FINAL_ANSWER: ["input_schema"], STEP_BY_STEP: ["step_schema"],
    STRUCTURED_SOLUTION: ["input_schema", "step_schema"]};
  for (const [mode, keys] of Object.entries(required)) {
    const exercise = exercises.find(item => item.interaction_mode === mode);
    const groups = mode === "STRUCTURED_SOLUTION" ? [...keys.map(key => [key]), keys] : [keys];
    for (const group of groups) {
      for (const state of ["missing", "null", "undefined"]) {
        const malformed = clone(exercise);
        for (const key of group) {
          if (state === "missing") delete malformed[key];
          else malformed[key] = state === "null" ? null : undefined;
        }
        assert.equal(dispatch(malformed), "unsupported", `${mode}: ${group.join("+")} ${state}`);
        // Reproduce the review bypass: an array must not evade mode-specific schema requirements.
        malformed.interaction_mode = [mode];
        assert.equal(dispatch(malformed), "unsupported", `${mode} array: ${group.join("+")} ${state}`);
      }
    }
  }
});
