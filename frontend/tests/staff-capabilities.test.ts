import {afterEach,it,expect} from 'vitest';
import {readStaffCapabilities} from '../src/shared/api/staff-capabilities';
const resources=['grades','subjects','sections','pages','publications','media_assets','redirects','users','groups'];
afterEach(()=>document.querySelectorAll('#mathstart-staff-capabilities').forEach(node=>node.remove()));
function add(value:unknown){const script=document.createElement('script');script.id='mathstart-staff-capabilities';script.type='application/json';script.textContent=JSON.stringify(value);document.head.append(script);}
const hints=()=>({version:1,own_password:true,resources:Object.fromEntries(resources.map(name=>[name,{view:true,add:false,change:false,delete:false}]))});
it('defaults missing or duplicate private presentation hints to denied',()=>{
 expect(readStaffCapabilities().own_password).toBe(false);
 add(hints());add(hints());
 expect(readStaffCapabilities().own_password).toBe(false);
});
it('reads the closed boolean-only private snapshot without rounding identifiers',()=>{
 add(hints());expect(readStaffCapabilities()).toEqual(hints());
});
it.each([null,{...hints(),user_id:1},{...hints(),version:2},{...hints(),resources:{}},{...hints(),own_password:'true'},{...hints(),resources:{...hints().resources,users:{view:true,add:true,change:true,delete:'false'}}}])('rejects malformed or expanded hints %j',value=>{
 add(value);expect(readStaffCapabilities().own_password).toBe(false);
 expect(Object.values(readStaffCapabilities().resources).every(row=>Object.values(row).every(flag=>flag===false))).toBe(true);
});
