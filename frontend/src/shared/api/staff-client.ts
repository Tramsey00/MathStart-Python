import contracts from './generated/staff-contracts.json';
import {parseJson} from './json-boundary';
import type {ApiResult} from './client';
type Schema=Record<string,any>;
const schema=contracts.schema as Schema;
const errors=contracts.errors as Schema;
export const staffWriteOperations=contracts.operations as Schema[];
export const staffOperations=staffWriteOperations.filter(op=>op.method==='GET'&&/^(?:staff_(?:list|get|history)_|get_page_publication_state$)/.test(op.operationId));
export function stringifyExact(value:any):string {
 if(typeof value==='bigint')return value.toString();
 if(value===null||typeof value!=='object')return JSON.stringify(value);
 if(Array.isArray(value))return '['+value.map(stringifyExact).join(',')+']';
 return '{'+Object.entries(value).map(([k,v])=>JSON.stringify(k)+':'+stringifyExact(v)).join(',')+'}';
}
const bound=(value:any)=>typeof value==='string'&&value.startsWith('int64:')?BigInt(value.slice(6)):value;
export function validateStaff(value:any,rule:Schema,errorScope=false,depth=0):boolean {
 if(depth>64)return false;
 if(rule.$ref){const name=rule.$ref.split('/').at(-1);const external=rule.$ref.includes('dto-v1.schema');const defs=external||errorScope?errors:schema.$defs;return !!defs[name]&&validateStaff(value,defs[name],external||errorScope,depth+1);}
 const check=(r:Schema)=>validateStaff(value,r,errorScope,depth+1);
 if(rule.allOf&&!rule.allOf.every(check)||rule.anyOf&&!rule.anyOf.some(check)||rule.not&&check(rule.not))return false;
 if(rule.if){if(check(rule.if)){if(rule.then&&!check(rule.then))return false;}else if(rule.else&&!check(rule.else))return false;}
 if('const'in rule&&value!==rule.const||rule.enum&&!rule.enum.includes(value))return false;
 const type=(name:string)=>name==='null'?value===null:name==='integer'?typeof value==='bigint'||typeof value==='number'&&Number.isSafeInteger(value):name==='number'?typeof value==='number'&&Number.isFinite(value):name==='array'?Array.isArray(value):name==='object'?value!==null&&typeof value==='object'&&!Array.isArray(value):typeof value===name;
 if(rule.type&&!(Array.isArray(rule.type)?rule.type.some(type):type(rule.type)))return false;
 if(typeof value==='number'||typeof value==='bigint'){if('minimum'in rule&&value<bound(rule.minimum)||'maximum'in rule&&value>bound(rule.maximum))return false;}
 if(typeof value==='string'){
  const length=Array.from(value).length;if('minLength'in rule&&length<rule.minLength||'maxLength'in rule&&length>rule.maxLength||rule.pattern&&!new RegExp(rule.pattern,'u').test(value))return false;
  if(rule.format==='date-time'&&!Number.isFinite(Date.parse(value)))return false;
  if(rule.format==='uuid'&&!/^(?:urn:uuid:)?[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i.test(value))return false;
 }
 if(Array.isArray(value)){if(rule.minItems&&value.length<rule.minItems||rule.maxItems&&value.length>rule.maxItems)return false;if(rule.uniqueItems&&new Set(value.map(stringifyExact)).size!==value.length)return false;if(rule.items&&!value.every(v=>validateStaff(v,rule.items,errorScope,depth+1)))return false;}
 if(value!==null&&typeof value==='object'&&!Array.isArray(value)){
  if(rule.required?.some((key:string)=>!Object.hasOwn(value,key)))return false;
  for(const[key,v]of Object.entries(value)){if(rule.properties?.[key]){if(!validateStaff(v,rule.properties[key],errorScope,depth+1))return false;}else if(rule.additionalProperties===false)return false;}
 }
 return true;
}
export function staffDefinition(name:string){return schema.$defs[name] as Schema;}
export function createStaffClient(fetcher:typeof fetch=globalThis.fetch.bind(globalThis)){

 async function call(operation:string,options:{id?:string;query?:Record<string,string|string[]>;signal?:AbortSignal}={}):Promise<ApiResult<any>>{
  const op=staffOperations.find(op=>op.operationId===operation);
  const invalidRequest=():ApiResult<never>=>({ok:false,error:{code:'INVALID_REQUEST',message:'Проверьте введённые данные.',status:null,outcome:'not-sent',retryable:false}});
  const invalid=():ApiResult<never>=>({ok:false,error:{code:'INVALID_RESPONSE',message:'Не удалось подтвердить ответ сервера.',status:null,outcome:'not-sent',retryable:false}});
  if(!op||op.method!=='GET'||!options||typeof options!=='object'||Array.isArray(options))return invalidRequest();
  if(Object.entries(Object.getOwnPropertyDescriptors(options)).some(([key,d])=>!['id','query','signal'].includes(key)||!('value'in d)))return invalidRequest();
  if(options.signal!==undefined&&!(options.signal instanceof AbortSignal))return invalidRequest();
  let path=op.path as string;
  if(path.includes('{id}')){if(typeof options.id!=='string'||! /^[1-9]\d*$/.test(options.id)||BigInt(options.id)>9223372036854775807n)return invalidRequest();path=path.replace('{id}',options.id);}
  else if(options.id!==undefined)return invalidRequest();
  if(options.query!==undefined){
   if(!options.query||typeof options.query!=='object'||Array.isArray(options.query))return invalidRequest();
   const params=new URLSearchParams();
   for(const[k,d]of Object.entries(Object.getOwnPropertyDescriptors(options.query))){
    if(!('value'in d)||typeof d.value!=='string')return invalidRequest();const v=d.value;
    const rule=k==='sort'?op['x-sort-contract']?.query_schema:op.parameters?.find((p:Schema)=>p.in==='query'&&p.name===k)?.schema;
    if(!rule)return invalidRequest();
    const decoded=rule.type==='boolean'?(v==='true'?true:v==='false'?false:undefined):rule.type==='integer'?(/^\d+$/.test(v)?BigInt(v):undefined):v;
    if(!validateStaff(decoded,rule))return invalidRequest();params.append(k,v);
   }
   if(params.size)path+='?'+params;
  }
  const headers:Record<string,string>={Accept:'application/json'};
  try{
   const response=await fetcher(path,{method:'GET',credentials:'same-origin',cache:'no-store',redirect:'error',headers,...(options.signal?{signal:options.signal}:{})});
   const rule=op.responses[response.status]?.content?.['application/json']?.schema;
   if(response.redirected||!rule||!/(?:^|,)\s*(?:private\s*,\s*)?no-store\s*(?:,|$)/i.test(response.headers.get('Cache-Control')??'')||!/^application\/json(?:\s*;\s*charset\s*=\s*"?utf-8"?)?\s*$/i.test(response.headers.get('Content-Type')??''))return invalid();
   const value=parseJson(new TextDecoder('utf-8',{fatal:true}).decode(await response.arrayBuffer()),true);
   if(!validateStaff(value,rule))return invalid();
   if(response.status<400){if((value as any).meta?.version!=='migration-r02-v1')return invalid();return {ok:true,value};}
   const error=(value as any).error;
   const messages:Record<string,string>={AUTHENTICATION_REQUIRED:'Войдите в аккаунт.',FORBIDDEN:'Действие недоступно.',NOT_FOUND:'Запись не найдена.',CSRF_FAILED:'Не удалось подтвердить безопасность запроса.',STATE_CONFLICT:'Состояние изменилось. Загрузите запись ещё раз.',RATE_LIMITED:'Слишком много запросов. Подождите.',SERVICE_UNAVAILABLE:'Сервис временно недоступен.',INVALID_REQUEST:'Проверьте введённые данные.'};
   if(error.retryable!==(response.status===429||response.status===503))return invalid();
   if(response.status===429&&!/^[1-9]\d*$/.test(response.headers.get('Retry-After')??''))return invalid();
   return {ok:false,error:{code:error.code,message:messages[error.code]??'Операция не выполнена.',status:response.status,outcome:op.method!=='GET'&&(response.status===409||response.status>=500)?'unknown':'rejected',retryable:error.retryable}};
  }catch{return invalid();}
 }
 return {call};
}
