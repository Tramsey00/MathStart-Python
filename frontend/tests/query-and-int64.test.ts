// @vitest-environment node
import {it,expect,vi} from 'vitest';
import {createApiClient} from '../src/shared/api/client';
import {parseJson} from '../src/shared/api/json-boundary';
it.each([null,[],['cursor'],1,true,'cursor'])('rejects non-object grade queries before fetch: %j',async query=>{
 const fetch=vi.fn();
 expect(await createApiClient(fetch).call('list_grades',{query} as never)).toMatchObject({ok:false,error:{code:'INVALID_REQUEST',outcome:'not-sent'}});
 expect(fetch).not.toHaveBeenCalled();
});
it('preserves adjacent numeric int64 IDs exactly without changing frozen wire JSON',()=>{
 const raw='{"id":9223372036854775807,"selected_grade_id":9007199254740993}';
 expect(parseJson(raw)).toEqual({id:'9223372036854775807',selected_grade_id:'9007199254740993'});
 expect(raw).toContain(':9223372036854775807');
 expect(()=>parseJson('{"username":9223372036854775807}')).toThrow();
});
