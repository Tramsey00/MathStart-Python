// @vitest-environment node
import {readFileSync} from "node:fs";
import {runInNewContext} from "node:vm";
import {describe,it,expect} from "vitest";
import raw from "../../specs/ui/fixtures/ui-states-v1.json";
import {dispatchExercise} from "../src/shared/exercise/dispatcher";
const slots=["self-check","final-answer","ordered-steps","structured-solution"];
const historical:{window:{MathStartUI?:{dispatchExercise:(v:unknown)=>string}}}={window:{}};
runInNewContext(readFileSync(new URL("../../static/mathstart/js/ui/schema-dispatch.js",import.meta.url),"utf8"),historical);
describe("historical dispatcher and canonical negative boundary",()=>{
  it("retains four slots without rendering or evaluating",()=>expect(raw.exercises.map(dispatchExercise)).toEqual(slots));
  it("matches the unchanged historical dispatcher for approved fixtures",()=>{
    for(const e of raw.exercises)expect(dispatchExercise(e)).toBe(historical.window.MathStartUI!.dispatchExercise(e));
  });
  const modes:unknown[]=[null,undefined,{},[],["SELF_CHECK"],new String("SELF_CHECK"),true,1,0,()=>{},Symbol("mode"),1n,
    {toString(){throw new Error("must not coerce");}},"__proto__","toString","UNKNOWN"];
  for(const [index,mode] of modes.entries()) it("rejects non-string/unknown mode "+index,()=>{
    for(const e of raw.exercises)expect(dispatchExercise({...e,interaction_mode:mode})).toBe("unsupported");
  });
  for(const name of ["input_schema","step_schema","exercise_version","version"] as const) it("rejects missing "+name,()=>{
    for(const e of raw.exercises){const clone:Record<string,unknown>={...e};delete clone[name];expect(dispatchExercise(clone)).toBe("unsupported");}
  });
  const malformed:Record<string,unknown>[]=[
    {input_schema:undefined},{step_schema:undefined},{input_schema:[]},{step_schema:"steps"},
    {input_schema:{type:"object",fields:[{name:"x",input_type:"text",required:"yes"}]}},
    {input_schema:{type:"object",fields:[],answer:"private"}},
    {step_schema:{type:"ordered_steps",allowed_step_types:[]}},
    {step_schema:{type:"ordered_steps",allowed_step_types:["UNKNOWN"]}},
    {step_schema:{type:"ordered_steps",allowed_step_types:["MATH_EXPRESSION","MATH_EXPRESSION"]}},
    {difficulty_level:3},{version:2},{skill_codes:["x","x"]},{allowed_help_actions:["CHECK"]},
    {answer:"private"},{checker:{code:"secret"}},{credentials:"secret"},
  ];
  malformed.forEach((change,index)=>it("rejects malformed metadata "+index,()=>{
    expect(dispatchExercise({...raw.exercises[3],...change})).toBe("unsupported");
  }));
  it("does not invoke accessors or coercion and handles cycles/proxy failures",()=>{
    const e={...raw.exercises[0]};Object.defineProperty(e,"interaction_mode",{get(){throw new Error("secret");}});
    expect(dispatchExercise(e)).toBe("unsupported");
    expect(dispatchExercise(new Proxy({}, {ownKeys(){throw new Error("private");}}))).toBe("unsupported");
    const cyclic:Record<string,unknown>={};cyclic.self=cyclic;expect(dispatchExercise(cyclic)).toBe("unsupported");
  });
  it("accepts newer consistent immutable identities",()=>{
    const e=structuredClone(raw.exercises[0]!);e.version=2;e.contract_version=2;e.exercise_version.version=2;e.exercise_version.contract_version=2;
    expect(dispatchExercise(e)).toBe("self-check");
  });
});
