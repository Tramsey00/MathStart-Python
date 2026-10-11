// @vitest-environment node
import {expect,it,vi} from "vitest";
import {createApiClient} from "../src/shared/api/client";
const meta={request_id:"12345678-1234-4234-8234-123456789abc",version:"http-v1"};
const json=(value:unknown,status=200)=>new Response(JSON.stringify(value),{status,headers:{"Content-Type":"application/json"}});
const csrf=()=>json({data:{csrf_token:"synthetic"},meta});
const unknownLogout={ok:false,error:{code:"INVALID_RESPONSE",status:200,outcome:"unknown",retryable:false}};
function transport(reply:()=>Response) {
  return vi.fn().mockImplementationOnce(async()=>csrf()).mockImplementationOnce(async()=>reply());
}
function singlePost(fetch:ReturnType<typeof transport>) {
  expect(fetch).toHaveBeenCalledTimes(2);
  expect(fetch.mock.calls.map(([url])=>url)).toEqual(["/api/v1/auth/csrf/","/api/v1/auth/logout/"]);
  expect(fetch.mock.calls[1]?.[1]).toMatchObject({method:"POST",body:"{}",credentials:"same-origin",redirect:"error"});
}
it("acknowledges logout only with validated HTTP200 completed:true",async()=>{
  const response={data:{completed:true},meta},fetch=transport(()=>json(response));
  expect(await createApiClient(fetch).call("logout",{body:{}})).toEqual({ok:true,value:response});
  singlePost(fetch);
});
it("keeps completed:false unacknowledged and unknown, with no automatic POST or reconciliation",async()=>{
  const fetch=transport(()=>json({data:{completed:false},meta}));
  const result=await createApiClient(fetch).call("logout",{body:{}});
  expect(result).toMatchObject(unknownLogout);
  singlePost(fetch);
  expect(JSON.stringify(result)).not.toContain("completed");
});
it.each([
  ["missing completed",()=>json({data:{},meta})],
  ["string completed",()=>json({data:{completed:"true"},meta})],
  ["numeric completed",()=>json({data:{completed:1},meta})],
  ["null completed",()=>json({data:{completed:null},meta})],
  ["private extra field",()=>json({data:{completed:true,password:"PRIVATE"},meta})],
  ["wrong envelope version",()=>json({data:{completed:true},meta:{...meta,version:"wrong"}})],
  ["malformed JSON",()=>new Response("{broken PRIVATE",{headers:{"Content-Type":"application/json"}})],
  ["wrong HTTP status",()=>json({data:{completed:true},meta},201)],
] as const)("rejects logout %s without weakening validation or retrying",async(_name,reply)=>{
  const fetch=transport(reply),result=await createApiClient(fetch).call("logout",{body:{}});
  expect(result).toMatchObject({ok:false,error:{code:"INVALID_RESPONSE",outcome:"unknown",retryable:false}});
  singlePost(fetch);
  expect(JSON.stringify(result)).not.toContain("PRIVATE");
});
it("lost logout response retains unknown outcome and never replays POST",async()=>{
  const fetch=vi.fn().mockImplementationOnce(async()=>csrf()).mockRejectedValueOnce(new TypeError("PRIVATE lost response"));
  const result=await createApiClient(fetch).call("logout",{body:{}});
  expect(result).toMatchObject({ok:false,error:{code:"NETWORK_ERROR",outcome:"unknown"}});
  singlePost(fetch);
});
it("an explicit later GET me does not rewrite an unacknowledged logout as success",async()=>{
  const fetch=transport(()=>json({data:{completed:false},meta}));
  const client=createApiClient(fetch),result=await client.call("logout",{body:{}});
  const user={data:{id:1,username:"synthetic",selected_grade_id:null,onboarding_mode:null,onboarding_complete:false},meta};
  singlePost(fetch); // no implicit session clearing, retry or GET me
  fetch.mockImplementationOnce(async()=>json(user));
  expect(await client.call("get_me",{})).toEqual({ok:true,value:user});
  expect(result).toMatchObject(unknownLogout);
  expect(fetch.mock.calls.filter(([url])=>url==="/api/v1/auth/logout/")).toHaveLength(1);
});
