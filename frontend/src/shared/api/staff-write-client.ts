import {createApiClient,type ApiResult} from './client';
import {parseJson} from './json-boundary';
import {createStaffClient,staffOperations,staffWriteOperations,stringifyExact,validateStaff} from './staff-client';

// Preserve the read adapter's closed interface and exact numeric handling.
// Mutations have a separate explicit caller; no request is retried automatically.
export function createStaffWriteClient(fetcher:typeof fetch=globalThis.fetch.bind(globalThis)){
 const reads=createStaffClient(fetcher),identity=createApiClient(fetcher);
 async function call(operation:string,options:{id?:string;query?:Record<string,string|string[]>;body?:unknown;signal?:AbortSignal}={}):Promise<ApiResult<any>>{
  if(staffOperations.some(op=>op.operationId===operation))return reads.call(operation,options);
  const op=staffWriteOperations.find(op=>op.operationId===operation);
  const mutation=op?.method!=='GET';let sent=false;
  const fail=(code:'INVALID_REQUEST'|'INVALID_RESPONSE'|'NETWORK_ERROR',outcome:'not-sent'|'unknown'='not-sent'):ApiResult<never>=>({ok:false,error:{code,message:code==='INVALID_REQUEST'?'Проверьте введённые данные.':'Не удалось подтвердить ответ сервера.',status:null,outcome,retryable:false}});
  if(!op||!options||typeof options!=='object'||Array.isArray(options)||Object.entries(Object.getOwnPropertyDescriptors(options)).some(([k,d])=>!['id','query','body','signal'].includes(k)||!('value'in d)))return fail('INVALID_REQUEST');
  if(options.signal!==undefined&&!(options.signal instanceof AbortSignal))return fail('INVALID_REQUEST');
  let path=op.path as string,body:string|undefined;
  if(path.includes('{id}')){
   if(typeof options.id!=='string'||! /^[1-9]\d*$/.test(options.id)||BigInt(options.id)>9223372036854775807n)return fail('INVALID_REQUEST');
   path=path.replace('{id}',options.id);
  }else if(options.id!==undefined)return fail('INVALID_REQUEST');
  if(options.query!==undefined){
   if(!options.query||typeof options.query!=='object'||Array.isArray(options.query))return fail('INVALID_REQUEST');
   const params=new URLSearchParams();
   for(const[k,d]of Object.entries(Object.getOwnPropertyDescriptors(options.query))){
    if(!('value'in d))return fail('INVALID_REQUEST');
    const rule=op.parameters?.find((p:any)=>p.in==='query'&&p.name===k)?.schema;
    if(!rule)return fail('INVALID_REQUEST');
    const values=Array.isArray(d.value)?d.value:[d.value];
    if(values.some(v=>typeof v!=='string'||! /^[1-9]\d*$/.test(v)))return fail('INVALID_REQUEST');
    const decoded=rule.type==='array'?values.map(v=>BigInt(v)):d.value;
    if(!validateStaff(decoded,rule))return fail('INVALID_REQUEST');
    for(const v of values)params.append(k,v);
   }
   if(params.size)path+='?'+params;
  }
  try{
   if(op.requestBody){
    if(!safeTree(options.body)||!validateStaff(options.body,op.requestBody.content['application/json'].schema))return fail('INVALID_REQUEST');
    body=stringifyExact(options.body);
    if(new TextEncoder().encode(body).length>65536)return fail('INVALID_REQUEST');
   }else if(options.body!==undefined)return fail('INVALID_REQUEST');
   const headers:Record<string,string>={Accept:'application/json'};
   if(mutation){
    const csrf=await identity.call('get_csrf',options.signal?{signal:options.signal}:{});
    if(!csrf.ok)return csrf;
    headers['X-CSRFToken']=csrf.value.data.csrf_token;
   }
   if(options.signal?.aborted)return fail('NETWORK_ERROR');
   if(body!==undefined)headers['Content-Type']='application/json';
   sent=true;
   const response=await fetcher(path,{method:op.method,credentials:'same-origin',cache:'no-store',redirect:'error',headers,...(body===undefined?{}:{body}),...(options.signal?{signal:options.signal}:{})});
   const outcome=(): 'not-sent'|'unknown'=>mutation&&sent?'unknown':'not-sent';
   const rule=op.responses[response.status]?.content?.['application/json']?.schema;
   if(response.redirected||!rule||!/(?:^|,)\s*no-store\s*(?:,|$)/i.test(response.headers.get('Cache-Control')??'')||!/^application\/json(?:\s*;\s*charset\s*=\s*"?utf-8"?)?\s*$/i.test(response.headers.get('Content-Type')??''))return fail('INVALID_RESPONSE',outcome());
   const value:any=parseJson(new TextDecoder('utf-8',{fatal:true}).decode(await response.arrayBuffer()),true);
   if(!validateStaff(value,rule))return fail('INVALID_RESPONSE',outcome());
   if(response.status<400){if(value.meta?.version!=='migration-r02-v1')return fail('INVALID_RESPONSE',outcome());return {ok:true,value};}
   const error=value.error;
   if(error.retryable!==(response.status===429||response.status===503)||response.status===429&&!/^[1-9]\d*$/.test(response.headers.get('Retry-After')??''))return fail('INVALID_RESPONSE',outcome());
   const messages:Record<string,string>={AUTHENTICATION_REQUIRED:'Войдите в аккаунт.',FORBIDDEN:'Действие недоступно.',NOT_FOUND:'Запись не найдена.',CSRF_FAILED:'Не удалось подтвердить безопасность запроса.',STATE_CONFLICT:'Состояние изменилось. Загрузите запись ещё раз.',RATE_LIMITED:'Слишком много запросов. Подождите.',SERVICE_UNAVAILABLE:'Сервис временно недоступен.',INVALID_REQUEST:'Проверьте введённые данные.'};
   return {ok:false,error:{code:error.code,message:messages[error.code]??'Операция не выполнена.',status:response.status,outcome:mutation&&response.status>=500?'unknown':'rejected',retryable:error.retryable}};
  }catch{return fail('NETWORK_ERROR',mutation&&sent?'unknown':'not-sent');}
  finally{body=undefined;}
 }
 return {call};
}

function safeTree(value:unknown,seen=new Set<object>(),depth=0):boolean{
 if(depth>64)return false;
 if(value===null||typeof value==='string'||typeof value==='boolean'||typeof value==='bigint')return true;
 if(typeof value==='number')return Number.isFinite(value)&&(!Number.isInteger(value)||Number.isSafeInteger(value));
 if(typeof value!=='object'||seen.has(value))return false;
 if(!Array.isArray(value)&&Object.getPrototypeOf(value)!==Object.prototype&&Object.getPrototypeOf(value)!==null)return false;
 seen.add(value);
 if(Reflect.ownKeys(value).some(k=>typeof k!=='string'))return false;
 const descriptors=Object.getOwnPropertyDescriptors(value);
 if(Array.isArray(value)&&(Object.keys(descriptors).length!==value.length+1||Array.from({length:value.length},(_,i)=>i).some(i=>!Object.hasOwn(descriptors,String(i)))))return false;
 for(const[k,d]of Object.entries(descriptors)){if(Array.isArray(value)&&k==='length')continue;if(!('value'in d)||!d.enumerable||!safeTree(d.value,seen,depth+1))return false;}
 seen.delete(value);return true;
}
