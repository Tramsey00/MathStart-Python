// Checkpoint2 evidence only. No application execution, DB, environment copy or Git writes.
import {createHash} from "node:crypto";
import {execFileSync} from "node:child_process";
import {copyFileSync,existsSync,mkdirSync,readFileSync,readdirSync,statSync,writeFileSync} from "node:fs";
import {dirname,join,relative,resolve} from "node:path";
import {fileURLToPath} from "node:url";
const root=fileURLToPath(new URL("../../",import.meta.url));
const prefix="docs/acceptance/MS7-MIG-I01/checkpoint2/";
const cp1prefix="docs/acceptance/MS7-MIG-I01/checkpoint1/";
const input="8d958aeeb17da46839722441425ccbb5889e2ab7";
const canonical="8c11edadc8debc81432d1db1145feac504f09061";
const primary="C:/Users/User/PycharmProjects/MathStart-Python";
const sha=b=>createHash("sha256").update(b).digest("hex");
const posix=p=>p.replaceAll("\\","/");
const git=(args,cwd=root)=>execFileSync("git",args,{cwd,env:{...process.env,GIT_OPTIONAL_LOCKS:"0"},maxBuffer:16*1024*1024});
const gitText=(args,cwd)=>git(args,cwd).toString("utf8").trim();
const read=p=>readFileSync(join(root,p));
const json=p=>JSON.parse(read(p));
const write=(p,value)=>{const path=join(root,p);mkdirSync(dirname(path),{recursive:true});writeFileSync(path,typeof value==="string"?value:JSON.stringify(value,null,2)+"\n");};
const head=gitText(["rev-parse","HEAD"]), branch=gitText(["branch","--show-current"]);
if(head!==input||branch!=="ms7-mig-i01-foundation")throw new Error("Unexpected task HEAD/branch; do not refresh stale evidence");
const tracked=gitText(["diff","HEAD","--name-only"]);
if(tracked)throw new Error("Accepted tracked source changed");
const primaryHead=gitText(["rev-parse","HEAD"],primary);
const primaryStatus=gitText(["status","--porcelain"],primary);
if(primaryHead!==canonical||primaryStatus)throw new Error("Primary checkout isolation changed");
const results=json(prefix+"command-results.json");
if(results.source_input!==input||results.results.some(r=>r.exit_code!==0||r.error))throw new Error("Scoped verification failed/missing");
const old=json(cp1prefix+"content-manifest.json");
const preserved=old.files.filter(f=>f.path.startsWith(cp1prefix));
for(const file of preserved)if(sha(read(file.path))!==file.sha256||read(file.path).length!==file.size)throw new Error("Checkpoint1 evidence changed: "+file.path);
const sourcePaths=["templates/base.html","static/mathstart/css/site.css","static/mathstart/css/ui/tokens.css","static/mathstart/css/ui/foundation.css"];
const sources=sourcePaths.map(path=>{
  const baseline=git(["show",canonical+":"+path]), accepted=git(["show",input+":"+path]), current=read(path);
  if(!baseline.equals(accepted)||current.toString("utf8").replaceAll("\r\n","\n")!==accepted.toString("utf8").replaceAll("\r\n","\n"))throw new Error("Appearance source changed: "+path);
  return {path,canonical_blob_sha256:sha(baseline),accepted_blob_sha256:sha(accepted),working_file_sha256:sha(current),canonical_equals_accepted:true,working_text_equal_ignoring_crlf:true};
});
const browser=json(prefix+"browser-evidence.json");
if(browser.sourceInput!==input||browser.canonicalAppearance!==canonical||browser.screenshots.length!==15)throw new Error("Browser evidence provenance");
function jpegDimensions(buffer) {
  if(buffer[0]!==0xff||buffer[1]!==0xd8)throw new Error("Not a JPEG");
  let i=2;
  while(i<buffer.length){
    if(buffer[i++]!==0xff)throw new Error("Invalid JPEG marker");
    while(buffer[i]===0xff)i++;
    const marker=buffer[i++];
    if(marker===0xda||marker===0xd9)break;
    if(marker===0x01||(marker>=0xd0&&marker<=0xd7))continue;
    const length=buffer.readUInt16BE(i);
    if([0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf].includes(marker))return {width:buffer.readUInt16BE(i+5),height:buffer.readUInt16BE(i+3)};
    i+=length;
  }
  throw new Error("JPEG dimensions unavailable");
}
const shots=browser.screenshots.map(s=>{
  if(!/^[a-z0-9-]+\.jpg$/.test(s.file))throw new Error("Unsafe screenshot path");
  const path=prefix+"screenshots/"+s.file, bytes=read(path);
  return {...s,path,pixelDimensions:jpegDimensions(bytes),size:bytes.length,sha256:sha(bytes)};
});
for(const width of [360,768,1440]){
  const a=shots.find(s=>s.file==="react-shell-"+width+".jpg"),b=shots.find(s=>s.file==="source-shell-"+width+".jpg");
  if(a.sha256!==b.sha256)throw new Error("Shell screenshots differ");
}
write(prefix+"screenshot-index.json",{source_input:input,canonical_appearance:canonical,implementation_sha:null,uncommitted:true,captured_at:browser.capturedAt,browser:browser.browser,browser_version_source:"Current User-Agent Client Hints; separate Codex IAB version unavailable/unconfirmed",comparison:"Controlled source-derived empty shell; no live Django/full-page parity",pixel_dimensions_note:"Viewport is browser CSS viewport. Full-page JPEG may exclude the vertical scrollbar gutter; raster dimensions are recorded separately.",screenshots:shots});
write(prefix+"screenshot-index.md","# Checkpoint2 screenshot index\n\nAccepted input: "+input+". Canonical appearance: "+canonical+". Implementation SHA: none (uncommitted; content-manifest.json).\n\nBrowser: Codex In-app Browser; Chromium / Google Chrome155.0.8059.27, from current UA Client Hints. Separate Codex IAB version unavailable/unconfirmed. Captured evidence: "+browser.capturedAt+". Raw metadata and per-file SHA-256: [JSON index](screenshot-index.json), [browser observations](browser-evidence.json).\n\nSource-derived empty shell comparison only; live Django unavailable. Browser viewport and actual JPEG raster size are distinct; full-page images can exclude the scrollbar gutter.\n\n|Screenshot|Exact URL|Viewport CSS px|Raster px|Full page|State|\n|---|---|---|---|---|---|\n"+shots.map(s=>"|["+s.file+"](screenshots/"+s.file+")|"+s.url+"|"+s.viewport.width+"×"+s.viewport.height+"|"+s.pixelDimensions.width+"×"+s.pixelDimensions.height+"|"+s.fullPage+"|"+s.state+"|").join("\n")+"\n");
copyFileSync(join(root,"frontend/.cache/production-client-modules.json"),join(root,prefix+"production-client-modules.json"));
const graph=json(prefix+"production-client-modules.json");
if(graph.forbidden.length)throw new Error("Forbidden production graph module");
const excluded=new Set(["node_modules",".cache",".react-router","build","test-results","playwright-report"]);
function walk(base,filter=false){return readdirSync(base).sort().flatMap(name=>{
  if(filter&&excluded.has(name))return [];
  const path=join(base,name);return statSync(path).isDirectory()?walk(path,filter):[posix(relative(root,path))];
});}
const digest=path=>{const b=read(path);return {path,size:b.length,sha256:sha(b)};};
const artifacts=walk(join(root,"frontend/build/client"));
write(prefix+"build-manifest.json",{source_input:input,implementation_sha:null,production_client_module_count:graph.modules.length,files:artifacts.map(digest),semantics:"Actual scoped production build artifacts; paths are task-relative and artifacts themselves remain ignored."});
write(prefix+"isolation.json",{recorded_at:new Date().toISOString(),task_worktree:posix(root),task_branch:branch,task_head:head,accepted_tracked_changed_paths:[],primary:{path:primary,head:primaryHead,status_porcelain:primaryStatus},appearance_sources:sources,checkpoint1_hashed_evidence_verified:preserved.map(f=>f.path),database:"NOT_ACCESSED; no fingerprint re-read; no DB/env/migration/publication command is performed by this script",github:"NO_MUTATIONS",implementation_sha:null});
const owned=()=>[...walk(join(root,"frontend"),true),...walk(join(root,"docs/acceptance/MS7-MIG-I01")),"docs/agent-traces/MS7-MIG-I01.md","docs/exec-plans/active/MS7-MIG-I01.md"].sort();
const outputs=["changed-files.txt","stage2-delta.json","evidence-validation.json","content-manifest.json"].map(x=>prefix+x);
let candidates=[...new Set([...owned(),...outputs])].sort();
write(prefix+"changed-files.txt",candidates.join("\n")+"\n");
const deltaExcluded=new Set([prefix+"stage2-delta.json",prefix+"content-manifest.json",prefix+"evidence-validation.json"]);
const previous=new Map(old.files.map(f=>[f.path,f]));
const delta=candidates.filter(p=>!deltaExcluded.has(p)).map(path=>{
  const current=digest(path),before=previous.get(path);
  return {...current,status:!before?"NEW":before.sha256===current.sha256?"UNCHANGED":"CHANGED",checkpoint1_sha256:before?.sha256??null};
});
write(prefix+"stage2-delta.json",{source_input:input,compared_to:cp1prefix+"content-manifest.json",semantics:"NEW means not hashed in checkpoint1; it does not imply a file was created later. Three self-referential current evidence files are excluded.",excluded:[...deltaExcluded],deleted_checkpoint1_paths:old.files.filter(f=>!existsSync(join(root,f.path))).map(f=>f.path),files:delta});
const mapping=json(prefix+"old-to-new-evidence.json");
const mappingPaths=mapping.records.flatMap(r=>[r.original_result.historical_record,...r.original_result.sources,...r.target_evidence.paths,r.target_evidence.command_results,r.target_evidence.working_tree_manifest,r.target_evidence.browser_evidence]).concat(mapping.known_baseline_defects.criteria_reference);
for(const path of mappingPaths)if(!candidates.includes(path)&&!existsSync(join(root,path)))throw new Error("Missing mapping evidence: "+path);
const badLinks=[];
for(const path of candidates.filter(p=>p.endsWith(".md")&&!p.startsWith(cp1prefix))){
  for(const match of read(path).toString("utf8").matchAll(/\[[^\]\r\n]*\]\(([^)\r\n]+)\)/g)){
    let target=match[1];
    if(/^(https?:|mailto:|#|codex:)/.test(target))continue;
    target=decodeURIComponent(target.replace(/^<|>$/g,"").split("#")[0]);
    const absolute=resolve(dirname(join(root,path)),target), local=posix(relative(root,absolute));
    if(!candidates.includes(local)&&!existsSync(absolute))badLinks.push({path,target});
  }
}
if(badLinks.length)throw new Error("Broken local links: "+JSON.stringify(badLinks));
const untracked=git(["ls-files","--others","--exclude-standard","-z"]).toString("utf8").split("\0").filter(Boolean);
if(untracked.some(p=>!candidates.includes(p)))throw new Error("Unexpected untracked path");
write(prefix+"evidence-validation.json",{recorded_at:new Date().toISOString(),command:"node frontend/scripts/record-evidence.mjs",exit_code:0,assertions:{expected_task_head:true,expected_task_branch:true,accepted_tracked_unchanged:true,primary_checkout_clean_and_unchanged:true,checkpoint1_hashed_evidence_unchanged:preserved.length,canonical_shell_sources_unchanged:sources.length,scoped_command_exit_zero:results.results.length,screenshot_count:shots.length,shell_byte_identical_pairs:3,production_forbidden_modules:graph.forbidden.length,production_client_modules:graph.modules.length,production_artifact_count:artifacts.length,mapping_paths_valid:mappingPaths.length,broken_local_links:badLinks.length},limits:browser.limits,checksum_validation:"Every manifest entry is read back and SHA-256 verified before the recorder exits; the manifest cannot hash itself."});
candidates=owned();
write(prefix+"content-manifest.json",{created_at:new Date().toISOString(),head,branch,implementation_sha:null,uncommitted:true,canonical_appearance:canonical,semantics:"Exact current bytes of own task source/evidence; excludes ignored runtime/build/cache/dependencies and this manifest itself. No claim that HEAD contains uncommitted implementation. SHA-256 of each included file; original accepted tracked sources are not duplicated.",excluded:[prefix+"content-manifest.json"],files:candidates.filter(p=>p!==prefix+"content-manifest.json").map(digest)});
const manifest=json(prefix+"content-manifest.json");
for(const file of manifest.files)if(file.sha256!==sha(read(file.path))||file.size!==read(file.path).length)throw new Error("Final checksum mismatch: "+file.path);
console.log("PASS: "+manifest.files.length+" exact file hashes; "+shots.length+" screenshots; "+preserved.length+" checkpoint1 evidence hashes preserved; local links/mapping/isolation checked");
console.log(JSON.stringify({candidate_files:candidates.length,delta:delta.reduce((a,f)=>(a[f.status]=(a[f.status]??0)+1,a),{}),manifest_sha256:sha(read(prefix+"content-manifest.json"))}));
