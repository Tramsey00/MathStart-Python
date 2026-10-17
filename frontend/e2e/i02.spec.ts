import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
const data=JSON.parse(readFileSync(process.env.MATHSTART_PUBLIC_VIEW!,'utf8'));
const config=JSON.parse(readFileSync(process.env.MATHSTART_BUILD_CONFIG!,'utf8'));
const manifest=JSON.parse(readFileSync(config.output+'/output-manifest.json','utf8'));

test('I02 matched home catalogue and structural snapshots with current assets',async({page,browser})=>{
 test.setTimeout(120_000);
 const legacy=process.env.MATHSTART_LEGACY_BASE_URL!;expect(legacy).toBeTruthy();
 const routes=['/','/karta-sajta/',Object.keys(data.routes).find(u=>data.routes[u].page.page_type==='grade')!];
 expect(routes.every(Boolean)).toBe(true);
 for(const [i,route]of routes.entries()){
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  for(const [side,origin]of [['legacy',legacy],['target',process.env.MATHSTART_E2E_BASE_URL!]]){
   expect((await page.goto(origin+route))?.status()).toBe(200);
   await expect(page.locator('h1').first()).toBeVisible();
   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
   if(side==='target'){
    expect(await page.locator('link[rel=stylesheet]').evaluateAll(ns=>ns.map(n=>n.getAttribute('href')))).toEqual(data.routes[route].page.assets.filter((a:any)=>a.kind==='style').map((a:any)=>a.url));
   }
   const path=test.info().outputPath(`i02-${i}-${side}.png`);await page.screenshot({path,fullPage:true});await test.info().attach(`i02-${i}-${side}.png`,{path,contentType:'image/png'});
  }
  expect(errors).toEqual([]);
 }
 await test.info().attach('browser-version.json',{body:JSON.stringify({actual_version:browser.version(),project:test.info().project.name,release_id:data.release_id,input_digest:data.manifest_digest}),contentType:'application/json'});
});

test('I02 redirect inventory and unknown asset precedence remain real HTTP',async({request})=>{
 test.setTimeout(30_000+manifest.redirects.length*5_000);
 const assets=new Set(Object.values(data.routes).flatMap((v:any)=>v.page.assets.map((a:any)=>a.url)));
 let checked=0;
 for(const rule of manifest.redirects){
  const response=await request.get(rule.old_path,{maxRedirects:0,timeout:5_000});
  if(data.routes[rule.old_path] || assets.has(rule.old_path)){expect(response.status()).toBe(200);continue;}
  expect(response.status(),rule.old_path).toBe(rule.is_permanent?301:302);
  const header=response.headers().location;expect(header).toBeTruthy();
  const location=new URL(header!,process.env.MATHSTART_E2E_BASE_URL!);
  expect(location.origin).toBe(process.env.MATHSTART_E2E_BASE_URL);expect(location.pathname).toBe(rule.new_path);checked++;
 }
 expect(checked).toBeGreaterThan(0);
 for(const path of ['/static/missing-i02.css','/media/missing-i02.png'])expect((await request.get(path)).status()).toBe(404);
});
