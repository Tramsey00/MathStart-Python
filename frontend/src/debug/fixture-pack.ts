// This module is reachable only from the development route.
import raw from "../../../specs/ui/fixtures/ui-states-v1.json";
import validate from "../shared/api/generated/UiFixturePack.mjs";
import { dispatchExercise, type PublicExercise } from "../shared/exercise/dispatcher";
import type { ViewState } from "../shared/ui/components";
interface FixturePack {
  fixture_version:1; fixture_only:true; provenance:{http_artifact:string};
  states:{state:ViewState;title:string;message:string}[]; exercises:PublicExercise[];
}
function checked(value: unknown): FixturePack {
  if (!validate(value)) throw new Error("Unsupported UI fixture pack");
  const pack=value as FixturePack;
  if (new Set(pack.states.map(s=>s.state)).size!==4
    || new Set(pack.exercises.map(e=>e.interaction_mode)).size!==4
    || new Set(pack.exercises.map(e=>e.id)).size!==4
    || pack.exercises.some(e=>dispatchExercise(e)==="unsupported")) throw new Error("Invalid UI fixture coverage");
  return pack;
}
export const fixtures=checked(raw);
