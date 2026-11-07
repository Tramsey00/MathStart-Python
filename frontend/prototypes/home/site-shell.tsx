import type { ReactNode } from 'react';
import catalogue from 'virtual:mathstart-catalogue';
import { Brand } from '../../src/shared/ui/brand';
import { LessonHeader, LessonFooter } from '../../src/shared/lesson/lesson-shell';
export { Brand } from '../../src/shared/ui/brand';
export { useSiteTheme } from '../../src/shared/ui/use-site-theme';
import './shell.css';

// The existing local instance owns public content and authentication.
export const site = 'http://127.0.0.1:8121';
const gradeLinks = catalogue.grades.map(grade => ({ title: grade.title, href: `/materials.html?grade=${grade.slug}` }));

export function LandingHeader({ dark, onTheme, leading, children, actions, panel, showCatalogueLink }: {
  dark: boolean; onTheme: () => void; leading?: ReactNode; children?: ReactNode;
  actions?: ReactNode; panel?: ReactNode; showCatalogueLink?: boolean;
}) {
  return <LessonHeader brand={<Brand/>} catalogueHref="/materials.html" loginHref="/#email-login"
    dark={dark} onTheme={onTheme} leading={leading} actions={actions} panel={panel}
    showCatalogueLink={showCatalogueLink}>{children}</LessonHeader>;
}

export function SiteFooter({ cataloguePage = false }: { cataloguePage?: boolean }) {
  return <div className={cataloguePage ? 'catalogue-footer' : undefined}>
    <LessonFooter brand={<Brand/>} catalogueHref="/materials.html" accountHref={`${site}/account/`}
      homeHref="/" gradeLinks={gradeLinks}/>
  </div>;
}
