// @vitest-environment node
import {it,expect,vi} from 'vitest';
import {createProgressClient} from '../src/shared/api/progress-client';
const id='12345678-1234-4234-8234-123456789abc';
const meta={request_id:id,version:'http-v1'};
const page={...meta,pagination:{next_cursor:null,page_size:20,has_more:false}};
const csrf={data:{csrf_token:'synthetic-only'},meta};
const json=(value:unknown,status=200)=>new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json'}});

it('accepts exact server projections and retained legacy event identities, sends only own canonical reads',async()=>{
  const events={data:[{event_id:'retained-event-1',skill_code:'negative_numbers',event_kind:'WRONG_ATTEMPT',
    occurred_at:'2026-01-01T00:00:00.000000Z',attempt_id:'retained-attempt-1',evidence_ref:'step:1',policy_version:'progress-v1'}],meta:page};
  const fetch=vi.fn().mockResolvedValue(json(events));
  expect(await createProgressClient(fetch).call('list_progress_events',{})).toEqual({ok:true,value:events});
  expect(fetch.mock.calls[0]).toMatchObject(['/api/v1/progress/events/',{method:'GET',credentials:'same-origin',cache:'no-store',redirect:'error'}]);
});
it('self-report uses CSRF and retains the same key/body on explicit unknown retry',async()=>{
  const result={data:{accepted_skill_codes:['negative_numbers'],already_reported_skill_codes:[]},meta};
  const fetch=vi.fn().mockResolvedValueOnce(json(csrf)).mockRejectedValueOnce(new Error('lost ACK'))
    .mockResolvedValueOnce(json(csrf)).mockResolvedValueOnce(json(result));
  const client=createProgressClient(fetch),options={body:{skill_codes:['negative_numbers']},idempotencyKey:'same-key'};
  expect(await client.call('create_self_report',options)).toMatchObject({ok:false,outcome:'unknown'});
  expect(fetch).toHaveBeenCalledTimes(2);
  expect(await client.call('create_self_report',options)).toEqual({ok:true,value:result});
  expect(fetch.mock.calls[1]?.[1].body).toBe(fetch.mock.calls[3]?.[1].body);
  expect(fetch.mock.calls[3]?.[1].headers['Idempotency-Key']).toBe('same-key');
});
it('rejects forged mastery writes, unexpected read owner filters and malformed numeric projections',async()=>{
  const fetch=vi.fn().mockResolvedValue(json({data:[{skill_code:'negative_numbers',mastery:'60.00'}],meta:page}));
  const client=createProgressClient(fetch);
  expect(await client.call('create_self_report',{body:{skill_codes:['negative_numbers'],mastery:100} as never,idempotencyKey:'x'})).toMatchObject({ok:false,outcome:'not-sent'});
  expect(fetch).not.toHaveBeenCalled();
  expect(await client.call('list_progress_skills',{query:{user_id:42} as never})).toMatchObject({ok:false,outcome:'not-sent'});
  expect(fetch).not.toHaveBeenCalled();
  expect(await client.call('list_progress_skills',{})).toMatchObject({ok:false,code:'INVALID_RESPONSE'});
});
