// Read-only browser audit. Run from repository root: node docs/audits/lesson-fixes-2026-10-23/run-audit.mjs
import { chromium } from '../../../frontend/node_modules/playwright/index.mjs';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import assert from 'node:assert/strict';
const out = resolve('docs/audits/lesson-fixes-2026-10-23');
const shots = resolve(out, 'screenshots'); mkdirSync(shots, {recursive:true});
const base = 'http://127.0.0.1:5173'; const route = '/materials/8-algebra-32';
const result = { started:new Date().toISOString(), browser:'', checks:[], observations:[], errors:[], resources:[], screenshots:[] };
const save = () => writeFileSync(resolve(out,'browser-audit.json'),JSON.stringify(result,null,2));
async function check(name, fn) { try { const evidence=await fn(); result.checks.push({name,status:'PASS',evidence}); } catch(e) {result.checks.push({name,status:'FAIL',error:e.stack});} save(); }
const browser = await chromium.launch({channel:'chrome',headless:true}); result.browser=browser.version();
async function newPage(options={}) {
  const context=await browser.newContext({viewport:{width:1440,height:1000},...options});
  const page=await context.newPage(); page.setDefaultTimeout(4000);
  page.on('pageerror',e=>result.errors.push({url:page.url(),type:'pageerror',message:e.message}));
  page.on('console',e=>{if(e.type()==='error')result.errors.push({url:page.url(),type:'console',message:e.text(),location:e.location()});});
  page.on('response',r=>{if(r.status()>=400)result.resources.push({url:r.url(),status:r.status()});});
  return {context,page};
}
async function open(page,theme='light',path=route) {
  await page.goto(base+path);await page.evaluate(theme=>localStorage.setItem('mathstart-mode',theme),theme);
  const response=await page.reload(); await page.locator('.lesson-section').first().waitFor(); await page.evaluate(()=>document.fonts.ready);
  await page.waitForFunction(theme=>document.documentElement.dataset.theme===theme,theme);await page.waitForTimeout(400);
  return response;
}
async function shot(page,name,selector) {
  if(selector) await page.locator(selector).first().evaluate(n=>window.scrollTo({top:scrollY+n.getBoundingClientRect().top-150,behavior:'instant'}));
  await page.waitForTimeout(300);
  await page.screenshot({path:resolve(shots,name+'.png')}); result.screenshots.push(name+'.png');
}
const closed = async page => { await page.waitForTimeout(320); assert.equal(await page.locator('dialog.lesson-contents-panel').evaluate(n=>n.open),false); };
const setRange = async (locator,value) => locator.fill(String(value));
const ranges = page => ['a','b','c'].map(key=>page.getByRole('slider',{name:'Коэффициент '+key,exact:true}));
async function coefficients(page,a,b,c) {const rr=ranges(page); for(const [i,v] of [a,b,c].entries())await setRange(rr[i],v);}
async function values(page) {return page.locator('.quadratic-lab input[type=range]').evaluateAll(ns=>ns.map(n=>n.value));}
async function animations(page,selector) {return page.locator(selector).evaluate(n=>n.getAnimations({subtree:true}).map(a=>({type:a.constructor.name,property:a.transitionProperty,playState:a.playState,timing:a.effect.getTiming(),pseudo:a.effect.pseudoElement,target:a.effect.target?.className})));}
try {
  for(const width of [360,768,1440,1920]) for(const theme of ['light','dark']) {
    const {page,context}=await newPage({viewport:{width,height:width===360?800:1000}}); const tag=`${width}-${theme}`;
    await check(`render ${tag}`,async()=>{
      assert.equal((await open(page,theme)).status(),200);
      assert.equal(await page.locator('.lesson-section').count(),8);assert.equal(await page.locator('.self-check').count(),10);
      assert.equal(await page.locator('.ms-quadratic-svg').count(),2);
      assert.equal(await page.locator('html').getAttribute('data-theme'),theme);
      await shot(page,`${tag}-top`);
      for(const [name,sel] of [['formula','.lesson-vertex-formula'],['lab','.quadratic-lab'],['diagram','.ms-quadratic-figure'],['table','.ms-values-table'],['footer','.lesson-navigation']]) await shot(page,`${tag}-${name}`,sel);
      // Scan descendants for clipping as well as document overflow; intentional scroll viewports are recorded separately.
      const layout=await page.evaluate(()=>({innerWidth,scrollWidth:document.documentElement.scrollWidth,
        overflow:[...document.querySelectorAll('.lesson-frame *')].filter(n=>n instanceof HTMLElement && n.clientWidth>0 && n.scrollWidth>n.clientWidth+2).map(n=>({tag:n.tagName,cls:n.className,client:n.clientWidth,scroll:n.scrollWidth,overflow:getComputedStyle(n).overflowX})),
        header:getComputedStyle(document.querySelector('.lesson-header')).backgroundColor,
        targets:[...document.querySelectorAll('button,a,input')].filter(n=>n.checkVisibility()).map(n=>({name:n.getAttribute('aria-label')||n.textContent.trim(),width:n.getBoundingClientRect().width,height:n.getBoundingClientRect().height}))}));
      result.observations.push({name:`layout ${tag}`,...layout}); assert.ok(layout.scrollWidth<=width);
      const buttons=page.locator('.self-check .lesson-answer-toggle');
      for(const index of [0,9]) {await buttons.nth(index).click(); await page.waitForTimeout(280); await shot(page,`${tag}-answer-${index}`,`.self-check:nth-of-type(${index+1})`); await buttons.nth(index).click();}
      await page.getByRole('button',{name:'Содержание урока',exact:true}).click(); await shot(page,`${tag}-contents`);
      result.observations.push({name:`contents layout ${tag}`,box:await page.locator('.lesson-contents-panel').boundingBox(),title:await page.locator('.lesson-panel-body>h2').evaluate(n=>({client:n.clientWidth,scroll:n.scrollWidth}))});
      await page.keyboard.press('Escape'); await closed(page); return {viewport:width,theme,documentOverflow:layout.scrollWidth-width};
    }); await context.close();
  }
  const {page,context}=await newPage(); await open(page);
  const trigger=page.getByRole('button',{name:'Содержание урока',exact:true}); const panel=page.locator('.lesson-contents-panel'); const close=page.getByRole('button',{name:'Закрыть содержание',exact:true});
  await check('contents keyboard, focus trap, scroll lock, Escape, close button, backdrop',async()=>{
    await trigger.focus(); await page.keyboard.press('Enter'); await page.waitForTimeout(320);
    assert.equal(await close.evaluate(n=>n===document.activeElement),true);
    assert.equal(await page.evaluate(()=>document.body.style.overflow),'hidden');
    const scroll=await page.evaluate(()=>scrollY); await page.mouse.move(1300,500); await page.mouse.wheel(0,800);await page.waitForTimeout(100);assert.equal(await page.evaluate(()=>scrollY),scroll);
    await panel.getByRole('link').last().focus();await page.keyboard.press('Tab');assert.equal(await close.evaluate(n=>n===document.activeElement),true);
    await page.keyboard.press('Shift+Tab');assert.equal(await panel.getByRole('link').last().evaluate(n=>n===document.activeElement),true);
    await page.keyboard.press('Escape');await closed(page);assert.equal(await trigger.evaluate(n=>n===document.activeElement),true);
    await trigger.click();await close.click();await closed(page);assert.equal(await trigger.evaluate(n=>n===document.activeElement),true);
    await trigger.click();await page.waitForTimeout(320);await page.mouse.click(1400,500);await closed(page);assert.equal(await trigger.evaluate(n=>n===document.activeElement),true);
    assert.equal(await page.evaluate(()=>document.body.style.overflow),'');
  });
  await check('contents section links: all 8 anchors, focus and active background',async()=>{
    const evidence=[];
    for(let i=0;i<8;i++) {await trigger.click();await page.waitForTimeout(300);const link=panel.locator('nav a').nth(i);const href=await link.getAttribute('href');await link.click();await closed(page);
      assert.ok(page.url().endsWith(href));const section=page.locator(href);assert.equal(await section.evaluate(n=>document.activeElement===n),true);
      const top=await section.evaluate(n=>n.getBoundingClientRect().top);assert.ok(top>=76 && top<=160,`${href}: ${top}`);
      await trigger.click();await page.waitForTimeout(320);assert.equal(await panel.locator('[aria-current=location]').getAttribute('href'),href);
      evidence.push({href,top,active:await panel.locator('[aria-current=location]').evaluate(n=>({color:getComputedStyle(n).color,background:getComputedStyle(n).backgroundColor,fontWeight:getComputedStyle(n).fontWeight}))});await page.keyboard.press('Escape');await closed(page);
    } return evidence;
  });
  await check('self-check all 10: only button, Enter/Space, aria-controls/expanded, inert answers',async()=>{
    const evidence=[];
    for(let i=0;i<10;i++) {const sc=page.locator('.self-check').nth(i),button=sc.getByRole('button'),answer=sc.locator('.lesson-reveal-expander');
      assert.equal(await button.getAttribute('aria-expanded'),'false');const id=await button.getAttribute('aria-controls');assert.equal(id,await answer.getAttribute('id'));
      assert.equal(await answer.getAttribute('aria-hidden'),'true');assert.equal(await answer.evaluate(n=>n.inert),true);
      await sc.locator('.lesson-question-copy').click();assert.equal(await button.getAttribute('aria-expanded'),'false');
      await button.focus();await button.press('Enter');await page.waitForTimeout(280);assert.equal(await button.getAttribute('aria-expanded'),'true');assert.equal(await answer.evaluate(n=>n.inert),false);assert.ok((await answer.boundingBox()).height>0);
      evidence.push({i,text:await answer.innerText(),height:(await answer.boundingBox()).height});
      await button.press('Space');await page.waitForTimeout(280);assert.equal(await button.getAttribute('aria-expanded'),'false');assert.equal(await answer.evaluate(n=>n.inert),true);assert.equal(await answer.evaluate(n=>getComputedStyle(n).visibility),'hidden');assert.equal((await answer.boundingBox()).height,0);
      // Tabbing must skip the hidden answer.
      await button.press('Tab');assert.equal(await answer.evaluate(n=>n.contains(document.activeElement)),false);
    }return evidence;
  });
  await check('normal motion: synchronized contents/backdrop and disclosure states',async()=>{
    await trigger.click();await page.waitForTimeout(55);const enter=await animations(page,'.lesson-contents-panel');await page.keyboard.press('Escape');await page.waitForTimeout(55);const exit=await animations(page,'.lesson-contents-panel');await closed(page);
    const button=page.locator('.self-check .lesson-answer-toggle').last();await button.click();await page.waitForTimeout(55);const reveal=await animations(page,'.self-check:last-of-type .lesson-reveal');await page.waitForTimeout(280);await button.click();await page.waitForTimeout(55);const collapse=await animations(page,'.self-check:last-of-type .lesson-reveal');await page.waitForTimeout(280);
    assert.ok(enter.length>0);assert.ok(exit.length>0);assert.ok(reveal.length>0);assert.ok(collapse.length>0);return {enter,exit,reveal,collapse};
  });
  await check('rapid repeated contents/answer actions settle and release scroll lock',async()=>{
    for(let i=0;i<8;i++){await trigger.focus();await page.keyboard.press('Enter');await page.waitForTimeout(35);await page.keyboard.press('Escape');await page.waitForTimeout(25);}await closed(page);
    assert.equal(await trigger.getAttribute('aria-expanded'),'false');assert.equal(await page.evaluate(()=>document.body.style.overflow),'');
    const b=page.locator('.self-check .lesson-answer-toggle').last();await b.focus();for(let i=0;i<12;i++){await page.keyboard.press(i%2?'Space':'Enter');await page.waitForTimeout(20);}await page.waitForTimeout(350);
    assert.equal(await b.getAttribute('aria-expanded'),'false');assert.equal(await page.locator('.self-check .lesson-reveal-expander').last().evaluate(n=>({h:n.getBoundingClientRect().height,inert:n.inert,visibility:getComputedStyle(n).visibility})).then(v=>v.h===0&&v.inert&&v.visibility==='hidden'),true);
  });
  await check('graph keyboard, extremes, linear and constant mathematics',async()=>{
    const [a,b,c]=ranges(page);const probe=page.getByRole('slider',{name:'Абсцисса исследуемой точки x'});await a.press('ArrowRight');assert.equal(await a.inputValue(),'1.1');await a.press('Home');assert.equal(await a.inputValue(),'-4');await a.press('End');assert.equal(await a.inputValue(),'4');
    const observed=[];
    for(const v of [[-4,-10,-10],[4,10,10],[0,2,-4],[0,0,3],[0,0,0],[1,-4,4],[1,0,1]]) {await coefficients(page,...v);const dd=await page.locator('.quadratic-properties dd').allTextContents();const actual=await page.locator('.quadratic-values td').allTextContents();const expected=[-2,0,1,2,3,4].map(x=>String(v[0]*x*x+v[1]*x+v[2]).replace('-','−'));assert.deepEqual(actual,expected);
      if(v[0]===0) {assert.equal(dd[0],v[1]===0?'Постоянная функция':'Линейная функция');if(v[1]===0&&v[2]===0)assert.equal(dd[5],'Любое действительное x');if(v[1]===2)assert.equal(dd[5],'x = 2');}
      observed.push({v,dd,actual});}
    await probe.press('End');assert.equal(await probe.inputValue(),'10');await probe.press('Home');assert.equal(await probe.inputValue(),'-10');await probe.press('ArrowRight');assert.equal(await probe.inputValue(),'-9.9');
    await page.getByRole('button',{name:'Сбросить коэффициенты'}).click();await page.waitForTimeout(420);assert.deepEqual(await values(page),['0','1','-4','3']);return observed;
  });
  await check('graph click chooses point; hover preserves selection; reset animates all ranges',async()=>{
    const graph=page.locator('.quadratic-plot svg'),probe=page.getByRole('slider',{name:'Абсцисса исследуемой точки x'});
    await graph.click({position:{x:200,y:100}});const selected=await probe.inputValue();await graph.hover({position:{x:250,y:120}});assert.equal(await probe.inputValue(),selected);
    await coefficients(page,-4,10,-10);await setRange(probe,8);const button=page.getByRole('button',{name:'Сбросить коэффициенты'});await button.click();await page.waitForTimeout(70);const midway=await values(page);await page.waitForTimeout(420);assert.deepEqual(await values(page),['0','1','-4','3']);assert.notDeepEqual(midway,['8','-4','10','-10']);assert.notDeepEqual(midway,['0','1','-4','3']);return {selected,midway,final:await values(page)};
  });
  await check('manual coefficient and point input interrupt an active reset',async()=>{
    const probe=page.getByRole('slider',{name:'Абсцисса исследуемой точки x'}),button=page.getByRole('button',{name:'Сбросить коэффициенты'});
    await coefficients(page,-4,10,-10);await setRange(probe,8);await button.click();await page.waitForTimeout(60);await setRange(ranges(page)[0],-2);const interrupted=await values(page);await page.waitForTimeout(450);assert.deepEqual(await values(page),interrupted);assert.equal(interrupted[1],'-2');
    await coefficients(page,-4,10,-10);await button.click();await page.waitForTimeout(60);await setRange(probe,6);const pointInterrupted=await values(page);await page.waitForTimeout(450);assert.deepEqual(await values(page),pointInterrupted);return {interrupted,pointInterrupted};
  });
  await check('visible keyboard focus and accessible names',async()=>{
    await page.goto(base+route);await page.locator('.lesson-section').first().waitFor();
    const unnamed=await page.locator('button,input,a').evaluateAll(ns=>ns.filter(n=>n.checkVisibility()&&!n.closest('[inert]')).filter(n=>!n.getAttribute('aria-label')&&!n.getAttribute('aria-labelledby')&&!n.textContent.trim()&&!(n.labels?.length)).map(n=>n.outerHTML));assert.deepEqual(unnamed,[]);
    const focus=[];
    for(const selector of ['.lesson-theme-toggle','.lesson-contents-trigger','.self-check .lesson-answer-toggle','.coefficient-control input','.quadratic-probe input','.lesson-next','.lesson-back']){const l=page.locator(selector).first();await l.focus();await page.keyboard.press('Tab');await page.keyboard.press('Shift+Tab');focus.push(await l.evaluate(n=>({selector:n.className,outline:getComputedStyle(n).outline,rect:n.getBoundingClientRect().toJSON(),focused:n===document.activeElement})));}
    await page.locator('.self-check .lesson-answer-toggle').first().focus();await page.keyboard.press('Tab');await page.keyboard.press('Shift+Tab');await shot(page,'1440-light-focus-answer');return {unnamed,focus};
  });
  await check('canonical text, answers, formulas, table cells and authored SVG preserved in actual DOM',async()=>{
    const raw=readFileSync(resolve('curriculum/8-klass/algebra/06-kvadratichnaya-funkciya-y-ax2-funkciya-y-k-x/06-kvadratichnaya-funkcziya-y-ax2-bx-c/body.html'),'utf8');
    const evidence=await page.evaluate(raw=>{
      const source=new DOMParser().parseFromString(raw,'text/html');const normalize=v=>(v??'').replace(/\s+/g,' ').trim();
      const text=root=>{const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),parts=[];while(w.nextNode()){const v=normalize(w.currentNode.textContent);if(v)parts.push(v);}return parts.join(' ');};
      const sections=[...document.querySelectorAll('.lesson-section')].map(section=>{const original=source.getElementById(section.id).cloneNode(true);original.querySelectorAll('h2,#ms-quadratic-lab-660,.ms-nav,.ms-quadratic-number,.ms-answer summary').forEach(n=>n.remove());const current=section.cloneNode(true);current.querySelectorAll('h2,.quadratic-lab,.lesson-answer-toggle,.lesson-diagram-tools,.lesson-diagram-help').forEach(n=>n.remove());return {id:section.id,equal:text(original)===text(current),sourceLength:text(original).length,renderedLength:text(current).length};});
      const answers=[...source.querySelectorAll('.ms-answer')].map(n=>{const c=n.cloneNode(true);c.querySelector('summary').remove();return text(c);});
      const compare=selector=>JSON.stringify([...source.querySelectorAll(selector)].map(n=>n.outerHTML))===JSON.stringify([...document.querySelectorAll(selector)].map(n=>n.outerHTML));
      return {sections,answersEqual:JSON.stringify(answers)===JSON.stringify([...document.querySelectorAll('.lesson-reveal-content')].map(text)),mathML:compare('math'),svg:compare('.ms-quadratic-svg'),tableCells:JSON.stringify([...source.querySelectorAll('.ms-values-table td,.ms-values-table th')].map(n=>normalize(n.textContent)))===JSON.stringify([...document.querySelectorAll('.ms-values-table td,.ms-values-table th')].map(n=>normalize(n.textContent)))};
    },raw);result.observations.push({name:'content preservation',...evidence});assert.ok(evidence.sections.every(s=>s.equal));assert.equal(evidence.answersEqual,true);assert.equal(evidence.mathML,true);assert.equal(evidence.svg,true);assert.equal(evidence.tableCells,true);return evidence;
  });
  await check('computed text contrast in both themes (screen-visible HTML text)',async()=>{
    const observations=[];
    for(const theme of ['light','dark']) {await open(page,theme);const data=await page.evaluate(()=>{
      const cvs=document.createElement('canvas');cvs.width=cvs.height=1;const ctx=cvs.getContext('2d');const rgba=color=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=color;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data];};
      const lum=c=>c.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;}).reduce((r,v,i)=>r+v*[.2126,.7152,.0722][i],0);
      const bg=n=>{while(n){const c=rgba(getComputedStyle(n).backgroundColor);if(c[3]===255)return c;n=n.parentElement;}return [255,255,255,255];};
      return [...document.querySelectorAll('.lesson-preview-page *')].filter(n=>n instanceof HTMLElement && n.checkVisibility() && !n.closest('[inert]') && [...n.childNodes].some(c=>c.nodeType===3&&c.textContent.trim())).map(n=>{const s=getComputedStyle(n),fg=rgba(s.color),back=bg(n),l1=lum(fg),l2=lum(back),ratio=(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);const large=parseFloat(s.fontSize)>=24||(parseFloat(s.fontSize)>=18.66&&parseInt(s.fontWeight)>=700);return {cls:n.className,tag:n.tagName,text:n.textContent.trim().slice(0,100),color:s.color,bg:back,font:s.fontSize,weight:s.fontWeight,ratio,threshold:large?3:4.5};}).filter(n=>n.ratio<n.threshold);
    });observations.push({theme,failures:data});}result.observations.push({name:'contrast',observations});assert.ok(observations.every(o=>o.failures.length===0));return observations;
  });
  await check('canonical URL, reload, redirect aliases and query/fragment',async()=>{
    const evidence=[];
    for(const alias of [route,route+'/', '/quadratic.html','/kvadratichnaya-funkcziya-y-ax2-bx-c','/kvadratichnaya-funkcziya-y-ax2-bx-c/']) {const response=await page.goto(base+alias+'?audit=1&source=test#lesson-section-8');await page.locator('.self-check').first().waitFor();assert.equal(page.url(),base+route+'?audit=1&source=test#lesson-section-8');assert.equal(response.status(),200);const chain=[];let req=response.request();while(req){chain.unshift({url:req.url(),status:(await req.response())?.status()});req=req.redirectedFrom();}evidence.push({alias,chain,url:page.url()});}
    await page.reload();assert.equal(page.url(),base+route+'?audit=1&source=test#lesson-section-8');return evidence;
  });
  await check('catalogue search and section list both point to fixed route',async()=>{
    await page.goto(base+'/materials.html?grade=8-klass&subject=algebra');await page.locator('#topic-search').fill('Квадратичная функция');const search=page.locator('.search-results a').filter({hasText:'Квадратичная функция y = ax² + bx + c'});await search.waitFor();assert.equal(await search.getAttribute('href'),route);await search.click();await page.locator('.lesson-section').first().waitFor();assert.equal(page.url(),base+route);
    await page.goto(base+'/materials.html?grade=8-klass&subject=algebra');const section=page.getByRole('button').filter({hasText:'Квадратичная функция y = ax2. Функция y = k/x'});result.observations.push({name:'catalogue buttons',buttons:await page.getByRole('button').allTextContents()});
    // Match by section data rather than brittle rendered formula spelling.
    const sectionButton=page.locator('.section-card').filter({hasText:'Квадратичная функция y = ax².'});await sectionButton.click();const link=page.locator('dialog a').filter({hasText:'Квадратичная функция y = ax² + bx + c'});await link.waitFor();assert.equal(await link.getAttribute('href'),route);await link.click();await page.locator('.lesson-section').first().waitFor();assert.equal(page.url(),base+route);
  });
  await context.close();
  for(const width of [360,768,1440,1920]) {const {page,context}=await newPage({viewport:{width,height:width===360?800:1000},reducedMotion:'reduce'});await open(page);
    await check(`reduced motion ${width}: dialog, answer, reset, hover`,async()=>{
      assert.equal(await page.evaluate(()=>matchMedia('(prefers-reduced-motion: reduce)').matches),true);await page.getByRole('button',{name:'Содержание урока',exact:true}).click();assert.equal((await animations(page,'.lesson-contents-panel')).length,0);await page.keyboard.press('Escape');await closed(page);
      const button=page.locator('.self-check .lesson-answer-toggle').last();await button.click();assert.equal((await animations(page,'.self-check:last-of-type .lesson-reveal')).length,0);await button.click();assert.equal((await animations(page,'.self-check:last-of-type .lesson-reveal')).length,0);
      await coefficients(page,-4,10,-10);await setRange(page.getByRole('slider',{name:'Абсцисса исследуемой точки x'}),8);await page.getByRole('button',{name:'Сбросить коэффициенты'}).click();assert.deepEqual(await values(page),['0','1','-4','3']);return {final:await values(page)};
    });await context.close();}
  await check('touch synthesis: coefficients, chosen point, contents, answers, SVG pan, vertical scrolling',async()=>{
    const {page,context}=await newPage({viewport:{width:360,height:800},isMobile:true,hasTouch:true});const evidence=[];
    for(const theme of ['light','dark']) {await open(page,theme);assert.equal(await page.evaluate(()=>matchMedia('(hover: none)').matches),true);
      const cd=await context.newCDPSession(page);
      const swipe=async(x,y,dx,dy)=>{await cd.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});for(let i=1;i<=8;i++){await cd.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x+dx*i/8,y:y+dy*i/8}]});await page.waitForTimeout(20);}await cd.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await page.waitForTimeout(200);};
      const a=ranges(page)[0];await a.scrollIntoViewIfNeeded();let box=await a.boundingBox();await swipe(box.x+box.width*.64,box.y+box.height/2,box.width*.25,0);assert.notEqual(await a.inputValue(),'1');
      const graph=page.locator('.quadratic-plot svg');await graph.scrollIntoViewIfNeeded();box=await graph.boundingBox();await page.touchscreen.tap(box.x+box.width*.7,box.y+box.height*.5);const selected=await page.getByRole('slider',{name:'Абсцисса исследуемой точки x'}).inputValue();assert.notEqual(selected,'0');
      await page.getByRole('button',{name:'Содержание урока',exact:true}).tap();await page.waitForTimeout(320);await page.getByRole('button',{name:'Закрыть содержание'}).tap();await closed(page);
      const answer=page.locator('.self-check .lesson-answer-toggle').last();await answer.tap();assert.equal(await answer.getAttribute('aria-expanded'),'true');await answer.tap();await page.waitForTimeout(280);assert.equal(await answer.getAttribute('aria-expanded'),'false');
      const diagram=page.locator('.lesson-diagram').first();await diagram.getByRole('button').tap();const viewport=diagram.getByRole('region');await viewport.scrollIntoViewIfNeeded();box=await viewport.boundingBox();const before=await viewport.evaluate(n=>n.scrollLeft);await swipe(box.x+box.width*.7,box.y+Math.min(120,box.height/2),-90,0);const after=await viewport.evaluate(n=>n.scrollLeft);assert.ok(after>before);await diagram.getByRole('button').tap();
      await graph.scrollIntoViewIfNeeded();box=await graph.boundingBox();const beforeScroll=await page.evaluate(()=>scrollY);await swipe(box.x+box.width/2,box.y+Math.min(box.height-20,160),0,-100);assert.ok(await page.evaluate(()=>scrollY)>beforeScroll);
      await shot(page,`touch-360-${theme}-lab`,'.quadratic-lab');evidence.push({theme,coefficient:await a.inputValue(),selected,svgScroll:{before,after}});await cd.detach();
    }await context.close();return evidence;
  });
  await check('real browser zoom 200% via Chrome profile; both themes',async()=>{
    const profile=resolve('frontend/.cache/lesson-fixes-zoom-profile');mkdirSync(resolve(profile,'Default'),{recursive:true});writeFileSync(resolve(profile,'Default/Preferences'),JSON.stringify({partition:{default_zoom_level:{x:Math.log(2)/Math.log(1.2)}}}));
    const context=await chromium.launchPersistentContext(profile,{channel:'chrome',headless:true,viewport:null,args:['--window-size=1440,1000']});const page=context.pages()[0];page.setDefaultTimeout(4000);const cd=await context.newCDPSession(page);const evidence=[];
    for(const theme of ['light','dark']) {await open(page,theme);const dim=await page.evaluate(()=>({dpr:devicePixelRatio,outer:outerWidth,inner:innerWidth,visualScale:visualViewport.scale,scroll:document.documentElement.scrollWidth}));assert.equal(dim.dpr,2);assert.ok(dim.outer/dim.inner>1.9);assert.ok(dim.scroll<=dim.inner);
      for(const [name,sel] of [['top','.lesson-heading'],['lab','.quadratic-lab'],['formula','.lesson-vertex-formula'],['diagram','.lesson-diagram'],['answer','.self-check:last-of-type'],['footer','.lesson-navigation']]) {await page.locator(sel).first().evaluate(n=>n.scrollIntoView({block:'start',behavior:'instant'}));if(name==='answer')await page.locator('.self-check .lesson-answer-toggle').last().press('Enter');await page.waitForTimeout(300);const image=await cd.send('Page.captureScreenshot',{format:'png',fromSurface:true});const file=`zoom200-${theme}-${name}.png`;writeFileSync(resolve(shots,file),Buffer.from(image.data,'base64'));result.screenshots.push(file);}
      await page.getByRole('button',{name:'Содержание урока',exact:true}).click();await page.getByRole('link',{name:'Самопроверка',exact:true}).click();await closed(page);assert.equal(await page.locator('#lesson-section-8').evaluate(n=>document.activeElement===n),true);
      const probe=page.getByRole('slider',{name:'Абсцисса исследуемой точки x'});await probe.press('ArrowRight');assert.equal(await probe.inputValue(),'0.1');await page.getByRole('button',{name:'Сбросить коэффициенты'}).click();await page.waitForTimeout(420);assert.equal(await probe.inputValue(),'0');evidence.push({theme,...dim});
    }await context.close();return evidence;
  });
  await check('no console errors or pageerrors during audit',async()=>{assert.deepEqual(result.errors,[]);});
} finally {await browser.close();result.finished=new Date().toISOString();save();}
console.log(JSON.stringify({checks:result.checks.length,passed:result.checks.filter(c=>c.status==='PASS').length,failures:result.checks.filter(c=>c.status==='FAIL').map(c=>({name:c.name,error:c.error})),errors:result.errors,screenshots:result.screenshots.length},null,2));
process.exitCode=result.checks.some(c=>c.status==='FAIL')?1:0;
