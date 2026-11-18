import type { ReactNode } from 'react';
import { Brand } from '../../shared/ui/brand';
import { OrbitHeader } from '../../shared/ui/orbit-header';
import { useSiteTheme } from '../../shared/ui/use-site-theme';
import { LessonFooter } from '../../shared/lesson/lesson-shell';

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
