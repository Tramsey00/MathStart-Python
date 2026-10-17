// @vitest-environment node
import {it,expect,vi} from 'vitest';
vi.mock('../src/server/public-input.server',()=>({loadPublicPage:vi.fn(()=>({verified:'public-view'}))}));
import {loader} from '../src/app/routes/public-foundation';
import {loadPublicPage} from '../src/server/public-input.server';

it('keeps the framework private SPA fallback free of a home publication view',async()=>{
 vi.mocked(loadPublicPage).mockClear();
 const request=new Request('http://localhost/',{headers:{'X-React-Router-SPA-Mode':'yes'}});
 expect(await loader({request})).toBeNull();
 expect(loadPublicPage).not.toHaveBeenCalled();
});

it('retains the verified public loader for ordinary publication prerender',async()=>{
 vi.mocked(loadPublicPage).mockClear();
 expect(await loader({request:new Request('http://localhost/verified-topic/')})).toEqual({verified:'public-view'});
 expect(loadPublicPage).toHaveBeenCalledWith('/verified-topic/');
});
