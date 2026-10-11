import {type ApiResult,type RequestOptions,createApiClient} from "./client";
import type {IdentityContracts} from "./generated/identity-contracts";
import {RequestScope} from "./request-scope";
type ReadOperation="get_me"|"get_csrf"|"list_grades";
// Only reads may supersede each other. Mutations have explicit unknown-outcome semantics.
export function createLatestReader(client:ReturnType<typeof createApiClient>,scope:RequestScope) {
  return async function read<K extends ReadOperation>(operation:K,options:RequestOptions<K>):Promise<ApiResult<IdentityContracts[K]["response"]>> {
    const lease=scope.begin();
    const signal=options.signal?AbortSignal.any([lease.signal,options.signal]):lease.signal;
    const result=await client.call(operation,{...options,signal});
    if(!lease.isCurrent())return {ok:false,error:{code:"CANCELLED",message:"Запрос отменён.",status:null,outcome:"not-sent",retryable:false}};
    return result;
  };
}
