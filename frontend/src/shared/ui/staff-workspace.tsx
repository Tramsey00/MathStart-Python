import {RouteErrorPage} from './route-error-page';
import {useEffect,useRef,useState,type ReactNode} from 'react';
import {Link,useLocation} from 'react-router';
import {Brand} from './brand';
import {OrbitHeader} from '../../features/public-pages/orbit-shell';
import {LessonFooter} from '../lesson/lesson-shell';
import {useSiteTheme} from './use-site-theme';
import {useSession,safeReturn,api as identityApi} from '../../features/identity/session';
import {loadStaffCapabilities,emptyStaffCapabilities,type StaffCapabilities} from '../api/staff-capabilities';
import {StaffAccess} from './staff-access-context';
export {useStaffCapabilities} from './staff-access-context';
import './staff.css';

export const staffResources=[['users','auth/user','Пользователи'],['groups','auth/group','Группы']] as const;

type Access={phase:'checking'|'staff'|'denied'|'error';actor:string|null;path:string;hints:StaffCapabilities};

// Hints only control presentation. Every API operation checks its own gate.
export function StaffWorkspace({children}:{children:ReactNode}){
 const [dark,setDark]=useSiteTheme(),{pathname}=useLocation(),{user,status,refresh}=useSession();
 const [access,setAccess]=useState<Access>({phase:'checking',actor:null,path:'',hints:emptyStaffCapabilities()});
 const [checking,setChecking]=useState(true),[retry,setRetry]=useState(0);
 const [failure,setFailure]=useState(false);
 const sequence=useRef(0),abort=useRef<AbortController|null>(null),frame=useRef<HTMLDivElement>(null);
 const identity=user?String(user.id):null;
 const initialSharedRead=useRef(status==='checking');
 const login='/auth?mode=login&return='+encodeURIComponent(safeReturn(pathname));
 useEffect(()=>{
  // Wait for the shared session's initial read instead of racing and aborting it.
  // Coalesce focus + visibility events only while a fresh check is in flight.
  if(status==='checking'){setChecking(true);return;}
  // Only the initial checking -> ready transition supplies a just-completed
  // server read. It can be the first actor check; it is never reused on return,
  // retry or navigation. A fresh read after capabilities still closes the gate.
  let initialProfile=initialSharedRead.current&&status==='ready'?user:null;
  initialSharedRead.current=false;
  let running:Promise<void>|null=null;
  async function reconcile(){
   if(running)return running;
   running=check().finally(()=>{running=null;});return running;
  }
  async function check(){
   const own=++sequence.current;abort.current?.abort();abort.current=new AbortController();const signal=abort.current.signal;
   setChecking(true);setFailure(false);
   const fail=(phase:Access['phase'])=>{
    setFailure(phase==='error');setChecking(phase==='error');
    // A transport failure locks the existing form without discarding its draft.
    // Only a confirmed denial/actor/scope change discards the private subtree.
    setAccess(old=>phase==='error'&&old.phase==='staff'?old:{phase,actor:null,path:pathname,hints:emptyStaffCapabilities()});
   };
   const snapshot=initialProfile;initialProfile=null;
   const before=snapshot?{ok:true as const,value:{data:snapshot}}:await identityApi.call('get_me',{signal});
   if(own!==sequence.current)return;
   if(!before.ok){if(before.error.code==='AUTHENTICATION_REQUIRED'){fail('denied');window.location.replace(login);}else fail('error');return;}
   const hints=await loadStaffCapabilities(signal);
   const after=await identityApi.call('get_me',{signal});
   if(own!==sequence.current)return;
   if(!after.ok){if(after.error.code==='AUTHENTICATION_REQUIRED'){fail('denied');window.location.replace(login);}else fail('error');return;}
   if(String(before.value.data.id)!==String(after.value.data.id)){fail('error');window.location.reload();return;}
   if(!hints){fail('error');return;}
   if(String(after.value.data.id)!==identity||status!=='ready'){const current=await refresh();if(own!==sequence.current)return;if(!current){fail('error');return;}}
   setAccess({phase:hints.own_password&&staffResources.some(r=>Object.values(hints.resources[r[0]]).some(Boolean))?'staff':'denied',actor:String(after.value.data.id),path:pathname,hints});setChecking(document.hidden);
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
 },[identity,status,pathname,retry]);
 const staff=access.phase==='staff'&&identity===access.actor;
 const hints=access.hints,info=staffResources.find(r=>pathname.startsWith('/admin/'+r[1]+'/'));
 const parts=pathname.split('/').filter(Boolean),last=parts.at(-1);
 const required=last==='add'?'add':last==='password'?'change':last==='delete'?'delete':'view';
 const permitted=!info||hints.resources[info[0]][required];
 const stateKey=access.actor+':'+JSON.stringify(hints);
 const verifying=checking||failure||status!=='ready'||access.path!==pathname;
 const denied=access.phase==='denied'&&identity;
 if(!/^\/admin\/(?:$|auth\/(?:user|group)\/|password_change\/)/.test(pathname))return <RouteErrorPage missing/>;
 return <><OrbitHeader dark={dark} onTheme={()=>setDark(v=>!v)}/><div className="staff-workspace">
  <a className="skip-link" href={staff&&verifying?'#staff-access':'#staff-main'}>К содержимому</a>
  {staff&&<div ref={frame} className="staff-frame" hidden={verifying} inert={verifying} key={stateKey}>
   <aside className="staff-sidebar"><nav aria-label="Администрирование">
    {staffResources.filter(r=>Object.values(hints.resources[r[0]]).some(Boolean)).map(r=><Link key={r[0]} to={'/admin/'+r[1]+'/'} aria-current={pathname.startsWith('/admin/'+r[1]+'/')?'page':undefined}>{r[2]}</Link>)}
   </nav></aside>
   <div className="staff-content" key={pathname}><StaffAccess.Provider value={hints}>{access.path===pathname&&(permitted?children:<main id="staff-main" tabIndex={-1}><h1>Нет доступа</h1><p>У вас нет разрешения на это действие.</p><Link to="/admin/">К доступным разделам</Link></main>)}</StaffAccess.Provider></div>
  </div>}
  {(!staff||verifying)&&<main id={staff?'staff-access':'staff-main'} className="staff-access" tabIndex={-1}>
   <h1>{failure?'Не удалось проверить доступ':denied&&!checking?'Нет доступа':'Проверяем доступ'}</h1>
   <p role="status">{failure?'Проверьте соединение и попробуйте ещё раз.':denied&&!checking?'Этот раздел доступен сотрудникам MathStart.':'Подождите, проверяем сессию и разрешения.'}</p>
   <div className="staff-access-actions">{failure&&<button className="ms-ui-button" onClick={()=>setRetry(v=>v+1)}>Повторить проверку</button>}<a href="/account/">Личный кабинет</a><a href="/">На главную</a></div>
  </main>}
  <LessonFooter brand={<Brand/>} catalogueHref="/materials" accountHref="/account/" homeHref="/" gradeLinks={[5,6,7,8,9,10].map(n=>({title:n+' класс',href:'/materials?grade='+n+'-klass'}))}/>
 </div></>;
}

export function StaffHeading({title,mode,children}:{title:string;mode?:string;children?:ReactNode}){
 return <header className="staff-heading"><div><h1>{title}</h1>{mode&&<p>{mode}</p>}</div>{children}</header>;
}
