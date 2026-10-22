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
  matematika: 'Как сравнить дроби, найти неизвестное и записать условие задачи? Разбираем числа и действия с ними, учимся считать и объяснять своё решение. На примерах с дробями, процентами и величинами прослеживаем каждый шаг: от условия и выбора действия до вычислений и проверки ответа',
  algebra: 'За формулами стоят знакомые действия с числами. Разбираем выражения, решаем уравнения и смотрим, как одна зависимость записывается словами, формулой и графиком. Выясняем, что обозначают буквы и какие преобразования допустимы. В примерах со степенями, уравнениями и системами прослеживаем решение от записи условия до проверки ответа',
  geometriya: 'Что можно узнать по рисунку, а что нужно доказать? Разбираем свойства фигур, связываем условия задачи и шаг за шагом находим решение. Работаем с углами, длинами и площадями, учимся выбирать нужную теорему и объяснять, почему её можно применить. Чертёж помогает увидеть связи, а доказательство — обосновать вывод',
  'veroyatnost-i-statistika': 'Как прочитать диаграмму и сравнить данные? Разбираем случайные события, считаем вероятности и проверяем, какие выводы действительно следуют из чисел. Переходим от таблиц и отдельных наблюдений к общим характеристикам, различаем возможные исходы и учимся объяснять результат вычислений',
};
const symbol: Record<string, string> = { matematika: '±', algebra: 'ƒ', geometriya: '△', 'veroyatnost-i-statistika': '▥' };
function Icon({ name, size = 20 }: { name: 'search' | 'chevron' | 'book' | 'sun' | 'moon' | 'menu' | 'close' | 'math'; size?: number }) {
  const paths: Record<typeof name, ReactNode> = {
    search: <><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/></>,
    chevron: <path d="m9 5 7 7-7 7"/>,
    book: <><path d="M12 5v15M3 4h5a5 5 0 0 1 4 2 5 5 0 0 1 4-2h5v15h-5a5 5 0 0 0-4 2 5 5 0 0 0-4-2H3Z"/></>,
    sun: <><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/></>,
    moon: <path d="M20 14a8 8 0 0 1-10-10 8.5 8.5 0 1 0 10 10Z"/>,
    menu: <path d="M4 6h16M4 12h16M4 18h16"/>,
    close: <path d="m6 6 12 12M6 18 18 6"/>,
    math: <path d="M6 8h12M12 3v10M6 19h12"/>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}
function SubjectMark({ subject }: { subject: string }) {
  return <span className="subject-symbol" aria-hidden="true">{subject === 'matematika' ? <Icon name="math"/> : symbol[subject] ?? '∑'}</span>;
}
function Brand() {
  return <a className="brand" href="/" draggable={false} aria-label="MathStart — главная"><span>Math<span className="brand-accent">Start</span></span></a>;
}
function GradePicker({ grade, onChange }: { grade: string; onChange: (value: string) => void }) {
  return <div className="grade-picker"><span className="nav-label">КЛАСС</span>
    <div className="grade-inline" role="group" aria-label="Выбор класса">{catalogue.grades.map(item => <button key={item.slug} aria-label={item.title} aria-pressed={grade === item.slug} onClick={() => onChange(item.slug)}>{item.order}</button>)}</div>
  </div>;
}
function MathIllustration() {
  return <svg className="math-illustration" viewBox="0 0 580 330" fill="none" aria-hidden="true" focusable="false">
    <path className="illustration-rule" d="M285 26v137M26 192h528"/>
    <g transform="translate(28 25)">
      <text className="illustration-caption" x="0" y="0">ЧАСТИ ЦЕЛОГО</text>
      <g className="illustration-formula" textAnchor="middle">
        <text x="28" y="43">1</text><text x="28" y="78">2</text>
        <text x="80" y="62">+</text><text x="132" y="43">1</text><text x="132" y="78">3</text>
        <text x="184" y="62">=</text><text x="225" y="43">5</text><text x="225" y="78">6</text>
      </g>
      <path className="illustration-line" d="M12 52h32m72 0h32m61 0h32" strokeWidth="1.5"/>
      <g transform="translate(0 105)">
        {[0, 1, 2, 3, 4, 5].map(i => <rect key={i} className={i < 3 ? 'fraction-first' : i < 5 ? 'fraction-second' : 'fraction-rest'} x={i * 42} y="0" width="36" height="25" rx="2"/>)}
        <path className="illustration-construction" d="M0 35v5h120v-5m6 0v5h78v-5"/>
      </g>
    </g>
    <g transform="translate(321 25)">
      <text className="illustration-caption" x="0" y="0">НАЙТИ НЕИЗВЕСТНОЕ</text>
      <g className="illustration-formula"><text x="0" y="54">2x + 4 = 12</text><text x="0" y="99">2x = 8</text><text x="0" y="144">x = 4</text></g>
      <path className="illustration-construction" d="M172 47h24v45h-19m5-5-5 5 5 5" strokeWidth="1.3"/>
      <text className="illustration-small" x="199" y="75">−4</text>
    </g>
    <g transform="translate(28 221)">
      <text className="illustration-caption" x="0" y="0">УВИДЕТЬ ЗАКОНОМЕРНОСТЬ</text>
      <g className="illustration-points">
        <circle cx="9" cy="47" r="4"/>
        {[0, 1].flatMap(row => [0, 1].map(col => <circle key={`two-${row}-${col}`} cx={69 + col * 14} cy={40 + row * 14} r="4"/>))}
        {[0, 1, 2].flatMap(row => [0, 1, 2].map(col => <circle key={`three-${row}-${col}`} cx={143 + col * 14} cy={33 + row * 14} r="4"/>))}
      </g>
      <g className="illustration-small" textAnchor="middle"><text x="9" y="85">1</text><text x="76" y="85">4</text><text x="157" y="85">9</text><text x="220" y="51">…</text></g>
    </g>
    <g transform="translate(321 209)">
      <g className="illustration-grid"><path d="M20 28h184M20 60h184M20 76h184M36 18v74M73 18v74M147 18v74M184 18v74"/></g>
      <path className="illustration-axes" d="M20 92h194m-5-4 5 4-5 4M110 104V7m-4 5 4-5 4 5" strokeWidth="1.2"/>
      <path className="illustration-construction" d="M36 28V92M184 28V92" strokeDasharray="3 4"/>
      <path className="illustration-curve" d="M36 28Q110 156 184 28" strokeWidth="2"/>
      <g className="illustration-points"><circle cx="36" cy="28" r="3"/><circle cx="73" cy="76" r="3"/><circle cx="110" cy="92" r="3"/><circle cx="147" cy="76" r="3"/><circle cx="184" cy="28" r="3"/></g>
      <g className="illustration-ticks" textAnchor="middle"><text x="36" y="108">−2</text><text x="73" y="108">−1</text><text x="147" y="108">1</text><text x="184" y="108">2</text></g>
      <g className="illustration-ticks" textAnchor="end"><text x="103" y="104">0</text><text x="103" y="80">1</text><text x="103" y="32">4</text></g>
      <text className="illustration-small" x="133" y="14">y = x²</text><text className="illustration-axis-label" x="219" y="97">x</text><text className="illustration-axis-label" x="98" y="12">y</text>
    </g>
  </svg>;
}
function SearchEmpty({ scope, onReset }: { scope: 'topics' | 'sections'; onReset: () => void }) {
  return <div className="empty-state" role="status">
    <span className="empty-mark"><Icon name="search" size={26}/></span>
    <div className="empty-copy"><h3>{scope === 'sections' ? 'Таких разделов нет' : 'Пока ничего не нашлось'}</h3><p>{scope === 'sections' ? 'Попробуй часть названия. Поиск здесь работает только по разделам выбранного предмета' : 'Попробуй другое слово или более короткий запрос — например, «дроби»'}</p></div>
    <button className="reset-button" onClick={onReset}>{scope === 'sections' ? 'Показать все разделы' : 'Сбросить поиск'}</button>
  </div>;
}
function plural(count: number, words: readonly [string, string, string] = ['тема', 'темы', 'тем']) {
  return count % 10 === 1 && count % 100 !== 11 ? words[0] : count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 12 || count % 100 > 14) ? words[1] : words[2];
}
function isOutsideDialog(dialog: HTMLDialogElement, x: number, y: number) {
  const bounds = dialog.getBoundingClientRect();
  return x < bounds.left || x > bounds.right || y < bounds.top || y > bounds.bottom;
}
function App() {
  const [grade, setGrade] = useState('7-klass');
  const [subject, setSubject] = useState('algebra');
  const [expandedSubject, setExpandedSubject] = useState<string | null>('algebra');
  const [query, setQuery] = useState('');
  const [dark, setDark] = useState(false);
  const [activeSection, setActiveSection] = useState<Section | null>(null);
  const [sectionQuery, setSectionQuery] = useState('');
  const topicDialog = useRef<HTMLDialogElement>(null);
  const topicBackdropPress = useRef(false);
  const menuDialog = useRef<HTMLDialogElement>(null);
  const search = useRef<HTMLInputElement>(null);
  const sectionSearch = useRef<HTMLInputElement>(null);
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
    const first = catalogue.subjects.filter(item => item.grade === next).sort((a, b) => a.order - b.order)[0]!.slug;
    setSubject(first); setExpandedSubject(first);
    setQuery(''); setSectionQuery('');
  }
  function chooseSubject(next: string) { setSubject(next); setExpandedSubject(next); setQuery(''); setSectionQuery(''); }
  function toggleSubject(next: string) {
    if (next !== subject) chooseSubject(next);
    else setExpandedSubject(value => value === next ? null : next);
  }
  function openSection(section: Section) {
    setActiveSection(section);
    topicBackdropPress.current = false;
    topicDialog.current?.showModal();
    if (topicDialog.current) topicDialog.current.scrollTop = 0;
  }
  function topicLink(topic: Topic) { return `${site}/${topic.slug}/`; }
  const navigation = (surface: 'desktop' | 'mobile') => <>
    <GradePicker grade={grade} onChange={chooseGrade}/>
    <p className="nav-label subject-label">ПРЕДМЕТЫ</p>
    <nav aria-label="Предметы">{subjects.map(item => <div key={item.slug}>
      <button className={`subject-button ${subject === item.slug ? 'is-selected' : ''}`} aria-current={subject === item.slug ? 'true' : undefined} aria-expanded={subject === item.slug && expandedSubject === item.slug} aria-controls={`${surface}-sections-${item.slug}`} onClick={() => toggleSubject(item.slug)}>
        <SubjectMark subject={item.slug}/><span>{item.title}</span><Icon name="chevron" size={14}/>
      </button>
      <div id={`${surface}-sections-${item.slug}`} className="section-navigation" hidden={subject !== item.slug || expandedSubject !== item.slug}>{subject === item.slug && sections.map(section => <button key={section.slug} onClick={() => { menuDialog.current?.close(); openSection(section); }}>{section.title}</button>)}</div>
    </div>)}</nav>
  </>;

  return <>
    <a className="skip-link" href="#learning">К учебным материалам</a>
    <header className="topbar">
      <div className="topbar-brand"><button className="icon-button mobile-menu" aria-label="Открыть меню" onClick={() => menuDialog.current?.showModal()}><Icon name="menu"/></button><Brand/></div>
      <div className="global-search"><Icon name="search"/><label className="sr-only" htmlFor="topic-search">Поиск по всем темам</label><input ref={search} id="topic-search" placeholder="Какую тему хочешь разобрать?" value={query} onChange={e => { setQuery(e.target.value); setSectionQuery(''); }} onKeyDown={e => { if (e.key === 'Escape') setQuery(''); }}/>{query && <button className="icon-button" aria-label="Очистить поиск" onClick={() => { setQuery(''); search.current?.focus(); }}><Icon name="close" size={16}/></button>}</div>
      <div className="header-actions"><a className="all-topics" href={`${site}/karta-sajta/`}>Все темы</a><button className="icon-button theme-button" aria-label={dark ? 'Включить светлую тему' : 'Включить тёмную тему'} onClick={() => setDark(value => !value)}><Icon name={dark ? 'sun' : 'moon'}/></button><a className="login-button" href={`${site}/account/`}>Войти</a></div>
    </header>
    <aside className="sidebar">{navigation('desktop')}</aside>
    <dialog ref={menuDialog} className="menu-dialog" aria-labelledby="menu-title"><div className="dialog-heading"><h2 id="menu-title">Навигация</h2><button className="icon-button" aria-label="Закрыть меню" onClick={() => menuDialog.current?.close()}><Icon name="close"/></button></div>{navigation('mobile')}</dialog>
    <main id="learning" tabIndex={-1}>
      <div className="mobile-grade-selector"><GradePicker grade={grade} onChange={chooseGrade}/></div>
      <section className="hero" aria-labelledby="subject-title">
        <div className="hero-copy"><div className="subject-kicker"><SubjectMark subject={subject}/>{catalogue.grades.find(item => item.slug === grade)!.title}</div><h1 id="subject-title">{selected.title}</h1><p>{subjectNotes[subject] ?? 'Выбирай тему и начинай разбираться — в своём темпе'}</p></div>
        <MathIllustration/>
      </section>
      <section className="materials" aria-labelledby="materials-title">
        <div className="materials-heading"><div><h2 id="materials-title">{query.trim() ? 'Найденные темы' : 'С чего начнём?'}</h2><p>{query.trim() ? 'Результаты по всем классам и предметам' : 'Выбери раздел — внутри всё разложено по темам'}</p></div>{!query.trim() && <div className="section-filter"><Icon name="search" size={18}/><label className="sr-only" htmlFor="section-search">Найти раздел</label><input ref={sectionSearch} id="section-search" placeholder="Найти раздел" value={sectionQuery} onChange={e => setSectionQuery(e.target.value)} onKeyDown={e => { if (e.key === 'Escape') setSectionQuery(''); }}/>{sectionQuery && <button className="icon-button search-clear" aria-label="Очистить фильтр разделов" onClick={() => { setSectionQuery(''); sectionSearch.current?.focus(); }}><Icon name="close" size={16}/></button>}</div>}</div>
        {query.trim() ? <div className="search-results" aria-live="polite">{results.length ? results.map(topic => <a key={topic.slug} className="result-row" href={topicLink(topic)}><div><span className="result-grade">{catalogue.grades.find(item => item.slug === topic.grade)?.title} · {catalogue.subjects.find(item => item.grade === topic.grade && item.slug === topic.subject)?.title}</span><h3>{topic.title}</h3></div></a>) : <SearchEmpty scope="topics" onReset={() => { setQuery(''); search.current?.focus(); }}/>}</div>
        : <><div className="section-grid">{visibleSections.map(section => {
          const children = topics.filter(topic => topic.section === section.slug);
          return <button key={section.slug} className="section-card" onClick={() => openSection(section)}><span className="card-number">{sections.indexOf(section) + 1}</span><div className="card-copy"><h3>{section.title}</h3></div><span className="card-topic-count">{children.length} {plural(children.length)}</span></button>;
        })}</div>{visibleSections.length === 0 && <SearchEmpty scope="sections" onReset={() => { setSectionQuery(''); sectionSearch.current?.focus(); }}/>}</>}
      </section>
    </main>
    <dialog ref={topicDialog} className="topics-dialog" aria-labelledby="topics-dialog-title" aria-describedby="topics-dialog-help"
      onPointerDown={event => { topicBackdropPress.current = event.button === 0 && event.target === event.currentTarget && isOutsideDialog(event.currentTarget, event.clientX, event.clientY); }}
      onPointerCancel={() => { topicBackdropPress.current = false; }}
      onClick={event => {
        const startedOutside = topicBackdropPress.current;
        topicBackdropPress.current = false;
        if (startedOutside && event.target === event.currentTarget && isOutsideDialog(event.currentTarget, event.clientX, event.clientY)) event.currentTarget.close();
      }}>
      <div className="topics-dialog-header"><div className="topics-context"><p className="eyebrow">{catalogue.grades.find(item => item.slug === activeSection?.grade)?.title} · {catalogue.subjects.find(item => item.grade === activeSection?.grade && item.slug === activeSection?.subject)?.title}</p><button className="icon-button" aria-label="Закрыть раздел" onClick={() => topicDialog.current?.close()}><Icon name="close"/></button></div><h2 id="topics-dialog-title">{activeSection?.title}</h2></div>
      <div className="topics-dialog-body"><div className="topics-list-heading"><h3 id="topics-dialog-help">Темы раздела</h3><span>{sectionTopics.length} {plural(sectionTopics.length)}</span></div><ol className="dialog-topic-list">{sectionTopics.map((topic, index) => <li key={topic.slug}><a href={topicLink(topic)}><span className="topic-index" aria-hidden="true">{index + 1}</span><span>{topic.title}</span></a></li>)}</ol></div>
    </dialog>
  </>;
}
createRoot(document.getElementById('root')!).render(<StrictMode><App/></StrictMode>);
