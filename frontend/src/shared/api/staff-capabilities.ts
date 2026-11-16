// Private server presentation hints only. API authorization is always server-side.
const resources=['grades','subjects','sections','pages','publications','media_assets','redirects','users','groups'] as const;
type Resource=typeof resources[number];
type Actions={view:boolean;add:boolean;change:boolean;delete:boolean};
export type StaffCapabilities={version:1;own_password:boolean;resources:Record<Resource,Actions>};
export const emptyStaffCapabilities=():StaffCapabilities=>({version:1,own_password:false,resources:Object.fromEntries(resources.map(name=>[name,{view:false,add:false,change:false,delete:false}])) as Record<Resource,Actions>});
export function parseStaffCapabilities(raw:string):StaffCapabilities|null {
 try{
  if(raw.length>4096)return null;
  const value=JSON.parse(raw);
  if(!value||Object.keys(value).sort().join(',')!=='own_password,resources,version'||value.version!==1||typeof value.own_password!=='boolean'||!value.resources||Object.keys(value.resources).sort().join(',')!==[...resources].sort().join(','))return null;
  for(const resource of resources){const row=value.resources[resource];if(!row||Object.keys(row).sort().join(',')!=='add,change,delete,view'||Object.values(row).some(flag=>typeof flag!=='boolean'))return null;}
  return value;
 }catch{return null;}
}
// Reuse the existing private document contract. Parse only the closed boolean
// payload in an inert document, never insert/execute returned HTML or scripts.
export async function loadStaffCapabilities(signal:AbortSignal):Promise<StaffCapabilities|null>{
 try{
  const response=await fetch('/admin/',{credentials:'same-origin',cache:'no-store',redirect:'error',signal,headers:{Accept:'text/html','X-MathStart-Staff-Presentation':'1'}});
  if(!response.ok||response.redirected||!response.headers.get('Cache-Control')?.includes('no-store')||!response.headers.get('Content-Type')?.startsWith('text/html'))return null;
  const html=await response.text();if(html.length>2_000_000)return null;
  const nodes=new DOMParser().parseFromString(html,'text/html').querySelectorAll('script#mathstart-staff-capabilities[type="application/json"]');
  return nodes.length===1?parseStaffCapabilities(nodes[0]!.textContent??''):null;
 }catch{return null;}
}
// Existing non-React consumers/tests retain a fail-closed document reader.
export function readStaffCapabilities():StaffCapabilities{
 if(typeof document==='undefined')return emptyStaffCapabilities();
 const nodes=document.querySelectorAll('script#mathstart-staff-capabilities[type="application/json"]');
 return nodes.length===1?parseStaffCapabilities(nodes[0]!.textContent??'')??emptyStaffCapabilities():emptyStaffCapabilities();
}
