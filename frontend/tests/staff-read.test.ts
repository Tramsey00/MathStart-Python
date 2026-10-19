// @vitest-environment node
import {describe,it,expect,vi} from 'vitest';
import {createStaffClient,staffDefinition,staffOperations,validateStaff,stringifyExact} from '../src/shared/api/staff-client';
import {parseJson} from '../src/shared/api/json-boundary';
const meta={request_id:'12345678-1234-4234-8234-123456789abc',version:'migration-r02-v1'};
const headers={'Content-Type':'application/json','Cache-Control':'private, no-store'};
const group={id:9223372036854775807n,name:'<script>escaped</script>',permissions:[9007199254740993n]};
it('validates frozen numeric int64 bounds exactly and emits numeric wire bytes',()=>{
 expect(validateStaff(group,staffDefinition('StaffGroupDTO'))).toBe(true);
 expect(validateStaff({...group,id:9223372036854775808n},staffDefinition('StaffGroupDTO'))).toBe(false);
 expect(stringifyExact(group)).toContain('"id":9223372036854775807');
 expect(parseJson('{"id":9.223372036854775807e18}',true)).toEqual({id:9223372036854775807n});
 expect(parseJson('{"id":9007199254740993.0}',true)).toEqual({id:9007199254740993n});
});
it('registers only the 28 I02 read interfaces and refuses a write before fetch',async()=>{
 expect(staffOperations).toHaveLength(28);expect(staffOperations.every(o=>o.method==='GET')).toBe(true);
 const fetch=vi.fn();expect(await createStaffClient(fetch).call('create_staff_users')).toMatchObject({ok:false,error:{code:'INVALID_REQUEST',outcome:'not-sent'}});expect(fetch).not.toHaveBeenCalled();
});
it('preserves max int64 read identifiers while using same-origin no-store GET',async()=>{
 const fetch=vi.fn().mockResolvedValue(new Response(stringifyExact({data:group,meta}),{headers}));
 const r=await createStaffClient(fetch).call('staff_get_groups',{id:'9223372036854775807'});
 expect(r).toMatchObject({ok:true,value:{data:group}});
 expect(fetch).toHaveBeenCalledWith('/api/v1/staff/groups/9223372036854775807/',expect.objectContaining({method:'GET',credentials:'same-origin',cache:'no-store',redirect:'error'}));
});
it.each(['1.0000000000000001','9007199254740990.1','1.0000000000000001e0','90071992547409901e-1'])('rejects a mathematically fractional ID before rounding: %s',async token=>{
 const raw=stringifyExact({data:group,meta}).replace('9223372036854775807',token);
 const fetch=vi.fn().mockResolvedValue(new Response(raw,{headers}));
 expect(await createStaffClient(fetch).call('staff_get_groups',{id:'1'})).toMatchObject({ok:false,error:{code:'INVALID_RESPONSE'}});
 expect(fetch).toHaveBeenCalledTimes(1);
});
it.each(['extra-secret','duplicate-key','html','cacheable','malformed'])('rejects unsafe staff response %s',async kind=>{
 let body=stringifyExact({data:group,meta});let hs:Record<string,string>={...headers};
 if(kind==='extra-secret')body=stringifyExact({data:{...group,password:'PRIVATE'},meta});
 if(kind==='duplicate-key')body=body.replace('"id":','"id":1,"id":');
 if(kind==='html')hs['Content-Type']='text/html';if(kind==='cacheable')hs['Cache-Control']='public,max-age=60';if(kind==='malformed')body='not json';
 const fetch=vi.fn().mockResolvedValue(new Response(body,{headers:hs}));
 expect(await createStaffClient(fetch).call('staff_get_groups',{id:'1'})).toMatchObject({ok:false,error:{code:'INVALID_RESPONSE'}});
});
it('renders fixed local errors without server details and does not retry',async()=>{
 const fetch=vi.fn().mockResolvedValue(new Response(JSON.stringify({error:{code:'FORBIDDEN',message:'PRIVATE SQL SECRET',request_id:meta.request_id,field_errors:{},retryable:false}}),{status:403,headers}));
 const r=await createStaffClient(fetch).call('staff_list_users');expect(r).toMatchObject({ok:false,error:{code:'FORBIDDEN',message:'Действие недоступно.'}});expect(JSON.stringify(r)).not.toContain('PRIVATE');expect(fetch).toHaveBeenCalledTimes(1);
});
it.each([null,[],1,'query',{unexpected:'x'},{filter__is_staff:'1'},{filter__groups:'9223372036854775808'}])('rejects malformed/noncanonical queries before a network request: %j',async query=>{
 const fetch=vi.fn();expect(await createStaffClient(fetch).call('staff_list_users',{query}as never)).toMatchObject({ok:false,error:{code:'INVALID_REQUEST',outcome:'not-sent'}});expect(fetch).not.toHaveBeenCalled();
});
