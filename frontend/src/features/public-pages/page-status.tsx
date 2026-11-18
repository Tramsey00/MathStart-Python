import { useEffect, useRef } from 'react';
import { Brand } from '../../shared/ui/brand';
import { LessonFooter } from '../../shared/lesson/lesson-shell';
import { OrbitHeader } from '../../shared/ui/orbit-header';
import { useSiteTheme } from '../../shared/ui/use-site-theme';
import { OrbitGeometry } from './orbit-geometry';
import './page-status.css';

const gradeLinks = [5, 6, 7, 8, 9, 10].map(grade => ({
  title: `${grade} класс`,
  href: `/materials?grade=${grade}-klass`,
}));

export function PageStatus({ missing }: { missing: boolean }) {
  const [dark, setDark] = useSiteTheme();
  const artwork = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const element = artwork.current;
    if (!element) return;
    const syncVisibility = () => { element.dataset.motion = document.hidden ? 'paused' : 'visible'; };
    syncVisibility();
    document.addEventListener('visibilitychange', syncVisibility);
    return () => document.removeEventListener('visibilitychange', syncVisibility);
  }, [missing]);

  return <div className="orbit-site public-status">
    <a className="skip-link" href="#main-content">К сообщению</a>
    <OrbitHeader contained dark={dark} onTheme={() => setDark(value => !value)} />
    <main className="orbit-home public-status-main" id="main-content" tabIndex={-1} data-page-status={missing ? 404 : 500}>
      <div className="public-status-layout">
        <div className="public-status-copy">
          {missing && <div className="public-status-code" aria-hidden="true">404</div>}
          <h1>{missing ? 'Страница не найдена' : 'Не удалось открыть страницу'}</h1>
          <p>{missing ? 'Проверьте адрес или найдите нужную тему в материалах.' : 'Попробуйте обновить страницу чуть позже.'}</p>
          <div className="public-status-actions">
            <a className="orbit-materials-action" href="/materials">К материалам</a>
            <a className="public-status-home" href="/">На главную</a>
          </div>
        </div>
        {missing && <div className="public-status-art" ref={artwork} aria-hidden="true"><OrbitGeometry compact /></div>}
      </div>
    </main>
    <LessonFooter brand={<Brand />} catalogueHref="/materials" accountHref="/account/" homeHref="/" gradeLinks={gradeLinks} />
  </div>;
}
