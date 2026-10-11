// @vitest-environment node
import {it,expect,vi} from "vitest";
import {createApiClient} from "../src/shared/api/client";
const meta={request_id:"12345678-1234-4234-8234-123456789abc",version:"http-v1"};
const json=(v:unknown)=>new Response(JSON.stringify(v),{headers:{"Content-Type":"application/json"}});
it("cancels a timed-out read without retries",async()=>{
  const fetch=vi.fn((_url,init)=>new Promise<Response>((_resolve,reject)=>{
    init.signal.addEventListener("abort",()=>reject(new DOMException("Cancelled","AbortError")));
  }));
  expect(await createApiClient(fetch).call("get_me",{timeoutMs:5})).toMatchObject({ok:false,error:{code:"CANCELLED",outcome:"not-sent"}});
  expect(fetch).toHaveBeenCalledTimes(1);
});
it("snapshots receipt key and raw body before asynchronous CSRF bootstrap",async()=>{
  const options={body:{username:"synthetic",password:"synthetic"},idempotencyKey:"original"};
  const fetch=vi.fn().mockImplementationOnce(async()=>{
    options.body.username="changed";options.idempotencyKey="changed";
    return json({data:{csrf_token:"synthetic"},meta});
  }).mockResolvedValueOnce(new Response(JSON.stringify({error:{code:"SERVICE_UNAVAILABLE",message:"Unavailable",field_errors:{},retryable:true,request_id:meta.request_id}}),{status:503,headers:{"Content-Type":"application/json"}}));
  await createApiClient(fetch).call("register",options);
  expect(fetch.mock.calls[1]?.[1].headers["Idempotency-Key"]).toBe("original");
  expect(JSON.parse(fetch.mock.calls[1]?.[1].body).username).toBe("synthetic");
});
it("rejects caller configuration overrides and accessors before fetching",async()=>{
  const fetch=vi.fn(),client=createApiClient(fetch);
  expect(await client.call("get_me",{credentials:"include"} as never)).toMatchObject({ok:false,error:{code:"INVALID_REQUEST"}});
  expect(await client.call("get_me",{get signal(){throw new Error("PRIVATE");}} as never)).toMatchObject({ok:false,error:{code:"INVALID_REQUEST"}});
  expect(await client.call("__proto__" as never,{} as never)).toMatchObject({ok:false,error:{code:"INVALID_REQUEST"}});
  expect(fetch).not.toHaveBeenCalled();
});
it("requires retryable flags to agree with status, not to authorize retries",async()=>{
  const fetch=vi.fn().mockResolvedValue(new Response(JSON.stringify({error:{code:"AUTHENTICATION_REQUIRED",message:"private",field_errors:{},retryable:true,request_id:meta.request_id}}),
    {status:401,headers:{"Content-Type":"application/json"}}));
  expect(await createApiClient(fetch).call("get_me",{})).toMatchObject({ok:false,error:{code:"INVALID_RESPONSE"}});
});

it("enforces R02 empty identity field errors and cursor bounds",async()=>{
  const fetch=vi.fn().mockResolvedValue(new Response(JSON.stringify({error:{code:"INVALID_REQUEST",message:"private",field_errors:{password:["private"]},retryable:false,request_id:meta.request_id}}),{status:400,headers:{"Content-Type":"application/json"}}));
  expect(await createApiClient(fetch).call("get_me",{})).toMatchObject({ok:false,error:{code:"INVALID_RESPONSE"}});
  fetch.mockClear();expect(await createApiClient(fetch).call("list_grades",{query:{cursor:"x".repeat(1025)}})).toMatchObject({ok:false,error:{code:"INVALID_REQUEST"}});expect(fetch).not.toHaveBeenCalled();
});

it.each(["get_me","login"] as const)("reports cancellation during response-body reading for %s without retry",async operation=>{
  const controller=new AbortController();
  const fetch=vi.fn(async(url:RequestInfo|URL)=>{
    if(url==="/api/v1/auth/csrf/")return json({data:{csrf_token:"synthetic"},meta});
    const response=json({});
    vi.spyOn(response,"arrayBuffer").mockImplementation(async()=>{
      controller.abort();
      throw new DOMException("PRIVATE aborted response body","AbortError");
    });
    return response;
  });
  const client=createApiClient(fetch);
  const result=operation==="login"
    ? await client.call("login",{body:{username:"synthetic",password:"synthetic"},signal:controller.signal})
    : await client.call("get_me",{signal:controller.signal});
  expect(result).toMatchObject({ok:false,error:{code:"CANCELLED",status:null,outcome:operation==="login"?"unknown":"not-sent"}});
  expect(fetch).toHaveBeenCalledTimes(operation==="login"?2:1);
  expect(JSON.stringify(result)).not.toContain("PRIVATE");
});
