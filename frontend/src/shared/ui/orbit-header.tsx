import type { ReactNode } from 'react';
import { AuthLink } from '../../features/identity/session';
import { Brand } from './brand';
import '../lesson/lesson-shell.css';
import '../../features/public-pages/orbit.css';

export function OrbitHeader({
  contained = false, catalogueHref = '/materials', dark, onTheme, leading, actions, panel, showCatalogueLink = true,
}: {
  contained?: boolean;
  catalogueHref?: string;
  dark: boolean;
  onTheme: () => void;
  leading?: ReactNode;
  actions?: ReactNode;
  panel?: ReactNode;
  showCatalogueLink?: boolean;
}) {
  const header = <header className="lesson-header"><div className="lesson-header-inner">
    <div className="lesson-header-start">{leading}<Brand /></div>
    <div className="lesson-header-end">
      {showCatalogueLink && <nav className="lesson-header-nav" aria-label="Основная навигация"><a href={catalogueHref}><svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M12 6c-3-2-6-2-9-1v14c3-1 6-1 9 1 3-2 6-2 9-1V5c-3-1-6-1-9 1Zm0 0v14"/></svg><span>Материалы</span></a></nav>}
      {actions}
      <button className="lesson-theme-toggle" type="button" aria-label={dark ? 'Включить светлую тему' : 'Включить тёмную тему'} onClick={onTheme}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" aria-hidden="true">
          <g className="lesson-theme-sun"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/></g>
          <path className="lesson-theme-moon" d="M20 14a8 8 0 0 1-10-10 8.5 8.5 0 1 0 10 10Z"/>
        </svg>
      </button>
      <AuthLink/>
    </div>
  </div>{panel}</header>;
  return contained ? header : <div className="orbit-site orbit-header-only">{header}</div>;
}
