import {useEffect,useRef,useState,type FormEvent} from 'react';
import {useLocation,type LinksFunction} from 'react-router';
import {createStaffClient,staffOperations} from '../../shared/api/staff-client';
import StaffWritePage from './staff-write';
import {StaffList,StaffDetails,StaffHistory} from '../../shared/ui/staff-records';
import {readStaffCapabilities} from '../../shared/api/staff-capabilities';
import tokens from '../../../../static/mathstart/css/ui/tokens.css?url';
import foundation from '../../../../static/mathstart/css/ui/foundation.css?url';
export const links:LinksFunction=()=>[{rel:'stylesheet',href:tokens},{rel:'stylesheet',href:foundation}];
export const meta=()=>[{title:'Администрирование · MathStart'},{name:'robots',content:'noindex, nofollow'}];
export const handle={skipLink:{target:'staff-main',label:'К администрированию'}};
export const staffResources=[['grades','content/grade','Классы'],['subjects','content/subject','Предметы'],['sections','content/section','Разделы'],['pages','content/contentpage','Страницы'],['publications','content/lessonpublication','Публикации'],['media_assets','content/mediaasset','Медиафайлы'],['redirects','content/redirect','Перенаправления'],['users','auth/user','Пользователи'],['groups','auth/group','Группы']] as const;
const labels:Record<string,string>={is_staff:'Доступ к администрированию',is_superuser:'Суперпользователь',is_active:'Активен',groups:'Группа',grade:'Класс',subject:'Предмет',section:'Раздел',page_type:'Тип страницы',is_published:'Опубликовано',is_permanent:'Постоянное перенаправление',is_active_redirect:'Активно'};
const api=createStaffClient();
function StaffReadPage(){
 const location=useLocation(),parts=location.pathname.replace(/^\/admin\/?/,'').split('/').filter(Boolean);
 const info=staffResources.find(r=>parts.slice(0,2).join('/')===r[1]),resource=info?.[0];
 const id=parts[2]&&/^[1-9]\d*$/.test(parts[2])?parts[2]:undefined;
 const history=parts[3]==='history',valid=parts.length===0||!!info&&(parts.length===2||!!id&&parts.length===4&&['change','history'].includes(parts[3]!));
 const [data,setData]=useState<any>(null),[message,setMessage]=useState(''),[busy,setBusy]=useState(false),[pagination,setPagination]=useState<any>(null);
 const [query,setQuery]=useState<Record<string,string>>({});
 const generation=useRef(0),controller=useRef<AbortController|null>(null),request=useRef(0);
 const base=info?'/admin/'+info[1]+'/':'/admin/',listOp=staffOperations.find(o=>o.operationId==='staff_list_'+resource);
 async function load(params:Record<string,string>=query){
  if(!resource||!valid)return;
  const current=generation.current,ownRequest=++request.current;controller.current?.abort();controller.current=new AbortController();
  setBusy(true);setMessage('Загружаем данные…');
  const r=await api.call((history?'staff_history_':id?'staff_get_':'staff_list_')+resource,{...(id?{id}:{}),...(!id||history?{query:params}:{}),signal:controller.current.signal});
  if(current!==generation.current||ownRequest!==request.current)return;
  setBusy(false);
  if(r.ok){setData(r.value.data);setPagination(r.value.meta.pagination??null);setMessage('Данные загружены.');}
  else{setData(null);setPagination(null);setMessage(r.error.message);}
 }
 useEffect(()=>{generation.current++;setData(null);setPagination(null);setQuery({});void load({});return()=>{generation.current++;controller.current?.abort();};},[location.pathname]);
 function search(event:FormEvent<HTMLFormElement>){event.preventDefault();const params:Record<string,string>={};for(const[k,v]of new FormData(event.currentTarget))if(v)params[k]=String(v);setQuery(params);void load(params);}
 async function publication(){if(!id)return;const current=generation.current,ownRequest=++request.current;controller.current?.abort();controller.current=new AbortController();setBusy(true);const r=await api.call('get_page_publication_state',{id,signal:controller.current.signal});if(current!==generation.current||ownRequest!==request.current)return;setBusy(false);if(r.ok)setData(r.value.data);else{setData(null);setMessage(r.error.message);}}
 return <main id="staff-main" className="ms-ui" tabIndex={-1} aria-busy={busy}><h1>Администрирование</h1><nav aria-label="Разделы администрирования"><a href="/admin/">Главная</a> · <a href="/account/">Личный кабинет / вход</a></nav>
  {!valid?<h2>Страница не найдена</h2>:!resource?<ul>{staffResources.filter(r=>Object.values(readStaffCapabilities().resources[r[0]]).some(Boolean)).map(r=><li key={r[0]}><a href={'/admin/'+r[1]+'/'}>{r[2]}</a></li>)}</ul>:<><h2>{info?.[2]}{history?' · История':''}</h2><p role="status" aria-live="polite">{message}</p><a href={base}>К списку</a> <button className="ms-ui-button" type="button" disabled={busy} onClick={()=>void load()}>Загрузить данные ещё раз</button>
  {!id&&<form onSubmit={search}><div className="ms-ui-field"><label htmlFor="staff-search">Поиск</label><input id="staff-search" name="q"/></div>{(listOp?.parameters??[]).filter((p:any)=>p.name.startsWith('filter__')).map((p:any)=><div className="ms-ui-field" key={p.name}><label htmlFor={p.name}>{labels[p.name.slice(8)]??p.name.slice(8)}</label>{p.schema.type==='boolean'?<select id={p.name} name={p.name}><option value="">Все</option><option value="true">Да</option><option value="false">Нет</option></select>:p.schema.enum?<select id={p.name} name={p.name}><option value="">Все</option>{p.schema.enum.map((v:string)=><option key={v} value={v}>{v}</option>)}</select>:<input id={p.name} name={p.name}/>}</div>)}<div className="ms-ui-field"><label htmlFor="staff-sort">Порядок</label><select id="staff-sort" name="sort"><option value="default">По умолчанию</option>{Object.keys(listOp?.['x-sort-contract']?.explicit_single_field_orders??{}).map(key=><option key={key} value={key}>{key}</option>)}</select></div><button type="submit" className="ms-ui-button" disabled={busy}>Показать</button></form>}
  {id&&<nav><a href={base+id+'/change/'}>Просмотр</a> · <a href={base+id+'/history/'}>История</a>{resource==='pages'&&<button type="button" className="ms-ui-button" disabled={busy} onClick={()=>void publication()}>Состояние публикации</button>}</nav>}
  {Array.isArray(data)?history?<StaffHistory rows={data}/>:<StaffList resource={resource} rows={data} base={base} caption={info?.[2]??'Записи'}/>:data&&<StaffDetails record={data}/>}
  {pagination?.next_cursor&&<button type="button" className="ms-ui-button" disabled={busy} onClick={()=>void load({...query,cursor:pagination.next_cursor})}>Следующая страница</button>}
  </>}<noscript><p>Для загрузки административных данных нужен JavaScript.</p></noscript></main>;
}

export default function StaffPage(){
 const {pathname}=useLocation();
 const write=/^\/admin\/(?:auth\/(?:user|group)\/|password_change\/)/.test(pathname);
 return write?<StaffWritePage/>:<StaffReadPage/>;
}
