import { useEffect, useRef, useState } from 'react';
import { useCatalogue } from './catalogue-context';
import { OrbitShell } from './orbit-shell';

// One shared curve for both the visible ink and the travelling dot.
const spiralTurns = 11, samplesPerTurn = 144;
const spiralPoints = Array.from({ length: spiralTurns * samplesPerTurn + 1 }, (_, i) => {
    const t = i / (spiralTurns * samplesPerTurn), angle = t * spiralTurns * Math.PI * 2;
    return [(630 - 280 * t) * Math.cos(angle), (278 - 193 * t) * Math.sin(angle)];
});
const spiralPath = spiralPoints.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(3)} ${y.toFixed(3)}`).join(' ');
function OrbitArtwork({ paused, onToggle }: { paused: boolean; onToggle: () => void }) {
    return <button type="button" className="orbit-artwork orbit-artwork-control" onClick={onToggle}
        aria-label={paused ? 'Продолжить движение спирали' : 'Остановить движение спирали'} aria-pressed={paused}>
        <svg className="orbit-artwork-svg" viewBox="-100 -100 1500 850" fill="none" aria-hidden="true" focusable="false">
        <ellipse className="orbit-hit-area" cx="0" cy="0" rx="680" ry="330" transform="translate(715 335) rotate(-26)" fill="transparent" />
        <g className="orbit-field"><g transform="translate(715 335) rotate(-26)">
            <path d={spiralPath} className="orbit-line" />
            {[0, 4, 8].map(turn => <path key={turn} className="orbit-line orbit-line-major" d={spiralPoints.slice(turn * samplesPerTurn, (turn + 1) * samplesPerTurn + 1).map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(3)} ${y.toFixed(3)}`).join(' ')} />)}
            <g className="orbit-traveller" style={{ offsetPath: `path("${spiralPath}")`, offsetRotate: '0deg' }}>
                <circle r="6" fill="var(--orb-warm)" stroke="var(--background)" strokeWidth="2" />
            </g>
        </g></g>
    </svg></button>;
}

export function HomePage() {
    const catalogue = useCatalogue(), hero = useRef<HTMLElement>(null);
    const [paused, setPaused] = useState(false), [offscreen, setOffscreen] = useState(false);
    useEffect(() => {
        // Remember only an explicit pause. A normal first visit starts animated.
        try { setPaused(localStorage.getItem('mathstart-orbit-paused') === 'true'); } catch {/* Optional storage. */ }
        const element = hero.current; if (!element) return;
        let visible = true;
        const observer = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; setOffscreen(!visible || document.hidden); }); observer.observe(element);
        const visibility = () => setOffscreen(!visible || document.hidden); document.addEventListener('visibilitychange', visibility);
        return () => { observer.disconnect(); document.removeEventListener('visibilitychange', visibility); };
    }, []);
    function toggleMotion() { const next = !paused; setPaused(next); try { localStorage.setItem('mathstart-orbit-paused', String(next)); } catch {/* Optional storage. */ } }
    return <OrbitShell mainId="home-main" grades={catalogue.grades.map(g => ({ title: g.title, href: '/materials?grade=' + encodeURIComponent(g.slug) }))}>
        <main id="home-main" className="orbit-home" tabIndex={-1}>
            <div className="orbit-light" aria-hidden="true" />
            <section ref={hero} className="orbit-hero" aria-labelledby="home-title" data-paused={paused || offscreen}>
                <div className="orbit-copy"><h1 id="home-title">Разобраться в математике.<br />Тема за темой</h1>
                    <p>Объяснения, примеры и самопроверка.<br />В своём темпе, с любой темы.</p>
                    <a className="orbit-action orbit-materials-action" href="/materials">Открыть материалы</a>
                </div>

                <OrbitArtwork paused={paused} onToggle={toggleMotion} />
                <section className="orbit-story" aria-labelledby="home-story-title"><h2 id="home-story-title">Есть тема –<br />будет понимание.</h2><div><p>Вспомнить правило перед уроком. Разобрать пример после школы. Вернуться к тому, что пока не получилось.</p><p>Выберите нужную тему и спокойно разберитесь в ней. Материалы доступны без регистрации.</p></div></section>

            </section>
        </main>
    </OrbitShell>;
}
