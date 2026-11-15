import { useCatalogue } from './catalogue-context';
import { Brand } from '../../shared/ui/brand';
import { LessonFooter } from '../../shared/lesson/lesson-shell';
export { useSiteTheme } from '../../shared/ui/use-site-theme';


export function SiteFooter({ cataloguePage = false }: { cataloguePage?: boolean }) {
  const catalogue = useCatalogue();
  const gradeLinks = catalogue.grades.map(grade => ({ title: grade.title, href: `/materials?grade=${grade.slug}` }));
  return <div className={cataloguePage ? 'catalogue-footer' : undefined}>
    <LessonFooter brand={<Brand />} catalogueHref="/materials" accountHref="/account/"
      homeHref="/" gradeLinks={gradeLinks} />
  </div>;
}
