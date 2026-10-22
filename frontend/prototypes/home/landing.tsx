import { StrictMode, useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import catalogue from 'virtual:mathstart-catalogue';
import './theme.css';
import './style.css';
import { LandingHeader, SiteFooter, useSiteTheme } from './site-shell';
import './landing.css';

function SquareExample() {
  const [b, setB] = useState(2);
  const [apart, setApart] = useState(false);
  const [instant, setInstant] = useState(false);
  const unit = 224 / (4 + b), aSize = 4 * unit, bSize = b * unit;
  const origin = (340 - aSize - bSize) / 2;
  const gap = apart ? 12 : 0;
  const piece = (x: number, y: number) => ({ transform: `translate(${x}px, ${y}px)` });
  return <section className="square-example" id="example" aria-labelledby="example-title" data-instant={instant} onKeyDownCapture={() => setInstant(true)} onPointerDownCapture={() => setInstant(false)}>
    <div className="example-caption"><span>Разберём на рисунке</span><span>Алгебра</span></div>
    <h2 id="example-title">Откуда берётся <span>2ab</span>?</h2>
    <div className="square-stage">
      <svg viewBox="0 0 340 280" role="img" aria-label={`Квадрат со стороной 4 + ${b}: площади частей 16, ${4 * b}, ${4 * b} и ${b * b}`}>
        <g className="square-piece" style={piece(origin - gap, 34 - gap)}><rect width={aSize} height={aSize} className="area-a"/><text x={aSize / 2} y={aSize / 2 + 8} className="area-label light-label">a²</text></g>
        <g className="square-piece" style={piece(origin + aSize + gap, 34 - gap)}><rect width={bSize} height={aSize} className="area-ab"/><text x={bSize / 2} y={aSize / 2 + 8} className="area-label">ab</text></g>
        <g className="square-piece" style={piece(origin - gap, 34 + aSize + gap)}><rect width={aSize} height={bSize} className="area-ab"/><text x={aSize / 2} y={bSize / 2 + 8} className="area-label">ab</text></g>
        <g className="square-piece" style={piece(origin + aSize + gap, 34 + aSize + gap)}><rect width={bSize} height={bSize} className="area-b"/><text x={bSize / 2} y={bSize / 2 + 8} className="area-label">b²</text></g>
        <text x={origin + aSize / 2} y="17" className="side-label">a = 4</text><text x={origin + aSize + bSize / 2} y="17" className="side-label">b = {b}</text>
      </svg>
    </div>
    <p className="square-formula">(a + b)² = a² + <span>2ab</span> + b²</p>
    <p className="example-explanation">Два прямоугольника по <i>ab</i>.<br/>Вот почему в формуле есть <i>2ab</i>.</p>
    <div className="example-controls"><div className="range-control"><label htmlFor="square-b"><span>Измени <i>b</i></span><output htmlFor="square-b">{b}</output></label><input id="square-b" type="range" min="1" max="4" step="1" value={b} onChange={event => setB(Number(event.target.value))}/></div><button className="split-button" aria-pressed={apart} onClick={() => setApart(value => !value)}>{apart ? 'Собрать квадрат' : 'Разобрать квадрат'}</button></div>
    <p className="example-numbers" aria-live="polite">(4 + {b})² = 16 + {8 * b} + {b * b} = <strong>{(4 + b) ** 2}</strong></p>
  </section>;
}

const gradeNotes: Record<string, string> = {
  '5-klass': 'Числа и действия с ними, дроби и первые геометрические понятия',
  '6-klass': 'Отношения, проценты, рациональные числа и преобразования выражений',
  '7-klass': 'От первых уравнений — к функциям, доказательствам и работе с данными',
  '8-klass': 'Квадратные уравнения, новые функции и свойства геометрических фигур',
  '9-klass': 'Системы, последовательности и связи между знакомыми понятиями',
  '10-klass': 'Продолжение школьного курса: алгебра, геометрия и работа с данными',
};
const subjectMarks: Record<string, string> = { matematika: '±', algebra: 'ƒ', geometriya: '△', 'veroyatnost-i-statistika': '▥' };
function topicCount(count: number) {
  const word = count % 10 === 1 && count % 100 !== 11 ? 'тема' : count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 12 || count % 100 > 14) ? 'темы' : 'тем';
  return `${count} ${word}`;
}
function ClassExplorer() {
  const [grade, setGrade] = useState('7-klass');
  const subjects = catalogue.subjects.filter(item => item.grade === grade && catalogue.topics.some(topic => topic.grade === grade && topic.subject === item.slug)).sort((a, b) => a.order - b.order);
  return <section className="class-explorer reveal-section" id="classes" aria-labelledby="classes-title">
    <div className="section-intro"><div><p className="landing-eyebrow">Учебные материалы</p><h2 id="classes-title">С какой темы начнём?</h2></div><p>Выбери класс, а затем предмет.<br/>Внутри — разделы и объяснения по темам.</p></div>
    <div className="landing-grades" role="group" aria-label="Выбор класса на главной">{catalogue.grades.map(item => <button key={item.slug} aria-pressed={grade === item.slug} onClick={() => setGrade(item.slug)}><span>{item.order}</span> класс</button>)}</div>
    <div className="class-content"><p className="class-note">{gradeNotes[grade]}</p><nav aria-label="Предметы выбранного класса" className="landing-subjects">{subjects.map(subject => <a key={subject.slug} href={`/materials.html?grade=${grade}&subject=${subject.slug}`}><span className="landing-subject-mark" aria-hidden="true">{subjectMarks[subject.slug]}</span><span>{subject.title}</span><span className="subject-topic-count">{topicCount(catalogue.topics.filter(topic => topic.grade === grade && topic.subject === subject.slug).length)}</span></a>)}</nav></div>
  </section>;
}

function Landing() {
  const [dark, setDark] = useSiteTheme();
  const root = useRef<HTMLElement>(null);
  useEffect(() => {
    if (!root.current || !('IntersectionObserver' in window)) return;
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('is-seen'); observer.unobserve(entry.target); }
    }), { threshold: 0.12 });
    root.current.querySelectorAll('.reveal-section').forEach(section => observer.observe(section));
    return () => observer.disconnect();
  }, []);
  return <><a className="skip-link" href="#home-main">К содержимому</a><LandingHeader dark={dark} onTheme={() => setDark(value => !value)}/>
    <main className="landing-main" id="home-main" ref={root} tabIndex={-1}>
      <section className="landing-hero" aria-labelledby="home-title"><div className="landing-hero-copy">
        <p className="landing-eyebrow hero-entrance">Математика · 5–10 классы</p>
        <h1 id="home-title" className="hero-entrance">У каждого ответа<br/>есть <span>объяснение.</span></h1>
        <p className="landing-lead hero-entrance">Почему дроби складывают именно так?<br className="desktop-break"/> Откуда берётся формула и что показывает график?</p>
        <p className="landing-description hero-entrance">Разбирайся в знакомых темах, замечай связи и проходи решение шаг за шагом. Начать можно с того вопроса, который возник сейчас.</p>
        <div className="landing-hero-actions hero-entrance"><a className="landing-primary" href="#classes">Выбрать тему</a><a className="landing-text-link" href="/materials.html">Открыть весь каталог</a></div>
        <div className="hero-margin-note"><span className="margin-line" aria-hidden="true"/><p>Формулу легче запомнить,<br/>когда видишь, как она устроена.</p></div>
      </div><div className="hero-example-entrance"><SquareExample/></div></section>
      <ClassExplorer/>
      <section className="approach-section reveal-section" id="approach" aria-labelledby="approach-title">
        <div className="approach-copy"><p className="landing-eyebrow">От вопроса к решению</p><h2 id="approach-title">Понятно — это когда<br/>можешь объяснить.</h2><p>Одного ответа мало. Важно увидеть, почему следующий шаг получается из предыдущего.</p><a className="landing-text-link" href="/materials.html">Найти своё объяснение</a></div>
        <div className="worked-example"><p className="worked-label">Например, сумма дробей</p><div className="worked-step"><span className="worked-math">½ + ⅓</span><p>Разные части целого.<br/>Сначала сделаем их одинаковыми.</p></div><div className="worked-step"><span className="worked-math">³⁄₆ + ²⁄₆</span><p>Теперь обе дроби выражены<br/>в шестых долях.</p></div><div className="worked-step"><span className="worked-math">⁵⁄₆</span><p>Три доли и ещё две.<br/>Вместе — пять шестых.</p></div></div>
      </section>
    </main><SiteFooter/>
  </>;
}
createRoot(document.getElementById('root')!).render(<StrictMode><Landing/></StrictMode>);
