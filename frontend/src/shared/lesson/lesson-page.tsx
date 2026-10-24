import { Brand } from '../ui/brand';
import { useSiteTheme } from '../ui/use-site-theme';
import { LessonPageShell } from './lesson-shell';
import { LessonContents, LessonHeading, LessonNavigation } from './lesson-components';
import { LessonSource } from './source-renderer';
import type { LessonDocument, LessonTopic } from './lesson-types';

export interface LessonPageNavigation {
  previous: (LessonTopic & { url: string; boundary?: 'section' }) | null;
  next: (LessonTopic & { url: string; boundary?: 'section' }) | null;
}
/** Shared composition. Subject matter lives entirely in the versioned document. */
export function LessonPage({ document: lesson, navigation, gradeLinks, section }: {
  document: LessonDocument; navigation: LessonPageNavigation; gradeLinks: readonly { title: string; href: string }[]; section?: { title: string; href: string };
}) {
  const [dark, setDark] = useSiteTheme();
  const catalogueHref = `/${lesson.grade}-${lesson.subject}/`;
  return <LessonPageShell brand={<Brand/>} contents={<LessonContents sections={lesson.sections} title={lesson.title} catalogueHref={section?.href ?? catalogueHref}/>}
    catalogueHref="/karta-sajta/" materialsHref="/karta-sajta/" loginHref="/account/" accountHref="/account/" gradeLinks={gradeLinks}
    dark={dark} onTheme={() => setDark(value => !value)}>
    <LessonHeading breadcrumbs={[{ label: lesson.grade.replace('-klass', ' класс'), href: `/${lesson.grade}/` },
      { label: lesson.subject === 'algebra' ? 'Алгебра' : lesson.subject, href: catalogueHref }, section ? { label: section.title, href: section.href } : { label: lesson.section }]} title={lesson.title} subtitle={lesson.subtitle}/>
    <noscript><p>Для изменения графика и управления содержанием включите JavaScript. Все объяснения и решения доступны ниже.</p></noscript>
    {lesson.sections.map(section => <section className="lesson-section" id={section.id} key={section.id} tabIndex={-1}>
      <h2>{section.title}</h2><LessonSource nodes={section.nodes}/>
    </section>)}
    <LessonNavigation previous={navigation.previous} next={navigation.next} href={topic => (topic as LessonTopic & { url: string; boundary?: 'section' }).url} catalogueHref={section?.href ?? catalogueHref}/>
  </LessonPageShell>;
}
