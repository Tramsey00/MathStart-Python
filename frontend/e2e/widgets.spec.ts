import {test,expect,type Page} from '@playwright/test';
const power='/10-klass-stepennye-funkcii-i-grafiki-2-0/',circle='/10-klass-chislovaya-okruzhnost-2-0/';
const legacy=['/linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii/','/funkcziya-kvadratnogo-kornya-eyo-svojstva-i-grafik/','/funkcziya-y-k-x-i-eyo-svojstva-giperbola/','/kvadratichnaya-funkcziya-y-ax2-bx-c/','/stepennaya-funkcziya-s-naturalnym-pokazatelem/','/stepennaya-funkcziya-s-otriczatelnym-czelym-pokazatelem/'];
async function capture(page:Page,name:string){const path=test.info().outputPath(name+'.png');await page.screenshot({path});await test.info().attach(name+'.png',{path,contentType:'image/png'});}
async function region(page:Page,selector:string,name:string){const path=test.info().outputPath(name+'.png');await page.locator(selector).screenshot({path});await test.info().attach(name+'.png',{path,contentType:'image/png'});}
async function fits(page:Page,selector:string){return page.locator(selector).evaluateAll(nodes=>nodes.map(n=>{const r=n.getBoundingClientRect();return {text:n.textContent,client:n.clientWidth,scroll:n.scrollWidth,rect:{left:r.left,right:r.right,top:r.top,bottom:r.bottom}};}).filter(n=>n.scroll>n.client+1));}
for(const route of legacy)test('real graph keyboard/pointer/reset and mathematical readouts '+route,async({page})=>{
 await page.goto(route);const control=page.locator('input[type=range]').first();const start=await control.inputValue();
 await control.focus();await page.keyboard.press('End');expect(await control.inputValue()).not.toBe(start);
 const values=await page.locator('input[type=range]').evaluateAll(nodes=>Object.fromEntries(nodes.map(n=>[n.getAttribute('data-role'),Number((n as HTMLInputElement).value)])));
 const cells=await page.locator('[data-role=table-value]').evaluateAll(nodes=>nodes.map(n=>({x:Number(n.getAttribute('data-x')),text:n.textContent??''})));
 for(const cell of cells){let expected:number;
  if(route.includes('naturalnym')||route.includes('otriczatelnym'))expected=Math.pow(cell.x,values['n-range']!);
  else if(route.includes('kvadratnogo-kornya'))expected=values['k-range']!*Math.sqrt(cell.x)+values['a-range']!;
  else if(route.includes('giperbola'))expected=values['k-range']!/cell.x+values['b-range']!;
  else expected=values['a-range']!*cell.x**2+values['b-range']!*cell.x+values['c-range']!;
  // The preserved power-table formatter displays three significant digits in
  // scientific notation for magnitudes >=1000 (for example1024 ->1.02e+3).
  if((route.includes('naturalnym')||route.includes('otriczatelnym'))&&Math.abs(expected)>=1000)expected=Number(expected.toExponential(2));
  if(Number.isFinite(expected))expect(Number(cell.text.replaceAll('−','-').replace(',','.'))).toBeCloseTo(expected,1);
 }
 const canvas=page.locator('canvas').first();await canvas.scrollIntoViewIfNeeded();await canvas.hover();
 await page.locator('[data-role=reset]').click();await expect(control).toHaveValue(start);
 await capture(page,'graph-controls');expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
});

test('F01 all four contents panels have readable labels and keyboard anchors',async({page})=>{
 for(const route of [legacy[0]!,power,circle,'/polozhitelnye-i-otriczatelnye-chisla-opredelenie-koordinatnoj-pryamoj/']){
  await page.goto(route);const toc=page.locator('.ms-lesson-toc');await toc.evaluate(n=>(n as HTMLDetailsElement).open=true);
  expect(await fits(page,'.ms-toc-copy strong,.ms-toc-copy small')).toEqual([]);
  await region(page,'.ms-lesson-toc','initial-contents-'+route.slice(1,25));
  const link=page.locator('.ms-toc-link').first();await link.focus();await page.keyboard.press('Enter');
  expect(new URL(page.url()).hash).not.toBe('');await capture(page,'contents-'+route.slice(1,25));
 }
});

test('F02 twelve power presets pointer/keyboard aria and F03 exact0.0625 table cell',async({page})=>{
 await page.goto(power);const presets=page.locator('#power-lab-v2 .ms-power-preset');await expect(presets).toHaveCount(12);
 for(let i=0;i<12;i++){
  const button=presets.nth(i);await button.focus();await page.keyboard.press('Enter');await expect(button).toHaveAttribute('aria-pressed','true');await expect(page.locator('#power-lab-v2 .ms-power-preset[aria-pressed=true]')).toHaveCount(1);
 }
 await page.locator('#power-lab-v2 .ms-power-preset[data-n="2"][data-d="1"]').click();
 await expect(page.locator('#power-lab-v2 [data-role=table-value][data-x="0.25"]')).toHaveText('0,0625');
 expect(await fits(page,'#power-lab-v2 .ms-power-preset,#power-lab-v2 .ms-live-table-cell')).toEqual([]);
 await region(page,'#power-lab-v2 .ms-power-presets','power-twelve-presets');
 await region(page,'#power-lab-v2 .ms-live-table','power-exact-table');
});

test('F04 circle angle coordinates/readouts and ordinary-scale SVG labels',async({page})=>{
 await page.goto(circle);const root=page.locator('#circle-lab-v2');await expect(root).toHaveAttribute('data-ready','true');
 await root.locator('[data-step="6"]').click();await expect(root.locator('[data-output=degrees]')).toHaveText('90°');
 await expect(root.locator('[data-role=point]')).toHaveAttribute('data-x','0');await expect(root.locator('[data-role=point]')).toHaveAttribute('data-y','1');
 await root.locator('[data-action=reset]').click();await region(page,'#circle-lab-v2','circle-lab-controls-coordinates');
 const stats=await page.locator('#circle-lab-v2 svg,#models svg').evaluateAll(nodes=>nodes.map(svg=>{
  const box=svg.getBoundingClientRect();return [...svg.querySelectorAll('text')].map(t=>{const r=t.getBoundingClientRect();return {text:t.textContent,height:r.height,inside:r.left>=box.left-1&&r.right<=box.right+1&&r.top>=box.top-1&&r.bottom<=box.bottom+1};});
 }).flat());
 expect(stats.every(t=>t.inside)).toBe(true);
 await test.info().attach('svg-labels.json',{body:JSON.stringify(stats),contentType:'application/json'});
 await region(page,'#models .ms-figure >> nth=0','circle-model-eight-parts');
 await region(page,'#models .ms-figure >> nth=1','circle-model-twelve-parts');
});
