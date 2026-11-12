import {HomeIdentity} from '../identity/auth-form';
import { LandingHeader, SiteFooter, site, useSiteTheme } from './site-shell';

export function HomePage() {
  const [dark, setDark] = useSiteTheme();
  return <><a className="skip-link" href="#home-main">К содержимому</a><LandingHeader dark={dark} onTheme={() => setDark(value => !value)}/>
    <main className="landing-main" id="home-main" tabIndex={-1}>
      <section className="homepage-intro" aria-labelledby="home-title">
        <div className="home-intro-copy"><h1 id="home-title">Математика<br/>для 5–10 классов</h1><p>Дроби, уравнения, функции и геометрия. Объяснения правил и разборы задач из школьной программы.</p><div className="materials-entry"><a className="materials-entry-link" href="/materials">Открыть материалы</a><span className="open-access-note">Без регистрации</span></div></div>
        <HomeIdentity/>
      </section>
    </main><SiteFooter/>
  </>;
}
