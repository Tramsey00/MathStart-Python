import { useEffect, useState } from 'react';
import catalogue from 'virtual:mathstart-catalogue';
import './shell.css';

// The existing local instance owns public content and authentication.
export const site = 'http://127.0.0.1:8121';
export function useSiteTheme() {
  const [dark, setDark] = useState(() => {
    try { return localStorage.getItem('mathstart-mode') === 'dark'; } catch { return false; }
  });
  useEffect(() => {
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    try { localStorage.setItem('mathstart-mode', dark ? 'dark' : 'light'); } catch { /* Storage is optional. */ }
  }, [dark]);
  return [dark, setDark] as const;
}
export function Brand() {
  return <a className="brand" href="/" draggable={false} aria-label="MathStart — главная"><span>Math<span className="brand-accent">Start</span></span></a>;
}
export function LandingHeader({ dark, onTheme }: { dark: boolean; onTheme: () => void }) {
  return <header className="site-header"><div className="site-header-inner"><Brand/>
    <nav aria-label="Основная навигация"><a href="/materials.html">Учебные материалы</a><a className="header-method" href="#approach">Как устроено</a></nav>
    <div className="site-header-actions"><button className="icon-button" aria-label={dark ? 'Включить светлую тему' : 'Включить тёмную тему'} onClick={onTheme}>
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">{dark ? <><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/></> : <path d="M20 14a8 8 0 0 1-10-10 8.5 8.5 0 1 0 10 10Z"/>}</svg>
    </button><a className="site-login" href={`${site}/account/`}>Войти</a></div>
  </div></header>;
}
export function SiteFooter({ cataloguePage = false }: { cataloguePage?: boolean }) {
  return <footer className={`site-footer${cataloguePage ? ' catalogue-footer' : ''}`}><div className="site-footer-inner">
    <div className="footer-intro"><a className="footer-wordmark" href="/">Math<span>Start</span></a><p>Разобраться можно.<br/>Начни с одного вопроса.</p></div>
    <div className="footer-grades"><p className="footer-label">Учебные материалы</p><nav aria-label="Классы в подвале">{catalogue.grades.map(grade => <a key={grade.slug} href={`/materials.html?grade=${grade.slug}`}>{grade.title}</a>)}</nav></div>
    <div className="footer-more"><p className="footer-label">MathStart</p><a href="/">Главная</a><a href="/materials.html">Каталог тем</a><a href={`${site}/account/`}>Личный кабинет</a></div>
  </div><div className="footer-bottom"><span>© {new Date().getFullYear()} MathStart</span><span>Математика, шаг за шагом</span></div></footer>;
}
