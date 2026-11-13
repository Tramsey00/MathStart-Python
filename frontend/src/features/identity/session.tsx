import {createContext,useContext,useEffect,useRef,useState,type ReactNode} from 'react';
import {createApiClient} from '../../shared/api/client';
import type {IdentityContracts} from '../../shared/api/generated/identity-contracts';
import {IdentityIcon} from './identity-icon';
export const api=createApiClient();
export type User=IdentityContracts['get_me']['response']['data'];
type Session={user:User|null;status:'checking'|'ready'|'error';refresh:()=>Promise<User|null|undefined>};
const Context=createContext<Session|null>(null);
export function SessionProvider({children}:{children:ReactNode}){
 const [user,setUser]=useState<User|null>(null),[status,setStatus]=useState<Session['status']>('checking');
 const generation=useRef(0);
 async function refresh(){const sequence=++generation.current;const r=await api.call('get_me',{});if(sequence!==generation.current)return undefined;
  if(r.ok){setUser(r.value.data);setStatus('ready');return r.value.data;}
  if(r.error.code==='AUTHENTICATION_REQUIRED'){setUser(null);setStatus('ready');return null;}
  setStatus('error');return undefined;
 }
 useEffect(()=>{void refresh();const update=()=>void refresh();window.addEventListener('focus',update);return()=>{generation.current++;window.removeEventListener('focus',update);};},[]);
 return <Context.Provider value={{user,status,refresh}}>{children}</Context.Provider>;
}
const neutral:Session={user:null,status:'checking',refresh:async()=>undefined};
export function useSession(){return useContext(Context)??neutral;}
export function safeReturn(value:string|null){
 if(!value||!value.startsWith('/')||value.startsWith('//')||/[\\\u0000-\u0020]/.test(value)||/%(?:2f|5c|0[0-9a-f]|1[0-9a-f]|20|25)/i.test(value))return '/account/';
 try{const url=new URL(value,'https://mathstart.invalid');if(url.origin!=='https://mathstart.invalid'||/^\/auth(?:\/|$)/i.test(decodeURIComponent(url.pathname)))return '/account/';return url.pathname+url.search+url.hash;}catch{return '/account/';}
}
export function AuthLink(){const {user,status}=useSession();const label=status==='ready'?(user?'Личный кабинет':'Войти'):'Аккаунт';
 return <a className="site-auth-link" href={user||status!=='ready'?'/account/':'/auth?mode=login'} aria-busy={status==='checking'}><IdentityIcon name="user"/><span>{label}</span></a>;
}
