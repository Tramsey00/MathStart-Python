import {HomeIdentity} from '../identity/auth-form';
import {useState} from 'react';
import {IdentityIcon} from '../identity/identity-icon';
import {useCatalogue} from './catalogue-context';
import {Brand, LandingHeader, useSiteTheme} from './site-shell';

export function HomePage() {
  const [dark, setDark] = useSiteTheme();
  const catalogue = useCatalogue();
  const [selected, setSelected] = useState(catalogue.grades.find(g => g.slug === '7-klass')?.slug ?? catalogue.grades[0]?.slug);
  const grade = catalogue.grades.find(g => g.slug === selected);
  return <><a className="skip-link" href="#home-main">К содержимому</a><LandingHeader dark={dark} onTheme={() => setDark(value => !value)}/>
    <main className="landing-main" id="home-main" tabIndex={-1}>
      <section className="homepage-intro" aria-labelledby="home-title">
        <div className="home-intro-copy"><h1 id="home-title">Математика.<br/>Начните со своей темы.</h1><p>Объяснения и самопроверка для 5–10 классов. Материалы доступны без регистрации.</p>
          <section className="home-class-surface" aria-labelledby="home-class-title"><h2 id="home-class-title">Какой класс вы изучаете?</h2>
            <div className="home-grades" role="group" aria-label="Выберите класс">{catalogue.grades.map(g => <button key={g.slug} type="button" aria-pressed={selected === g.slug} onClick={() => setSelected(g.slug)}>{g.title}</button>)}</div>
            <nav className="home-subjects" aria-label={`Предметы · ${grade?.title ?? ''}`}>{catalogue.subjects.filter(s => s.grade === selected).map(s => <a key={s.slug} href={`/materials?grade=${encodeURIComponent(selected ?? '')}&subject=${encodeURIComponent(s.slug)}`}><IdentityIcon name="book"/><span>{s.title}</span><IdentityIcon name="arrow"/></a>)}</nav>
          </section>
        </div>
        <HomeIdentity/>
      </section>
    </main><footer className="home-footer"><div><Brand/><span>Математика для 5–10 классов</span></div><a href="/materials">Все материалы <IdentityIcon name="arrow"/></a></footer>
  </>;
}
