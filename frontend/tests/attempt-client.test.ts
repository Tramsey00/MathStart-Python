// @vitest-environment node
import {it,expect,vi} from 'vitest';
import fixture from './fixtures/attempt-states.json';
import {createAttemptClient,type AttemptRecovery} from '../src/shared/api/attempt-client';
import * as validate from '../src/shared/api/generated/attempt-validators.mjs';

const id=fixture.started.data.id,meta=fixture.started.meta;
const csrf={data:{csrf_token:'synthetic-csrf'},meta};
const json=(value:unknown,status=200)=>new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json'}});
const failure=(code:string)=>({error:{code,message:'private diagnostics',field_errors:{},retryable:code==='SERVICE_UNAVAILABLE',request_id:meta.request_id}});
const pending=()=>({...fixture.started,data:{...fixture.started.data,state:'SUBMITTED',revision:3,
  snapshot_digest:'a'.repeat(64),operation_id:id,submitted_at:'2026-11-19T00:00:01.000000Z',
  eligibility:{independent:false,positive_credit_eligible:false,reason:'PENDING'}}});
const options={id,body:{expected_revision:2,contract_version:1},idempotencyKey:fixture.recovery.operationKey};

it('validates synthetic states and keeps raw recovery data outside public runtime',()=>{
  expect(validate.AttemptResponse(fixture.started)).toBe(true);
  expect(validate.PendingAttemptResponse(pending())).toBe(true);
  for(const state of ['ready','pending','unknown','conflict','unauthorized'] as const){
    const recovery:AttemptRecovery={...fixture.recovery,state};
    expect(recovery.draft.payload.answer).toBe(' −2,5 ');
    expect(recovery.operationKey).toBe(options.idempotencyKey);
  }
});
it('returns durable pending and GET recovery without creating or submitting again',async()=>{
  const fetch=vi.fn().mockResolvedValueOnce(json(csrf)).mockResolvedValueOnce(json(pending(),202))
    .mockResolvedValueOnce(json(pending()));
  const client=createAttemptClient(fetch);
  expect(await client.call('submit_attempt',options)).toMatchObject({ok:true,pending:true});
  expect(await client.call('get_attempt',{id})).toMatchObject({ok:true,pending:true});
  expect(fetch).toHaveBeenCalledTimes(3);
  expect(fetch.mock.calls[1]?.[0]).toBe(`/api/v1/attempts/${id}/submit/`);
  expect(fetch.mock.calls[1]?.[1]).toMatchObject({credentials:'same-origin',cache:'no-store',redirect:'error',
    headers:{'Idempotency-Key':options.idempotencyKey,'X-CSRFToken':'synthetic-csrf'}});
});
it('preserves key and body on explicit lost-ACK retry, never automatically retries',async()=>{
  const fetch=vi.fn().mockResolvedValueOnce(json(csrf)).mockRejectedValueOnce(new Error('lost ACK'))
    .mockResolvedValueOnce(json(csrf)).mockResolvedValueOnce(json(pending(),202));
  const client=createAttemptClient(fetch);
  expect(await client.call('submit_attempt',options)).toMatchObject({ok:false,outcome:'unknown'});
  expect(fetch).toHaveBeenCalledTimes(2);
  expect(await client.call('submit_attempt',options)).toMatchObject({ok:true,pending:true});
  expect(fetch.mock.calls[1]?.[1].body).toBe(fetch.mock.calls[3]?.[1].body);
  expect(fetch.mock.calls[3]?.[1].headers['Idempotency-Key']).toBe(options.idempotencyKey);
});
it('polls the same submitted snapshot and distinguishes a safe terminal fallback',async()=>{
  const accepted=pending();
  const terminal={...accepted,data:{...accepted.data,state:'COMPLETED',completed_at:'2026-11-19T00:00:02Z',
    eligibility:{independent:false,positive_credit_eligible:false,reason:'UNSUPPORTED_INPUT'},
    result:{outcome:'UNSUPPORTED',service_state:'DEGRADED',safe_feedback:'Try another entry',
      positive_credit_awarded:false,first_error_step_id:null,misconception_code:null}}};
  const fetch=vi.fn().mockResolvedValueOnce(json(csrf)).mockResolvedValueOnce(json(accepted,202))
    .mockResolvedValueOnce(json(accepted)).mockResolvedValueOnce(json(terminal))
    .mockResolvedValueOnce(json({...terminal,data:{...terminal.data,snapshot_digest:'b'.repeat(64)}}));
  const client=createAttemptClient(fetch);
  const submit=await client.submit(options);
  if(!submit.ok)throw Error('Expected a durable submit receipt');
  expect(await client.pollSubmission(submit.value)).toMatchObject({ok:true,pending:true,value:{state:'SUBMITTED'}});
  expect(await client.pollSubmission(submit.value)).toMatchObject({ok:true,pending:false,value:{
    state:'COMPLETED',result:{outcome:'UNSUPPORTED',service_state:'DEGRADED'}}});
  expect(await client.pollSubmission(submit.value)).toMatchObject({ok:false,code:'MISMATCHED_SUBMISSION'});
});
it('keeps 503 uncertain and rejects fabricated 202 without a snapshot',async()=>{
  for(const response of [json(failure('SERVICE_UNAVAILABLE'),503),json(fixture.started,202)]){
    const fetch=vi.fn().mockResolvedValueOnce(json(csrf)).mockResolvedValueOnce(response);
    expect(await createAttemptClient(fetch).call('submit_attempt',options)).toMatchObject({ok:false,outcome:'unknown'});
    expect(fetch).toHaveBeenCalledTimes(2);
  }
});
it('returns safe revision reconciliation, and never exposes server diagnostics',async()=>{
  const conflict=failure('REVISION_CONFLICT');
  const response={error:{...conflict.error,current_revision:3,reload_url:`/api/v1/attempts/${id}/`}};
  const fetch=vi.fn().mockResolvedValueOnce(json(csrf)).mockResolvedValueOnce(json(response,409));
  const result=await createAttemptClient(fetch).call('update_draft',{id,body:{expected_revision:2,contract_version:1,draft:fixture.recovery.draft}});
  expect(result).toMatchObject({ok:false,code:'REVISION_CONFLICT',currentRevision:3,reloadUrl:`/api/v1/attempts/${id}/`});
  expect(JSON.stringify(result)).not.toContain('diagnostics');
  expect(fixture.recovery.draft.payload.answer).toBe(' −2,5 ');
});
it('blocks invalid raw payload, foreign canonical paths and missing CSRF before mutation',async()=>{
  const fetch=vi.fn().mockResolvedValue(json(failure('AUTHENTICATION_REQUIRED'),401));
  const client=createAttemptClient(fetch);
  expect(await client.call('get_attempt',{id:'https://elsewhere.example'})).toMatchObject({ok:false,outcome:'not-sent'});
  expect(fetch).not.toHaveBeenCalled();
  const bad={...options,body:{...options.body,unexpected:true}};
  expect(await client.call('submit_attempt',bad)).toMatchObject({ok:false,outcome:'not-sent'});
  expect(fetch).not.toHaveBeenCalled();
  expect(await client.call('submit_attempt',options)).toMatchObject({ok:false,outcome:'not-sent'});
  expect(fetch).toHaveBeenCalledTimes(1);
});
