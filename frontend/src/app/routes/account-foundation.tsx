import {useEffect,useRef,useState,type FormEvent} from 'react';
import type {LinksFunction} from 'react-router';
import {createApiClient,type ApiResult} from '../../shared/api/client';
import type {IdentityContracts} from '../../shared/api/generated/identity-contracts';
import tokens from '../../../../static/mathstart/css/ui/tokens.css?url';
import foundation from '../../../../static/mathstart/css/ui/foundation.css?url';
import account from '../../../../static/mathstart/css/ui/account.css?url';
export const links:LinksFunction=()=>[{rel:'stylesheet',href:tokens},{rel:'stylesheet',href:foundation},{rel:'stylesheet',href:account}];
export const meta=()=>[{title:'Личный кабинет · MathStart'},{name:'robots',content:'noindex, nofollow'}];
export const handle={skipLink:{target:'account-main',label:'К личному кабинету'}};
type User=IdentityContracts['get_me']['response']['data'];
type Grade=IdentityContracts['list_grades']['response']['data'][number];
type Pending={operation:'register';body:IdentityContracts['register']['request'];key:string}|{operation:'complete_onboarding';body:IdentityContracts['complete_onboarding']['request'];key:string;owner:User['id']};
const modes=[['START_ZERO','Начать с начала'],['SELF_REPORT','Самооценка'],['DIAGNOSTIC','Выбрать диагностику']] as const;
const api=createApiClient();
export default function AccountPage(){
 const [user,setUser]=useState<User|null>(null),[ready,setReady]=useState(false),[busy,setBusy]=useState(false);
 const [mode,setMode]=useState<'login'|'register'>('login'),[message,setMessage]=useState('Загружаем сохранённое состояние…');
 const [grades,setGrades]=useState<Grade[]>([]),[cursor,setCursor]=useState<string|null>(null),[canRetry,setCanRetry]=useState(false);
 const [retryAfter,setRetryAfter]=useState(0);
 const pending=useRef<Pending|null>(null),generation=useRef(0),restoreSequence=useRef(0),gradeSequence=useRef(0),controller=useRef<AbortController|null>(null);
 const forms=useRef<HTMLDivElement>(null);
 function clear(){pending.current=null;setCanRetry(false);forms.current?.querySelectorAll<HTMLInputElement>('input[type=password]').forEach(input=>input.value='');}
 function invalidate(){generation.current++;controller.current?.abort();controller.current=new AbortController();}
 async function restore(quiet=false){
  const current=generation.current,sequence=++restoreSequence.current;
  const r=await api.call('get_me',{signal:controller.current!.signal});
  if(current!==generation.current||sequence!==restoreSequence.current)return;
  if(r.ok){
   const p=pending.current;
   if(p&&(p.operation==='register'?p.body.username!==r.value.data.username:String(p.owner)!==String(r.value.data.id)))clear();
   setUser(r.value.data);setMessage('Сохранённое состояние загружено.');
  }
  else if(r.error.code==='AUTHENTICATION_REQUIRED'){if(pending.current?.operation==='complete_onboarding')clear();setUser(null);setMessage(quiet?'':'Войдите или зарегистрируйтесь.');}
  else setMessage(r.error.message);
  setReady(r.ok||!r.ok&&r.error.code==='AUTHENTICATION_REQUIRED');
  return r.ok||r.error.code==='AUTHENTICATION_REQUIRED';
 }
 async function loadGrades(next?:string){
  const current=generation.current,sequence=++gradeSequence.current;
  const r=await api.call('list_grades',{query:next?{cursor:next}:{},signal:controller.current!.signal});
  if(current!==generation.current||sequence!==gradeSequence.current)return;
  if(r.ok){setGrades(old=>next?[...old,...r.value.data]:r.value.data);setCursor(r.value.meta.pagination?.next_cursor??null);}
  else setMessage(r.error.message);
 }
 useEffect(()=>{invalidate();void restore(true);void loadGrades();return()=>{generation.current++;controller.current?.abort();pending.current=null;forms.current?.querySelectorAll<HTMLInputElement>('input[type=password]').forEach(input=>input.value='');};},[]);
 async function finish(r:ApiResult<unknown>,current:number){
  if(current!==generation.current)return;
  if(r.ok){clear();await restore();}
  else{
   setMessage(r.error.message+(r.error.outcome==='unknown'?' Результат пока неизвестен. Сначала загрузите сохранённое состояние.':''));
   setRetryAfter(Date.now()+(r.error.retryAfterSeconds??0)*1000);
   if(r.error.outcome==='unknown')await restore();
   if(r.error.outcome==='unknown'||r.error.code==='RATE_LIMITED'||r.error.code==='CSRF_FAILED'||r.error.code==='SERVICE_UNAVAILABLE')setCanRetry(pending.current!==null);
   else clear();
   if(r.error.code==='AUTHENTICATION_REQUIRED'){clear();setUser(null);}
  }
  setBusy(false);
 }
 async function replay(){
  if(busy||Date.now()<retryAfter)return;
  const p=pending.current;if(!p)return;
  setBusy(true);const current=generation.current;
  // GET-first reconciliation before an explicit immutable, same-key replay.
  const reconciled=await restore();if(current!==generation.current)return;
  if(!reconciled||pending.current!==p){setBusy(false);return;}
  const r=p.operation==='register'?await api.call('register',{body:p.body,idempotencyKey:p.key,signal:controller.current!.signal}):await api.call('complete_onboarding',{body:p.body,idempotencyKey:p.key,signal:controller.current!.signal});
  await finish(r,current);
 }
 async function auth(event:FormEvent<HTMLFormElement>){
  event.preventDefault();if(busy)return;
  const data=new FormData(event.currentTarget),username=String(data.get('username')),password=String(data.get('password'));
  const body=Object.freeze({username,password,...(mode==='register'&&data.get('email')?{email:String(data.get('email'))}:{})});
  if(mode==='register'&&Array.from(username).length>30){setMessage('Имя пользователя должно содержать не больше 30 символов.');return;}
  clear();event.currentTarget.querySelector<HTMLInputElement>('input[type=password]')!.value='';
  invalidate();setBusy(true);const current=generation.current;
  if(mode==='register'){pending.current={operation:'register',body,key:crypto.randomUUID()};await finish(await api.call('register',{body,idempotencyKey:pending.current.key,signal:controller.current!.signal}),current);}
  else await finish(await api.call('login',{body,signal:controller.current!.signal}),current);
 }
 async function save(event:FormEvent<HTMLFormElement>,onboarding:boolean){
  event.preventDefault();if(busy)return;
  const data=new FormData(event.currentTarget),grade=grades.find(g=>String(g.id)===data.get('selected_grade_id'));
  if(!grade){setMessage('Выберите класс из списка.');return;}
  clear();setBusy(true);const current=generation.current;
  if(onboarding){const selected=modes.find(m=>m[0]===data.get('mode'));if(!selected){setBusy(false);return;}
   if(!user){setBusy(false);return;}
   const body=Object.freeze({selected_grade_id:grade.id,mode:selected[0]});pending.current={operation:'complete_onboarding',body,key:crypto.randomUUID(),owner:user.id};
   await finish(await api.call('complete_onboarding',{body,idempotencyKey:pending.current.key,signal:controller.current!.signal}),current);
  }else await finish(await api.call('update_me',{body:{selected_grade_id:grade.id},signal:controller.current!.signal}),current);
 }
 async function logout(){clear();invalidate();setMode('login');setUser(null);setBusy(true);const current=generation.current;await finish(await api.call('logout',{body:{},signal:controller.current!.signal}),current);}
 function select(id:string,label:string){return <div className="ms-ui-field"><label htmlFor={id}>{label}</label><select id={id} name="selected_grade_id" required defaultValue={user?.selected_grade_id===null?'':String(user?.selected_grade_id??'')}><option value="">Выберите класс</option>{grades.map(g=><option key={String(g.id)} value={String(g.id)}>{g.title}</option>)}</select></div>;}
 return <main id="account-main" className="ms-ui ms-account" tabIndex={-1} aria-busy={busy||!ready}>
  <header className="ms-ui-intro"><h1>Личный кабинет</h1><p>Войдите или зарегистрируйтесь, чтобы сохранить класс и выбрать, с чего начать.</p></header>
  <section className="ms-ui-state" aria-label="Состояние личного кабинета"><p role="status" aria-live="polite">{message}</p><button type="button" className="ms-ui-button" disabled={busy} onClick={()=>void restore()}>Загрузить сохранённое состояние</button>{canRetry&&<button type="button" className="ms-ui-button" disabled={busy} onClick={()=>void replay()}>Повторить тот же запрос</button>}</section>
  <div ref={forms}>{ready&&!user&&<div className="ms-account-auth"><div role="group" aria-label="Вход или регистрация">{(['login','register'] as const).map(value=><button type="button" className="ms-ui-button" key={value} aria-pressed={mode===value} disabled={busy} onClick={()=>{clear();invalidate();setMode(value);setMessage('');}}>{value==='login'?'Вход':'Регистрация'}</button>)}</div>
   <section className="ms-ui-card"><h2>{mode==='login'?'Вход':'Регистрация'}</h2><form key={mode} onSubmit={event=>void auth(event)}><fieldset disabled={busy||canRetry}><legend className="ms-ui-sr-only">{mode==='login'?'Войти в MathStart':'Создать аккаунт'}</legend>
    <div className="ms-ui-field"><label htmlFor="auth-username">Имя пользователя</label><input id="auth-username" name="username" autoComplete="username" maxLength={mode==='register'?30:150} required/></div>
    <div className="ms-ui-field"><label htmlFor="auth-password">Пароль</label><input id="auth-password" name="password" type="password" autoComplete={mode==='register'?'new-password':'current-password'} required/></div>
    {mode==='register'&&<div className="ms-ui-field"><label htmlFor="auth-email">Электронная почта (необязательно)</label><input id="auth-email" name="email" type="email" autoComplete="email"/></div>}
    <button className="ms-ui-button" type="submit">{mode==='login'?'Войти':'Зарегистрироваться'}</button></fieldset></form></section></div>}
  {ready&&user&&<section aria-labelledby="profile-title"><h2 id="profile-title">Ваш профиль</h2><dl className="ms-account-summary"><dt>Имя пользователя</dt><dd>{user.username}</dd><dt>Класс</dt><dd>{grades.find(g=>g.id===user.selected_grade_id)?.title??'Не выбран'}</dd><dt>Выбранный путь</dt><dd>{modes.find(m=>m[0]===user.onboarding_mode)?.[1]??'Не выбран'}</dd><dt>Начальная настройка</dt><dd>{user.onboarding_complete?'Сохранена':'Не завершена'}</dd></dl>
   <div className="ms-ui-grid"><section className="ms-ui-card"><h3>Выбор класса</h3><form onSubmit={e=>void save(e,false)}><fieldset disabled={busy||canRetry||!grades.length}>{select('profile-grade','Ваш класс')}<button type="submit" className="ms-ui-button">Сохранить класс</button></fieldset></form></section>
   <section className="ms-ui-card"><h3>С чего начать</h3><form onSubmit={e=>void save(e,true)}><fieldset disabled={busy||canRetry||!grades.length}>{select('onboarding-grade','Класс для начала занятий')}<fieldset className="ms-account-modes"><legend>Выберите путь (обязательно)</legend>{modes.map(([value,label])=><label key={value}><input type="radio" name="mode" value={value} required defaultChecked={user.onboarding_mode===value}/>{label}</label>)}<p>Сохраняется выбранный путь. Диагностические задания и отметки знакомых тем здесь не запускаются.</p></fieldset><button type="submit" className="ms-ui-button">Сохранить начальную настройку</button></fieldset></form></section></div>
   <button type="button" className="ms-ui-button" disabled={busy} onClick={()=>void logout()}>Выйти</button></section>}</div>
  {ready&&user&&<button type="button" className="ms-ui-button" disabled={busy} onClick={()=>void loadGrades(cursor??undefined)}>{cursor?'Загрузить следующие классы':'Загрузить классы ещё раз'}</button>}
  <noscript><p>Для безопасного входа и сохранения настроек нужен JavaScript. Учебные материалы доступны в навигации выше.</p></noscript>
 </main>;
}
