// @vitest-environment node
import {expect,it} from "vitest";
import {spawnSync} from "node:child_process";
import {existsSync,mkdirSync,mkdtempSync,readFileSync,writeFileSync} from "node:fs";
import {join,resolve} from "node:path";
import {fileURLToPath} from "node:url";
const frontend=fileURLToPath(new URL("../",import.meta.url));
const source=fileURLToPath(new URL("../scripts/verify-foundation.mjs",import.meta.url));
const parent=join(frontend,".cache","verification-test-fixtures");
mkdirSync(parent,{recursive:true});
const npm=process.env.npm_execpath;
if(!npm)throw new Error("Run regression tests through npm test");
function fixture() {
  const root=mkdtempSync(join(parent,"run-"));
  const put=(p:string,s:string)=>{const path=join(root,p);mkdirSync(resolve(path,".."),{recursive:true});writeFileSync(path,s);};
  put(".gitignore",".cache/\n");
  put("package.json",JSON.stringify({private:true,type:"commonjs"}));
  put("frontend/scripts/verify-foundation.mjs",readFileSync(source,"utf8"));
  const scripts=Object.fromEntries(["generate:api","typecheck","test","build"].map(k=>[k,"node scripts/noop.mjs"]));
  put("frontend/package.json",JSON.stringify({name:"synthetic-verification-fixture",version:"1.0.0",private:true,type:"module",scripts:{...scripts,"verify:foundation":"node scripts/verify-foundation.mjs"}}));
  put("frontend/package-lock.json",JSON.stringify({name:"synthetic-verification-fixture",version:"1.0.0",lockfileVersion:3,requires:true,packages:{"":{name:"synthetic-verification-fixture",version:"1.0.0"}}}));
  put("frontend/scripts/noop.mjs",'import fs from "node:fs";fs.mkdirSync(".cache",{recursive:true});fs.appendFileSync(".cache/commands.log","synthetic command\\n");console.log("synthetic runner fixture only");\n');
  put("frontend/scripts/check-validators.mjs",'console.log("synthetic validator fixture only");\n');
  put("tests/test_i02_schema_dispatch.js",'const test=require("node:test");test("synthetic runner fixture only",()=>{});\n');
  put("marker.txt","original source\n");
  for(const stage of ["checkpoint1","checkpoint2","final"])put("docs/acceptance/MS7-MIG-I01/"+stage+"/command-results.json",JSON.stringify({historical:true,stage,immutable:"original bytes"})+"\n");
  const env={...process.env,GIT_OPTIONAL_LOCKS:"0"};
  for(const args of [["init","--quiet"],["add","--","."],["-c","user.name=Synthetic fixture","-c","user.email=fixture@example.invalid","commit","--quiet","-m","synthetic fixture"]]) {
    const r=spawnSync("git",args,{cwd:root,env,encoding:"utf8",windowsHide:true});
    if(r.status!==0)throw new Error("Unable to initialize isolated synthetic fixture");
  }
  const head=spawnSync("git",["rev-parse","HEAD"],{cwd:root,env,encoding:"utf8",windowsHide:true}).stdout.trim();
  const history=()=>["checkpoint1","checkpoint2","final"].map(stage=>readFileSync(join(root,"docs/acceptance/MS7-MIG-I01",stage,"command-results.json")));
  const run=(args:string[]=[])=>spawnSync(process.execPath,[npm!,"run","verify:foundation",...(args.length?["--",...args]:[])],
    {cwd:join(root,"frontend"),encoding:"utf8",maxBuffer:8*1024*1024,windowsHide:true});
  const evidence=(r:ReturnType<typeof run>)=>{
    const path=r.stdout.match(/^EVIDENCE_PATH=(.+)$/m)?.[1]?.trim();
    if(!path)throw new Error("Missing new verification evidence: "+r.stdout+" "+r.stderr);
    return {path,bytes:readFileSync(path),report:JSON.parse(readFileSync(path,"utf8"))};
  };
  return {root,put,head,history,run,evidence};
}
it("keeps historical JSON byte-identical after actual npm run verify:foundation and stores fresh runs",()=>{
  const f=fixture(),before=f.history(),first=f.run();
  expect(first.status,first.stdout+first.stderr).toBe(0);
  expect(f.history().every((bytes,index)=>bytes.equals(before[index]!))).toBe(true);
  const a=f.evidence(first);
  expect(a.path).toContain(join(".cache","verification-runs"));
  expect(a.report.git_before).toMatchObject({head:f.head,dirty:false});
  expect(a.report.tested_implementation_sha).toBe(f.head);
  expect(a.report.dirty_or_uncommitted).toBe(false);
  expect(a.report.history_integrity.changed_paths).toEqual([]);
  expect(a.report.started_at).toBeTruthy();
  expect(a.report.finished_at).toBeTruthy();
  expect(a.report.results).toHaveLength(10);
  for(const result of a.report.results) {
    expect(result.exit_code).toBe(0);
    expect(result.command.length).toBeGreaterThan(1);
    expect(result.started_at).toBeTruthy();
    expect(result.finished_at).toBeTruthy();
  }
  // Change actual source, not just HEAD metadata; the next report must not call it committed.
  f.put("marker.txt","uncommitted source\n");
  const second=f.run();
  expect(second.status,second.stdout+second.stderr).toBe(0);
  expect(f.history().every((bytes,index)=>bytes.equals(before[index]!))).toBe(true);
  const b=f.evidence(second);
  expect(b.path).not.toBe(a.path);
  expect(readFileSync(a.path)).toEqual(a.bytes);
  expect(b.report.git_before).toMatchObject({head:f.head,dirty:true});
  expect(b.report.dirty_or_uncommitted).toBe(true);
  expect(b.report.tested_implementation_sha).toBeNull();
  expect(b.report.git_before.source_fingerprint_sha256).not.toBe(a.report.git_before.source_fingerprint_sha256);
},60_000);
it("accepts an explicit new output and refuses to overwrite it without running checks again",()=>{
  const f=fixture(),r=f.run(["--output",".cache/explicit.json"]);
  expect(r.status,r.stdout+r.stderr).toBe(0);
  const a=f.evidence(r),log=join(f.root,"frontend/.cache/commands.log"),before=readFileSync(log);
  const repeat=f.run(["--output",".cache/explicit.json"]);
  expect(repeat.status).not.toBe(0);
  expect(readFileSync(a.path)).toEqual(a.bytes);
  expect(readFileSync(log)).toEqual(before);
},30_000);
it.each(["checkpoint1","checkpoint2","final","FINAL"])("rejects historical %s output, including a new filename",stage=>{
  const f=fixture(),before=f.history(),output="../docs/acceptance/MS7-MIG-I01/"+stage+"/new.json";
  const r=f.run(["--output",output]);
  expect(r.status).not.toBe(0);
  expect(r.stderr).toContain("Protected");
  expect(f.history().every((bytes,index)=>bytes.equals(before[index]!))).toBe(true);
  expect(existsSync(resolve(f.root,"frontend",output))).toBe(false);
  expect(existsSync(join(f.root,"frontend/.cache/commands.log"))).toBe(false);
});
it.each([["--output"],["--unknown"],["--output","../.git/new.json"],["--output","../.GIT/new.json"],["--output","../../../outside.json"]])("rejects invalid or unsafe output args %j",(...args)=>{
  const f=fixture(),before=f.history(),r=f.run(args);
  expect(r.status).not.toBe(0);
  expect(f.history().every((bytes,index)=>bytes.equals(before[index]!))).toBe(true);
  expect(existsSync(join(f.root,"frontend/.cache/commands.log"))).toBe(false);
});
it("fails verification rather than claiming a stable SHA when a command changes source",()=>{
  const f=fixture();
  f.put("frontend/scripts/noop.mjs",'import fs from "node:fs";fs.appendFileSync("../marker.txt","changed during run\\n");\n');
  const r=f.run(),result=f.evidence(r).report;
  expect(r.status).not.toBe(0);
  expect(result.source_changed_during_run).toBe(true);
  expect(result.tested_implementation_sha).toBeNull();
},30_000);
