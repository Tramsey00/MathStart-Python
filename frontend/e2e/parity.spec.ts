import {test,expect} from '@playwright/test';
const routes=[
 {path:'/linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii/',regions:['.ms-lesson-toc']},
 {path:'/10-klass-stepennye-funkcii-i-grafiki-2-0/',regions:['.ms-lesson-toc','#power-lab-v2 .ms-power-presets','#power-lab-v2 .ms-live-table']},
 {path:'/10-klass-chislovaya-okruzhnost-2-0/',regions:['.ms-lesson-toc','#circle-lab-v2','#models .ms-figure >> nth=0','#models .ms-figure >> nth=1']},
 {path:'/polozhitelnye-i-otriczatelnye-chisla-opredelenie-koordinatnoj-pryamoj/',regions:['.ms-lesson-toc']},
];
test('matched live Django and React F01–F04 captures at ordinary scale',async({browser})=>{
 const legacy=process.env.MATHSTART_LEGACY_BASE_URL;if(!legacy)throw Error('Separate live disposable legacy origin required for matched captures');
 const target=process.env.MATHSTART_E2E_BASE_URL;if(!target)throw Error('Real target origin required');
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
