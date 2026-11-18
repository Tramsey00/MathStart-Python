import { Brand } from '../../shared/ui/brand';
import { LessonFooter, LessonHeader } from '../../shared/lesson/lesson-shell';
import { useSiteTheme } from '../../shared/ui/use-site-theme';
import './page-status.css';

const gradeLinks = [5, 6, 7, 8, 9, 10].map(grade => ({
  title: `${grade} класс`,
  href: `/materials?grade=${grade}-klass`,
}));

export function PageStatus({ missing }: { missing: boolean }) {
  const [dark, setDark] = useSiteTheme();
  return <div className="public-status">
    <a className="skip-link" href="#main-content">К сообщению</a>
    <LessonHeader brand={<Brand />} catalogueHref="/materials"
      dark={dark} onTheme={() => setDark(!dark)} />
    <main className="public-status-main" id="main-content" tabIndex={-1} data-page-status={missing ? 404 : 500}>
      <h1>{missing ? 'Страница не найдена' : 'Не удалось открыть страницу'}</h1>
      <p>{missing ? 'Проверьте адрес или найдите нужную тему в материалах.' : 'Попробуйте обновить страницу чуть позже.'}</p>
      <div className="public-status-actions">
        <a className="public-status-primary" href="/materials">К материалам</a>
        <a href="/">На главную</a>
      </div>
    </main>
    <LessonFooter brand={<Brand />} catalogueHref="/materials" accountHref="/account/" homeHref="/" gradeLinks={gradeLinks} />
  </div>;
}
