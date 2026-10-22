import { StrictMode, useState, type FormEvent } from 'react';
import { createRoot } from 'react-dom/client';
import './theme.css';
import './style.css';
import { LandingHeader, SiteFooter, site, useSiteTheme } from './site-shell';
import './landing.css';

function EmailLogin() {
  const [showPassword, setShowPassword] = useState(false);
  const [emailError, setEmailError] = useState('');
  const [message, setMessage] = useState('');
  function preview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    event.currentTarget.reset();
    setShowPassword(false);
    setMessage('Форма проверена. Вход по почте пока не подключён.');
  }
  return <section className="email-login" id="email-login" aria-labelledby="email-login-title" tabIndex={-1}>
    <h2 id="email-login-title">Войти в MathStart</h2>
    <p className="login-description">Вход по электронной почте</p>
    <form onSubmit={preview} aria-describedby="login-preview-note">
      <div className="login-field"><label htmlFor="login-email">Электронная почта</label><input id="login-email" name="email" type="email" autoComplete="email" placeholder="name@example.com" required aria-invalid={emailError ? 'true' : undefined} aria-describedby={emailError ? 'email-error' : undefined} onBlur={event => setEmailError(event.currentTarget.value && !event.currentTarget.validity.valid ? 'Проверь адрес: например, name@example.com' : '')} onInput={() => { setEmailError(''); setMessage(''); }}/>{emailError && <p id="email-error" className="field-error">{emailError}</p>}</div>
      <div className="login-field"><label htmlFor="login-password">Пароль</label><div className="password-input"><input id="login-password" name="password" type={showPassword ? 'text' : 'password'} autoComplete="current-password" required/><button className="password-toggle" type="button" onClick={() => setShowPassword(value => !value)} aria-label={showPassword ? 'Скрыть пароль' : 'Показать пароль'} aria-pressed={showPassword}><svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>{showPassword && <path d="m3 3 18 18"/>}</svg></button></div></div>
      <button className="email-submit" type="submit">Войти</button>
      <p id="login-preview-note" className="login-preview-note">Предпросмотр формы. Подключение почты — следующим шагом.</p>
      <p className="login-feedback" role="status">{message}</p>
    </form>
    <a className="existing-login" href={`${site}/account/`}>Войти по логину</a>
  </section>;
}

function Landing() {
  const [dark, setDark] = useSiteTheme();
  return <><a className="skip-link" href="#home-main">К содержимому</a><LandingHeader dark={dark} onTheme={() => setDark(value => !value)}/>
    <main className="landing-main" id="home-main" tabIndex={-1}>
      <section className="homepage-intro" aria-labelledby="home-title">
        <div className="home-intro-copy"><h1 id="home-title">Математика<br/>для 5–10 классов</h1><p>Дроби, уравнения, функции и геометрия. Объяснения правил и разборы задач из школьной программы.</p><div className="materials-entry"><a className="materials-entry-link" href="/materials.html">Открыть материалы</a><span className="open-access-note">Без регистрации</span></div></div>
        <EmailLogin/>
      </section>
    </main><SiteFooter/>
  </>;
}
createRoot(document.getElementById('root')!).render(<StrictMode><Landing/></StrictMode>);
