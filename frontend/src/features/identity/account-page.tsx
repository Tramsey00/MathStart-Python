import {useEffect,useState,type FormEvent,type ReactNode} from 'react';
import {useSearchParams} from 'react-router';
import {api,safeReturn,useSession} from './session';
import {AuthForm,PasswordField,SessionPlaceholder} from './auth-form';
import {IdentityIcon} from './identity-icon';
import {Brand} from '../../shared/ui/brand';
import {useSiteTheme} from '../../shared/ui/use-site-theme';
import {LessonHeader} from '../../shared/lesson/lesson-shell';
import type {IdentityContracts} from '../../shared/api/client';
import type {ApiResult} from '../../shared/api/client';
import './identity.css';
export function IdentityShell({children}:{children:ReactNode}){const [dark,setDark]=useSiteTheme();return <div className="identity-page"><a className="skip-link" href="#identity-main">К содержимому</a><LessonHeader brand={<Brand/>} catalogueHref="/materials" loginHref="/auth?mode=login" dark={dark} onTheme={()=>setDark(v=>!v)}/>{children}<footer className="identity-footer"><a href="/">MathStart</a><span>Математика для 5–10 классов</span></footer></div>;}
export function AuthPage(){
 const [params]=useSearchParams(),{user,status,refresh}=useSession();const raw=params.get('mode'),mode=['register','recover','verify','reset'].includes(raw??'')?raw:'login';
 const [token,setToken]=useState(''),[message,setMessage]=useState(''),[busy,setBusy]=useState(false),[locked,setLocked]=useState(false);
 useEffect(()=>{const value=new URLSearchParams(location.hash.slice(1)).get('token')??'';if(value)setToken(value);if(location.hash)history.replaceState(null,'',location.pathname+location.search);},[]);
 useEffect(()=>{if(status==='ready'&&user&&(mode==='login'||mode==='register'))location.replace('/account/');},[user,status,mode]);
 async function action(e:FormEvent<HTMLFormElement>){e.preventDefault();if(busy||locked)return;setBusy(true);const form=e.currentTarget,data=new FormData(form);
  const r=mode==='recover'?await api.call('account_recover',{body:{username:String(data.get('username'))}}):mode==='verify'?await api.call('account_verify',{body:{token}}):await api.call('account_reset',{body:{token,new_password:String(data.get('new_password'))}});
  form.reset();setBusy(false);
  if(r.ok){setLocked(true);setToken('');setMessage(mode==='recover'?'Если для этого логина доступно восстановление, запрос на письмо принят. Проверьте почту.':mode==='verify'?'Почта подтверждена. Теперь она доступна для восстановления.':'Пароль изменён. Войдите с новым паролем.');return;}
  if(r.error.code==='SERVICE_UNAVAILABLE'){setLocked(true);setMessage('Почтовая отправка сейчас недоступна. Доставка письма не подтверждена. Вход по логину продолжает работать.');}
  else if(r.error.outcome==='unknown'){setLocked(true);setMessage('Не удалось подтвердить результат. Откройте кабинет или попробуйте войти с новым паролем. Повторно эту операцию не отправляем.');}
  else setMessage(r.error.code==='INVALID_REQUEST'?'Ссылка недействительна или срок её действия истёк. Для нового пароля используйте 15–128 символов.':r.error.message+(r.error.retryAfterSeconds?` Повторите через ${r.error.retryAfterSeconds} с.`:''));
 }
 const title=mode==='register'?'Создать аккаунт':mode==='recover'?'Восстановить доступ':mode==='verify'?'Подтвердить почту':mode==='reset'?'Новый пароль':'С возвращением';
 useSiteTheme();
 const entry=mode==='login'||mode==='register';
 const authHref=(next:string)=>`/auth?mode=${next}${params.get('return')?'&return='+encodeURIComponent(safeReturn(params.get('return'))):''}`;
 return <div className="identity-page auth-page" data-auth-mode={mode}><a className="skip-link" href="#identity-main">К содержимому</a><a className="auth-back" href="/">← На главную</a>
 <main id="identity-main" className="auth-main" tabIndex={-1}><div className="auth-surface"><div className="brand auth-brand" aria-label="MathStart"><span>Math<span className="brand-accent">Start</span></span></div>
 {entry&&<nav className="auth-tabs" aria-label="Вход и регистрация"><a href={authHref('login')} aria-current={mode==='login'?'page':undefined}>Вход</a><a href={authHref('register')} aria-current={mode==='register'?'page':undefined}>Регистрация</a></nav>}
 <h1>{title}</h1>
 {entry?<><p className="identity-lead">{mode==='register'?'Придумайте логин и надёжный пароль.':'Войдите, чтобы продолжить обучение.'}</p>
 {status==='checking'||status==='ready'&&user?<SessionPlaceholder/>:status==='error'?<div className="identity-retry"><p role="status">Не удалось проверить вход.</p><button className="identity-button" onClick={()=>void refresh()}>Попробовать снова</button></div>:<><AuthForm key={mode} register={mode==='register'} returnTo={safeReturn(params.get('return'))}/>{mode==='register'&&<p className="auth-mail-hint">Почту для восстановления можно добавить и подтвердить позже в кабинете.</p>}</>}</>:<>
 <p className="identity-lead">{mode==='recover'?'Введите логин. Восстановление доступно только с подтверждённой почтой из кабинета.':mode==='verify'?'Подтвердите адрес кнопкой ниже. Простое открытие ссылки не меняет настройки.':'Придумайте новый пароль. После сохранения все устройства выйдут из аккаунта.'}</p>
 {mode==='verify'&&status!=='ready'?status==='checking'?<SessionPlaceholder/>:<div className="identity-retry"><p>Не удалось проверить вход.</p><button className="identity-button" onClick={()=>void refresh()}>Попробовать снова</button></div>:mode==='verify'&&!user?<p>Войдите в аккаунт, для которого добавляли почту. Затем снова откройте ссылку из письма. <a href="/auth?mode=login">Войти</a></p>:<form onSubmit={e=>void action(e)}><fieldset disabled={busy||locked||mode!=='recover'&&!token}>
 {mode==='recover'&&<div className="login-field"><label htmlFor="recover-login">Логин</label><div className="input-with-icon"><IdentityIcon name="user"/><input id="recover-login" name="username" autoComplete="username" autoCapitalize="none" spellCheck={false} required maxLength={150}/></div></div>}
 {mode==='reset'&&<PasswordField name="new_password" label="Новый пароль" fresh/>}
 <button className="email-submit" type="submit">{busy?'Подождите…':mode==='recover'?'Получить ссылку':mode==='verify'?'Подтвердить почту':'Сохранить пароль'}</button></fieldset></form>}
 {mode!=='recover'&&!token&&!locked&&<p>Откройте полную ссылку из письма. Если она устарела, запросите новую.</p>}<p className="login-feedback" role="status">{message}</p><a className="existing-login" href="/auth?mode=login">Вернуться ко входу</a></>}
 </div></main></div>;
}

type Grade=IdentityContracts['list_grades']['response']['data'][number];
export function AccountPage(){
 const {user,status,refresh}=useSession(),[grades,setGrades]=useState<Grade[]>([]),[state,setState]=useState<IdentityContracts['account_state']['response']['data']|null>(null),[message,setMessage]=useState(''),[busy,setBusy]=useState(false),[blocked,setBlocked]=useState(false),[retryAt,setRetryAt]=useState(0);
 async function load(){const r=await api.call('account_state',{});if(r.ok)setState(r.value.data);else setMessage(r.error.message);}
 useEffect(()=>{if(status==='ready'&&!user)location.replace('/auth?mode=login&return=%2Faccount%2F');if(status==='ready'&&user){void load();void (async()=>{let cursor:string|undefined;let all:Grade[]=[];do{const r=await api.call('list_grades',{query:{page_size:100,...(cursor?{cursor}:{})}});if(!r.ok){setMessage(r.error.message);return;}all=all.concat(r.value.data);cursor=r.value.meta.pagination?.next_cursor??undefined;}while(cursor);setGrades(all);})();}},[status,user?.id]);
 async function perform(e:FormEvent<HTMLFormElement>,action:'grade'|'email'|'password'|'sessions'){
  e.preventDefault();if(busy||blocked)return;if(Date.now()<retryAt){setMessage(`Повторите через ${Math.ceil((retryAt-Date.now())/1000)} с.`);return;}const form=e.currentTarget,data=new FormData(form);setBusy(true);setMessage('');
  const current_password=String(data.get('current_password'));let r:ApiResult<unknown>;
  if(action==='grade'){const grade=grades.find(g=>String(g.id)===data.get('grade'));if(!grade){setBusy(false);return;}r=await api.call('update_me',{body:{selected_grade_id:grade.id}});}
  else if(action==='email')r=await api.call('account_email',{body:{current_password,email:String(data.get('email')??'')}});
  else if(action==='password')r=await api.call('account_password',{body:{current_password,new_password:String(data.get('new_password'))}});
  else r=await api.call('account_sessions',{body:{current_password}});
  form.querySelectorAll<HTMLInputElement>('input[type=password],input[name=current_password],input[name=new_password]').forEach(i=>i.value='');
  if(r.ok){if(action==='password'||action==='sessions'){location.assign('/auth?mode=login');return;}await refresh();await load();setMessage(action==='email'?(data.get('email')?'Ссылка отправлена. Подтвердите новый адрес из письма.':'Почта удалена.'):'Класс сохранён.');}
  else{if(r.error.code==='AUTHENTICATION_REQUIRED')await refresh();if(r.error.outcome==='unknown'){await refresh();await load();setBlocked(true);setMessage('Ответ не получен. Состояние обновлено; проверьте его перед новой операцией. Для продолжения обновите страницу.');}else setMessage(r.error.code==='AUTHENTICATION_REQUIRED'?'Проверьте текущий пароль. Если сессия истекла, войдите снова.':r.error.code==='INVALID_REQUEST'?'Проверьте адрес и новый пароль. Пароль: 15–128 символов, не распространённый и не похожий на логин.':r.error.message+(r.error.retryAfterSeconds?` Повторите через ${r.error.retryAfterSeconds} с.`:''));setRetryAt(Date.now()+(r.error.retryAfterSeconds??0)*1000);}
  setBusy(false);
 }
 async function logout(){if(busy||blocked)return;setBusy(true);const r=await api.call('logout',{body:{}});if(r.ok){location.assign('/');return;}await refresh();setMessage('Не удалось подтвердить выход. Проверьте соединение и обновите страницу.');setBlocked(true);setBusy(false);}
 const [params,setParams]=useSearchParams();
 const section=params.get('section')==='account'?'account':params.get('section')==='security'?'security':'learn';
 const [editingGrade,setEditingGrade]=useState(false);
 const grade=grades.find(g=>g.id===user?.selected_grade_id);
 const sections=[{id:'learn',label:'Моё обучение',icon:'book'},{id:'account',label:'Аккаунт',icon:'user'},{id:'security',label:'Безопасность',icon:'shield'}] as const;
 const heading=sections.find(s=>s.id===section)!.label;
 return <IdentityShell><div className="account-layout">
 <aside className="account-sidebar" aria-label="Личный кабинет"><div className="account-profile"><strong>{status==='ready'&&user?user.username:'Личный кабинет'}</strong><span>{status==='ready'&&user?'Личный кабинет':'MathStart'}</span></div>
 <nav className="account-nav" aria-label="Разделы кабинета">{sections.map(s=><button type="button" key={s.id} disabled={busy} aria-current={section===s.id?'page':undefined} onClick={()=>{setParams(s.id==='learn'?{}:{section:s.id});setMessage('');}}><IdentityIcon name={s.icon}/><span>{s.label}</span></button>)}</nav>
 {status==='ready'&&user&&<button className="account-logout" disabled={busy||blocked} onClick={()=>void logout()}><IdentityIcon name="logout"/><span>Выйти</span></button>}</aside>
 <main id="identity-main" className="account-main" tabIndex={-1} aria-busy={busy||status==='checking'}><header className="account-intro"><h1>{heading}</h1><p>{section==='learn'?'Ваш класс и материалы для занятий.':section==='account'?'Логин и восстановление доступа.':'Пароль и вход на ваших устройствах.'}</p></header>
 {status==='checking'?<div className="account-pane"><SessionPlaceholder/></div>:status==='error'?<div className="account-pane identity-retry"><p role="status">Не удалось проверить вход. Проверьте соединение.</p><button className="identity-button" onClick={()=>void refresh()}>Попробовать снова</button></div>:user&&<>
 {message&&<p className="account-feedback" role="status">{message}</p>}
 {section==='learn'&&<section className="account-pane" aria-label="Ваше обучение"><div className="account-current-grade"><div><span>Ваш класс</span><strong>{grade?.title??(grades.length?'Выберите класс':'—')}</strong></div><button className="identity-secondary" type="button" aria-expanded={editingGrade} aria-controls="grade-editor" onClick={()=>setEditingGrade(v=>!v)}>{editingGrade?'Отменить':grade?'Изменить класс':'Выбрать класс'}</button></div>
 {editingGrade&&<form id="grade-editor" className="account-grade-editor" onSubmit={e=>void perform(e,'grade')}><fieldset disabled={busy||blocked}><div className="login-field"><label htmlFor="account-grade">Класс</label><select key={String(user.selected_grade_id)+'-'+grades.length} id="account-grade" name="grade" defaultValue={String(user.selected_grade_id??'')} required><option value="">Выберите класс</option>{grades.map(g=><option key={g.id} value={String(g.id)}>{g.title}</option>)}</select></div><button className="identity-button" type="submit">Сохранить класс</button></fieldset></form>}
 <div className="account-materials"><h2>Материалы</h2><p className="identity-hint">{grade?'Откройте темы своего класса.':'Все темы доступны без выбора класса.'}</p><a href={grade?'/materials?grade='+grade.number+'-klass':'/materials'}><IdentityIcon name="book"/><span>{grade?'Материалы · '+grade.title:'Все материалы'}</span><IdentityIcon name="arrow"/></a></div></section>}
 {section==='account'&&<section className="account-pane" aria-label="Настройки аккаунта"><dl className="account-login"><dt>Логин</dt><dd>{user.username}</dd></dl><h2>Почта для восстановления</h2>
 {!state?<button className="identity-secondary" onClick={()=>void load()}>Загрузить настройки</button>:<><p className="account-email">{state.email??'Почта не добавлена'}{state.email&&<span>{state.email_verified?'Подтверждена':'Ожидает подтверждения'}</span>}</p><p className="identity-hint">Почта необязательна. Без подтверждённого адреса восстановить доступ по email невозможно.</p>
 {!state.mail_available&&<p className="identity-notice">Почтовая отправка пока не подключена. Добавить и подтвердить адрес можно будет после подключения сервиса.</p>}
 {(state.mail_available||state.email)&&<form onSubmit={e=>void perform(e,'email')}><fieldset disabled={busy||blocked}>{state.mail_available?<div className="login-field"><label htmlFor="recovery-email">Почта восстановления</label><input key={state.email} id="recovery-email" name="email" type="email" autoComplete="email" maxLength={254} defaultValue={state.email??''}/><p className="identity-hint">Чтобы удалить почту, оставьте поле пустым и сохраните.</p></div>:<input type="hidden" name="email" value=""/>}<PasswordField name="current_password" label="Текущий пароль"/><button className="identity-button" type="submit">{state.mail_available?'Сохранить почту':'Удалить почту'}</button></fieldset></form>}</>}
 </section>}
 {section==='security'&&<section className="account-pane" aria-label="Защита аккаунта"><h2>Сменить пароль</h2><p className="identity-hint">После смены все устройства выйдут из аккаунта, включая это. Затем войдите с новым паролем.</p><form onSubmit={e=>void perform(e,'password')}><fieldset disabled={busy||blocked}><PasswordField name="current_password" label="Текущий пароль"/><PasswordField name="new_password" label="Новый пароль" fresh/><button className="identity-button" type="submit">Сменить пароль</button></fieldset></form>
 <div className="account-devices"><h2>Выйти со всех устройств</h2><p className="identity-hint">Завершите все сеансы, если входили на чужом устройстве. Это устройство тоже выйдет из аккаунта.</p><form onSubmit={e=>void perform(e,'sessions')}><fieldset disabled={busy||blocked}><PasswordField name="current_password" label="Текущий пароль"/><button className="identity-secondary" type="submit">Выйти везде</button></fieldset></form></div></section>}
 </>}
 </main></div></IdentityShell>;
}
