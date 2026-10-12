import validate from "../api/generated/PublicExerciseDTO.mjs";
import type { components } from "../api/generated/openapi";
import { isJsonTree } from "../api/json-boundary";
export type PublicExercise = components["schemas"]["PublicExerciseDTO"];
export type FoundationSlot = "self-check" | "final-answer" | "ordered-steps" | "structured-solution" | "unsupported";
const slots = { SELF_CHECK: "self-check", FINAL_ANSWER: "final-answer",
  STEP_BY_STEP: "ordered-steps", STRUCTURED_SOLUTION: "structured-solution" } as const;

export function isPublicExercise(value: unknown): value is PublicExercise {
  try {
    if (!isJsonTree(value) || !validate(value)) return false;
    const e=value as PublicExercise;
    const version=e.exercise_version;
    return version.exercise_id===e.id && version.version===e.version
      && version.contract_version===e.version && e.contract_version===e.version
      && e.difficulty===({1:"easy",2:"easy",3:"medium",4:"hard"} as const)[e.difficulty_level];
  } catch { return false; }
}
export function dispatchExercise(value: unknown): FoundationSlot {
  if (!isPublicExercise(value)) return "unsupported";
  // No renderer, assessment, normalization, reveal or progress mutation.
  return slots[value.interaction_mode];
}
