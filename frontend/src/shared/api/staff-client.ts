import contracts from './generated/staff-contracts.json';
import {parseJson} from './json-boundary';
import {createApiClient,type ApiResult} from './client';
type Schema=Record<string,any>;
const schema=contracts.schema as Schema;
const errors=contracts.errors as Schema;
export const staffOperations=contracts.operations as Schema[];
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
 const identity=createApiClient(fetcher);
 async function call(operation:string,options:{id?:string;query?:Record<string,string|string[]>;body?:any;signal?:AbortSignal}={}):Promise<ApiResult<any>>{
  const op=staffOperations.find(op=>op.operationId===operation);
  const invalid=():ApiResult<never>=>({ok:false,error:{code:'INVALID_RESPONSE',message:'Не удалось подтвердить ответ сервера.',status:null,outcome:op?.method==='GET'?'not-sent':'unknown',retryable:false}});
  if(!op)return invalid();
  let path=op.path as string;
  if(path.includes('{id}')){if(!options.id||!/^\d+$/.test(options.id))return invalid();path=path.replace('{id}',options.id);}
  if(options.query){const params=new URLSearchParams();for(const[k,v]of Object.entries(options.query)){for(const item of Array.isArray(v)?v:[v])params.append(k,item);}if(params.size)path+='?'+params;}
  let body:string|undefined;
  if(op.requestBody){if(!validateStaff(options.body,op.requestBody.content['application/json'].schema))return {ok:false,error:{code:'INVALID_REQUEST',message:'Проверьте введённые данные.',status:null,outcome:'not-sent',retryable:false}};body=stringifyExact(options.body);}
  const headers:Record<string,string>={Accept:'application/json'};
  if(op.method!=='GET'){
   const csrf=await identity.call('get_csrf',options.signal?{signal:options.signal}:{});
   if(!csrf.ok)return csrf;headers['X-CSRFToken']=csrf.value.data.csrf_token;
  }
  if(body!==undefined)headers['Content-Type']='application/json';
  try{
   const response=await fetcher(path,{method:op.method,credentials:'same-origin',cache:'no-store',redirect:'error',headers,...(body===undefined?{}:{body}),...(options.signal?{signal:options.signal}:{})});
   const rule=op.responses[response.status]?.content?.['application/json']?.schema;
   if(response.redirected||!rule||!/^application\/json(?:\s*;\s*charset\s*=\s*"?utf-8"?)?\s*$/i.test(response.headers.get('Content-Type')??''))return invalid();
   const value=parseJson(new TextDecoder('utf-8',{fatal:true}).decode(await response.arrayBuffer()),true);
   if(!validateStaff(value,rule))return invalid();
   if(response.status<400){if((value as any).meta?.version!=='http-v1')return invalid();return {ok:true,value};}
   const error=(value as any).error;
   const messages:Record<string,string>={AUTHENTICATION_REQUIRED:'Войдите в аккаунт.',FORBIDDEN:'Действие недоступно.',NOT_FOUND:'Запись не найдена.',CSRF_FAILED:'Не удалось подтвердить безопасность запроса.',STATE_CONFLICT:'Состояние изменилось. Загрузите запись ещё раз.',RATE_LIMITED:'Слишком много запросов. Подождите.',SERVICE_UNAVAILABLE:'Сервис временно недоступен.',INVALID_REQUEST:'Проверьте введённые данные.'};
   if(error.retryable!==(response.status===429||response.status===503))return invalid();
   if(response.status===429&&!/^[1-9]\d*$/.test(response.headers.get('Retry-After')??''))return invalid();
   return {ok:false,error:{code:error.code,message:messages[error.code]??'Операция не выполнена.',status:response.status,outcome:op.method!=='GET'&&(response.status===409||response.status>=500)?'unknown':'rejected',retryable:error.retryable}};
  }catch{return invalid();}finally{body=undefined;}
 }
 return {call};
}
