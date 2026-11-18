import type { ComponentProps, ReactNode } from 'react';
import { Brand } from '../../shared/ui/brand';
import { useSiteTheme } from '../../shared/ui/use-site-theme';
import { LessonHeader, LessonFooter } from '../../shared/lesson/lesson-shell';
import './orbit.css';
// Shared Orbit header; lesson/footer styling stays in the shared lesson shell.

type OrbitHeaderProps = Omit<ComponentProps<typeof LessonHeader>, 'brand' | 'catalogueHref'> & { contained?: boolean; catalogueHref?: string };
export function OrbitHeader({ contained = false, catalogueHref = '/materials', ...props }: OrbitHeaderProps) {
    const header = <LessonHeader brand={<Brand />} catalogueHref={catalogueHref} {...props} />;
    return contained ? header : <div className="orbit-site orbit-header-only">{header}</div>;
}

export function OrbitShell({ children, grades, mainId, catalogueHref = '/materials' }: { children: ReactNode; grades: readonly { title: string; href: string }[]; mainId: string; catalogueHref?: string }) {
    const [dark, setDark] = useSiteTheme();
    const home = mainId === 'home-main';
    const footer = <LessonFooter brand={<Brand />} catalogueHref={catalogueHref} accountHref="/account/" homeHref="/" gradeLinks={grades} />;
    if (!home) return <div className="account-page-shell">
        <div className="orbit-site account-page-content"><a className="skip-link" href={'#' + mainId}>К содержимому</a>
            <OrbitHeader contained catalogueHref={catalogueHref} dark={dark} onTheme={() => setDark(v => !v)} />
            {children}
        </div>
        <div className="home-lesson-footer">{footer}</div>
    </div>;
    return <><div className="orbit-site orbit-home-site"><a className="skip-link" href={'#' + mainId}>К содержимому</a>
        <OrbitHeader contained dark={dark} onTheme={() => setDark(v => !v)} />
        {children}
    </div><div className="home-lesson-footer">{footer}</div></>;
}
