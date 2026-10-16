import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
// The external disposable-runtime orchestrator mints this opaque cookie. Never
// attach it, storageState, request headers or a private trace to evidence.
test.use({trace:'off'});
const resources=[['grades','content/grade'],['subjects','content/subject'],['sections','content/section'],['pages','content/contentpage'],['publications','content/lessonpublication'],['media_assets','content/mediaasset'],['redirects','content/redirect'],['users','auth/user'],['groups','auth/group']];

test('real anonymous staff reads remain denied, with private no-store',async({page})=>{
 const response=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/v1/staff/users/');await page.goto('/admin/auth/user/');
 const wire=await response;expect(wire.status()).toBe(401);expect(wire.headers()['cache-control']).toContain('no-store');
 await expect(page.getByRole('status')).toHaveText('Войдите в аккаунт.');
});

for(const [resource,native]of resources)test('real staff list/detail/history reads '+resource,async({page,context})=>{
 const file=process.env.MATHSTART_STAFF_COOKIE_FILE;if(!file)throw Error('Guarded disposable staff cookie file required');
 const input=JSON.parse(readFileSync(file,'utf8'));
 await context.addCookies(Array.isArray(input)?input:input.cookies);
 const network:{path:string;status:number;cache:string}[]=[];
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 page.on('response',r=>{const path=new URL(r.url()).pathname;if(path.startsWith('/api/v1/staff/'))network.push({path,status:r.status(),cache:r.headers()['cache-control']??''});});
  const list=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/v1/staff/'+resource+'/');await page.goto('/admin/'+native+'/');
  expect((await list).status(),resource).toBe(200);await expect(page.getByRole('status')).toHaveText('Данные загружены.');
  const links=page.locator('#staff-main > ul a');
  // The disposable runtime fixture contains one row in every registered resource.
  // An empty list is a setup/API/UI failure, never a reason to omit detail reads.
  expect(await links.count(),resource+' fixture rows').toBeGreaterThanOrEqual(1);
   const href=await links.first().getAttribute('href');const id=href!.split('/').at(-3)!;expect(id).toMatch(/^[1-9]\d*$/);
   const detail=page.waitForResponse(r=>new URL(r.url()).pathname===`/api/v1/staff/${resource}/${id}/`);await links.first().click();expect((await detail).status()).toBe(200);await expect(page.getByRole('status')).toHaveText('Данные загружены.');
   const history=page.waitForResponse(r=>new URL(r.url()).pathname===`/api/v1/staff/${resource}/${id}/history/`);await page.getByRole('link',{name:'История',exact:true}).click();expect((await history).status()).toBe(200);await expect(page.getByRole('status')).toHaveText('Данные загружены.');
 expect(network.length).toBeGreaterThanOrEqual(3);expect(network.every(r=>r.status===200&&r.cache.includes('no-store'))).toBe(true);
 expect(errors).toEqual([]);
 await test.info().attach('sanitized-staff-network.json',{body:JSON.stringify(network),contentType:'application/json'});
});
