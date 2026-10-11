import assert from "node:assert/strict";
import {readFileSync,readdirSync} from "node:fs";
import validateRegister from "../src/shared/api/generated/RegisterRequest.mjs";
import validatePack from "../src/shared/api/generated/UiFixturePack.mjs";
for(const name of readdirSync(new URL("../src/shared/api/generated/",import.meta.url)).filter(n=>n.endsWith(".mjs")))
  await import(new URL("../src/shared/api/generated/"+name,import.meta.url));
assert.equal(validateRegister({username:"x",password:"synthetic"}),true);
assert.equal(validateRegister({username:"😀".repeat(150),password:"synthetic"}),true);
assert.equal(validateRegister({username:"😀".repeat(151),password:"synthetic"}),false);
assert.equal(validateRegister({username:12,password:"synthetic"}),false);
assert.equal(validatePack(JSON.parse(readFileSync(new URL("../../specs/ui/fixtures/ui-states-v1.json",import.meta.url),"utf8"))),true);
console.log("PASS: all standalone validators import in native ESM; Unicode length and approved pack checks");
