/* Public metadata shape dispatch only. No form generation or mathematical verdict. */
(() => {
  "use strict";
  const slots = Object.freeze({SELF_CHECK: "self-check", FINAL_ANSWER: "final-answer",
    STEP_BY_STEP: "ordered-steps", STRUCTURED_SOLUTION: "structured-solution"});
  const fieldTypes = ["math_text", "text", "positive_integer", "enum", "object"];
  const stepTypes = ["MATH_EXPRESSION", "EQUATION_STATE", "STRUCTURED_FIELDS", "FINAL_STATEMENT"];
  const isObject = value => value !== null && typeof value === "object" && !Array.isArray(value);
  const shape = (value, required, optional = []) => isObject(value)
    && required.every(key => Object.hasOwn(value, key))
    && Object.keys(value).every(key => required.includes(key) || optional.includes(key));
  const text = value => typeof value === "string" && value.length > 0;
  const integer = value => Number.isInteger(value) && value > 0;
  const uuid = value => typeof value === "string" && /^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(value);
  const unique = list => new Set(list).size === list.length;
  const field = value => shape(value, ["name", "input_type", "required"], ["label"])
    && text(value.name) && fieldTypes.includes(value.input_type) && typeof value.required === "boolean"
    && (!Object.hasOwn(value, "label") || typeof value.label === "string");
  const inputSchema = value => shape(value, ["type", "fields"]) && value.type === "object"
    && Array.isArray(value.fields) && value.fields.length <= 40 && value.fields.every(field);
  const stepSchema = value => shape(value, ["type", "allowed_step_types"], ["step_fields", "ordering", "serialization"])
    && value.type === "ordered_steps" && Array.isArray(value.allowed_step_types)
    && value.allowed_step_types.length > 0 && unique(value.allowed_step_types)
    && value.allowed_step_types.every(type => stepTypes.includes(type))
    && (!Object.hasOwn(value, "step_fields") || (Array.isArray(value.step_fields) && value.step_fields.every(field)))
    && (!Object.hasOwn(value, "ordering") || (shape(value.ordering, ["field", "direction"])
      && value.ordering.field === "step_no" && value.ordering.direction === "ascending"))
    && (!Object.hasOwn(value, "serialization") || (Array.isArray(value.serialization)
      && value.serialization.every(item => shape(item, ["step_type", "payload_fields"])
        && stepTypes.includes(item.step_type) && Array.isArray(item.payload_fields)
        && unique(item.payload_fields) && item.payload_fields.every(text))));

  function dispatchExercise(exercise) {
    const required = ["id", "code", "topic", "statement", "interaction_mode", "input_schema", "step_schema",
      "parser_profile", "difficulty", "reveal_policy", "contract_version", "version", "exercise_version",
      "difficulty_level", "skill_codes", "allowed_help_actions"];
    if (!shape(exercise, required, ["hint_policy", "presentation"])) return "unsupported";
    const mode = exercise.interaction_mode, identity = exercise.exercise_version;
    if (!Object.hasOwn(slots, mode) || !uuid(exercise.id) || !text(exercise.code) || !text(exercise.statement)
      || !shape(exercise.topic, ["id", "slug"]) || !["string", "number"].includes(typeof exercise.topic.id)
      || (typeof exercise.topic.id === "number" && !Number.isInteger(exercise.topic.id)) || !text(exercise.topic.slug)
      || !shape(identity, ["id", "exercise_id", "version", "contract_version", "status"])
      || !uuid(identity.id) || identity.exercise_id !== exercise.id || !["PUBLISHED", "ARCHIVED"].includes(identity.status)
      || !integer(exercise.version) || exercise.version !== exercise.contract_version
      || exercise.version !== identity.version || exercise.version !== identity.contract_version
      || !["easy", "medium", "hard"].includes(exercise.difficulty)
      || !integer(exercise.difficulty_level) || exercise.difficulty_level > 4
      || exercise.difficulty !== ({1: "easy", 2: "easy", 3: "medium", 4: "hard"})[exercise.difficulty_level]
      || (exercise.parser_profile !== null && !text(exercise.parser_profile))
      || !Array.isArray(exercise.skill_codes) || !unique(exercise.skill_codes) || !exercise.skill_codes.every(text)
      || !Array.isArray(exercise.allowed_help_actions) || !unique(exercise.allowed_help_actions)
      || !exercise.allowed_help_actions.every(action => ["HINT", "REVEAL"].includes(action))
      || !shape(exercise.reveal_policy, ["allowed", "confirmation_required"])
      || typeof exercise.reveal_policy.allowed !== "boolean" || typeof exercise.reveal_policy.confirmation_required !== "boolean"
      || (exercise.input_schema !== null && !inputSchema(exercise.input_schema))
      || (exercise.step_schema !== null && !stepSchema(exercise.step_schema))) return "unsupported";
    if (Object.hasOwn(exercise, "hint_policy")) {
      const policy = exercise.hint_policy;
      if (!shape(policy, ["allowed", "levels"]) || typeof policy.allowed !== "boolean"
        || !Array.isArray(policy.levels) || !unique(policy.levels)
        || !policy.levels.every(level => Number.isInteger(level) && level >= 1 && level <= 3)) return "unsupported";
    }
    if (Object.hasOwn(exercise, "presentation")) {
      const presentation = exercise.presentation;
      if (!shape(presentation, [], ["submit_label", "submit_control", "reveal_control", "add_step_label"])
        || Object.entries(presentation).some(([key, value]) => typeof value !== (key.endsWith("_control") ? "boolean" : "string"))) return "unsupported";
    }
    if (mode === "SELF_CHECK" && (exercise.input_schema !== null || exercise.step_schema !== null)) return "unsupported";
    if (["FINAL_ANSWER", "STRUCTURED_SOLUTION"].includes(mode) && exercise.input_schema === null) return "unsupported";
    if (["STEP_BY_STEP", "STRUCTURED_SOLUTION"].includes(mode) && exercise.step_schema === null) return "unsupported";
    // A newer immutable exercise version is acceptable; enum/object metadata is not a guessed form.
    return slots[mode];
  }
  window.MathStartUI = Object.freeze({dispatchExercise});
})();
