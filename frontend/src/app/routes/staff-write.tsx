import {useEffect,useRef,useState,type FormEvent} from 'react';
import {useLocation,type LinksFunction} from 'react-router';
import {staffWriteOperations as staffOperations,staffDefinition,stringifyExact} from '../../shared/api/staff-client';
import {createStaffWriteClient} from '../../shared/api/staff-write-client';
import tokens from '../../../../static/mathstart/css/ui/tokens.css?url';
import foundation from '../../../../static/mathstart/css/ui/foundation.css?url';
export const links:LinksFunction=()=>[{rel:'stylesheet',href:tokens},{rel:'stylesheet',href:foundation}];
export const meta=()=>[{title:'Администрирование · MathStart'},{name:'robots',content:'noindex, nofollow'}];
export const handle={skipLink:{target:'staff-main',label:'К администрированию'}};
const resources=[['grades','content/grade','Классы'],['subjects','content/subject','Предметы'],['sections','content/section','Разделы'],['pages','content/contentpage','Страницы'],['publications','content/lessonpublication','Публикации'],['media_assets','content/mediaasset','Медиафайлы'],['redirects','content/redirect','Перенаправления'],['users','auth/user','Пользователи'],['groups','auth/group','Группы']] as const;
const labels:Record<string,string>={username:'Имя пользователя',first_name:'Имя',last_name:'Фамилия',email:'Электронная почта',is_active:'Активен',is_staff:'Доступ к администрированию',is_superuser:'Суперпользователь',last_login:'Последний вход',date_joined:'Дата регистрации',groups:'Группы',user_permissions:'Прямые права',name:'Название',permissions:'Права',usable_password:'Разрешить вход по паролю',password1:'Пароль',password2:'Повторите пароль',old_password:'Текущий пароль',new_password1:'Новый пароль',new_password2:'Повторите новый пароль',confirm_disable:'Подтверждаю отключение входа по паролю'};
const api=createStaffWriteClient();
export default function StaffPage(){
 const location=useLocation(),parts=location.pathname.replace(/^\/admin\/?/,'').split('/').filter(Boolean);
 const info=resources.find(r=>parts.slice(0,2).join('/')===r[1]),resource=info?.[0];
 const id=parts[2]&&/^\d+$/.test(parts[2])?parts[2]:undefined;
 const action=parts[2]==='add'?'add':parts.at(-1)==='history'?'history':parts.at(-1)==='password'?'password':parts.at(-1)==='delete'?'delete':parts[0]==='password_change'?'own-password':id?'detail':'list';
 const editable=resource==='users'||resource==='groups',base=info?'/admin/'+info[1]+'/':'/admin/';
 const [data,setData]=useState<any>(null),[fields,setFields]=useState<Record<string,any>>({}),[message,setMessage]=useState(''),[busy,setBusy]=useState(false),[unknown,setUnknown]=useState(false);
 const [pagination,setPagination]=useState<any>(null),[selected,setSelected]=useState<string[]>([]),[preview,setPreview]=useState<any>(null),[permissions,setPermissions]=useState<any[]>([]),[groups,setGroups]=useState<any[]>([]);
 const gen=useRef(0),abort=useRef<AbortController|null>(null),form=useRef<HTMLFormElement>(null),lastQuery=useRef<Record<string,string|string[]>>({});
 const operation=action==='add'?'create_staff_'+resource:action==='password'?'change_staff_password':action==='own-password'?'change_own_staff_password':'update_staff_'+resource;
 const op=staffOperations.find(o=>o.operationId===operation);
 const rule=op?.requestBody?.content?.['application/json']?.schema?.$ref?.split('/').at(-1),definition=rule?staffDefinition(rule):null;
 function clearPasswords(){setFields(old=>Object.fromEntries(Object.entries(old).filter(([k])=>!k.includes('password')||k==='usable_password')));form.current?.querySelectorAll<HTMLInputElement>('input[type=password]').forEach(input=>input.value='');}
 async function read(query:Record<string,string|string[]>=lastQuery.current){
  const current=gen.current;setBusy(true);setMessage('Загружаем данные…');lastQuery.current=query;
  const operation=resource?(action==='history'?'staff_history_':id?'staff_get_':'staff_list_')+resource:null;
  if(!operation){setBusy(false);setMessage('');return;}
  const r=await api.call(operation,{...(id?{id}:{}),...(!id||action==='history'?{query}:{}),signal:abort.current!.signal});
  if(current!==gen.current)return;
  if(r.ok){setData(r.value.data);setPagination(r.value.meta.pagination??null);setMessage('Данные загружены.');if(!Array.isArray(r.value.data)){const next:Record<string,any>={};for(const name of Object.keys(definition?.properties??{}))if(name in r.value.data)next[name]=r.value.data[name];if(action==='password')next.usable_password=true;setFields(next);}}
  else{setData(null);setMessage(r.error.message);}
  setBusy(false);
 }
 useEffect(()=>{
  gen.current++;abort.current?.abort();abort.current=new AbortController();setData(null);setFields({});setSelected([]);setPreview(null);setUnknown(false);lastQuery.current={};
  if(action==='add')setFields(resource==='users'?{username:'',usable_password:true,password1:'',password2:''}:{name:'',permissions:[]});
  else if(action==='own-password')setFields({old_password:'',new_password1:'',new_password2:''});
  else void read();
  if(editable&&(action==='add'||action==='detail')){const current=gen.current;void api.call('list_staff_permission_choices',{signal:abort.current.signal}).then(r=>{if(current===gen.current&&r.ok)setPermissions(r.value.data);});if(resource==='users'&&id)void api.call('list_user_form_group_choices',{id,signal:abort.current.signal}).then(r=>{if(current===gen.current&&r.ok)setGroups(r.value.data);});}
  return()=>{gen.current++;abort.current?.abort();form.current?.reset();};
 },[location.pathname]);
 async function submit(event:FormEvent<HTMLFormElement>){
  event.preventDefault();if(busy||unknown||!op)return;
  const current=gen.current,body={...fields};
  if(action==='password'&&body.usable_password===false){delete body.password1;delete body.password2;}else delete body.confirm_disable;
  clearPasswords();setBusy(true);const r=await api.call(operation,{...(id?{id}:{}),body,signal:abort.current!.signal});
  if(current!==gen.current)return;setBusy(false);
  if(r.ok){setMessage('Изменения сохранены.');if(r.value.data?.id&&action==='add')window.location.assign(base+String(r.value.data.id)+'/change/');else if(action==='detail')await read();}
  else{setMessage(r.error.message+(r.error.outcome==='unknown'?' Результат неизвестен. Проверьте сохранённое состояние перед дальнейшими действиями.':''));if(r.error.outcome==='unknown'){setUnknown(true);await read();}}
 }
 async function deletePreview(ids:string[]){
  if(!resource||!ids.length)return;setBusy(true);const current=gen.current;
  const r=await api.call(ids.length===1?'preview_delete_staff_'+resource:'preview_bulk_delete_staff_'+resource,{...(ids.length===1?{id:ids[0]!}:{query:{ids}}),signal:abort.current!.signal});
  if(current!==gen.current)return;setBusy(false);if(r.ok)setPreview({...r.value.data,selected:ids});else setMessage(r.error.message);
 }
 async function remove(event:FormEvent<HTMLFormElement>){
  event.preventDefault();if(!preview||busy||unknown)return;setBusy(true);const current=gen.current,ids=preview.selected.map((v:string)=>BigInt(v));
  const r=await api.call(ids.length===1?'delete_staff_'+resource:'delete_selected_staff_'+resource,{...(ids.length===1?{id:String(ids[0])}:{}),body:{ids,confirmation_token:preview.confirmation_token},signal:abort.current!.signal});
  if(current!==gen.current)return;setPreview(null);setSelected([]);setBusy(false);
  if(r.ok)window.location.assign(base);else{setMessage(r.error.message);if(r.error.outcome==='unknown')setUnknown(true);await read();}
 }
 function query(event:FormEvent<HTMLFormElement>){event.preventDefault();const q:Record<string,string>={};for(const[k,v]of new FormData(event.currentTarget))if(v)q[k]=String(v);setSelected([]);setPreview(null);void read(q);}
 function field(name:string,r:any){
  const password=name.includes('password')&&name!=='usable_password',value=fields[name],choices=name==='groups'?groups:permissions;
  if(r.type==='array')return <div className="ms-ui-field" key={name}><label htmlFor={'staff-'+name}>{labels[name]??name}</label><select id={'staff-'+name} multiple value={(value??[]).map(String)} onChange={e=>setFields({...fields,[name]:[...e.target.selectedOptions].map(o=>BigInt(o.value))})}>{choices.map(c=><option key={String(c.id)} value={String(c.id)}>{c.name??c.title??c.codename}</option>)}</select></div>;
  if(name==='confirm_disable'&&fields.usable_password!==false)return null;
  if(r.type==='boolean'||name==='confirm_disable')return <label key={name}><input type="checkbox" checked={value===true} onChange={e=>setFields({...fields,[name]:e.target.checked})} required={name==='confirm_disable'&&fields.usable_password===false}/>{labels[name]??name}</label>;
  if(password&&fields.usable_password===false)return null;
  return <div className="ms-ui-field" key={name}><label htmlFor={'staff-'+name}>{labels[name]??name}</label><input id={'staff-'+name} type={password?'password':'text'} autoComplete={password?'new-password':'off'} value={value??''} required={definition?.required?.includes(name)||password&&fields.usable_password===true} maxLength={r.maxLength} onChange={e=>setFields({...fields,[name]:e.target.value===''&&name==='last_login'?null:e.target.value})}/></div>;
 }
 const listOp=staffOperations.find(o=>o.operationId==='staff_list_'+resource);
 return <main id="staff-main" className="ms-ui" tabIndex={-1} aria-busy={busy}><h1>Администрирование</h1><nav aria-label="Разделы администрирования"><a href="/admin/">Главная</a> · <a href="/account/">Личный кабинет / вход</a> · <a href="/admin/password_change/">Изменить свой пароль</a></nav>
  {!resource&&action!=='own-password'?<ul>{resources.map(r=><li key={r[0]}><a href={'/admin/'+r[1]+'/'}>{r[2]}</a></li>)}</ul>:<><h2>{info?.[2]??'Изменить свой пароль'}</h2><p role="status" aria-live="polite">{message}</p>{resource&&<a href={base}>К списку</a>}
   {resource&&<button className="ms-ui-button" type="button" disabled={busy} onClick={()=>void read()}>Загрузить сохранённое состояние</button>}{unknown&&<p role="alert">Результат записи пока неизвестен. Автоматического повтора нет. Проверьте список и откройте запись заново.</p>}
   {action==='list'&&<><form onSubmit={query}><div className="ms-ui-field"><label htmlFor="staff-search">Поиск</label><input id="staff-search" name="q"/></div>{(listOp?.parameters??[]).filter((p:any)=>p.name.startsWith('filter__')).map((p:any)=><div className="ms-ui-field" key={p.name}><label htmlFor={p.name}>{labels[p.name.slice(8)]??p.name.slice(8)}</label>{p.schema.type==='boolean'?<select id={p.name} name={p.name}><option value="">Все</option><option value="true">Да</option><option value="false">Нет</option></select>:<input id={p.name} name={p.name}/>}</div>)}<div className="ms-ui-field"><label htmlFor="staff-sort">Порядок</label><select id="staff-sort" name="sort"><option value="default">По умолчанию</option>{Object.keys(listOp?.['x-sort-contract']?.explicit_single_field_orders??{}).map(key=><option key={key} value={key}>{key}</option>)}</select></div><button type="submit" className="ms-ui-button" disabled={busy}>Показать</button></form>
    {editable&&<a href={base+'add/'}>Добавить</a>}{Array.isArray(data)&&<ul>{data.map(row=><li key={String(row.id)}>{editable&&<input type="checkbox" aria-label={'Выбрать '+(row.username??row.name??row.title??String(row.id))} checked={selected.includes(String(row.id))} onChange={e=>setSelected(e.target.checked?[...selected,String(row.id)]:selected.filter(v=>v!==String(row.id)))}/>}<a href={base+String(row.id)+'/change/'}>{row.title??row.username??row.name??row.slug??row.source_path??row.old_path??String(row.id)}</a></li>)}</ul>}{pagination?.next_cursor&&<button type="button" className="ms-ui-button" disabled={busy} onClick={()=>void read({...lastQuery.current,cursor:pagination.next_cursor})}>Следующая страница</button>}{editable&&selected.length>0&&<button type="button" className="ms-ui-button" disabled={busy} onClick={()=>void deletePreview(selected)}>Удалить выбранные</button>}</>}
   {id&&<nav><a href={base+id+'/history/'}>История</a>{editable&&<> · <a href={base+id+'/change/'}>Изменить</a> · <a href={base+id+'/delete/'}>Удалить</a>{resource==='users'&&<> · <a href={base+id+'/password/'}>Изменить пароль</a></>}</>}{resource==='pages'&&<button type="button" className="ms-ui-button" onClick={()=>{const current=gen.current;void api.call('get_page_publication_state',{id,signal:abort.current!.signal}).then(r=>{if(current!==gen.current)return;if(r.ok)setData(r.value.data);else setMessage(r.error.message);});}}>Состояние публикации</button>}</nav>}
   {data&&action!=='list'&&<pre style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere'}}>{stringifyExact(data)}</pre>}
   {definition&&(action==='add'||action==='detail'&&editable||action==='password'||action==='own-password')&&<form ref={form} onSubmit={e=>void submit(e)}><fieldset disabled={busy||unknown}>{Object.entries(definition.properties).map(([name,r])=>field(name,r))}{action==='detail'&&<label><input type="checkbox" required/>Подтверждаю изменение профиля, доступа и прав этой записи.</label>}<button type="submit" className="ms-ui-button">Сохранить</button></fieldset></form>}
   {action==='delete'&&id&&!preview&&<button type="button" className="ms-ui-button" disabled={busy} onClick={()=>void deletePreview([id])}>Проверить возможность удаления</button>}
   {preview&&<section className="ms-ui-card"><h3>Подтверждение удаления</h3><pre style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere'}}>{stringifyExact(Object.fromEntries(Object.entries(preview).filter(([k])=>k!=='confirmation_token')))}</pre><form onSubmit={e=>void remove(e)}><label><input type="checkbox" required/>Подтверждаю удаление показанных записей.</label><button type="submit" className="ms-ui-button" disabled={busy||unknown||preview.protected===true}>Удалить</button><button type="button" className="ms-ui-button" onClick={()=>setPreview(null)}>Отмена</button></form></section>}
  </>}<noscript><p>Для административных операций нужен JavaScript.</p></noscript></main>;
}
