// @vitest-environment node
import {it,expect,vi} from "vitest";
import {createApiClient} from "../src/shared/api/client";
import {RequestScope} from "../src/shared/api/request-scope";
import {parseJson,isJsonTree} from "../src/shared/api/json-boundary";
const id="12345678-1234-4234-8234-123456789abc";
const meta={request_id:id,version:"http-v1"};
const user={data:{id:1,username:"synthetic",selected_grade_id:null,onboarding_mode:null,onboarding_complete:false},meta};
const csrf={data:{csrf_token:"synthetic-csrf"},meta};
const json=(value:unknown,status=200,headers:Record<string,string>={})=>new Response(JSON.stringify(value),{status,headers:{"Content-Type":"application/json",...headers}});
const failure=(code:string,retryable=false)=>({error:{code,message:"PRIVATE server details <script>secret</script>",field_errors:{},retryable,request_id:id}});
const login={body:{username:"synthetic",password:"TEST_PASSWORD_CANARY_DO_NOT_SHIP"}};
it("uses relative canonical paths, same-origin cookies, no-store, fresh CSRF and one mutation only",async()=>{
  const fetch=vi.fn().mockResolvedValueOnce(json(csrf)).mockResolvedValueOnce(json(user));
  const result=await createApiClient(fetch).call("login",login);
  expect(result).toEqual({ok:true,value:user});
  expect(fetch).toHaveBeenCalledTimes(2);
  expect(fetch.mock.calls[0]?.[0]).toBe("/api/v1/auth/csrf/");
  const [url,init]=fetch.mock.calls[1]!;
  expect(url).toBe("/api/v1/auth/login/");
  expect(init).toMatchObject({method:"POST",credentials:"same-origin",cache:"no-store",redirect:"error",body:JSON.stringify(login.body)});
  expect(init.headers).toMatchObject({"X-CSRFToken":"synthetic-csrf","Content-Type":"application/json"});
});
it("refreshes CSRF on explicit receipt retry while keeping supplied key/body",async()=>{
  const fetch=vi.fn().mockResolvedValueOnce(json(csrf)).mockResolvedValueOnce(json(failure("SERVICE_UNAVAILABLE",true),503))
    .mockResolvedValueOnce(json({...csrf,data:{csrf_token:"new-synthetic"}})).mockResolvedValueOnce(json(user,201));
  const client=createApiClient(fetch),options={body:login.body,idempotencyKey:"synthetic-receipt"};
  const first=await client.call("register",options);
  expect(first).toMatchObject({ok:false,error:{outcome:"unknown"}});
  expect(fetch).toHaveBeenCalledTimes(2); // no retry
  expect((await client.call("register",options)).ok).toBe(true);
  expect(fetch.mock.calls[1]?.[1].body).toBe(fetch.mock.calls[3]?.[1].body);
  expect(fetch.mock.calls[3]?.[1].headers).toMatchObject({"Idempotency-Key":"synthetic-receipt","X-CSRFToken":"new-synthetic"});
});
it("never sends mutation when bootstrap fails and sanitizes server messages",async()=>{
  const fetch=vi.fn().mockResolvedValue(json(failure("SERVICE_UNAVAILABLE",true),503));
  const result=await createApiClient(fetch).call("login",login);
  expect(result).toMatchObject({ok:false,error:{code:"SERVICE_UNAVAILABLE",outcome:"not-sent"}});
  expect(fetch).toHaveBeenCalledTimes(1);expect(JSON.stringify(result)).not.toContain("PRIVATE");
});
for(const [status,code,retryable] of [[400,"INVALID_REQUEST",false],[401,"AUTHENTICATION_REQUIRED",false],
  [403,"CSRF_FAILED",false],[409,"STATE_CONFLICT",false],[429,"RATE_LIMITED",true],[503,"SERVICE_UNAVAILABLE",true]] as const)
it("maps canonical HTTP "+status+" safely without automatic retries",async()=>{
  const fetch=vi.fn().mockResolvedValueOnce(json(csrf)).mockResolvedValueOnce(json(failure(code,retryable),status,status===429?{"Retry-After":"3"}:{}));
  const result=await createApiClient(fetch).call("login",login);
  expect(result).toMatchObject({ok:false,error:{code,status,retryable}});
  expect(JSON.stringify(result)).not.toContain("PRIVATE");expect(fetch).toHaveBeenCalledTimes(2);
});
for(const [name,response] of [
  ["HTML",()=>new Response("<html>PRIVATE</html>",{status:200,headers:{"Content-Type":"text/html"}})],
  ["invalid JSON",()=>new Response("{broken",{headers:{"Content-Type":"application/json"}})],
  ["duplicate member",()=>new Response('{"data":{},"data":{},"meta":{}}',{headers:{"Content-Type":"application/json"}})],
  ["wrong envelope",()=>json({data:{password:"private"},meta})],
  ["wrong status",()=>json(user,201)],
  ["wrong error/status",()=>json(failure("CSRF_FAILED"),400)],
  ["wrong version",()=>json({...user,meta:{...meta,version:"unexpected"}})],
  ["charset",()=>new Response(JSON.stringify(user),{headers:{"Content-Type":"application/json; charset=windows-1251"}})],
  ["invalid UTF8",()=>new Response(new Uint8Array([0xff]),{headers:{"Content-Type":"application/json"}})],
  ["429 without Retry-After",()=>json(failure("RATE_LIMITED",true),429)],
  ["redirect",()=>new Response(null,{status:302,headers:{Location:"https://example.test"}})],
] as const)it("rejects "+name,async()=>{
  const fetch=vi.fn().mockResolvedValue(response());
  expect(await createApiClient(fetch).call("get_me",{})).toMatchObject({ok:false,error:{code:"INVALID_RESPONSE"}});
  expect(fetch).toHaveBeenCalledTimes(1);
});
it("rejects unvalidated bodies, coercion, limits and missing receipt before any fetch",async()=>{
  const fetch=vi.fn();
  const client=createApiClient(fetch);
  for(const body of [{username:1,password:"x"},{username:"x",password:"x",checker:"secret"},{username:"x",password:NaN},{username:"x",password:undefined}])
    expect(await client.call("login",{body:body as never})).toMatchObject({ok:false,error:{code:"INVALID_REQUEST",outcome:"not-sent"}});
  expect(await client.call("register",{body:login.body} as never)).toMatchObject({ok:false});
  expect(await client.call("login",{body:{username:"x",password:"x".repeat(65536)}})).toMatchObject({ok:false,error:{code:"LIMIT_EXCEEDED"}});
  expect(fetch).not.toHaveBeenCalled();
});
it("keeps cancelled/failed mutation outcomes unknown, never repeats login/logout",async()=>{
  for(const operation of ["login","logout"] as const){
    const fetch=vi.fn().mockResolvedValueOnce(json(csrf)).mockRejectedValueOnce(new TypeError("PRIVATE network"));
    const result=await createApiClient(fetch).call(operation,{body:operation==="login"?login.body:{}} as never);
    expect(result).toMatchObject({ok:false,error:{code:"NETWORK_ERROR",outcome:"unknown"}});
    expect(fetch).toHaveBeenCalledTimes(2);expect(JSON.stringify(result)).not.toContain("PRIVATE");
  }
});
it("propagates AbortController and ignores late mutation success after cancellation",async()=>{
  const controller=new AbortController();
  const fetch=vi.fn().mockResolvedValueOnce(json(csrf)).mockImplementationOnce(async(_url,init)=>{
    expect(init.signal.aborted).toBe(false);controller.abort();return json(user);
  });
  expect(await createApiClient(fetch).call("login",{...login,signal:controller.signal})).toMatchObject({ok:false,error:{code:"CANCELLED",outcome:"unknown"}});
  const before=vi.fn();controller.abort();
  expect(await createApiClient(before).call("get_me",{signal:controller.signal})).toMatchObject({ok:false,error:{code:"CANCELLED",outcome:"not-sent"}});
  expect(before).not.toHaveBeenCalled();
});
it("stale guards reject old responses even when a transport ignores abort",async()=>{
  const scope=new RequestScope(); const a=scope.begin(); const b=scope.begin();
  expect(a.signal.aborted).toBe(true);expect(a.isCurrent()).toBe(false);expect(b.isCurrent()).toBe(true);
  scope.invalidate();expect(b.isCurrent()).toBe(false);const c=scope.begin();scope.dispose();expect(c.isCurrent()).toBe(false);
});
it("supports canonical grade cursor/page size without caller URL or auth override",async()=>{
  const fetch=vi.fn().mockResolvedValue(json({data:[],meta:{...meta,pagination:{page_size:20,next_cursor:null,has_more:false}}}));
  // Canonical list envelope is validated on the API boundary.
  expect((await createApiClient(fetch).call("list_grades",{query:{cursor:"opaque",page_size:20}})).ok).toBe(true);
  expect(fetch.mock.calls[0]?.[0]).toBe("/api/v1/grades/?cursor=opaque&page_size=20");
  fetch.mockClear();
  expect(await createApiClient(fetch).call("list_grades",{query:{page_size:0}})).toMatchObject({ok:false});
  expect(fetch).not.toHaveBeenCalled();
});
it("parses JSON without duplicate keys, non-finite values, trailing garbage or prototypes",()=>{
  for(const raw of ['{"a":1,"a":2}','{"a":NaN}','{"a":1e999}','[1,]','{"a":1} x','{"a":"\\uZZZZ"}'])
    expect(()=>parseJson(raw)).toThrow();
  expect(parseJson('{"a":[true,false,null,-1.5e2,"x"]}')).toEqual({a:[true,false,null,-150,"x"]});
  expect(isJsonTree({toJSON(){return {}}})).toBe(false);
  expect(isJsonTree(new Date())).toBe(false);expect(isJsonTree([,])).toBe(false);
});
