import {readdirSync,readFileSync,statSync} from "node:fs";
import {join,relative} from "node:path";
import {fileURLToPath} from "node:url";
const root=fileURLToPath(new URL("../build/client/",import.meta.url));
function files(directory){return readdirSync(directory).flatMap(name=>{
  const p=join(directory,name);return statSync(p).isDirectory()?files(p):[p];
});}
const all=files(root);
const forbidden=["FIXTURE ONLY","Только синтетические примеры","fixture_only_self_check","fixture_only_final_answer",
  "fixture_only_step_by_step","fixture_only_structured_solution","__ui__/foundation","__i01_reference__","foundation-gallery",
  "TEST_PASSWORD_CANARY_DO_NOT_SHIP","synthetic-csrf","PRIVATE server details"];
for(const p of all.filter(p=>/\.(html|js|json|css|map)$/.test(p))){
  const content=readFileSync(p,"utf8");
  for(const marker of forbidden)if(content.includes(marker))throw new Error("Forbidden production payload: "+relative(root,p));
}
if(all.filter(p=>p.endsWith(".html")).some(p=>relative(root,p)!=="index.html"))throw new Error("Unexpected/private HTML export");
if(all.some(p=>p.endsWith(".map")))throw new Error("Unreviewed source map export");
const graph=JSON.parse(readFileSync(new URL("../.cache/production-client-modules.json",import.meta.url),"utf8"));
if(graph.forbidden.length)throw new Error("Debug/private fixture module in production graph");
console.log("PASS: production payload scan, "+graph.modules.length+" client modules, anonymous index only ("+all.length+" files)");
