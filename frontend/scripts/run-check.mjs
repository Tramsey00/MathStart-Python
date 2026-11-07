// Real command receipt adapter. No receipt is emitted after failure or skips.
import {spawnSync} from 'node:child_process';
import {mkdirSync,readFileSync,writeFileSync,mkdtempSync} from 'node:fs';
import {join,resolve} from 'node:path';
const mode=process.argv[2];
const checkId={typecheck:'frontend-typecheck',tests:'frontend-tests',build:'frontend-build',e2e:'frontend-e2e',i02:'frontend-i02',identity:'frontend-identity'}[mode];
if(!checkId || (process.env.MATHSTART_CHECK_ID && process.env.MATHSTART_CHECK_ID!==checkId))throw Error('Check identity mismatch');
mkdirSync('.cache/checks',{recursive:true});
const run=mkdtempSync('.cache/checks/run-');
const cases=[];
function execute(command,args,options={}){
  const r=spawnSync(command,args,{stdio:'inherit',windowsHide:true,...options});
  if(r.error || r.status!==0) process.exit(r.status || 1);
}
const cli=(name)=>resolve('node_modules',name);
if(mode==='typecheck'){
  for(const [id,args] of [
    ['frozen-contract-generation',['scripts/generate-api.mjs','--check']],
    ['frozen-staff-read-contract-generation',['scripts/generate-staff.mjs','--check']],
    ['react-router-route-types',[cli('@react-router/dev/bin.js'),'typegen']],
    ['typescript-no-emit',[cli('typescript/bin/tsc'),'--noEmit']]]){
    execute(process.execPath,args);cases.push(id);
  }
}else if(mode==='tests'){
  const report=join(run,'vitest.json');
  execute(process.execPath,[cli('vitest/vitest.mjs'),'run','--reporter=dot','--reporter=json','--outputFile='+report]);
  const data=JSON.parse(readFileSync(report,'utf8'));
  if(data.numFailedTests!==0 || data.numPendingTests!==0 || data.numTodoTests!==0 || data.numPassedTests<1)throw Error('Failed/empty/skipped tests');
  for(const file of data.testResults)for(const test of file.assertionResults){if(test.status!=='passed')throw Error('Non-passing case');cases.push(test.fullName);}
}else if(mode==='build'){
  if(!process.env.MATHSTART_BUILD_CONFIG)throw Error('MATHSTART_BUILD_CONFIG must identify verified immutable build inputs');
  const c=JSON.parse(readFileSync(process.env.MATHSTART_BUILD_CONFIG,'utf8'));
  const python=process.env.MATHSTART_PYTHON || 'python';
  const args=['-m','frontend.build_public'];
  for(const [key,value] of Object.entries(c))args.push('--'+key.replaceAll('_','-'),String(value));
  execute(python,args,{cwd:'..'});
  const receipt=JSON.parse(readFileSync(resolve('..',c.output,'output-manifest.json'),'utf8'));
  if(receipt.pages<1 || receipt.private_exports.length || receipt.build_engine!=='react-router-framework')throw Error('Incomplete public artifact');
  cases.push(...receipt.public_urls.map(url=>'prerender:'+url),...receipt.files.map(f=>'hash:'+f.path));
}else{
  if(!process.env.MATHSTART_E2E_BASE_URL||!process.env.MATHSTART_PUBLIC_VIEW)throw Error('Externally managed ASGI URL and verified public view are required; the caller owns start/health/stop');
  const report=join(run,'playwright.json');
  const selection=['i02','identity'].includes(mode)?['public.spec.ts','staff-read.spec.ts','i02.spec.ts',...(mode==='identity'?['identity.spec.ts']:[]),'--project=chrome-360','--grep','complete public URL/body/head|no JavaScript|real .*staff|I02'+(mode==='identity'?'|Identity migration':'')]:[];
  execute(process.execPath,[cli('@playwright/test/cli.js'),'test',...selection],{env:{...process.env,MATHSTART_E2E_SCOPE:['i02','identity'].includes(mode)?'i02':'combined',PLAYWRIGHT_JSON_OUTPUT_NAME:resolve(report)}});
  const data=JSON.parse(readFileSync(report,'utf8'));
  if(data.stats.unexpected || data.stats.skipped || data.stats.flaky || data.stats.expected<1)throw Error('Incomplete browser matrix');
  function walk(s){for(const spec of s.specs||[])for(const t of spec.tests){if(t.status!=='expected')throw Error('Non-passing browser case');cases.push(t.projectName+':'+spec.title);}for(const child of s.suites||[])walk(child);}
  walk(data);
  const expectedProjects=['i02','identity'].includes(mode)?['chrome-360']:['chrome','edge','firefox'].flatMap(name=>[360,768,1440].map(width=>name+'-'+width)).sort();
  const actualProjects=[...new Set(cases.map(id=>id.split(':')[0]))].sort();
  if(JSON.stringify(expectedProjects)!==JSON.stringify(actualProjects))throw Error('Incomplete browser/project coverage');
  if(mode==='identity'&&cases.length!==18)throw Error('Incomplete identity + I02 inventory: expected 18 measured cases');
  if(mode==='i02' && cases.length!==14)throw Error('Incomplete I02 case inventory: expected 14 measured cases');
}
if(cases.length<1)throw Error('Empty result');
const receipt={check_id:checkId,status:'PASS',evidence_class:'TARGET_RUNTIME',scope:mode==='i02'?'I02 only; I05 final matrix pending':mode,assertions:cases.length,skipped:0,case_ids:cases,node:process.version,finished_at:new Date().toISOString()};
writeFileSync(join(run,'receipt.json'),JSON.stringify(receipt,null,2));
if(process.env.MATHSTART_CHECK_RESULT)writeFileSync(process.env.MATHSTART_CHECK_RESULT,JSON.stringify(receipt),{flag:'wx'});
console.log('PASS: '+checkId+', '+cases.length+' measured assertions');
