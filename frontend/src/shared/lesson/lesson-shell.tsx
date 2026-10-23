import type { ReactNode } from 'react';
import './lesson-shell.css';

type LessonHeaderProps = {
  brand: ReactNode;
  catalogueHref: string;
  loginHref: string;
  dark: boolean;
  onTheme: () => void;
};

export function LessonHeader({ brand, catalogueHref, loginHref, dark, onTheme }: LessonHeaderProps) {
  return <header className="lesson-header"><div className="lesson-header-inner">
    <div className="lesson-header-start">{brand}</div>
    <div className="lesson-header-end">
      <nav className="lesson-header-nav" aria-label="Основная навигация"><a href={catalogueHref}><svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M12 6c-3-2-6-2-9-1v14c3-1 6-1 9 1 3-2 6-2 9-1V5c-3-1-6-1-9 1Zm0 0v14"/></svg><span>Материалы</span></a></nav>
      <button className="lesson-theme-toggle" type="button" aria-label={dark ? 'Включить светлую тему' : 'Включить тёмную тему'} onClick={onTheme}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" aria-hidden="true">{dark
          ? <><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/></>
          : <path d="M20 14a8 8 0 0 1-10-10 8.5 8.5 0 1 0 10 10Z"/>}</svg>
      </button>
      <a className="lesson-login" href={loginHref} aria-label="Войти" title="Войти">
        <svg width="23" height="23" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M10 4h7a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3h-7"/><path className="lesson-login-arrow" d="M3 12h11m-4-4 4 4-4 4"/></svg>
      </a>
    </div>
  </div></header>;
}

type GradeLink = { title: string; href: string };

export function LessonFooter({ brand, catalogueHref, accountHref, homeHref, gradeLinks }: {
  brand: ReactNode;
  catalogueHref: string;
  accountHref: string;
  homeHref: string;
  gradeLinks: readonly GradeLink[];
}) {
  return <footer className="lesson-footer"><div className="lesson-footer-inner">
    <div className="lesson-footer-main">
      <div className="lesson-footer-brand">{brand}<p>Материалы по школьной математике</p></div>
      <nav className="lesson-footer-grades" aria-label="Материалы по классам"><h2>По классам</h2><div>{gradeLinks.map(grade => <a key={grade.href} href={grade.href}>{grade.title}</a>)}</div></nav>
      <nav className="lesson-footer-nav" aria-label="Навигация в подвале"><h2>Навигация</h2>
        <a href={homeHref}>Главная</a><a href={catalogueHref}>Учебные материалы</a><a href={accountHref}>Личный кабинет</a>
      </nav>
    </div>
    <div className="lesson-footer-bottom"><span className="lesson-copyright">© {new Date().getFullYear()} MathStart</span></div>
  </div></footer>;
}

export function LessonPageShell({ children, brand, contents, catalogueHref, materialsHref, loginHref, accountHref, homeHref = '/', gradeLinks, dark, onTheme }: LessonHeaderProps & {
  children: ReactNode;
  contents: ReactNode;
  materialsHref: string;
  accountHref: string;
  homeHref?: string;
  gradeLinks: readonly GradeLink[];
}) {
  return <div className="lesson-page-shell">
    <a className="skip-link" href="#lesson-content">К тексту урока</a>
    <LessonHeader brand={brand} catalogueHref={catalogueHref} loginHref={loginHref} dark={dark} onTheme={onTheme}/>
    {contents}
    <div className="lesson-frame"><main id="lesson-content" className="lesson-article" tabIndex={-1}>{children}</main></div>
    <LessonFooter brand={brand} catalogueHref={materialsHref} accountHref={accountHref} homeHref={homeHref} gradeLinks={gradeLinks}/>
  </div>;
}
