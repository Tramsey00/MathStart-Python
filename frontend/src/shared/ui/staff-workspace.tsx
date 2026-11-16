import {createContext,useContext,useEffect,useRef,useState,type ReactNode} from 'react';
import {useLocation} from 'react-router';
import {Brand} from './brand';
import {LessonHeader,LessonFooter} from '../lesson/lesson-shell';
import {useSiteTheme} from './use-site-theme';
import {useSession,safeReturn,api as identityApi} from '../../features/identity/session';
import {loadStaffCapabilities,emptyStaffCapabilities,type StaffCapabilities} from '../api/staff-capabilities';
import './staff.css';

export const staffResources=[['grades','content/grade','Классы'],['subjects','content/subject','Предметы'],['sections','content/section','Разделы'],['pages','content/contentpage','Страницы'],['publications','content/lessonpublication','Публикации'],['media_assets','content/mediaasset','Медиафайлы'],['redirects','content/redirect','Перенаправления'],['users','auth/user','Пользователи'],['groups','auth/group','Группы']] as const;

const StaffAccess=createContext<StaffCapabilities>(emptyStaffCapabilities());
export const useStaffCapabilities=()=>useContext(StaffAccess);
type Access={phase:'checking'|'staff'|'denied'|'error';actor:string|null;hints:StaffCapabilities};

// Hints only control presentation. Every API operation checks its own gate.
export function StaffWorkspace({children}:{children:ReactNode}){
 const [dark,setDark]=useSiteTheme(),{pathname}=useLocation(),{user,status,refresh}=useSession();
 const [access,setAccess]=useState<Access>({phase:'checking',actor:null,hints:emptyStaffCapabilities()});
 const [checking,setChecking]=useState(true),[retry,setRetry]=useState(0);
 const sequence=useRef(0),abort=useRef<AbortController|null>(null),frame=useRef<HTMLDivElement>(null);
 const identity=user?String(user.id):null;
 const login='/auth?mode=login&return='+encodeURIComponent(safeReturn(pathname));
 useEffect(()=>{
  async function reconcile(){
   const own=++sequence.current;abort.current?.abort();abort.current=new AbortController();const signal=abort.current.signal;
   setChecking(true);
   const fail=(phase:Access['phase'])=>{setAccess({phase,actor:null,hints:emptyStaffCapabilities()});setChecking(false);};
   const before=await identityApi.call('get_me',{signal});
   if(own!==sequence.current)return;
   if(!before.ok){if(before.error.code==='AUTHENTICATION_REQUIRED'){fail('denied');window.location.replace(login);}else fail('error');return;}
   const hints=await loadStaffCapabilities(signal);
   const after=await identityApi.call('get_me',{signal});
   if(own!==sequence.current)return;
   if(!after.ok){if(after.error.code==='AUTHENTICATION_REQUIRED'){fail('denied');window.location.replace(login);}else fail('error');return;}
   if(String(before.value.data.id)!==String(after.value.data.id)){fail('error');window.location.reload();return;}
   if(!hints){fail('error');return;}
   if(String(after.value.data.id)!==identity){const current=await refresh();if(own!==sequence.current)return;if(!current){fail('error');return;}}
   setAccess({phase:hints.own_password?'staff':'denied',actor:String(after.value.data.id),hints});setChecking(false);
  }
  // Keep ordinary form state on blur. Hide it while revalidating on return;
  // discard it only after a real denial, identity or permission-scope change.
  const hide=()=>{if(frame.current){frame.current.hidden=true;frame.current.inert=true;}setChecking(true);};
  const visibility=()=>{if(document.hidden)hide();else void reconcile();};
  const pageshow=(event:PageTransitionEvent)=>{if(event.persisted)void reconcile();};
  const denied=()=>void reconcile();
  void reconcile();window.addEventListener('focus',denied);document.addEventListener('visibilitychange',visibility);
  window.addEventListener('pagehide',hide);window.addEventListener('pageshow',pageshow);window.addEventListener('mathstart-staff-denied',denied);
  return()=>{sequence.current++;abort.current?.abort();window.removeEventListener('focus',denied);document.removeEventListener('visibilitychange',visibility);window.removeEventListener('pagehide',hide);window.removeEventListener('pageshow',pageshow);window.removeEventListener('mathstart-staff-denied',denied);};
 },[identity,pathname,retry]);
 const staff=access.phase==='staff'&&status==='ready'&&identity===access.actor;
 const hints=access.hints,info=staffResources.find(r=>pathname.startsWith('/admin/'+r[1]+'/'));
 const parts=pathname.split('/').filter(Boolean),last=parts.at(-1);
 const required=last==='add'?'add':last==='password'?'change':last==='delete'?'delete':'view';
 const permitted=!info||hints.resources[info[0]][required];
 const stateKey=access.actor+':'+JSON.stringify(hints);
 const denied=access.phase==='denied'&&identity;
 return <div className="staff-workspace">
  <a className="skip-link" href={staff&&checking?'#staff-access':'#staff-main'}>К содержимому</a>
  <LessonHeader brand={<Brand/>} catalogueHref="/materials" loginHref={login} dark={dark} onTheme={()=>setDark(v=>!v)}/>
  {staff&&<div ref={frame} className="staff-frame" hidden={checking} inert={checking} key={stateKey}>
   <aside className="staff-sidebar"><nav aria-label="Администрирование">
    <a href="/admin/" aria-current={pathname==='/admin/'?'page':undefined}>Все разделы</a>
    {staffResources.filter(r=>Object.values(hints.resources[r[0]]).some(Boolean)).map(r=><a key={r[0]} href={'/admin/'+r[1]+'/'} aria-current={pathname.startsWith('/admin/'+r[1]+'/')?'page':undefined}>{r[2]}</a>)}
    <a href="/admin/password_change/" aria-current={pathname.startsWith('/admin/password_change/')?'page':undefined}>Мой пароль</a>
   </nav></aside>
   <div className="staff-content"><StaffAccess.Provider value={hints}>{permitted?children:<main id="staff-main" tabIndex={-1}><h1>Нет доступа</h1><p>У вас нет разрешения на это действие.</p><a href="/admin/">К доступным разделам</a></main>}</StaffAccess.Provider></div>
  </div>}
  {(!staff||checking)&&<main id={staff?'staff-access':'staff-main'} className="staff-access" tabIndex={-1}>
   <h1>{denied&&!checking?'Нет доступа':access.phase==='error'?'Не удалось проверить доступ':'Проверяем доступ'}</h1>
   <p role="status">{denied&&!checking?'Этот раздел доступен сотрудникам MathStart.':access.phase==='error'?'Проверьте соединение и попробуйте ещё раз.':'Подождите, проверяем сессию и разрешения.'}</p>
   <div className="staff-access-actions">{access.phase==='error'&&<button className="ms-ui-button" onClick={()=>setRetry(v=>v+1)}>Повторить проверку</button>}<a href="/account/">Личный кабинет</a><a href="/">На главную</a></div>
  </main>}
  <LessonFooter brand={<Brand/>} catalogueHref="/materials" accountHref="/account/" homeHref="/" gradeLinks={[5,6,7,8,9,10].map(n=>({title:n+' класс',href:'/materials?grade='+n+'-klass'}))}/>
 </div>;
}

export function StaffHeading({title,mode,children}:{title:string;mode?:string;children?:ReactNode}){
 return <header className="staff-heading"><div><h1>{title}</h1>{mode&&<p>{mode}</p>}</div>{children}</header>;
}
