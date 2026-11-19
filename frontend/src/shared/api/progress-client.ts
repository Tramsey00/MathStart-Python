import {progressOperations} from './generated/progress-contracts';
import * as validators from './generated/progress-validators.mjs';
import {createApiClient} from './client';
import {parseJson,isJsonTree} from './json-boundary';

export type SkillProgress={skill_code:string;mastery:number;confidence:number;evidence_count:number;
  status:'NOT_STARTED'|'LEARNING'|'WEAK'|'MASTERED';last_updated:string|null;reducer_version:'progress-v1.1';self_reported:boolean};
export type TopicProgress={topic:{id:number;slug:string};mastery:number;confidence:number;assessed_skill_count:number;total_skill_count:number};
export type ProgressEventRead={event_id:string;skill_code:string;event_kind:string;occurred_at:string;
  attempt_id:string|null;evidence_ref:string;policy_version:'progress-v1'};
export type CompletionRead={completion_id:string;attempt_id:string;skill_code:string;
  outcome:'CORRECT'|'WRONG'|'UNSUPPORTED'|'INDETERMINATE';independent_correct:boolean;completed_at:string;policy_version:'progress-v1.1'};
type Meta={request_id:string;version?:string;pagination:{next_cursor:string|null;has_more:boolean;page_size:number}};
type Contracts={list_progress_skills:{data:SkillProgress[];meta:Meta};list_progress_topics:{data:TopicProgress[];meta:Meta};
  list_progress_events:{data:ProgressEventRead[];meta:Meta};
  list_progress_completions:{data:CompletionRead[];meta:Meta};
  create_self_report:{data:{accepted_skill_codes:string[];already_reported_skill_codes:string[]};meta:Omit<Meta,'pagination'>}};
type Operation=keyof Contracts;
type Options<K extends Operation>={signal?:AbortSignal}&(K extends 'create_self_report'
  ?{body:{skill_codes:string[]};idempotencyKey:string;query?:never}
  :{body?:never;idempotencyKey?:never;query?:{page_size?:number;cursor?:string}});
export type ProgressResult<T>={ok:true;value:T}|{ok:false;code:string;status:number|null;outcome:'not-sent'|'unknown'|'rejected'};
type Fetcher=(input:RequestInfo|URL,init?:RequestInit)=>Promise<Response>;

/** Read-only knowledge projections plus explicit self-report. Never sends mastery/events/facts. */
export function createProgressClient(fetcher:Fetcher=globalThis.fetch.bind(globalThis)){
  const auth=createApiClient(fetcher),checks=validators as Record<string,(v:unknown)=>boolean>;
  return {async call<K extends Operation>(operation:K,options:Options<K>):Promise<ProgressResult<Contracts[K]>>{
    let sent=false;
    const fail=(code:string,status:number|null=null,outcome:'not-sent'|'unknown'|'rejected'='not-sent')=>({ok:false as const,code,status,outcome});
    if(!Object.hasOwn(progressOperations,operation)||!options)return fail('INVALID_REQUEST');
    const config=progressOperations[operation];
    let path:string=config.path;
    try{
      const headers:Record<string,string>={Accept:'application/json'};
      let body:string|undefined;
      if(config.request){
        if(!isJsonTree(options.body)||checks[config.request]?.(options.body)!==true
          ||!options.idempotencyKey||options.idempotencyKey.length>256||/[\r\n\0]/.test(options.idempotencyKey))return fail('INVALID_REQUEST');
        body=JSON.stringify(options.body);
        if(new TextEncoder().encode(body).length>65536)return fail('INVALID_REQUEST');
        const csrf=await auth.call('get_csrf',options.signal?{signal:options.signal}:{});
        if(!csrf.ok)return fail(csrf.error.code,csrf.error.status);
        headers['X-CSRFToken']=csrf.value.data.csrf_token;
        headers['Idempotency-Key']=options.idempotencyKey;
        headers['Content-Type']='application/json';
      }else if(options.body!==undefined||options.idempotencyKey!==undefined)return fail('INVALID_REQUEST');
      if(options.query){
        if(operation==='create_self_report'||!isJsonTree(options.query)||Object.keys(options.query).some(k=>k!=='page_size'&&k!=='cursor'))return fail('INVALID_REQUEST');
        const {page_size,cursor}=options.query;
        if((page_size!==undefined&&(!Number.isInteger(page_size)||page_size<1||page_size>100))
          ||(cursor!==undefined&&(!cursor.length||cursor.length>1024)))return fail('INVALID_REQUEST');
        const q=new URLSearchParams();
        if(page_size!==undefined)q.set('page_size',String(page_size));
        if(cursor!==undefined)q.set('cursor',cursor);
        if(q.size)path+='?'+q;
      }
      if(options.signal?.aborted)return fail('CANCELLED');
      sent=!!config.request;
      const response=await fetcher(path,{method:config.method,headers,credentials:'same-origin',redirect:'error',cache:'no-store',
        ...(body===undefined?{}:{body}),...(options.signal?{signal:options.signal}:{})});
      const outcome=sent?'unknown':'not-sent';
      if(response.redirected||!/^application\/json(?:\s*;.*)?$/i.test(response.headers.get('Content-Type')??''))return fail('INVALID_RESPONSE',response.status,outcome);
      const bytes=await response.arrayBuffer();
      if(bytes.byteLength>1048576)return fail('INVALID_RESPONSE',response.status,outcome);
      const value=parseJson(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
      if(!isJsonTree(value))return fail('INVALID_RESPONSE',response.status,outcome);
      if(response.status===200){
        if(checks[config.response]?.(value)!==true)return fail('INVALID_RESPONSE',200,outcome);
        return {ok:true,value:value as Contracts[K]};
      }
      const schemas:Record<number,string>={400:'BadRequestError',401:'AuthenticationError',403:'ForbiddenError',404:'NotFoundError',409:'ConflictEnvelope',429:'RateLimitError',503:'UnavailableError'};
      const schema=schemas[response.status];
      if(!schema||checks[schema]?.(value)!==true)return fail('INVALID_RESPONSE',response.status,outcome);
      return fail((value as {error:{code:string}}).error.code,response.status,sent&&response.status===503?'unknown':'rejected');
    }catch{return fail(options.signal?.aborted?'CANCELLED':'NETWORK_ERROR',null,sent?'unknown':'not-sent');}
  }};
}
