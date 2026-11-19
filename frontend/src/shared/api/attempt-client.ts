import {attemptOperations,type AttemptContracts} from './generated/attempt-contracts';
import * as validators from './generated/attempt-validators.mjs';
import {createApiClient} from './client';
import {isJsonTree,parseJson} from './json-boundary';

export type AttemptOperation=keyof AttemptContracts;
export type Attempt=AttemptContracts['get_attempt']['response']['data'];
export const attemptPollDelaysMs=[1000,2000,4000] as const;
type Options<K extends AttemptOperation>={signal?:AbortSignal}
  & (K extends 'create_attempt'|'list_attempts'?{id?:never}:{id:string})
  & (AttemptContracts[K]['request'] extends never?{body?:never}:{body:AttemptContracts[K]['request']})
  & (typeof attemptOperations[K]['receipt'] extends true?{idempotencyKey:string}:{idempotencyKey?:never})
  & (K extends 'list_attempts'?{query?:{cursor?:string;page_size?:number}}:{query?:never});
export type AttemptResult<T>={ok:true;value:T;pending:boolean}|{ok:false;status:number|null;
  outcome:'not-sent'|'rejected'|'unknown';code:string;currentRevision?:number;reloadUrl?:string};
type Fetcher=(input:RequestInfo|URL,init?:RequestInit)=>Promise<Response>;
const uuid=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/** No automatic mutation retries. Retain the same key and raw draft on unknown outcome. */
export function createAttemptClient(fetcher:Fetcher=globalThis.fetch.bind(globalThis)){
  const identity=createApiClient(fetcher);
  return {async call<K extends AttemptOperation>(operation:K,options:Options<K>):Promise<AttemptResult<AttemptContracts[K]['response']>>{
    let sent=false;
    const fail=(code:string,status:number|null=null,outcome:'not-sent'|'rejected'|'unknown'='not-sent')=>
      ({ok:false as const,status,outcome,code});
    if(!Object.hasOwn(attemptOperations,operation)||!options)return fail('INVALID_REQUEST');
    const config=attemptOperations[operation];
    let path:string=config.path;
    if(path.includes('{id}')){
      if(!options.id||!uuid.test(options.id))return fail('INVALID_REQUEST');
      path=path.replace('{id}',options.id.toLowerCase());
    }
    const validate=validators as Record<string,(value:unknown)=>boolean>;
    if(config.request&&(!isJsonTree(options.body)||validate[config.request]?.(options.body)!==true))return fail('INVALID_REQUEST');
    if(!config.request&&options.body!==undefined)return fail('INVALID_REQUEST');
    if(config.receipt&&(!options.idempotencyKey||options.idempotencyKey.length>256||/[\r\n\0]/.test(options.idempotencyKey)))return fail('INVALID_REQUEST');
    if(!config.receipt&&options.idempotencyKey!==undefined)return fail('INVALID_REQUEST');
    if(options.query){
      const {cursor,page_size}=options.query;
      if(operation!=='list_attempts'||Object.keys(options.query).some(k=>k!=='cursor'&&k!=='page_size')
        ||(cursor!==undefined&&(!cursor.length||cursor.length>1024))
        ||(page_size!==undefined&&(!Number.isInteger(page_size)||page_size<1||page_size>100)))return fail('INVALID_REQUEST');
      const query=new URLSearchParams();
      if(cursor!==undefined)query.set('cursor',cursor);
      if(page_size!==undefined)query.set('page_size',String(page_size));
      if(query.size)path+='?'+query;
    }
    const mutation=config.method!=='GET';
    try{
      const body=config.request?JSON.stringify(options.body):undefined;
      if(body&&new TextEncoder().encode(body).length>65536)return fail('LIMIT_EXCEEDED');
      const headers:Record<string,string>={Accept:'application/json'};
      if(mutation){
        const csrf=await identity.call('get_csrf',options.signal?{signal:options.signal}:{});
        if(!csrf.ok)return fail(csrf.error.code,csrf.error.status);
        headers['X-CSRFToken']=csrf.value.data.csrf_token;
        headers['Content-Type']='application/json';
      }
      if(options.signal?.aborted)return fail('CANCELLED');
      if(config.receipt)headers['Idempotency-Key']=options.idempotencyKey!;
      sent=mutation;
      const response=await fetcher(path,{method:config.method,credentials:'same-origin',cache:'no-store',
        redirect:'error',headers,...(body===undefined?{}:{body}),...(options.signal?{signal:options.signal}:{})});
      const outcome=mutation?'unknown':'not-sent';
      if(response.redirected||!/^application\/json(?:\s*;.*)?$/i.test(response.headers.get('Content-Type')??''))return fail('INVALID_RESPONSE',response.status,outcome);
      const bytes=await response.arrayBuffer();
      if(bytes.byteLength>1048576)return fail('INVALID_RESPONSE',response.status,outcome);
      const value=parseJson(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
      if(!isJsonTree(value))return fail('INVALID_RESPONSE',response.status,outcome);
      if(response.ok){
        const expected=operation==='create_attempt'?201:operation==='submit_attempt'?202:200;
        const schema=response.status===202?'PendingAttemptResponse':config.response;
        if(response.status!==expected||validate[schema]?.(value)!==true||(value as {meta:{version?:string}}).meta.version!=='http-v1')return fail('INVALID_RESPONSE',response.status,outcome);
        const data=(value as {data?:{state?:string}}).data;
        return {ok:true,value:value as AttemptContracts[K]['response'],pending:response.status===202||data?.state==='SUBMITTED'};
      }
      const errors:Record<number,string>={400:'BadRequestError',401:'AuthenticationError',403:'ForbiddenError',404:'NotFoundError',
        409:'ConflictEnvelope',429:'RateLimitError',503:'UnavailableError'};
      const errorSchema=errors[response.status];
      if(!errorSchema||validate[errorSchema]?.(value)!==true)return fail('INVALID_RESPONSE',response.status,outcome);
      const error=(value as {error:{code:string;current_revision?:number;reload_url?:string}}).error;
      const result=fail(error.code,response.status,response.status===503&&mutation?'unknown':'rejected');
      return error.code==='REVISION_CONFLICT'&&error.current_revision!==undefined&&error.reload_url!==undefined
        ?{...result,currentRevision:error.current_revision,reloadUrl:error.reload_url}:result;
    }catch{return fail(options.signal?.aborted?'CANCELLED':'NETWORK_ERROR',null,sent?'unknown':'not-sent');}
  }};
}

/** Memory-only recovery handoff; never discard raw input or replace the submit key. */
export type AttemptRecovery={attemptId:string;draft:Attempt['draft'];confirmedRevision:number;operationKey:string;
  state:'ready'|'pending'|'unknown'|'conflict'|'unauthorized'};
