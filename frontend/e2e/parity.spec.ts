import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
const routes=[
 {path:'/linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii/',regions:['.ms-lesson-toc','#ms-linear-lab-723']},
 {path:'/10-klass-stepennye-funkcii-i-grafiki-2-0/',regions:['.ms-lesson-toc','#power-lab-v2 .ms-power-presets','#power-lab-v2 .ms-live-table']},
 {path:'/10-klass-chislovaya-okruzhnost-2-0/',regions:['.ms-lesson-toc','#circle-lab-v2','#models .ms-figure >> nth=0','#models .ms-figure >> nth=1']},
 {path:'/polozhitelnye-i-otriczatelnye-chisla-opredelenie-koordinatnoj-pryamoj/',regions:['.ms-lesson-toc']},
 {path:'/funkcziya-kvadratnogo-kornya-eyo-svojstva-i-grafik/',regions:['.ms-lesson-toc','#ms-root-lab-832']},
 {path:'/funkcziya-y-k-x-i-eyo-svojstva-giperbola/',regions:['.ms-lesson-toc','#ms-hyperbola-lab-621']},
 {path:'/kvadratichnaya-funkcziya-y-ax2-bx-c/',regions:['.ms-lesson-toc','#ms-quadratic-lab-660']},
 {path:'/stepennaya-funkcziya-s-naturalnym-pokazatelem/',regions:['.ms-lesson-toc','#ms-power-lab-935']},
 {path:'/stepennaya-funkcziya-s-otriczatelnym-czelym-pokazatelem/',regions:['.ms-lesson-toc','#ms-negative-power-lab-936']},
];
test('matched live Django and React all script families plus F01–F04 at ordinary scale',async({browser})=>{
 const legacy=process.env.MATHSTART_LEGACY_BASE_URL;if(!legacy)throw Error('Separate live disposable legacy origin required for matched captures');
 const target=process.env.MATHSTART_E2E_BASE_URL;if(!target)throw Error('Real target origin required');
 const input=process.env.MATHSTART_PUBLIC_VIEW;if(!input)throw Error('Verified complete public view required');
 const data=JSON.parse(readFileSync(input,'utf8')) as {routes:Record<string,{page:{assets:{kind:string;url:string}[]}}>} ;
 const scripts=(view:{page:{assets:{kind:string;url:string}[]}})=>view.page.assets.filter(asset=>asset.kind==='script').map(asset=>asset.url);
 const required=[...new Set(Object.values(data.routes).flatMap(scripts))].sort();
 const covered=[...new Set(routes.flatMap(route=>{const view=data.routes[route.path];expect(view,route.path).toBeTruthy();return scripts(view!);} ))].sort();
 expect(covered,'Every published script family needs matched baseline/target captures').toEqual(required);
 await test.info().attach('matched-family-coverage.json',{body:JSON.stringify({required,covered,routes:routes.map(route=>route.path)}),contentType:'application/json'});
 const context=await browser.newContext({viewport:test.info().project.use.viewport!});
 try{
  const page=await context.newPage();const pairs=[];
  for(let r=0;r<routes.length;r++)for(const [side,origin]of [['legacy',legacy],['target',target]]){
   const entry=routes[r]!;expect((await page.goto(origin+entry.path))?.status()).toBe(200);
   await page.locator('.ms-lesson-toc').evaluate(n=>(n as HTMLDetailsElement).open=true);
   for(let i=0;i<entry.regions.length;i++){
    const selector=entry.regions[i]!,path=test.info().outputPath(`r${r}-region${i}-${side}.png`);
    await page.locator(selector).screenshot({path});await test.info().attach(`r${r}-region${i}-${side}.png`,{path,contentType:'image/png'});
    pairs.push({route:entry.path,selector,side,project:test.info().project.name,viewport:test.info().project.use.viewport,device_scale_factor:1,browser_version:browser.version(),screenshot:`r${r}-region${i}-${side}.png`});
   }
  }
  await test.info().attach('matched-capture-index.json',{body:JSON.stringify(pairs,null,2),contentType:'application/json'});
 }finally{await context.close();}
});
