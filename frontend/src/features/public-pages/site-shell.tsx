import type { ReactNode } from 'react';
import { useCatalogue } from './catalogue-context';
import { Brand } from '../../shared/ui/brand';
import { LessonHeader, LessonFooter } from '../../shared/lesson/lesson-shell';
export { Brand } from '../../shared/ui/brand';
export { useSiteTheme } from '../../shared/ui/use-site-theme';

// All links stay on the same FastAPI origin as the current page.
export const site = '';


export function LandingHeader({ dark, onTheme, leading, children, actions, panel, showCatalogueLink }: {
  dark: boolean; onTheme: () => void; leading?: ReactNode; children?: ReactNode;
  actions?: ReactNode; panel?: ReactNode; showCatalogueLink?: boolean;
}) {
  return <LessonHeader brand={<Brand/>} catalogueHref="/materials" loginHref="/account/"
    dark={dark} onTheme={onTheme} leading={leading} actions={actions} panel={panel}
    showCatalogueLink={showCatalogueLink}>{children}</LessonHeader>;
}

export function SiteFooter({ cataloguePage = false }: { cataloguePage?: boolean }) {
  const catalogue = useCatalogue();
  const gradeLinks = catalogue.grades.map(grade => ({ title: grade.title, href: `/materials?grade=${grade.slug}` }));
  return <div className={cataloguePage ? 'catalogue-footer' : undefined}>
    <LessonFooter brand={<Brand/>} catalogueHref="/materials" accountHref={`${site}/account/`}
      homeHref="/" gradeLinks={gradeLinks}/>
  </div>;
}
