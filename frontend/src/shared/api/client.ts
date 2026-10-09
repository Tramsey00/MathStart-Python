import { identityOperations } from "./generated/identity-operations";
import type { IdentityContracts } from "./generated/identity-contracts";
import { isJsonTree, parseJson } from "./json-boundary";
export type Operation = keyof IdentityContracts;
type Contracts<K extends Operation> = IdentityContracts[K];
type CommonOptions = { signal?:AbortSignal; timeoutMs?:number };
export type RequestOptions<K extends Operation> = CommonOptions
  & (Contracts<K>["request"] extends never ? {body?:never} : {body:Contracts<K>["request"]})
  & (typeof identityOperations[K]["receipt"] extends true ? {idempotencyKey:string} : {idempotencyKey?:never})
  & (K extends "list_grades" ? {query?:{cursor?:string;page_size?:number}} : {query?:never});
export type ErrorCode = "INVALID_REQUEST"|"LIMIT_EXCEEDED"|"AUTHENTICATION_REQUIRED"|"CSRF_FAILED"|"FORBIDDEN"|"NOT_FOUND"
  |"REVISION_CONFLICT"|"IDEMPOTENCY_CONFLICT"|"VERSION_CONFLICT"|"STATE_CONFLICT"|"RATE_LIMITED"|"SERVICE_UNAVAILABLE"
  |"INVALID_RESPONSE"|"NETWORK_ERROR"|"CANCELLED";
export type Outcome = "not-sent"|"rejected"|"unknown";
export interface ApiError {
  code:ErrorCode; message:string; status:number|null; outcome:Outcome;
  // retryable is advisory only. This client never retries or replays a mutation.
  retryable:boolean; requestId?:string; retryAfterSeconds?:number;
}
export type ApiResult<T> = {ok:true;value:T}|{ok:false;error:ApiError};
const messages:Record<ErrorCode,string>={
  INVALID_REQUEST:"Проверьте введённые данные.", LIMIT_EXCEEDED:"Превышен допустимый объём данных.",
  AUTHENTICATION_REQUIRED:"Войдите в аккаунт.", CSRF_FAILED:"Не удалось подтвердить безопасность запроса.",
  FORBIDDEN:"Действие недоступно.", NOT_FOUND:"Данные не найдены.",
  REVISION_CONFLICT:"Данные изменились. Обновите состояние.", IDEMPOTENCY_CONFLICT:"Запрос конфликтует с предыдущим.",
  VERSION_CONFLICT:"Версия данных изменилась.", STATE_CONFLICT:"Состояние изменилось. Обновите данные.",
  RATE_LIMITED:"Слишком много запросов. Подождите перед повтором.", SERVICE_UNAVAILABLE:"Сервис временно недоступен.",
  INVALID_RESPONSE:"Не удалось подтвердить ответ сервера.", NETWORK_ERROR:"Не удалось подтвердить результат запроса.",
  CANCELLED:"Запрос отменён."
};
const error=(code:ErrorCode,status:number|null,outcome:Outcome,retryable=false):ApiResult<never> =>
  ({ok:false,error:{code,message:messages[code],status,outcome,retryable}});
type WireError={error:{code:ErrorCode;request_id:string;retryable:boolean;field_errors:Record<string,unknown>}};
type Fetcher=(input:RequestInfo|URL,init?:RequestInit)=>Promise<Response>;

export function createApiClient(fetcher:Fetcher = globalThis.fetch.bind(globalThis)) {
  async function call<K extends Operation>(operation:K,options:RequestOptions<K>):Promise<ApiResult<Contracts<K>["response"]>> {
    const config=identityOperations[operation];
    if (!Object.hasOwn(identityOperations,operation) || !config) return error("INVALID_REQUEST",null,"not-sent");
    if (!options || typeof options!=="object" || Object.entries(Object.getOwnPropertyDescriptors(options)).some(([k,d])=>!["body","query","signal","timeoutMs","idempotencyKey"].includes(k)||!("value" in d))) return error("INVALID_REQUEST",null,"not-sent");
    if(options.signal!==undefined && !(options.signal instanceof AbortSignal))return error("INVALID_REQUEST",null,"not-sent");
    const idempotencyKey=options.idempotencyKey;
    const mutation=config.method!=="GET"; let sent=false;
    let body:string|undefined;
    // Validate the body before serializing: JSON.stringify must never silently coerce.
    if (config.request) {
      if (!isJsonTree(options.body) || !config.request(options.body)) return error("INVALID_REQUEST",null,"not-sent");
      body=JSON.stringify(options.body);
      if(new TextEncoder().encode(body).length>65536) return error("LIMIT_EXCEEDED",null,"not-sent");
    } else if (options.body!==undefined) return error("INVALID_REQUEST",null,"not-sent");
    if (config.receipt && (typeof options.idempotencyKey!=="string" || !options.idempotencyKey.length
      || /[\r\n]/.test(options.idempotencyKey))) return error("INVALID_REQUEST",null,"not-sent");
    if (!config.receipt && options.idempotencyKey!==undefined) return error("INVALID_REQUEST",null,"not-sent");
    let path:string=config.path;
    if (options.query!==undefined) {
      if(operation!=="list_grades" || !isJsonTree(options.query)
        || Object.keys(options.query).some(k=>k!=="cursor"&&k!=="page_size")) return error("INVALID_REQUEST",null,"not-sent");
      const {cursor,page_size}=options.query;
      if ((cursor!==undefined&&(typeof cursor!=="string"||!cursor.length||cursor.length>1024))
        || (page_size!==undefined&&(!Number.isInteger(page_size)||page_size<1||page_size>100))) return error("INVALID_REQUEST",null,"not-sent");
      const q=new URLSearchParams();
      if(cursor!==undefined)q.set("cursor",cursor);
      if(page_size!==undefined)q.set("page_size",String(page_size));
      if(q.size)path+="?"+q.toString();
    }
    if (options.timeoutMs!==undefined&&(!Number.isFinite(options.timeoutMs)||options.timeoutMs<=0))
      return error("INVALID_REQUEST",null,"not-sent");
    const controller=new AbortController();
    const abort=()=>controller.abort();
    if(options.signal?.aborted)controller.abort(); else options.signal?.addEventListener("abort",abort,{once:true});
    const timer=options.timeoutMs===undefined?undefined:setTimeout(abort,options.timeoutMs);
    const outcome=():Outcome=>mutation&&sent?"unknown":"not-sent";
    async function exchange(op:Operation,url:string,requestBody?:string,csrf?:string):Promise<ApiResult<unknown>> {
      if(controller.signal.aborted)return error("CANCELLED",null,outcome());
      const cfg=identityOperations[op]; const headers:Record<string,string>={Accept:"application/json"};
      if(requestBody!==undefined)headers["Content-Type"]="application/json";
      if(csrf!==undefined)headers["X-CSRFToken"]=csrf;
      if(cfg.receipt)headers["Idempotency-Key"]=idempotencyKey!;
      if(cfg.method!=="GET")sent=true;
      const response=await fetcher(url,{method:cfg.method,headers,credentials:"same-origin",cache:"no-store",
        redirect:"error",signal:controller.signal,...(requestBody===undefined?{}:{body:requestBody})});
      if(controller.signal.aborted)return error("CANCELLED",null,outcome());
      const validate=(cfg.responses as Record<number,((value:unknown)=>boolean)>)[response.status];
      if(response.redirected || !validate || !/^application\/json(?:\s*;\s*charset\s*=\s*"?utf-8"?)?\s*$/i.test(response.headers.get("Content-Type")??""))
        return error("INVALID_RESPONSE",response.status,outcome());
      let value:unknown;
      try {
        const bytes=await response.arrayBuffer();
        if(controller.signal.aborted)return error("CANCELLED",null,outcome());
        value=parseJson(new TextDecoder("utf-8",{fatal:true}).decode(bytes));
        if(!isJsonTree(value)||!validate(value))return error("INVALID_RESPONSE",response.status,outcome());
      } catch {return controller.signal.aborted
        ? error("CANCELLED",null,outcome())
        : error("INVALID_RESPONSE",response.status,outcome());}
      if(response.status===cfg.success) {
        const meta=(value as {meta:{version?:string}}).meta;
        if(meta.version!=="http-v1")return error("INVALID_RESPONSE",response.status,outcome());
        return {ok:true,value};
      }
      const wire=(value as WireError).error;
      if(Object.keys(wire.field_errors).length!==0)return error("INVALID_RESPONSE",response.status,outcome());
      if(wire.retryable !== (response.status===429 || response.status===503))return error("INVALID_RESPONSE",response.status,outcome());
      let retryAfter:number|undefined;
      const header=response.headers.get("Retry-After");
      if(response.status===429 || header!==null) {
        if(!header||!/^[1-9]\d*$/.test(header)||!Number.isSafeInteger(Number(header)))return error("INVALID_RESPONSE",response.status,outcome());
        retryAfter=Number(header);
      }
      const result=error(wire.code,response.status,mutation&&sent&&(response.status===409||response.status>=500)?"unknown":"rejected",wire.retryable);
      if(!result.ok) {
        result.error.requestId=wire.request_id;
        if(retryAfter!==undefined)result.error.retryAfterSeconds=retryAfter;
      }
      return result;
    }
    try {
      if(mutation) {
        // A fresh bootstrap on every explicit attempt; never store or log the token.
        const csrf=await exchange("get_csrf",identityOperations.get_csrf.path);
        if(!csrf.ok)return {...csrf,error:{...csrf.error,outcome:"not-sent"}};
        const token=(csrf.value as IdentityContracts["get_csrf"]["response"]).data.csrf_token;
        return await exchange(operation,path,body,token) as ApiResult<Contracts<K>["response"]>;
      }
      return await exchange(operation,path) as ApiResult<Contracts<K>["response"]>;
    } catch {
      return error(controller.signal.aborted?"CANCELLED":"NETWORK_ERROR",null,outcome());
    } finally {
      if(timer!==undefined)clearTimeout(timer);
      options.signal?.removeEventListener("abort",abort);
      body=undefined; // No retained password, pending body or receipt registry in the transport.
    }
  }
  return {call};
}
