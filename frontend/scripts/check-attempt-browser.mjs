// Explicit scoped check: production-build the actual N009 client and run it in
// a clean headless browser. No product UI, live API, provider or shared profile.
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {existsSync,mkdirSync,mkdtempSync,readFileSync,rmSync} from 'node:fs';
import {resolve,extname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {build} from 'vite';
import {chromium} from '@playwright/test';

const root=fileURLToPath(new URL('..',import.meta.url));
const cache=resolve(root,'.cache');
mkdirSync(cache,{recursive:true});
const work=mkdtempSync(resolve(cache,'n009-browser-'));
let server,browser;
try{
  const generated=readFileSync(resolve(root,'src/shared/api/generated/attempt-validators.mjs'),'utf8');
  assert.doesNotMatch(generated,/\brequire\s*\(/,'standalone validator must be browser ESM');
  await build({root,configFile:false,cacheDir:resolve(work,'vite-cache'),logLevel:'error',
    build:{outDir:resolve(work,'dist'),emptyOutDir:true,minify:false,
      lib:{entry:resolve(root,'src/shared/api/attempt-client.ts'),formats:['es'],fileName:()=> 'attempt-client.js'}}});
  server=createServer((request,response)=>{
    if(request.url==='/'){
      response.setHeader('Content-Type','text/html; charset=utf-8');
      response.end('<!doctype html><title>N009 scoped browser verification</title><script type="module">import {createAttemptClient} from "/attempt-client.js";window.n009Client=createAttemptClient;</script>');
      return;
    }
    const path=resolve(work,'dist','.'+new URL(request.url,'http://localhost').pathname);
    if(!path.startsWith(resolve(work,'dist')+'/')&&!path.startsWith(resolve(work,'dist')+'\\')){
      response.writeHead(404).end();return;
    }
    if(!existsSync(path)){response.writeHead(404).end();return;}
    response.setHeader('Content-Type',extname(path)==='.js'?'text/javascript':'application/octet-stream');
    response.end(readFileSync(path));
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const bundled=chromium.executablePath();
  const edge=[process.env['PROGRAMFILES(X86)'],process.env.PROGRAMFILES]
    .filter(Boolean).map(p=>resolve(p,'Microsoft/Edge/Application/msedge.exe')).find(existsSync);
  browser=await chromium.launch({headless:true,...(existsSync(bundled)?{}:edge?{executablePath:edge}:{})});
  const page=await browser.newPage();
  const errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(`http://127.0.0.1:${server.address().port}/`);
  await page.waitForFunction(()=>typeof window.n009Client==='function');
  const fixture=JSON.parse(readFileSync(resolve(root,'tests/fixtures/attempt-states.json'),'utf8'));
  const results=await page.evaluate(async fixture=>{
    const checks=[];
    const check=(name,value)=>{if(!value)throw Error(name);checks.push(name);};
    const started=fixture.started,id=started.data.id,meta=started.meta;
    const pending={...started,data:{...started.data,state:'SUBMITTED',revision:3,snapshot_digest:'a'.repeat(64),
      operation_id:id,submitted_at:'2026-11-19T00:00:01.000000Z',eligibility:{independent:false,positive_credit_eligible:false,reason:'PENDING'}}};
    const csrf={data:{csrf_token:'synthetic-browser-csrf'},meta};
    const json=(value,status=200,extra={})=>new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json',...extra}});
    check('no CommonJS global',typeof window.require==='undefined');
    let result=await window.n009Client(async()=>json(started)).call('get_attempt',{id});
    check('GET validates UUID/date-time in real browser',result.ok);
    result=await window.n009Client(async()=>json({...started,data:{...started.data,created_at:'not-a-date'}})).call('get_attempt',{id});
    check('invalid date-time rejected',!result.ok&&result.code==='INVALID_RESPONSE');
    let sent=false;
    result=await window.n009Client(async()=>{sent=true;return json(started);}).call('create_attempt',{
      idempotencyKey:'create',body:{exercise_id:'not-uuid',contract_version:1,version:1}});
    check('request UUID format runs before fetch',!result.ok&&!sent);
    const calls=[];
    let posts=0;
    const client=window.n009Client(async(url,init)=>{
      if(url==='/api/v1/auth/csrf/')return json(csrf);
      calls.push({url,body:init.body,key:init.headers['Idempotency-Key']});
      if(++posts===1)throw Error('synthetic lost ACK');
      return json(pending,202);
    });
    const options={id,body:{expected_revision:2,contract_version:1},idempotencyKey:'same-browser-key'};
    result=await client.call('submit_attempt',options);
    check('lost ACK is unknown with no automatic retry',!result.ok&&result.outcome==='unknown'&&posts===1);
    result=await client.call('submit_attempt',options);
    check('202 submit snapshot validates',result.ok&&result.pending);
    check('explicit retry preserves route/body/key',JSON.stringify(calls[0])===JSON.stringify(calls[1]));
    const hinted={data:{action_id:id,level:2,text:'Synthetic bounded strategy',exposure:{...started.data.exposure,max_help_level:2},service_state:'NORMAL'},meta};
    result=await window.n009Client(async url=>json(url==='/api/v1/auth/csrf/'?csrf:hinted)).call('request_hint',{
      id,body:{contract_version:1,level:2},idempotencyKey:'hint'});
    check('hint response validates',result.ok);
    const revealed={data:{action_id:id,reveal_recorded_at:'2026-11-19T00:00:02.000000Z',
      revealed_content:{answer:'synthetic explicit reveal',steps:['Synthetic explicit solution']},
      exposure:{...started.data.exposure,revealed_at:'2026-11-19T00:00:02.000000Z'},attempt:pending.data},meta};
    result=await window.n009Client(async url=>json(url==='/api/v1/auth/csrf/'?csrf:revealed)).call('reveal_attempt',{
      id,body:{contract_version:1,confirm:true},idempotencyKey:'reveal'});
    check('reveal nested Attempt validates',result.ok);
    const limited={error:{code:'RATE_LIMITED',message:'Try later',field_errors:{},retryable:true,request_id:meta.request_id}};
    result=await window.n009Client(async url=>url==='/api/v1/auth/csrf/'?json(csrf):json(limited,429,{'Retry-After':'17'})).call('submit_attempt',options);
    check('429 exposes Retry-After seconds',!result.ok&&result.status===429&&result.retryAfterSeconds===17&&result.outcome==='rejected');
    result=await window.n009Client(async url=>url==='/api/v1/auth/csrf/'?json(csrf):json(limited,429)).call('submit_attempt',options);
    check('429 without required header rejected',!result.ok&&result.code==='INVALID_RESPONSE');
    return checks;
  },fixture);
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({browser:browser.version(),productionBuild:true,passed:results.length,checks:results}));
}finally{
  if(browser)await browser.close();
  if(server)await new Promise(resolve=>server.close(resolve));
  rmSync(work,{recursive:true,force:true});
}
