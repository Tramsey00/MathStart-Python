import { chromium } from '../../../frontend/node_modules/playwright/index.mjs';
import { mkdirSync,writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import assert from 'node:assert/strict';
const out=resolve('docs/audits/lesson-fixes-2026-10-23'),shots=resolve(out,'screenshots'),base='http://127.0.0.1:5173',route='/materials/8-algebra-32';
const result={started:new Date().toISOString(),checks:[],resources:[],console:[]};
async function check(name,fn){try{result.checks.push({name,status:'PASS',evidence:await fn()});}catch(e){result.checks.push({name,status:'FAIL',error:e.stack});}writeFileSync(resolve(out,'supplement.json'),JSON.stringify(result,null,2));}
const browser=await chromium.launch({channel:'chrome',headless:true});
for(const theme of ['light','dark']) {
  const context=await browser.newContext({viewport:{width:360,height:800},isMobile:true,hasTouch:true});await context.addInitScript(theme=>localStorage.setItem('mathstart-mode',theme),theme);
  const page=await context.newPage();await page.goto(base+route);await page.locator('.quadratic-lab').waitFor();await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(400);
  await check(`vertical touch scroll must preserve selected point ${theme}`,async()=>{
    const graph=page.locator('.quadratic-plot svg'),probe=page.getByRole('slider',{name:'Абсцисса исследуемой точки x'});
    await graph.evaluate(n=>n.scrollIntoView({block:'center',behavior:'instant'}));await page.screenshot({path:resolve(shots,`touch-scroll-before-${theme}.png`)});
    const box=await graph.boundingBox(),before={x:await probe.inputValue(),scroll:await page.evaluate(()=>scrollY)};
    const cd=await context.newCDPSession(page);const events=[];await page.evaluate(()=>{window.auditEvents=[];for(const type of ['pointerdown','pointercancel','pointerup'])document.querySelector('.quadratic-plot svg').addEventListener(type,e=>window.auditEvents.push({type:e.type,pointerType:e.pointerType}));});
    const x=box.x+box.width*.75,y=box.y+box.height*.75;await cd.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});for(let i=1;i<=8;i++){await cd.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x,y:y-i*12}]});await page.waitForTimeout(20);}await cd.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await page.waitForTimeout(300);
    const after={x:await probe.inputValue(),scroll:await page.evaluate(()=>scrollY)},observed={theme,before,after,events:await page.evaluate(()=>window.auditEvents)};result.checks.push({name:`touch scroll observation ${theme}`,status:'OBSERVATION',evidence:observed});
    await graph.evaluate(n=>n.scrollIntoView({block:'center',behavior:'instant'}));await page.screenshot({path:resolve(shots,`touch-scroll-after-${theme}.png`)});assert.ok(after.scroll>before.scroll);assert.equal(after.x,before.x,'a cancelled touch/scroll changed selected x');return observed;
  });
  await check(`button selection and interactive copy restrictions ${theme}`,async()=>{
    const data=await page.evaluate(()=>({button:getComputedStyle(document.querySelector('.lesson-answer-toggle')).userSelect,question:getComputedStyle(document.querySelector('.lesson-question-copy')).userSelect,lab:getComputedStyle(document.querySelector('.quadratic-lab')).userSelect,copyAllowed:document.querySelector('.quadratic-lab').dispatchEvent(new ClipboardEvent('copy',{bubbles:true,cancelable:true})),cutAllowed:document.querySelector('.quadratic-lab').dispatchEvent(new ClipboardEvent('cut',{bubbles:true,cancelable:true}))}));assert.equal(data.button,'none');assert.equal(data.question,'text');assert.equal(data.lab,'none');assert.equal(data.copyAllowed,false);assert.equal(data.cutAllowed,false);return data;
  });await context.close();
}
await check('catalogue must not request a missing favicon or log errors',async()=>{
  const context=await browser.newContext();const page=await context.newPage();page.on('console',m=>{if(m.type()==='error')result.console.push({text:m.text(),location:m.location()});});page.on('response',r=>{if(r.status()>=400)result.resources.push({url:r.url(),status:r.status()});});const cd=await context.newCDPSession(page);await cd.send('Network.enable');cd.on('Network.responseReceived',r=>{if(r.response.status>=400)result.resources.push({url:r.response.url,status:r.response.status,type:r.type});});await page.goto(base+'/materials.html?grade=8-klass&subject=algebra');await page.waitForTimeout(1000);await context.close();assert.deepEqual(result.resources,[]);assert.deepEqual(result.console,[]);return {resources:result.resources,console:result.console};
});
await browser.close();
for(const outer of [720,768,1920]) {
  const profile=resolve('frontend/.cache/lesson-fixes-extra-zoom-'+outer);mkdirSync(resolve(profile,'Default'),{recursive:true});writeFileSync(resolve(profile,'Default/Preferences'),JSON.stringify({partition:{default_zoom_level:{x:Math.log(2)/Math.log(1.2)}}}));
  const context=await chromium.launchPersistentContext(profile,{channel:'chrome',headless:true,viewport:null,args:[`--window-size=${outer},1000`]});const page=context.pages()[0];page.setDefaultTimeout(5000);const cd=await context.newCDPSession(page);
  for(const theme of ['light','dark']) await check(`real zoom 200% outer ${outer} ${theme}`,async()=>{
    await page.goto(base+route);await page.evaluate(theme=>localStorage.setItem('mathstart-mode',theme),theme);await page.reload();await page.locator('.self-check').first().waitFor();await page.waitForTimeout(400);
    const dimensions=await page.evaluate(()=>({outer:outerWidth,inner:innerWidth,dpr:devicePixelRatio,scroll:document.documentElement.scrollWidth,visualScale:visualViewport.scale}));assert.equal(dimensions.dpr,2);assert.ok(dimensions.outer/dimensions.inner>1.9);assert.ok(dimensions.scroll<=dimensions.inner);
    const button=page.locator('.self-check .lesson-answer-toggle').nth(8);await button.press('Enter');await page.waitForTimeout(300);assert.equal(await button.getAttribute('aria-expanded'),'true');await button.evaluate(n=>n.closest('.self-check').scrollIntoView({block:'start',behavior:'instant'}));
    const image=await cd.send('Page.captureScreenshot',{format:'png',fromSurface:true});writeFileSync(resolve(shots,`zoom200-outer${outer}-${theme}-long-solution.png`),Buffer.from(image.data,'base64'));await button.press('Space');assert.equal(await button.getAttribute('aria-expanded'),'false');return dimensions;
  });await context.close();
}
result.finished=new Date().toISOString();writeFileSync(resolve(out,'supplement.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));process.exitCode=result.checks.some(c=>c.status==='FAIL')?1:0;
