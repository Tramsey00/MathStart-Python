// @vitest-environment node
import {it,expect} from "vitest";
import {productionBoundaryPlugin} from "../scripts/production-boundary.mjs";
import {createApiClient} from "../src/shared/api/client";
import {createLatestReader} from "../src/shared/api/latest-read";
import {RequestScope} from "../src/shared/api/request-scope";
const meta={request_id:"12345678-1234-4234-8234-123456789abc",version:"http-v1"};
const payload={data:{id:1,username:"synthetic",selected_grade_id:null,onboarding_mode:null,onboarding_complete:false},meta};
it("rejects debug/fixture modules before writing any production graph",()=>{
  for(const path of ["/src/debug/fixture-pack.ts","/src/app/routes/foundation-gallery.tsx",
    "/specs/ui/fixtures/ui-states-v1.json","/src/shared/api/generated/UiFixturePack.mjs"]){
    const plugin=productionBoundaryPlugin();
    expect(()=>plugin.generateBundle({},{"fake":{type:"chunk",modules:{[path]:{}}}})).toThrow("Forbidden production modules");
  }
});
it("rejects late reads after newer data or session invalidation",async()=>{
  const resolves:((r:Response)=>void)[]=[];
  const client=createApiClient(()=>new Promise(resolve=>resolves.push(resolve)));
  const scope=new RequestScope(),read=createLatestReader(client,scope);
  const older=read("get_me",{}),newer=read("get_me",{});
  resolves[1]!(new Response(JSON.stringify(payload),{headers:{"Content-Type":"application/json"}}));
  expect((await newer).ok).toBe(true);
  resolves[0]!(new Response(JSON.stringify(payload),{headers:{"Content-Type":"application/json"}}));
  expect(await older).toMatchObject({ok:false,error:{code:"CANCELLED"}});
  const pending=read("get_me",{});scope.invalidate();
  resolves[2]!(new Response(JSON.stringify(payload),{headers:{"Content-Type":"application/json"}}));
  expect(await pending).toMatchObject({ok:false,error:{code:"CANCELLED"}});
});
