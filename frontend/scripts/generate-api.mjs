import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import openapiTS, { astToString } from "openapi-typescript";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import standaloneCode from "ajv/dist/standalone/index.js";
const root = fileURLToPath(new URL("../../", import.meta.url));
const read = p => JSON.parse(readFileSync(resolve(root, p), "utf8"));
const hash = b => createHash("sha256").update(b).digest("hex");
for (const [manifest, field] of [
  ["specs/api/candidate-manifest-v1.json", "artifacts"],
  ["docs/acceptance/MS7-MIG-R02/contract-digests.json", "files"],
]) {
  const pins = read(manifest)[field];
  for (const [p, expected] of Object.entries(pins)) {
    const blob = execFileSync("git", ["show", "HEAD:" + p], { cwd: root });
    if (hash(blob) !== expected) throw new Error("Frozen Git pin mismatch: " + p);
    // Windows checkout newline normalization is the only permitted difference.
    if (readFileSync(resolve(root,p),"utf8").replace(/\r\n/g,"\n") !== blob.toString("utf8").replace(/\r\n/g,"\n"))
      throw new Error("Contract working copy changed: " + p);
  }
}
const oas = read("specs/api/openapi-v1.json");
const dto = read("specs/api/schemas/dto-v1.schema.json");
const ajv = new Ajv2020({ strict: false, allErrors: false, ownProperties: true, validateFormats: true,
  coerceTypes: false, useDefaults: false, removeAdditional: false, code: { source: true, esm: true } });
addFormats(ajv);
// No outer dialect extension is used: bind the official #meta anchor statically.
// Ajv nested dynamic references otherwise resolve to the enclosing OAS object.
const structural = read("specs/api/schemas/openapi-3.1-2025-09-15.schema.json");
function bindMeta(node) {
  if (!node || typeof node !== "object") return;
  if (node.$dynamicRef === "#meta") { delete node.$dynamicRef; node.$ref = "#/$defs/schema"; }
  for (const child of Object.values(node)) bindMeta(child);
}
bindMeta(structural);
ajv.addFormat("media-range", /^[a-zA-Z0-9!#$&^_.+-]+\/[a-zA-Z0-9!#$&^_.+*-]+$/);
if (!ajv.compile(structural)(oas))
  throw new Error("Invalid canonical OpenAPI");
ajv.addSchema(dto);
ajv.addSchema({$id:"urn:mathstart:api:dto:v1", $ref:dto.$id, $defs:dto.$defs});
for (const name of Object.keys(dto.$defs)) ajv.getSchema(dto.$id + "#/$defs/" + name);
const inventory = read("specs/migration/r02-v1/implemented-routes-v1.json").operations;
if (inventory.length !== 37) throw new Error("Unexpected canonical inventory");
for (const op of inventory) {
  if (oas.paths[op.path]?.[op.method]?.operationId !== op.operation_id) throw new Error("Operation inventory mismatch");
}
const generated = new Map();
generated.set("schema-helpers.mjs", "// JSON Schema lengths count Unicode code points, including unpaired surrogates.\nexport default function unicodeLength(text){let length=0;for(const point of text){void point;length++;}return length;}\n");
generated.set("schema-helpers.d.mts", "export default function unicodeLength(text:string):number;\n");
generated.set("openapi.d.ts", "// Generated from frozen canonical OpenAPI; do not edit.\n" +
  astToString(await openapiTS(new URL("../../specs/api/openapi-v1.json", import.meta.url))));
const names = new Set(["PublicExerciseDTO"]);
const ops = inventory.filter(op => op.baseline_state === "IMPLEMENTED");
for (const op of ops) {
  if (op.request) names.add(op.request);
  names.add(op.response);
  for (const [status, response] of Object.entries(oas.paths[op.path][op.method].responses)) {
    const resolved = response.$ref ? oas.components.responses[response.$ref.split("/").at(-1)] : response;
    const name = resolved.content?.["application/json"]?.schema?.$ref?.split("/").at(-1);
    if (!name) throw new Error("Unvalidated response: " + op.operation_id + "/" + status);
    names.add(name);
  }
}
// Emit each root using only its transitive definitions, never exchange fixtures.
for (const name of names) {
  const needed = new Set();
  function visit(value) {
    if (!value || typeof value !== "object") return;
    if (typeof value.$ref === "string" && value.$ref.startsWith("#/$defs/")) {
      const child = value.$ref.slice(8);
      if (!needed.has(child)) { needed.add(child); visit(dto.$defs[child]); }
    }
    for (const child of Object.values(value)) visit(child);
  }
  visit(dto.$defs[name]);
  const schema = { ...dto.$defs[name], $defs: Object.fromEntries([...needed].map(n => [n,dto.$defs[n]])) };
  const validator = ajv.compile(schema);
  let code = standaloneCode(ajv, validator);
  // Ajv standalone's helpers are static bundler imports, no runtime eval/compilation.
  const imports = new Map();
  code = code.replace(/require\("([^"]+)"\)/g, (_, p) => {
    if (p !== "ajv/dist/runtime/ucs2length") throw new Error("Unexpected helper import: " + p);
    if (!imports.has(p)) imports.set(p, "helper" + imports.size);
    return imports.get(p);
  });
  code = [...imports].map(([p,n]) => 'import * as ' + n + ' from "' + "./schema-helpers.mjs" + '";').join("\n") + "\n" + code;
  generated.set(name + ".mjs", "// Generated canonical schema validator; no fixture payloads.\n" + code + "\n");
  generated.set(name + ".d.mts", "declare const validate: (value: unknown) => boolean;\nexport default validate;\n");
}
const ui = read("specs/ui/ui-state-fixtures-v1.schema.json");
const validateUi = ajv.compile(ui);
if (!validateUi(read("specs/ui/fixtures/ui-states-v1.json"))) throw new Error("Invalid approved UI fixture pack");
let uiCode = standaloneCode(ajv, validateUi);
const uiImports = new Map();
uiCode = uiCode.replace(/require\("([^"]+)"\)/g, (_,p) => {
  if (p !== "ajv/dist/runtime/ucs2length") throw new Error("Unexpected UI helper: " + p);
  if (!uiImports.has(p)) uiImports.set(p,"uiHelper"+uiImports.size);
  return uiImports.get(p);
});
generated.set("UiFixturePack.mjs", [...uiImports].map(([p,n])=>'import * as '+n+' from "'+'./schema-helpers.mjs'+'";').join("\n")+"\n"+uiCode+"\n");
generated.set("UiFixturePack.d.mts", "declare const validate:(value:unknown)=>boolean;\nexport default validate;\n");
generated.set("identity-contracts.ts", "// Generated canonical wire types. No fixtures.\nimport type {components} from './openapi';\nexport interface IdentityContracts {\n" +
  ops.map(op=>op.operation_id+": {request: "+(op.request?"components['schemas']['"+op.request+"']":"never")+"; response: components['schemas']['"+op.response+"']};").join("\n")+"\n}\n");
const imports = [...names].map(n => 'import ' + n + ' from "./' + n + '.mjs";').join("\n");
generated.set("identity-operations.ts", "// Generated from canonical OpenAPI + R02 inventory. Only eight baseline operations.\n" +
  imports + "\nexport const identityOperations = " + JSON.stringify(Object.fromEntries(ops.map(op => [op.operation_id, {
    path: op.path, method: op.method.toUpperCase(), receipt: op.idempotency, request: op.request,
    success: op.status, responses: Object.fromEntries(Object.entries(oas.paths[op.path][op.method].responses).map(([status,r]) => {
      const rr=r.$ref?oas.components.responses[r.$ref.split("/").at(-1)]:r;
      return [status,rr.content["application/json"].schema.$ref.split("/").at(-1)];
    }))
  }])),null,2).replace(/"request": "(.*?)"/g, '"request": $1').replace(/"request": null/g,'"request": null')
    .replace(/"(\d+)": "([^"]+)"/g,'"$1": $2') + " as const;\n");
for (const [p, text] of generated) {
  const target = resolve(root,"frontend/src/shared/api/generated",p);
  if (process.argv.includes("--check")) {
    if (readFileSync(target,"utf8") !== text) throw new Error("Generated contract stale: " + p);
  } else { mkdirSync(dirname(target),{recursive:true}); writeFileSync(target,text); }
}
console.log("PASS: 17 frozen + 24 R02 pins; OAS, DTO schemas, 37 operations; generated types and " + names.size + " boundary validators");
