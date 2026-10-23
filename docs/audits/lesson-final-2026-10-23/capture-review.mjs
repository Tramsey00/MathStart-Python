import { chromium } from '../../../frontend/node_modules/playwright/index.mjs';
import { writeFileSync } from 'node:fs';
const out='docs/audits/lesson-final-2026-10-23/',base='http://127.0.0.1:5173/materials/8-algebra-32';
const browser=await chromium.launch({channel:'chrome',headless:true});const results=[];
for(const width of [360,768,1440,1920]) for(const theme of ['light','dark']) {
 const context=await browser.newContext({viewport:{width,height:width===360?800:1000}});await context.addInitScript(theme=>localStorage.setItem('mathstart-mode',theme),theme);const page=await context.newPage();await page.goto(base);await page.locator('.self-check').first().waitFor();await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(400);const tag=`${width}-${theme}`;
 const capture=async(name,locator)=>{if(locator)await locator.evaluate(n=>window.scrollTo({top:scrollY+n.getBoundingClientRect().top-150,behavior:'instant'}));else await page.evaluate(()=>window.scrollTo({top:0,behavior:'instant'}));await page.waitForTimeout(50);await page.screenshot({path:out+'screenshots/'+tag+'-'+name+'.png'});};
 await capture('top');for(const [name,selector] of [['formula','.lesson-vertex-formula'],['lab','.quadratic-lab'],['diagram','.ms-quadratic-figure'],['table','.ms-values-table'],['footer','.lesson-footer']])await capture(name,page.locator(selector).first());
 for(const i of [0,8,9]){const check=page.locator('.self-check').nth(i);await check.getByRole('button').click();await page.waitForTimeout(280);await capture('answer-'+i,check);await check.getByRole('button').click();await page.waitForTimeout(280);}
 await page.getByRole('button',{name:'Содержание урока',exact:true}).click();await page.waitForTimeout(320);await page.screenshot({path:out+'screenshots/'+tag+'-contents.png'});
 results.push({width,theme,topFormula:await page.locator('.lesson-vertex-formula').textContent(),captureTime:new Date().toISOString()});await context.close();
}await browser.close();writeFileSync(out+'capture-review.json',JSON.stringify(results,null,2));console.log('Captured 80 current screenshots with target offset below sticky navigation.');
