// Scoped checkpoint verification. No Django/DB/full verify_repo.
import {spawnSync} from "node:child_process";
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {fileURLToPath} from "node:url";
const frontend=fileURLToPath(new URL("../",import.meta.url));
const evidence=fileURLToPath(new URL("../../docs/acceptance/MS7-MIG-I01/checkpoint2/",import.meta.url));
mkdirSync(evidence,{recursive:true});
const npm=process.env.npm_execpath;
if(!npm)throw new Error("Run through npm run verify:foundation");
const commands=[
  ["versions",process.execPath,["--version"]],
  ["npm-version",process.execPath,[npm,"--version"]],
  ["typecheck",process.execPath,[npm,"run","typecheck"]],
  ["native-validator-esm",process.execPath,["scripts/check-validators.mjs"]],
  ["unit-component-security",process.execPath,[npm,"test"]],
  ["historical-dispatcher",process.execPath,["--test","../tests/test_i02_schema_dispatch.js"]],
  ["production-build",process.execPath,[npm,"run","build"]],
  ["dependency-tree",process.execPath,[npm,"ls","--depth=0"]],
  ["audit",process.execPath,[npm,"audit","--audit-level=low"]],
];
const results=[];let failed=false;
for(const [name,exe,args] of commands){
  const r=spawnSync(exe,args,{cwd:frontend,encoding:"utf8",maxBuffer:16*1024*1024});
  const entry={name,command:[exe,...args],exit_code:r.status,stdout:r.stdout??"",stderr:r.stderr??"",error:r.error?.message??null};
  results.push(entry);console.log(name+": "+r.status);
  if(r.status!==0)failed=true;
}
writeFileSync(evidence+"command-results.json",JSON.stringify({source_input:"8d958aeeb17da46839722441425ccbb5889e2ab7",
  executed_at:new Date().toISOString(),results},null,2)+"\n");
process.exitCode=failed?1:0;
