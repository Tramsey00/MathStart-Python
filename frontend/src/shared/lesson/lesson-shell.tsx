import type { ReactNode } from 'react';
import './lesson-shell.css';
import { OrbitHeader } from '../ui/orbit-header';

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
    <div className="lesson-footer-bottom"><span className="lesson-copyright">© 2026 MathStart</span></div>
  </div></footer>;
}

export function LessonPageShell({ children, brand, contents, catalogueHref, materialsHref, accountHref, homeHref = '/', gradeLinks, dark, onTheme }: {
  brand: ReactNode;
  catalogueHref: string;
  dark: boolean;
  onTheme: () => void;
  children: ReactNode;
  contents: ReactNode;
  materialsHref: string;
  accountHref: string;
  homeHref?: string;
  gradeLinks: readonly GradeLink[];
}) {
  return <div className="lesson-page-shell">
    <a className="skip-link" href="#lesson-content">К тексту урока</a>
    <OrbitHeader catalogueHref={catalogueHref} dark={dark} onTheme={onTheme}/>
    {contents}
    <div className="lesson-frame"><main id="lesson-content" className="lesson-article" tabIndex={-1}>{children}</main></div>
    <LessonFooter brand={brand} catalogueHref={materialsHref} accountHref={accountHref} homeHref={homeHref} gradeLinks={gradeLinks}/>
  </div>;
}
