import { StrictMode, useEffect, useRef, useState, type ReactNode } from 'react';
import { createRoot } from 'react-dom/client';
import catalogue from 'virtual:mathstart-catalogue';
import './theme.css';
import './style.css';

// The existing local instance owns public content and authentication.
const site = 'http://127.0.0.1:8121';
type Topic = typeof catalogue.topics[number];
type Section = typeof catalogue.sections[number];
const subjectNotes: Record<string, string> = {
  matematika: 'От первых правил к уверенным решениям. Числа, дроби, уравнения и наглядная геометрия.',
  algebra: 'Находи закономерности, разбирайся в формулах и учись решать уравнения. Одна понятная тема за другой.',
  geometriya: 'Исследуй фигуры и их свойства. От наглядного рисунка — к понятному доказательству.',
  'veroyatnost-i-statistika': 'Учись работать с данными, оценивать вероятность и замечать закономерности.',
};
const symbol: Record<string, string> = { matematika: '±', algebra: 'ƒ', geometriya: '△', 'veroyatnost-i-statistika': '▥' };
function Icon({ name, size = 20 }: { name: 'search' | 'arrow' | 'chevron' | 'book' | 'sun' | 'moon' | 'menu' | 'close'; size?: number }) {
  const paths: Record<typeof name, ReactNode> = {
    search: <><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/></>,
    arrow: <><path d="M5 12h14M13 6l6 6-6 6"/></>,
    chevron: <path d="m9 5 7 7-7 7"/>,
    book: <><path d="M12 5v15M3 4h5a5 5 0 0 1 4 2 5 5 0 0 1 4-2h5v15h-5a5 5 0 0 0-4 2 5 5 0 0 0-4-2H3Z"/></>,
    sun: <><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/></>,
    moon: <path d="M20 14a8 8 0 0 1-10-10 8.5 8.5 0 1 0 10 10Z"/>,
    menu: <path d="M4 6h16M4 12h16M4 18h16"/>,
    close: <path d="m6 6 12 12M6 18 18 6"/>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}
function Brand() {
  return <a className="brand" href="/" aria-label="MathStart — главная"><span className="brand-mark" aria-hidden="true">√</span><span>MathStart<span className="brand-dot">.</span></span></a>;
}
function plural(count: number) {
  return count % 10 === 1 && count % 100 !== 11 ? 'тема' : count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 12 || count % 100 > 14) ? 'темы' : 'тем';
}
function App() {
  const [grade, setGrade] = useState('7-klass');
  const [subject, setSubject] = useState('algebra');
  const [query, setQuery] = useState('');
  const [dark, setDark] = useState(false);
  const [activeSection, setActiveSection] = useState<Section | null>(null);
  const [sectionQuery, setSectionQuery] = useState('');
  const topicDialog = useRef<HTMLDialogElement>(null);
  const menuDialog = useRef<HTMLDialogElement>(null);
  const search = useRef<HTMLInputElement>(null);
  const subjects = catalogue.subjects.filter(item => item.grade === grade).sort((a, b) => a.order - b.order);
  const selected = subjects.find(item => item.slug === subject)!;
  const sections = catalogue.sections.filter(item => item.grade === grade && item.subject === subject && catalogue.topics.some(topic => topic.grade === grade && topic.subject === subject && topic.section === item.slug)).sort((a, b) => a.order - b.order);
  const topics = catalogue.topics.filter(item => item.grade === grade && item.subject === subject);
  const results = query.trim() ? catalogue.topics.filter(item => item.title.toLocaleLowerCase('ru').includes(query.trim().toLocaleLowerCase('ru'))) : [];
  const visibleSections = sections.filter(item => !sectionQuery || item.title.toLocaleLowerCase('ru').includes(sectionQuery.toLocaleLowerCase('ru')));
  const sectionTopics = activeSection ? catalogue.topics.filter(item => item.grade === activeSection.grade && item.subject === activeSection.subject && item.section === activeSection.slug) : [];

  useEffect(() => { document.documentElement.dataset.theme = dark ? 'dark' : 'light'; }, [dark]);
  function chooseGrade(next: string) {
    setGrade(next);
    setSubject(catalogue.subjects.filter(item => item.grade === next).sort((a, b) => a.order - b.order)[0]!.slug);
    setQuery(''); setSectionQuery('');
  }
  function chooseSubject(next: string) { setSubject(next); setQuery(''); setSectionQuery(''); }
  function openSection(section: Section) { setActiveSection(section); topicDialog.current?.showModal(); }
  function topicLink(topic: Topic) { return `${site}/${topic.slug}/`; }
  const navigation = <>
    <p className="nav-label">ТВОЁ ОБУЧЕНИЕ</p>
    <a className="nav-home" href="#learning" onClick={() => menuDialog.current?.close()}><Icon name="book"/>Учебные материалы<span className="nav-active-dot"/></a>
    <div className="sidebar-divider"/>
    <label className="grade-select-label"><span className="nav-label">КЛАСС</span>
    <select value={grade} onChange={e => chooseGrade(e.target.value)}>{catalogue.grades.map(item => <option key={item.slug} value={item.slug}>{item.title}</option>)}</select></label>
    <p className="nav-label subject-label">ПРЕДМЕТЫ</p>
    <nav aria-label="Предметы">{subjects.map(item => <div key={item.slug}>
      <button className={`subject-button ${subject === item.slug ? 'is-selected' : ''}`} aria-current={subject === item.slug ? 'true' : undefined} onClick={() => chooseSubject(item.slug)}>
        <span className="subject-symbol" aria-hidden="true">{symbol[item.slug] ?? '∑'}</span><span>{item.title}</span><Icon name="chevron" size={14}/>
      </button>
      {subject === item.slug && <div className="section-navigation">{sections.map(section => <button key={section.slug} onClick={() => { menuDialog.current?.close(); openSection(section); }}>{section.title}</button>)}</div>}
    </div>)}</nav>
    <div className="sidebar-tip"><span aria-hidden="true">✧</span><strong>В своём темпе</strong><p>Можно начать с любой темы и вернуться к сложному позже.</p></div>
    <a className="sidebar-about" href={`${site}/o-proekte/`}>О проекте <Icon name="arrow" size={15}/></a>
  </>;

  return <>
    <a className="skip-link" href="#learning">К учебным материалам</a>
    <header className="topbar">
      <div className="topbar-brand"><button className="icon-button mobile-menu" aria-label="Открыть меню" onClick={() => menuDialog.current?.showModal()}><Icon name="menu"/></button><Brand/></div>
      <div className="global-search"><Icon name="search"/><label className="sr-only" htmlFor="topic-search">Поиск по всем темам</label><input ref={search} id="topic-search" placeholder="Какую тему хочешь разобрать?" value={query} onChange={e => { setQuery(e.target.value); setSectionQuery(''); }} onKeyDown={e => { if (e.key === 'Escape') setQuery(''); }}/>{query && <button className="icon-button" aria-label="Очистить поиск" onClick={() => { setQuery(''); search.current?.focus(); }}><Icon name="close" size={16}/></button>}</div>
      <div className="header-actions"><a className="all-topics" href={`${site}/karta-sajta/`}>Все темы</a><button className="icon-button theme-button" aria-label={dark ? 'Включить светлую тему' : 'Включить тёмную тему'} onClick={() => setDark(value => !value)}><Icon name={dark ? 'sun' : 'moon'}/></button><a className="login-button" href={`${site}/account/`}>Войти <Icon name="arrow" size={16}/></a></div>
    </header>
    <aside className="sidebar">{navigation}</aside>
    <dialog ref={menuDialog} className="menu-dialog" aria-labelledby="menu-title"><div className="dialog-heading"><h2 id="menu-title">Навигация</h2><button className="icon-button" aria-label="Закрыть меню" onClick={() => menuDialog.current?.close()}><Icon name="close"/></button></div>{navigation}</dialog>
    <main id="learning" tabIndex={-1}>
      <div className="breadcrumbs"><span>Учебные материалы</span><Icon name="chevron" size={13}/><span>{catalogue.grades.find(item => item.slug === grade)!.title}</span></div>
      <div className="intro-line"><p className="eyebrow">МАЛЕНЬКИЕ ШАГИ. БОЛЬШИЕ ОТКРЫТИЯ.</p><span className="prototype-label">Пример нового дизайна</span></div>
      <section className="hero" aria-labelledby="subject-title">
        <div className="hero-copy"><div className="subject-kicker"><span aria-hidden="true">{symbol[subject]}</span>МАТЕМАТИКА СТАНОВИТСЯ ПОНЯТНЕЕ</div><h1 id="subject-title">{selected.title}<span className="hero-period">.</span></h1><p>{subjectNotes[subject] ?? 'Выбирай тему и начинай разбираться — в своём темпе.'}</p><div className="hero-tags"><span><Icon name="book" size={16}/>{topics.length} {plural(topics.length)}</span><span><span className="small-check" aria-hidden="true">✓</span>Теория и примеры</span><span>Без спешки</span></div></div>
        <div className="math-art" aria-hidden="true"><div className="art-grid"/><svg viewBox="0 0 300 200"><path className="art-axis" d="M32 154h244M82 184V22"/><path className="art-line" d="M42 164 244 35"/><circle className="art-point" cx="144" cy="99" r="6"/><circle className="art-point" cx="211" cy="56" r="6"/><path className="art-triangle" d="M144 99h67V56Z"/></svg><span className="art-formula">y = kx + b</span><span className="art-x">x</span><span className="art-y">y</span><span className="art-coordinate">(x, y)</span></div>
      </section>
      <div className="grade-bar"><span>Твой класс</span><div className="grade-options" role="group" aria-label="Выбор класса">{catalogue.grades.map(item => <button key={item.slug} aria-label={item.title} aria-pressed={grade === item.slug} onClick={() => chooseGrade(item.slug)}>{item.order}<span> класс</span></button>)}</div></div>
      <section className="materials" aria-labelledby="materials-title">
        <div className="materials-heading"><div><h2 id="materials-title">{query.trim() ? 'Найденные темы' : 'С чего начнём?'} <span className="count-badge">{query.trim() ? results.length : sections.length}</span></h2><p>{query.trim() ? 'Результаты по всем классам и предметам' : 'Выбери раздел — внутри всё разложено по темам.'}</p></div>{!query.trim() && <div className="section-filter"><Icon name="search" size={16}/><label className="sr-only" htmlFor="section-search">Найти раздел</label><input id="section-search" placeholder="Найти раздел" value={sectionQuery} onChange={e => setSectionQuery(e.target.value)}/></div>}</div>
        {query.trim() ? <div className="search-results" aria-live="polite">{results.length ? results.map(topic => <a key={topic.slug} className="result-row" href={topicLink(topic)}><div><span className="result-grade">{catalogue.grades.find(item => item.slug === topic.grade)?.title}</span><h3>{topic.title}</h3></div><Icon name="arrow"/></a>) : <div className="empty-state"><Icon name="search" size={28}/><h3>Пока ничего не нашлось</h3><p>Попробуй более короткий запрос, например «дроби» или «уравнения».</p><button className="text-button" onClick={() => { setQuery(''); search.current?.focus(); }}>Сбросить поиск</button></div>}</div>
        : <><div className="section-grid">{visibleSections.map((section, index) => {
          const children = topics.filter(topic => topic.section === section.slug);
          return <button key={section.slug} className="section-card" onClick={() => openSection(section)}><div className="card-top"><span className="card-number">{String(index + 1).padStart(2, '0')}</span><span className="card-topic-count">{children.length} {plural(children.length)}</span></div><h3>{section.title}</h3><p>{children.slice(0, 2).map(topic => topic.title).join(' · ')}</p><div className="card-bottom"><span>Открыть раздел</span><span className="card-arrow"><Icon name="arrow" size={18}/></span></div></button>;
        })}</div>{visibleSections.length === 0 && <div className="empty-state"><h3>Таких разделов нет</h3><button className="text-button" onClick={() => setSectionQuery('')}>Показать все разделы</button></div>}</>}
      </section>
      {!query.trim() && <section className="other-subjects" aria-labelledby="other-title"><h2 id="other-title">Посмотрим на математику с другой стороны?</h2><div>{subjects.filter(item => item.slug !== subject).map(item => <button key={item.slug} onClick={() => { chooseSubject(item.slug); document.getElementById('learning')?.scrollIntoView({ behavior: 'instant' }); }}><span className="other-symbol" aria-hidden="true">{symbol[item.slug]}</span><span>{item.title}<small>{catalogue.topics.filter(topic => topic.grade === grade && topic.subject === item.slug).length} тем</small></span><Icon name="arrow" size={18}/></button>)}{subjects.length === 1 && <p className="single-subject-note">Здесь математика — единый курс. Другие материалы можно посмотреть, переключив класс.</p>}</div></section>}
      <footer className="page-footer"><span>MathStart <span aria-hidden="true">·</span> Разобраться может каждый.</span><span>Прототип · ссылки на уроки и вход ведут на локальный сайт :8121</span><a href="https://www.figma.com/community/file/1652599323840288360/math-learning-website-ui">Структура: Ayush Kumbhar’s team · CC BY 4.0</a></footer>
    </main>
    <dialog ref={topicDialog} className="topics-dialog" aria-labelledby="topics-dialog-title"><div className="dialog-heading"><div><p className="eyebrow">{catalogue.grades.find(item => item.slug === activeSection?.grade)?.title} · {sectionTopics.length} {plural(sectionTopics.length)}</p><h2 id="topics-dialog-title">{activeSection?.title}</h2></div><button className="icon-button" aria-label="Закрыть раздел" onClick={() => topicDialog.current?.close()}><Icon name="close"/></button></div><p className="dialog-help">Выбери тему. Материал откроется на текущем локальном сайте MathStart.</p><div className="dialog-topic-list">{sectionTopics.map((topic, index) => <a key={topic.slug} href={topicLink(topic)}><span className="topic-index">{String(index + 1).padStart(2, '0')}</span><span>{topic.title}</span><Icon name="arrow" size={17}/></a>)}</div></dialog>
  </>;
}
createRoot(document.getElementById('root')!).render(<StrictMode><App/></StrictMode>);
