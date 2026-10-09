import {it,expect} from "vitest";
import {createApiClient} from "../src/shared/api/client";
import {createLatestReader} from "../src/shared/api/latest-read";
import {RequestScope} from "../src/shared/api/request-scope";
// Compiled by strict tsc; this function is deliberately never executed.
function checkTypes(client:ReturnType<typeof createApiClient>) {
  // @ts-expect-error receipt required for register
  void client.call("register",{body:{username:"x",password:"x"}});
  // @ts-expect-error no auth body on read
  void client.call("get_me",{body:{password:"x"}});
  // @ts-expect-error idempotency is not retrofitted onto logout
  void client.call("logout",{body:{},idempotencyKey:"x"});
  // @ts-expect-error cannot choose arbitrary external endpoints
  void client.call("https://example.test/",{});
  // @ts-expect-error no coercing a number to password
  void client.call("login",{body:{username:"x",password:12}});
  // @ts-expect-error latest-reader cannot implicitly supersede/retry mutations
  void createLatestReader(client,new RequestScope())("login",{body:{username:"x",password:"x"}});
}
it("keeps compile-time negative examples inert",()=>expect(typeof checkTypes).toBe("function"));
