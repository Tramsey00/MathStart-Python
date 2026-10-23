import { Brand } from '../../src/shared/ui/brand';
export { Brand } from '../../src/shared/ui/brand';
export { useSiteTheme } from '../../src/shared/ui/use-site-theme';
import './shell.css';

// The existing local instance owns public content and authentication.
export const site = 'http://127.0.0.1:8121';
export function LandingHeader({ dark, onTheme }: { dark: boolean; onTheme: () => void }) {
  return <header className="site-header"><div className="site-header-inner"><Brand/>
    <nav aria-label="Основная навигация"><a href="/materials.html">Материалы</a></nav>
    <div className="site-header-actions"><button className="icon-button" aria-label={dark ? 'Включить светлую тему' : 'Включить тёмную тему'} onClick={onTheme}>
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">{dark ? <><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/></> : <path d="M20 14a8 8 0 0 1-10-10 8.5 8.5 0 1 0 10 10Z"/>}</svg>
    </button><a className="site-login" href="#email-login" onClick={event => { event.preventDefault(); document.getElementById('login-email')?.focus(); }}>Войти</a></div>
  </div></header>;
}
export function SiteFooter({ cataloguePage = false }: { cataloguePage?: boolean }) {
  return <footer className={`site-footer${cataloguePage ? ' catalogue-footer' : ''}`}><div className="site-footer-inner">
    <a className="footer-wordmark" href="/">Math<span>Start</span></a><nav aria-label="Навигация в подвале"><a href="/materials.html">Учебные материалы</a><a href={`${site}/account/`}>Личный кабинет</a></nav><span className="footer-copyright">© {new Date().getFullYear()} MathStart</span>
  </div></footer>;
}
