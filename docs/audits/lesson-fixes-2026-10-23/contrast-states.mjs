import { chromium } from '../../../frontend/node_modules/playwright/index.mjs';
import { mkdirSync, writeFileSync } from 'node:fs';
import assert from 'node:assert/strict';
const out='docs/audits/lesson-fixes-2026-10-23/',result={started:new Date().toISOString(),samples:[],errors:[]};
mkdirSync(out+'screenshots',{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});
try {
 for(const theme of ['light','dark']) {
  const context=await browser.newContext({viewport:{width:1440,height:1000}});await context.addInitScript(theme=>localStorage.setItem('mathstart-mode',theme),theme);const page=await context.newPage();page.on('pageerror',e=>result.errors.push(e.message));await page.goto('http://127.0.0.1:5173/materials/8-algebra-32');await page.locator('.self-check').first().waitFor();await page.waitForTimeout(400);
  const sample=async(selector,state)=>{
   const data=await page.locator(selector).first().evaluate(element=>{
    const canvas=document.createElement('canvas');canvas.width=canvas.height=1;const ctx=canvas.getContext('2d');
    const rgba=color=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=color;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data].map(v=>v/255);};
    const over=(top,bottom)=>[0,1,2].map(i=>top[i]*top[3]+bottom[i]*(1-top[3])).concat(1);
    const ancestry=[];for(let n=element;n;n=n.parentElement)ancestry.unshift(n);let bg=[1,1,1,1];for(const n of ancestry)bg=over(rgba(getComputedStyle(n).backgroundColor),bg);
    const style=getComputedStyle(element),fg=over(rgba(style.color),bg);const lum=c=>c.slice(0,3).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);const a=lum(fg),b=lum(bg);
    return {foreground:style.color,background:bg.slice(0,3).map(v=>Math.round(v*255)),fontSize:style.fontSize,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
   });result.samples.push({theme,selector,state,...data});assert.ok(data.ratio>=4.5,`${theme} ${selector} ${state}: ${data.ratio}`);
  };
  const items=['.lesson-footer-brand p','.lesson-copyright','.coefficient-control output','.legend-curve','.legend-root','.quadratic-reset','.lesson-next .lesson-direction','.lesson-answer-toggle','.lesson-header-nav a','.lesson-footer-grades a','.lesson-diagram-tools button'];
  // Diagram tools are only displayed in a narrow diagram container; other samples use desktop.
  for(const selector of items){const l=page.locator(selector).first();if(!await l.isVisible())continue;await page.mouse.move(1400,900);await page.waitForTimeout(220);await sample(selector,'normal');if(['.quadratic-reset','.lesson-next .lesson-direction','.lesson-answer-toggle','.lesson-header-nav a','.lesson-footer-grades a','.lesson-diagram-tools button'].includes(selector)){await l.hover();await page.waitForTimeout(220);await sample(selector,'hover');}}
  const answer=page.locator('.lesson-answer-toggle').first();await answer.click();await page.waitForTimeout(300);await sample('.lesson-answer-toggle','open-hover');await page.mouse.move(1400,900);await page.waitForTimeout(220);await sample('.lesson-answer-toggle','open');
  await page.screenshot({path:out+'screenshots/contrast-'+theme+'-open.png'});await context.close();
 }
 assert.deepEqual(result.errors,[]);
}catch(e){result.failure=e.stack;process.exitCode=1;}finally{await browser.close();result.finished=new Date().toISOString();writeFileSync(out+'contrast-states.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));}
