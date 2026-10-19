// @vitest-environment node
import {it,expect,vi} from 'vitest';
import {createStaffWriteClient} from '../src/shared/api/staff-write-client';
import {stringifyExact} from '../src/shared/api/staff-client';

const requestId='12345678-1234-4234-8234-123456789abc';
const headers={'Content-Type':'application/json','Cache-Control':'private, no-store'};
const csrf=()=>new Response(JSON.stringify({data:{csrf_token:'a'.repeat(64)},meta:{request_id:requestId,version:'http-v1'}}),{headers});
const group={id:9223372036854775807n,name:'Synthetic group',permissions:[9007199254740993n]};
const response=(data:unknown)=>new Response(stringifyExact({data,meta:{request_id:requestId,version:'migration-r02-v1'}}),{status:201,headers});

it('validates a write then obtains fresh CSRF, preserving numeric int64 bytes',async()=>{
 const fetch=vi.fn().mockResolvedValueOnce(csrf()).mockResolvedValueOnce(response(group));
 const r=await createStaffWriteClient(fetch).call('create_staff_groups',{body:{name:group.name,permissions:group.permissions}});
 expect(r).toEqual({ok:true,value:{data:group,meta:{request_id:requestId,version:'migration-r02-v1'}}});
 expect(fetch).toHaveBeenCalledTimes(2);
 expect(fetch.mock.calls[1]).toEqual(['/api/v1/staff/groups/',expect.objectContaining({method:'POST',credentials:'same-origin',cache:'no-store',redirect:'error',body:'{"name":"Synthetic group","permissions":[9007199254740993]}',headers:expect.objectContaining({'X-CSRFToken':'a'.repeat(64)})})]);
});

it.each([null,{name:'x',permissions:[9223372036854775808n]},{name:'x',permissions:[1,1]},{name:'x',permissions:[],extra:true}])('rejects invalid write before CSRF or mutation %#',async body=>{
 const fetch=vi.fn();expect(await createStaffWriteClient(fetch).call('create_staff_groups',{body})).toMatchObject({ok:false,error:{code:'INVALID_REQUEST',outcome:'not-sent'}});expect(fetch).not.toHaveBeenCalled();
});

it('rejects accessors, cycles, sparse arrays and unsafe rounded numeric requests',async()=>{
 const fetch=vi.fn(),getter=vi.fn();const body=Object.defineProperty({permissions:[]},'name',{get:getter,enumerable:true});
 for(const invalid of [body,{name:'x',permissions:[9007199254740992]},{name:'x',permissions:new Array(1)}]){
  expect(await createStaffWriteClient(fetch).call('create_staff_groups',{body:invalid})).toMatchObject({ok:false,error:{outcome:'not-sent'}});
 }
 expect(fetch).not.toHaveBeenCalled();expect(getter).not.toHaveBeenCalled();
});

it('reports an unknown mutation outcome after lost acknowledgement without replay',async()=>{
 const fetch=vi.fn().mockResolvedValueOnce(csrf()).mockRejectedValueOnce(new Error('lost ack'));
 expect(await createStaffWriteClient(fetch).call('create_staff_groups',{body:{name:'x',permissions:[]}})).toMatchObject({ok:false,error:{outcome:'unknown'}});
 expect(fetch).toHaveBeenCalledTimes(2);
});

it('refuses cacheable or malformed mutation responses without claiming success',async()=>{
 for(const bad of [new Response('not json',{status:201,headers}),new Response(stringifyExact({data:group,meta:{request_id:requestId,version:'migration-r02-v1'}}),{status:201,headers:{...headers,'Cache-Control':'public, max-age=100'}})]){
  const fetch=vi.fn().mockResolvedValueOnce(csrf()).mockResolvedValueOnce(bad);
  expect(await createStaffWriteClient(fetch).call('create_staff_groups',{body:{name:'x',permissions:[]}})).toMatchObject({ok:false,error:{outcome:'unknown'}});
  expect(fetch).toHaveBeenCalledTimes(2);
 }
});

it('does not send a mutation after CSRF fails',async()=>{
 const fetch=vi.fn().mockRejectedValue(new Error('offline'));
 expect(await createStaffWriteClient(fetch).call('create_staff_groups',{body:{name:'x',permissions:[]}})).toMatchObject({ok:false,error:{outcome:'not-sent'}});
 expect(fetch).toHaveBeenCalledTimes(1);
});
