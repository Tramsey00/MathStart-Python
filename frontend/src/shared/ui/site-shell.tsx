import type { ReactNode } from "react";

export function SiteHeader() {
  return (
    <nav className="ms-site-header" aria-label="Основная навигация">
      <a className="ms-site-brand" href="/">
        <svg className="ms-brand-mark" width="32" height="32" viewBox="0 0 32 32" aria-hidden="true" focusable="false">
          <rect x="1" y="1" width="30" height="30" rx="9" fill="currentColor" />
          <path d="M8 17h4l3 6 8-14" fill="none" stroke="white" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <span>MathStart</span>
      </a>
      <div>
        <a href="/karta-sajta/">Все темы</a>
        <a href="/account/">Личный кабинет</a>
      </div>
    </nav>
  );
}

export function SiteFooter() {
  return (
    <footer className="ms-site-footer">
      <div className="ms-footer-identity">
        <a className="ms-footer-brand" href="/">MathStart</a>
        <p>Математика для 5–10 классов: объяснения, примеры и самопроверка.</p>
      </div>
      <nav className="ms-footer-links" aria-label="Навигация в подвале">
        <a href="/karta-sajta/">Все темы</a>
        <a href="/o-proekte/">О проекте</a>
        <a href="/kontakty/">Контакты</a>
      </nav>
    </footer>
  );
}

export function SiteShell({ children, skipLink }: { children?: ReactNode; skipLink?: ReactNode }) {
  return <>{skipLink}<SiteHeader />{children}<SiteFooter /></>;
}
