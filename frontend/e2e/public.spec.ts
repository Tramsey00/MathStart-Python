import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
const input=process.env.MATHSTART_PUBLIC_VIEW;
if(!input)throw Error('MATHSTART_PUBLIC_VIEW is required for complete manifest browser verification');
const data=JSON.parse(readFileSync(input,'utf8'));
const entries=Object.entries(data.routes) as [string,any][];
const families=new Map<string,string>();
for(const [url,view] of entries)for(const asset of view.page.assets)if(asset.kind==='script'&&!families.has(asset.url))families.set(asset.url,url);
const representatives=[...new Set(families.values())];
const styleFamilies=new Map<string,string>();
for(const [url,view] of entries)for(const asset of view.page.assets)if(asset.kind==='style'&&!styleFamilies.has(asset.url))styleFamilies.set(asset.url,url);
const styleRepresentatives=[...new Set(styleFamilies.values())].filter(url=>!representatives.includes(url));
test.beforeEach(async({browser},info)=>{await info.attach('browser-version.json',{body:JSON.stringify({project:info.project.name,actual_version:browser.version(),input_release:data.release_id,input_digest:data.manifest_digest}),contentType:'application/json'});});

for(const route of styleRepresentatives)test('style family '+route,async({page})=>{
 const errors:string[]=[];const failed:string[]=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)failed.push(new URL(r.url()).pathname);});
 expect((await page.goto(route))?.status()).toBe(200);await expect(page.locator('h1').first()).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1)).toBe(true);
 expect(errors).toEqual([]);expect(failed).toEqual([]);
 const path=test.info().outputPath('style.png');await page.screenshot({path});await test.info().attach('style.png',{path,contentType:'image/png'});
});

test('complete public URL/body/head manifest, alias and private exclusion',async({request})=>{
 // This case deliberately requests the full inventory sequentially. Keep each
 // response bounded while allowing the measured volume to grow with the manifest.
 test.setTimeout(30_000+entries.length*5_000);
 const started=Date.now();
 for(const [url,view] of entries){
  const r=await request.get(url,{timeout:5_000});expect(r.status(),url).toBe(200);
  const html=await r.text();expect(html,url).toContain(view.page.body_html);
  expect(html,url).toContain('lang="ru"');expect(html,url).toContain('<link rel="canonical" href="'+view.canonical_url+'"');
  expect(html,url).not.toContain('window.__reactRouterContext');expect(html,url).not.toContain('fixture_only_');
 }
 for(const path of ['/not-a-real-page/','/__ui__/foundation/','/_private/shell.html','/api/unknown/'])expect((await request.get(path)).status(),path).toBe(404);
 expect((await request.get('/sitemap.xml')).status()).toBe(200);expect((await request.get('/robots.txt')).status()).toBe(200);
 await test.info().attach('complete-inventory-elapsed.json',{body:JSON.stringify({urls:entries.length,elapsed_ms:Date.now()-started,per_url_timeout_ms:5000,total_timeout_ms:30000+entries.length*5000}),contentType:'application/json'});
});

test('no JavaScript home/catalogue/GET search, keyboard and focus',async({browser})=>{
 const context=await browser.newContext({javaScriptEnabled:false,viewport:test.info().project.use.viewport!});
 try{
  const page=await context.newPage();await page.goto('/');await expect(page.locator('h1').first()).toBeVisible();
  await page.getByRole('link',{name:'Все темы',exact:true}).first().click();
  await expect(page.locator('.ms-catalogue-count')).toContainText('263');
  await page.getByLabel('Название темы').fill('уравнения');await page.getByRole('button',{name:'Показать темы'}).click();
  expect(new URL(page.url()).searchParams.get('q')).toBe('уравнения');await expect(page.locator('.ms-catalogue-results a').first()).toBeVisible();
  await page.getByLabel('Название темы').fill('<script>');await page.getByRole('button',{name:'Показать темы'}).click();
  await expect(page.locator('.ms-catalogue-empty')).toBeVisible();await expect(page.getByLabel('Название темы')).toHaveValue('<script>');
  await page.keyboard.press('Tab');expect(await page.evaluate(()=>document.activeElement?.tagName)).not.toBe('BODY');
  const shot=test.info().outputPath('catalogue-no-js.png');await page.screenshot({path:shot});await test.info().attach('catalogue-no-js.png',{path:shot,contentType:'image/png'});
 }finally{await context.close();}
});

for(const route of representatives)test('widget full document lifecycle '+route,async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 const response=await page.goto(route);expect(response?.status()).toBe(200);
 await expect(page.locator('[data-lesson-host]')).toBeAttached();
 const expected=data.routes[route].page.assets;
 expect(await page.locator('script[src]').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('src')))).toEqual(expected.filter((a:any)=>a.kind==='script').map((a:any)=>a.url));
 const styles=await page.locator('link[rel=stylesheet]').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('href')));
 expect(styles.slice(0,-1)).toEqual(expected.filter((a:any)=>a.kind==='style').map((a:any)=>a.url));
 expect(styles.at(-1)).toMatch(/^\/assets\/public-migration-.*\.css$/);
 await page.evaluate(()=>{(window as any).__documentLifecycleMarker='old-document';});
 await page.getByRole('link',{name:'Все темы',exact:true}).first().click();
 expect(await page.evaluate(()=>(window as any).__documentLifecycleMarker)).toBeUndefined();
 await page.goBack();await expect(page.locator('[data-lesson-host]')).toBeAttached();
 const width=test.info().project.use.viewport!.width;await page.setViewportSize({width:width===360?768:360,height:800});
 await page.setViewportSize(test.info().project.use.viewport!);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1)).toBe(true);
 const shot=test.info().outputPath('lesson.png');await page.screenshot({path:shot});await test.info().attach('lesson.png',{path:shot,contentType:'image/png'});
 expect(errors).toEqual([]);
});
