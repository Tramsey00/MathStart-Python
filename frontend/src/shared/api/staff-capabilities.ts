// Private server presentation hints only. API authorization is always server-side.
const resources=['grades','subjects','sections','pages','publications','media_assets','redirects','users','groups'] as const;
type Resource=typeof resources[number];
type Actions={view:boolean;add:boolean;change:boolean;delete:boolean};
export type StaffCapabilities={version:1;own_password:boolean;resources:Record<Resource,Actions>};
const empty=():StaffCapabilities=>({version:1,own_password:false,resources:Object.fromEntries(resources.map(name=>[name,{view:false,add:false,change:false,delete:false}])) as Record<Resource,Actions>});
export function readStaffCapabilities():StaffCapabilities{
 try{
  if(typeof document==='undefined')return empty();
  const nodes=document.querySelectorAll('script#mathstart-staff-capabilities[type="application/json"]');
  if(nodes.length!==1)return empty();
  const raw=nodes[0]!.textContent??'';if(raw.length>4096)return empty();
  const value=JSON.parse(raw);
  if(!value||Object.keys(value).sort().join(',')!=='own_password,resources,version'||value.version!==1||typeof value.own_password!=='boolean'||!value.resources||Object.keys(value.resources).sort().join(',')!==[...resources].sort().join(','))return empty();
  for(const resource of resources){const row=value.resources[resource];if(!row||Object.keys(row).sort().join(',')!=='add,change,delete,view'||Object.values(row).some(flag=>typeof flag!=='boolean'))return empty();}
  return value;
 }catch{return empty();}
}
