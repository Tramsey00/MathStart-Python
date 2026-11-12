import {useEffect,useId,useState,type FormEvent} from 'react';
import {api,safeReturn,useSession} from './session';
export function PasswordField({name='password',label='Пароль',fresh=false}:{name?:string;label?:string;fresh?:boolean}){
 const id=useId(),[visible,setVisible]=useState(false);
 return <div className="login-field"><label htmlFor={id}>{label}</label><div className="password-input"><input id={id} name={name} type={visible?'text':'password'} autoComplete={fresh?'new-password':'current-password'} required minLength={fresh?15:undefined} maxLength={fresh?128:4096} aria-describedby={fresh?id+'-hint':undefined}/><button className="password-toggle" type="button" onClick={()=>setVisible(v=>!v)} aria-label={visible?'Скрыть пароль':'Показать пароль'} aria-pressed={visible}><svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>{visible&&<path d="m3 3 18 18"/>}</svg></button></div>{fresh&&<p id={id+'-hint'} className="identity-hint">От 15 до 128 символов. Можно использовать фразу с пробелами.</p>}</div>;
}
export function AuthForm({register=false,returnTo=null}:{register?:boolean;returnTo?:string|null}){
 const {refresh}=useSession(),id=useId();const [busy,setBusy]=useState(false),[message,setMessage]=useState(''),[until,setUntil]=useState(0),[seconds,setSeconds]=useState(0),[uncertain,setUncertain]=useState(false);
 useEffect(()=>{const timer=setInterval(()=>setSeconds(Math.max(0,Math.ceil((until-Date.now())/1000))),1000);return()=>clearInterval(timer);},[until]);
 async function submit(e:FormEvent<HTMLFormElement>){e.preventDefault();if(busy||seconds||uncertain)return;const form=e.currentTarget,data=new FormData(form);setBusy(true);setMessage('');
  const body={username:String(data.get('username')),password:String(data.get('password'))};
  if(register&&(!/^[\p{L}\p{N}_@.+-]+$/u.test(body.username)||Array.from(body.username).length>30)){setMessage('Логин: от 1 до 30 букв, цифр или символов @ . + - _.');setBusy(false);return;}
  const r=register?await api.call('register',{body,idempotencyKey:crypto.randomUUID()}):await api.call('login',{body});
  form.querySelector<HTMLInputElement>('[name=password]')!.value='';
  if(r.ok){await refresh();window.location.assign(register?'/account/':safeReturn(returnTo));return;}
  if(r.error.outcome==='unknown'){const restored=await refresh();if(restored?.username===body.username){window.location.assign(register?'/account/':safeReturn(returnTo));return;}setUncertain(true);setMessage('Не удалось подтвердить результат. Проверьте соединение и обновите страницу перед новой попыткой.');}
  else setMessage(r.error.code==='AUTHENTICATION_REQUIRED'?'Неверный логин или пароль':r.error.code==='INVALID_REQUEST'?(register?'Проверьте логин и пароль. Логин: до 30 букв, цифр или символов @ . + − _. Пароль: от 15 символов, не распространённый и не похожий на логин.':'Проверьте введённые данные.'):r.error.message);
  setUntil(Date.now()+(r.error.retryAfterSeconds??0)*1000);setSeconds(r.error.retryAfterSeconds??0);setBusy(false);
 }
 return <form onSubmit={e=>void submit(e)} aria-busy={busy}><fieldset disabled={busy||seconds>0||uncertain}>
  <div className="login-field"><label htmlFor={id}>Логин</label><input id={id} name="username" autoComplete="username" autoCapitalize="none" spellCheck={false} required maxLength={register?30:150} aria-describedby={register?id+'-hint':undefined}/>{register&&<p id={id+'-hint'} className="identity-hint">До 30 букв, цифр или символов @ . + - _. Без пробелов.</p>}</div>
  <PasswordField fresh={register}/><button className="email-submit" type="submit">{busy?'Подождите…':register?'Создать аккаунт':'Войти'}</button></fieldset>
  <p className="login-feedback" role="status">{message}{seconds>0&&` Повторите через ${seconds} с.`}</p>
  {!register&&<a className="identity-forgot" href="/auth?mode=recover">Не помню пароль</a>}
 </form>;
}
export function HomeIdentity(){const {user,status,refresh}=useSession();return <section className="email-login" aria-labelledby="home-auth-title"><h2 id="home-auth-title">{status==='ready'&&user?'С возвращением!':'Войти в MathStart'}</h2>
 {status==='checking'?<p role="status">Проверяем сессию…</p>:status==='error'?<><p role="status">Не удалось проверить вход. Проверьте соединение.</p><button className="email-submit" onClick={()=>void refresh()}>Попробовать снова</button></>:user?<><p className="login-description">{user.username}</p><a className="email-submit identity-link" href="/account/">Личный кабинет</a></>:<><p className="login-description">Продолжите обучение в своём аккаунте</p><AuthForm/><a className="existing-login" href="/auth?mode=register">Зарегистрироваться</a></>}</section>;}
