// Final I01 evidence. No app/DB execution, environment copying or Git mutation.
import {createHash} from "node:crypto";
import {spawnSync} from "node:child_process";
import * as fs from "node:fs";
import {dirname,join,relative,resolve} from "node:path";
import {fileURLToPath} from "node:url";
const root=fileURLToPath(new URL("../../../../",import.meta.url)),prefix="docs/acceptance/MS7-MIG-I01/final/",cp2="docs/acceptance/MS7-MIG-I01/checkpoint2/";
const input="8d958aeeb17da46839722441425ccbb5889e2ab7",canonical="8c11edadc8debc81432d1db1145feac504f09061",primary="C:/Users/User/PycharmProjects/MathStart-Python";
const sha=b=>createHash("sha256").update(b).digest("hex"),posix=p=>p.replaceAll("\\","/");
const read=p=>fs.readFileSync(join(root,p)),json=p=>JSON.parse(read(p));
const write=(p,v)=>{fs.mkdirSync(dirname(join(root,p)),{recursive:true});fs.writeFileSync(join(root,p),typeof v==="string"?v:JSON.stringify(v,null,2)+"\n");};
const gitCommands=[];
function git(args,cwd=root){
 const r=spawnSync("git",args,{cwd,env:{...process.env,GIT_OPTIONAL_LOCKS:"0"},encoding:null,maxBuffer:32*1024*1024,windowsHide:true});
 gitCommands.push({command:["git",...args],cwd:posix(cwd),exit_code:r.status,stdout:r.stdout?.toString()??"",stderr:r.stderr?.toString()??""});
 if(r.error||r.status!==0)throw new Error("Git read failed:"+args.join(" "));return r.stdout;
}
const gt=(args,cwd)=>git(args,cwd).toString().trim();
const branch=gt(["branch","--show-current"]),head=gt(["rev-parse","HEAD"]);
if(branch!=="ms7-mig-i01-foundation"||head!==input)throw new Error("Task HEAD/branch changed");
if(gt(["diff","HEAD","--name-only"]))throw new Error("Accepted tracked source changed");
git(["diff","--check"]);
const primaryHead=gt(["rev-parse","HEAD"],primary),primaryStatus=gt(["status","--porcelain"],primary);
if(primaryHead!==canonical||primaryStatus)throw new Error("Primary checkout changed");
if(gt(["diff","--name-only",canonical,input,"--","content","curriculum","site_content","config","users","templates","static","requirements.txt","requirements.lock",".github/workflows/ci.yml"]))throw new Error("Canonical application delta");
const old=json(cp2+"content-manifest.json");
const historical=old.files.filter(f=>f.path.startsWith("docs/acceptance/MS7-MIG-I01/checkpoint"));
const functional=old.files.filter(f=>f.path.startsWith("frontend/")&&f.path!=="frontend/README.md");
for(const f of [...historical,...functional])if(sha(read(f.path))!==f.sha256||read(f.path).length!==f.size)throw new Error("Preserved file changed:"+f.path);
const appearanceSources=["templates/base.html","static/mathstart/css/site.css","static/mathstart/css/ui/tokens.css","static/mathstart/css/ui/foundation.css"].map(path=>{
 const a=git(["show",canonical+":"+path]),b=git(["show",input+":"+path]),c=read(path);
 if(!a.equals(b)||c.toString().replaceAll("\r\n","\n")!==b.toString().replaceAll("\r\n","\n"))throw new Error("Appearance source changed");
 return {path,canonical_blob_sha256:sha(a),accepted_blob_sha256:sha(b),working_file_sha256:sha(c),git_blobs_byte_identical:true,working_text_equal_ignoring_crlf:true};
});
const front=json(prefix+"frontend-commands.json"),repo=json(prefix+"repository-commands.json"),contracts=json(prefix+"additional-contract-commands.json");
for(const suite of [front,repo,contracts])if(suite.results.some(r=>r.exit_code!==0))throw new Error("Verification command failed");
const mapping=json(cp2+"old-to-new-evidence.json");
mapping.version="i01-final-verification";mapping.scope="§17 I01 only; original_result/history unchanged; current local verification; independent acceptance pending";
for(const r of mapping.records){
 r.platform_disposition="ADAPT_PLATFORM_PRESERVE_DOMAIN_AND_HISTORICAL_EVIDENCE";
 r.current_status="IMPLEMENTED_UNCOMMITTED_LOCAL_VERIFICATION_PASS; EXACT_SHA_CI_INDEPENDENT_ACCEPTANCE_PENDING";
 Object.assign(r.target_evidence,{command_results:prefix+"frontend-commands.json",repository_results:prefix+"repository-commands.json",working_tree_manifest:prefix+"content-manifest.json",browser_evidence:prefix+"browser-evidence.json",status:r.current_status});
}
write(prefix+"old-to-new-evidence.json",mapping);
const browser=json(prefix+"browser-evidence.json");
if(browser.source_input!==input||browser.canonical_appearance!==canonical||browser.screenshots.length!==10)throw new Error("Browser provenance");
function jpegSize(b){
 let i=2;if(b[0]!==255||b[1]!==216)throw new Error("JPEG expected");
 while(i<b.length){if(b[i++]!==255)throw new Error("JPEG marker");while(b[i]===255)i++;const m=b[i++];if(m===218||m===217)break;if(m===1||(m>=208&&m<=215))continue;const n=b.readUInt16BE(i);if([192,193,194,195,197,198,199,201,202,203,205,206,207].includes(m))return {width:b.readUInt16BE(i+5),height:b.readUInt16BE(i+3)};i+=n;}
 throw new Error("JPEG dimensions");
}
const shots=browser.screenshots.map(s=>{const path=prefix+"screenshots/"+s.file,b=read(path);return {...s,path,pixel_dimensions:jpegSize(b),size:b.length,sha256:sha(b)};});
const pairs=[360,768,1440].map(width=>{
 const a=shots.find(s=>s.file==="react-gallery-"+width+".jpg"),b=shots.find(s=>s.file==="django-sqlite-gallery-"+width+".jpg"),c=browser.comparisons.find(x=>x.width===width);
 if(a.sha256!==b.sha256||!c?.equal)throw new Error("Gallery comparison mismatch");
 return {width,byte_identical:true,sha256:a.sha256,compared_elements:c.elements};
});
if(browser.keyboard.length!==3||browser.css_isolation.some(x=>!x.headerFooterStylesEqual||x.rootHasDebugCss)||browser.logs.length)throw new Error("Browser check failed");
write(prefix+"screenshot-index.json",{source_input:input,canonical_appearance:canonical,implementation_sha:null,uncommitted:true,captured_at:browser.captured_at,browser:browser.browser,version_source:"Current UA Client Hints; Chromium/Google Chrome155.0.8059.27; separate Codex IAB version unavailable/unconfirmed",comparison:browser.comparison_profile,pixel_dimensions_note:"CSS viewport and full-page JPEG raster differ; screenshot may exclude vertical scrollbar gutter",pairs,screenshots:shots});
write(prefix+"screenshot-index.md","# Final screenshot index\n\nInput:"+input+". Canonical appearance:"+canonical+". Implementation:uncommitted; [exact bytes](content-manifest.json).\n\nBrowser:Chromium/Google Chrome155.0.8059.27 from current UA Client Hints; separate Codex IAB version unavailable/unconfirmed. Capture:"+browser.captured_at+".\n\nLive fresh task-local Django SQLite gallery comparison, not R01 PostgreSQL or whole-site/target runtime parity. [Hashes/metadata](screenshot-index.json), [keyboard/CSS observations](browser-evidence.json). CSS viewport differs from full-page raster.3/3 gallery JPEG pairs byte-identical.\n\n|Screenshot|Exact URL|Viewport CSS px|Raster px|Full-page|State|\n|---|---|---|---|---|---|\n"+shots.map(s=>"|["+s.file+"](screenshots/"+s.file+")|"+s.url+"|"+s.viewport.width+"×"+s.viewport.height+"|"+s.pixel_dimensions.width+"×"+s.pixel_dimensions.height+"|"+s.fullPage+"|"+s.state+"|").join("\n")+"\n\n[Checkpoint2 source-derived shell comparison](../checkpoint2/screenshot-index.md) preserved separately.\n");
const ignored=new Set(["node_modules",".cache",".react-router","build","test-results","playwright-report"]);
function walk(base,filter=false){return fs.readdirSync(base).sort().flatMap(n=>{if(filter&&ignored.has(n))return [];const p=join(base,n),s=fs.lstatSync(p);if(s.isSymbolicLink())throw new Error("Unexpected symlink");return s.isDirectory()?walk(p,filter):[posix(relative(root,p))];});}
const owned=()=>[...walk(join(root,"frontend"),true),...walk(join(root,"docs/acceptance/MS7-MIG-I01")),"docs/agent-traces/MS7-MIG-I01.md","docs/exec-plans/active/MS7-MIG-I01.md"].sort();
const digest=path=>{const b=read(path);return {path,size:b.length,sha256:sha(b)};};
fs.copyFileSync(join(root,"frontend/.cache/production-client-modules.json"),join(root,prefix+"production-client-modules.json"));
const graph=json(prefix+"production-client-modules.json");
if(graph.forbidden.length)throw new Error("Forbidden production module");
write(prefix+"build-manifest.json",{source_input:input,implementation_sha:null,client_module_count:graph.modules.length,files:walk(join(root,"frontend/build/client")).map(digest),artifacts_ignored:true,semantics:"Actual final clean build; not gateway/deployment evidence"});
const generated=["source-scope-audit.json","evidence-validation.json","changed-files.txt","content-manifest.json"].map(p=>prefix+p);
const candidates=[...new Set([...owned(),...generated])].sort();
const untracked=git(["ls-files","--others","--exclude-standard","-z"]).toString().split("\0").filter(Boolean);
const unexpected=untracked.filter(p=>!candidates.includes(p));
if(unexpected.length)throw new Error("Unexpected untracked files");
const unsafe=candidates.filter(p=>/(^|\/)(\.env(?:\..*)?|.*\.env|.*\.(?:sqlite3?|db|dump|backup|bak|sql|sql\.gz|pem|pfx|key)|cookies?|profiles?)($|\/)/i.test(p));
if(unsafe.length)throw new Error("Unsafe evidence path");
const suspicious=[],patterns=[/-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/,/\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9]{24,})\b/,/postgres(?:ql)?:\/\/[^\s"'@]+:[^\s"'@]+@/i,/\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\b/];
const texts=candidates.filter(p=>fs.existsSync(join(root,p))&&!/\.(jpg|png|webp|pdf|zip)$/i.test(p));
for(const p of texts)if(patterns.some(r=>r.test(read(p).toString())))suspicious.push(p);
if(suspicious.length)throw new Error("Potential secret in:"+suspicious.join(","));
const whitespace=[];
for(const p of texts){
 const r=spawnSync("git",["-c","core.safecrlf=false","diff","--no-index","--check","--","/dev/null",p],{cwd:root,env:{...process.env,GIT_OPTIONAL_LOCKS:"0"},encoding:"utf8",windowsHide:true});
 whitespace.push({path:p,exit_code:r.status,diagnostic:r.stdout+r.stderr});
 if(r.error||r.status>1||r.stdout||r.stderr)throw new Error("Whitespace diagnostic:"+p);
}
write(prefix+"source-scope-audit.json",{recorded_at:new Date().toISOString(),head,branch,implementation_sha:null,accepted_tracked_changed_paths:[],canonical_to_input_application_changed_paths:[],primary:{path:primary,head:primaryHead,status_porcelain:primaryStatus},source_materials:json(prefix+"repository-isolation.json"),appearance_sources:appearanceSources,checkpoint_hashed_evidence_unchanged:historical.length,checkpoint2_functional_files_byte_identical:functional.length,git_commands:gitCommands,whitespace:{tracked_diff_check_exit:0,untracked_command_prefix:["git","-c","core.safecrlf=false","diff","--no-index","--check","--","/dev/null"],untracked_file_checks:whitespace,semantics:"no-index exit1 represents differences from /dev/null; exit0/1 with empty --check output means no whitespace error"},unexpected_untracked_paths:unexpected,privacy:{candidate_paths:candidates.length,text_files_scanned:texts.length,unsafe_paths:unsafe,potential_secret_paths:suspicious,excluded:"Ignored var/runtime/venv/SQLite/media/static/temp;node_modules/build/cache/typegen;no env/cookies/browser profiles/DB dumps included",synthetic_content:"Approved synthetic examples/test canaries only; debug/test fixtures excluded from production graph/artifacts",limit:"Scoped path/pattern/source/production review, not universal secret detection"},github_mutations:"NONE",working_and_r01_db_access:"NONE"});
const mapped=mapping.records.flatMap(r=>[r.original_result.historical_record,...r.original_result.sources,...r.target_evidence.paths,r.target_evidence.command_results,r.target_evidence.repository_results,r.target_evidence.working_tree_manifest,r.target_evidence.browser_evidence]).concat(mapping.known_baseline_defects.criteria_reference);
for(const p of mapped)if(!fs.existsSync(join(root,p))&&!candidates.includes(p))throw new Error("Missing mapping path:"+p);
const broken=[];
for(const p of candidates.filter(p=>p.endsWith(".md")))for(const m of read(p).toString().matchAll(/\[[^\]\r\n]*\]\(([^)\r\n]+)\)/g)){
 let t=m[1];if(/^(https?:|mailto:|#|codex:)/.test(t))continue;t=decodeURIComponent(t.replace(/^<|>$/g,"").split("#")[0]);
 const a=resolve(dirname(join(root,p)),t),rel=posix(relative(root,a));if(!fs.existsSync(a)&&!candidates.includes(rel))broken.push({path:p,target:t});
}
if(broken.length)throw new Error("Broken links:"+JSON.stringify(broken));
write(prefix+"changed-files.txt",candidates.join("\n")+"\n");
write(prefix+"evidence-validation.json",{recorded_at:new Date().toISOString(),command:"node docs/acceptance/MS7-MIG-I01/final/record-final-evidence.mjs",exit_code:0,assertions:{head_branch_isolated:true,accepted_tracked_unchanged:true,primary_unchanged:true,historical_evidence_hashes:historical.length,functional_files_unchanged:functional.length,appearance_sources:appearanceSources.length,frontend_commands_exit0:front.results.length,repository_commands_exit0:repo.results.length,contract_commands_exit0:contracts.results.length,screenshots:shots.length,byte_identical_live_gallery_pairs:pairs.length,production_client_modules:graph.modules.length,production_artifacts:walk(join(root,"frontend/build/client")).length,mapping_records:mapping.records.length,mapping_paths:mapped.length,broken_links:0,unexpected_files:0,whitespace_diagnostics:0,unsafe_paths:0,potential_secrets:0},limits:browser.limits,postgresql:"NOT_RUN; infrastructure.json",implementation_sha_ci_independent_review:"PENDING",checksum_note:"Each manifest entry read back; manifest excludes itself"});
const files=owned();
write(prefix+"content-manifest.json",{created_at:new Date().toISOString(),head,branch,implementation_sha:null,uncommitted:true,canonical_appearance:canonical,semantics:"Exact task bytes; HEAD is accepted input, not uncommitted implementation. Historical checkpoint1/2 preserved. Ignored runtime/build/cache/dependencies excluded.",excluded:[prefix+"content-manifest.json"],files:files.filter(p=>p!==prefix+"content-manifest.json").map(digest)});
for(const f of json(prefix+"content-manifest.json").files)if(sha(read(f.path))!==f.sha256||read(f.path).length!==f.size)throw new Error("Checksum mismatch");
console.log(JSON.stringify({result:"PASS",candidate_files:files.length+(files.includes(prefix+"content-manifest.json")?0:1),frontend_files:files.filter(p=>p.startsWith("frontend/")).length,historical_evidence_preserved:historical.length,unchanged_functional_files:functional.length,final_screenshots:shots.length,manifest_sha256:sha(read(prefix+"content-manifest.json"))}));
