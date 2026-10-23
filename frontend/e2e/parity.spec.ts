import {test,expect} from '@playwright/test';
import {readFileSync,writeFileSync} from 'node:fs';
const routes=[
 {path:'/10-klass-stepennye-funkcii-i-grafiki-2-0/',regions:['.ms-lesson-toc','#power-lab-v2 .ms-power-presets','#power-lab-v2 .ms-live-table']},
 {path:'/10-klass-chislovaya-okruzhnost-2-0/',regions:['.ms-lesson-toc','#circle-lab-v2','#models .ms-figure >> nth=0','#models .ms-figure >> nth=1']},
 {path:'/polozhitelnye-i-otriczatelnye-chisla-opredelenie-koordinatnoj-pryamoj/',regions:['.ms-lesson-toc']},
 {path:'/funkcziya-kvadratnogo-kornya-eyo-svojstva-i-grafik/',regions:['.ms-lesson-toc','#ms-root-lab-832']},
 {path:'/funkcziya-y-k-x-i-eyo-svojstva-giperbola/',regions:['.ms-lesson-toc','#ms-hyperbola-lab-621']},
 {path:'/kvadratichnaya-funkcziya-y-ax2-bx-c/',regions:['.ms-lesson-toc','#ms-quadratic-lab-660']},
 {path:'/stepennaya-funkcziya-s-naturalnym-pokazatelem/',regions:['.ms-lesson-toc','#ms-power-lab-935']},
 {path:'/stepennaya-funkcziya-s-otriczatelnym-czelym-pokazatelem/',regions:['.ms-lesson-toc','#ms-negative-power-lab-936']},
];
const templates=[...routes,{path:'/',regions:['body']},{path:'/karta-sajta/',regions:['body']},{path:'structural-grade',regions:['body']}];
for(const [r,template] of templates.entries())test(`matched live Django and React ${template.path} at ordinary scale`,async({browser})=>{
 const legacy=process.env.MATHSTART_LEGACY_BASE_URL;if(!legacy)throw Error('Separate live disposable legacy origin required for matched captures');
 const target=process.env.MATHSTART_E2E_BASE_URL;if(!target)throw Error('Real target origin required');
 const input=process.env.MATHSTART_PUBLIC_VIEW;if(!input)throw Error('Verified complete public view required');
 const data=JSON.parse(readFileSync(input,'utf8')) as {routes:Record<string,{page:{page_type:string;assets:{kind:string;url:string}[]}}>} ;
 const grade=Object.entries(data.routes).find(([,view])=>view.page.page_type==='grade')?.[0];expect(grade,'Real published structural grade route required').toBeTruthy();
 const allRoutes=templates.map(entry=>({...entry,path:entry.path==='structural-grade'?grade!:entry.path}));
 const scripts=(view:{page:{assets:{kind:string;url:string}[]}})=>view.page.assets.filter(asset=>asset.kind==='script').map(asset=>asset.url);
 const required=[...new Set(Object.values(data.routes).flatMap(scripts))].sort();
 const covered=[...new Set(allRoutes.flatMap(route=>{const view=data.routes[route.path];expect(view,route.path).toBeTruthy();return scripts(view!);} ))].sort();
 expect(covered,'Every published script family needs matched baseline/target captures').toEqual(required);
 const coverage=test.info().outputPath('matched-family-coverage.json');writeFileSync(coverage,JSON.stringify({required,covered,routes:allRoutes.map(route=>route.path)}));await test.info().attach('matched-family-coverage.json',{path:coverage,contentType:'application/json'});
 const context=await browser.newContext({viewport:test.info().project.use.viewport!});
 try{
  const page=await context.newPage();const pairs=[];
  for(const [side,origin]of [['legacy',legacy],['target',target]]){
   const entry=allRoutes[r]!;expect((await page.goto(origin+entry.path))?.status()).toBe(200);
   if(entry.regions.includes('.ms-lesson-toc'))await page.locator('.ms-lesson-toc').evaluate(n=>(n as HTMLDetailsElement).open=true);
   if(side==='target'&&entry.path==='/karta-sajta/'){
    await expect(page.locator('#topics-catalogue h1')).toHaveText('Все темы');
    await expect(page.locator('#topics-catalogue > [data-mathstart-catalogue]')).toHaveCSS('display','contents');
   }
   if(side==='target'&&template.path==='structural-grade'){
    const cards=page.locator('.ms-site-page .ms-stat-grid > .ms-stat');
    await expect(cards).toHaveCount(3);
    const clipped=await cards.evaluateAll(nodes=>nodes.flatMap(n=>{const p=n.getBoundingClientRect();return [...n.children].map(c=>{const r=c.getBoundingClientRect();return{text:c.textContent?.trim(),width:r.width,left:r.left,right:r.right,scroll:c.scrollWidth,client:c.clientWidth,parentLeft:p.left,parentRight:p.right};}).filter(c=>c.width<=0||c.left<c.parentLeft-1||c.right>c.parentRight+1||c.scroll>c.client+1);}));
    expect(clipped,'All three structural statistics and their labels must remain readable').toEqual([]);
   }

   for(let i=0;i<entry.regions.length;i++){
    const selector=entry.regions[i]!,path=test.info().outputPath(`r${r}-region${i}-${side}.png`);
    await page.locator(selector).screenshot({path});await test.info().attach(`r${r}-region${i}-${side}.png`,{path,contentType:'image/png'});
    pairs.push({route:entry.path,selector,side,project:test.info().project.name,viewport:test.info().project.use.viewport,device_scale_factor:1,browser_version:browser.version(),screenshot:`r${r}-region${i}-${side}.png`});
   }
  }
  const index=test.info().outputPath('matched-capture-index.json');writeFileSync(index,JSON.stringify(pairs,null,2));await test.info().attach('matched-capture-index.json',{path:index,contentType:'application/json'});
 }finally{await context.close();}
});
