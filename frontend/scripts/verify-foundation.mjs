// Scoped frontend verification. Captures are immutable; no Django/DB/full verify_repo.
import {spawnSync} from "node:child_process";
import {createHash} from "node:crypto";
import {closeSync,existsSync,lstatSync,mkdirSync,mkdtempSync,openSync,readFileSync,readlinkSync,realpathSync,writeFileSync} from "node:fs";
import {dirname,isAbsolute,join,relative,resolve,sep} from "node:path";
import {fileURLToPath} from "node:url";

const frontend=fileURLToPath(new URL("../",import.meta.url));
const root=realpathSync(join(frontend,".."));
const sha=value=>createHash("sha256").update(value).digest("hex");
const posix=value=>value.split(sep).join("/");
const gitEnv={...process.env,GIT_OPTIONAL_LOCKS:"0"};
function git(args) {
  const r=spawnSync("git",args,{cwd:root,env:gitEnv,encoding:"utf8",maxBuffer:32*1024*1024,windowsHide:true});
  if(r.error||r.status!==0)throw new Error("Cannot establish verification Git provenance");
  return r.stdout;
}
function snapshot(output) {
  if(realpathSync(git(["rev-parse","--show-toplevel"]).trim())!==root)throw new Error("Unexpected repository root");
  const excluded=posix(relative(root,output));
  const paths=[...new Set(git(["ls-files","--cached","--others","--exclude-standard","-z"]).split("\0").filter(p=>p&&p!==excluded))].sort();
  const files=paths.map(path=>{
    const absolute=join(root,path);
    if(!existsSync(absolute))return {path,deleted:true};
    const stat=lstatSync(absolute);
    const bytes=stat.isSymbolicLink()?Buffer.from(readlinkSync(absolute)):readFileSync(absolute);
    return {path,size:bytes.length,sha256:sha(bytes)};
  });
  const status=git(["status","--porcelain=v1","--untracked-files=all"]);
  const history=files.filter(f=>/^docs\/acceptance\/MS7-MIG-I01\/(checkpoint1|checkpoint2|final)\//.test(f.path));
  return {head:git(["rev-parse","HEAD"]).trim(),branch:git(["branch","--show-current"]).trim(),
    tree:git(["rev-parse","HEAD^{tree}"]).trim(),dirty:status.length!==0,status_porcelain:status,
    source_fingerprint_sha256:sha(JSON.stringify(files)),source_file_count:files.length,history};
}
function safeParents(directory) {
  const rel=relative(root,directory);
  if(rel.startsWith(".."+sep)||rel===".."||isAbsolute(rel))throw new Error("Evidence output must stay inside the task repository");
  let current=root;
  for(const part of rel.split(sep).filter(Boolean)) {
    current=join(current,part);
    if(!existsSync(current))mkdirSync(current);
    const stat=lstatSync(current);
    if(stat.isSymbolicLink()||!stat.isDirectory())throw new Error("Unsafe evidence output directory");
  }
}
function outputPath(args) {
  if(args.length&&!(args.length===2&&args[0]==="--output"&&args[1]&&!args[1].startsWith("--")))
    throw new Error("Usage: npm run verify:foundation -- [--output NEW_FILE.json]");
  if(args.length) {
    const target=resolve(frontend,args[1]),rel=posix(relative(root,target));
    if(rel.startsWith("../")||isAbsolute(rel)||/^\.git(\/|$)/i.test(rel)
      ||/^docs\/acceptance\/MS7-MIG-I01\/(checkpoint1|checkpoint2|final)(\/|$)/i.test(rel))
      throw new Error("Protected or external evidence output");
    if(!target.endsWith(".json"))throw new Error("Evidence output must be a new JSON file");
    safeParents(dirname(target));
    return target;
  }
  const directory=join(frontend,".cache","verification-runs");
  safeParents(directory);
  const run=mkdtempSync(join(directory,"run-"+new Date().toISOString().replaceAll(/[:.]/g,"-")+"-"));
  return join(run,"command-results.json");
}
export function runFoundation(args=process.argv.slice(2)) {
  const npm=process.env.npm_execpath;
  if(!npm)throw new Error("Run through npm run verify:foundation");
  // Verify the repository before creating any output, then reserve a NEW file atomically.
  if(realpathSync(git(["rev-parse","--show-toplevel"]).trim())!==root)throw new Error("Unexpected repository root");
  const output=outputPath(args),before=snapshot(output);
  const fd=openSync(output,"wx"); // Existing files, including symlinks, are never overwritten.
  const started=new Date().toISOString();
  const report={format:"i01-verification-run-v2",started_at:started,finished_at:null,cwd:frontend,
    output,tooling:{node:process.version,npm_cli:npm},git_before:before,git_after:null,
    tested_implementation_sha:null,dirty_or_uncommitted:before.dirty,
    source_changed_during_run:null,history_integrity:null,results:[],exit_code:1};
  let failed=false;
  try {
    const commands=[
      ["node-version",process.execPath,["--version"]],
      ["npm-version",process.execPath,[npm,"--version"]],
      ["generate-api",process.execPath,[npm,"run","generate:api"]],
      ["typecheck",process.execPath,[npm,"run","typecheck"]],
      ["native-validator-esm",process.execPath,["scripts/check-validators.mjs"]],
      ["unit-component-security",process.execPath,[npm,"test"]],
      ["historical-dispatcher",process.execPath,["--test","../tests/test_i02_schema_dispatch.js"]],
      ["production-build",process.execPath,[npm,"run","build"]],
      ["dependency-tree",process.execPath,[npm,"ls","--depth=0"]],
      ["audit",process.execPath,[npm,"audit","--audit-level=low"]],
    ];
    for(const [name,exe,args] of commands) {
      const begin=Date.now();
      const r=spawnSync(exe,args,{cwd:frontend,encoding:"utf8",maxBuffer:16*1024*1024,windowsHide:true});
      report.results.push({name,command:[exe,...args],cwd:frontend,started_at:new Date(begin).toISOString(),
        finished_at:new Date().toISOString(),duration_ms:Date.now()-begin,exit_code:r.status,
        signal:r.signal,stdout:r.stdout??"",stderr:r.stderr??"",error:r.error?.message??null});
      console.log(name+": "+r.status);
      if(r.error||r.status!==0)failed=true;
    }
    const after=snapshot(output);
    report.git_after=after;
    report.source_changed_during_run=before.head!==after.head||before.source_fingerprint_sha256!==after.source_fingerprint_sha256;
    const a=new Map(before.history.map(f=>[f.path,JSON.stringify(f)]));
    const b=new Map(after.history.map(f=>[f.path,JSON.stringify(f)]));
    const changed=[...new Set([...a.keys(),...b.keys()])].filter(p=>a.get(p)!==b.get(p));
    report.history_integrity={file_count:before.history.length,before_sha256:sha(JSON.stringify(before.history)),
      after_sha256:sha(JSON.stringify(after.history)),changed_paths:changed};
    report.dirty_or_uncommitted=before.dirty||after.dirty||report.source_changed_during_run;
    report.tested_implementation_sha=report.dirty_or_uncommitted?null:before.head;
    if(changed.length||report.source_changed_during_run)failed=true;
  } catch {
    report.runner_error="Unable to complete provenance or verification; no passing claim";
    failed=true;
  } finally {
    report.finished_at=new Date().toISOString();
    report.exit_code=failed?1:0;
    try {writeFileSync(fd,JSON.stringify(report,null,2)+"\n");} finally {closeSync(fd);}
  }
  console.log("EVIDENCE_PATH="+output);
  console.log(report.dirty_or_uncommitted?"Tested uncommitted working tree; HEAD is provenance only":"Tested Git SHA="+report.tested_implementation_sha);
  return report.exit_code;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  try {process.exitCode=runFoundation();} catch(error) {
    console.error(error instanceof Error?error.message:"Verification startup failed");
    process.exitCode=1;
  }
}
