import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import lesson from 'virtual:mathstart-quadratic';
import catalogue from 'virtual:mathstart-catalogue';
import { LessonContents, LessonHeading, LessonNavigation } from '../../src/shared/lesson/lesson-components';
import { LessonSource } from '../../src/shared/lesson/source-renderer';
import { Brand, site, useSiteTheme } from './site-shell';
import { LessonPageShell } from '../../src/shared/lesson/lesson-shell';
import '../../src/shared/styles/theme.css';
import './style.css';
import '../../src/shared/lesson/lesson.css';

const catalogueHref = `/materials.html?grade=${lesson.grade}&subject=${lesson.subject}`;
const gradeLinks = catalogue.grades.map(grade => ({ title: grade.title, href: `/materials.html?grade=${grade.slug}` }));
const formulaStart = lesson.title.indexOf('y =');
function QuadraticLesson() {
  const [dark, setDark] = useSiteTheme();
  return <LessonPageShell brand={<Brand/>} contents={<LessonContents sections={lesson.sections} title={lesson.title} catalogueHref={catalogueHref}/>}
    catalogueHref={catalogueHref} materialsHref="/materials.html" loginHref="/#email-login" accountHref={`${site}/account/`} gradeLinks={gradeLinks}
    dark={dark} onTheme={() => setDark(value => !value)}>
      <LessonHeading breadcrumbs={[
        { label: catalogue.grades.find(grade => grade.slug === lesson.grade)!.title, href: `/materials.html?grade=${lesson.grade}` },
        { label: catalogue.subjects.find(subject => subject.grade === lesson.grade && subject.slug === lesson.subject)!.title, href: catalogueHref },
        { label: 'Квадратичная функция' },
      ]} title={<>{lesson.title.slice(0, formulaStart)}<span>{lesson.title.slice(formulaStart)}</span></>} subtitle={lesson.subtitle}/>
      {lesson.sections.map(section => <section className="lesson-section" id={section.id} key={section.id} tabIndex={-1}><h2>{section.title}</h2><LessonSource nodes={section.nodes}/></section>)}
      <LessonNavigation previous={lesson.previous} next={lesson.next} href={topic => `${site}/${topic.slug}/`} catalogueHref={catalogueHref}/>
  </LessonPageShell>;
}
createRoot(document.getElementById('root')!).render(<StrictMode><QuadraticLesson/></StrictMode>);
