import {useEffect,useRef,useState,type ReactNode} from 'react';
import {useLocation} from 'react-router';
import {Brand} from './brand';
import {LessonHeader,LessonFooter} from '../lesson/lesson-shell';
import {useSiteTheme} from './use-site-theme';
import {useSession,api as identityApi} from '../../features/identity/session';
import {readStaffCapabilities} from '../api/staff-capabilities';
import './staff.css';

export const staffResources=[['grades','content/grade','Классы'],['subjects','content/subject','Предметы'],['sections','content/section','Разделы'],['pages','content/contentpage','Страницы'],['publications','content/lessonpublication','Публикации'],['media_assets','content/mediaasset','Медиафайлы'],['redirects','content/redirect','Перенаправления'],['users','auth/user','Пользователи'],['groups','auth/group','Группы']] as const;

// Presentation only. Every read and write still goes through the server gate.
export function StaffWorkspace({children}:{children:ReactNode}){
 const [dark,setDark]=useSiteTheme(),{pathname}=useLocation(),{user,status}=useSession();
 const [denied,setDenied]=useState(false);
 const [active,setActive]=useState(true),[epoch,setEpoch]=useState(0);
 const actor=useRef<string|null>(null),sequence=useRef(0);
 const identity=user?String(user.id):null;
 useEffect(()=>{
  if(identity&&actor.current===null)actor.current=identity;
  else if(identity&&actor.current!==identity)window.location.reload();
 },[identity]);
 useEffect(()=>{
  const hide=()=>{sequence.current++;setActive(false);};
  const reconcile=async()=>{const own=++sequence.current;setActive(false);const result=await identityApi.call('get_me',{});const next=result.ok?result.value.data:null;if(own!==sequence.current)return;if(next&&String(next.id)===actor.current){setEpoch(v=>v+1);setActive(true);}else if(next)window.location.reload();};
  const visibility=()=>{if(document.hidden)hide();else void reconcile();};
  window.addEventListener('blur',hide);window.addEventListener('focus',reconcile);document.addEventListener('visibilitychange',visibility);
  return()=>{sequence.current++;window.removeEventListener('blur',hide);window.removeEventListener('focus',reconcile);document.removeEventListener('visibilitychange',visibility);};
 },[]);
 const hints=readStaffCapabilities();
 useEffect(()=>{const deny=()=>setDenied(true);window.addEventListener('mathstart-staff-denied',deny);return()=>window.removeEventListener('mathstart-staff-denied',deny);},[]);
 const ready=!denied&&status==='ready'&&identity&&(actor.current===null||identity===actor.current)&&active;
 return <div className="staff-workspace">
  <a className="skip-link" href="#staff-main">К администрированию</a>
  <LessonHeader brand={<Brand/>} catalogueHref="/materials" loginHref="/auth?mode=login" dark={dark} onTheme={()=>setDark(v=>!v)}/>
  <div className="staff-frame">
   <aside className="staff-sidebar"><nav aria-label="Администрирование">
    <a href="/admin/" aria-current={pathname==='/admin/'?'page':undefined}>Администрирование</a>
    {ready&&staffResources.filter(r=>Object.values(hints.resources[r[0]]).some(Boolean)).map(r=><a key={r[0]} href={'/admin/'+r[1]+'/'} aria-current={pathname.startsWith('/admin/'+r[1]+'/')?'page':undefined}>{r[2]}</a>)}
    {ready&&hints.own_password&&<a href="/admin/password_change/" aria-current={pathname.startsWith('/admin/password_change/')?'page':undefined}>Мой пароль</a>}
   </nav></aside>
   {ready?<div className="staff-content" key={identity+':'+epoch+':'+pathname}>{children}</div>:<main id="staff-main" className="staff-content" tabIndex={-1}><h1>Администрирование</h1><p role="status">{denied?'Сессия истекла или доступ изменился. Откройте страницу заново.':status==='error'?'Не удалось проверить сессию. Вернитесь на страницу, чтобы повторить проверку.':status==='ready'&&!user?'Для продолжения войдите в аккаунт.':'Проверяем сессию…'}</p><a href={pathname}>Открыть заново</a> <a href={'/auth?mode=login&next='+encodeURIComponent(pathname)}>Войти</a></main>}
  </div>
  <LessonFooter brand={<Brand/>} catalogueHref="/materials" accountHref="/account/" homeHref="/" gradeLinks={[5,6,7,8,9,10].map(n=>({title:n+' класс',href:'/materials?grade='+n}))}/>
 </div>;
}

export function StaffHeading({title,mode,children}:{title:string;mode?:string;children?:ReactNode}){
 return <header className="staff-heading"><div><h1>{title}</h1>{mode&&<p>{mode}</p>}</div>{children}</header>;
}
