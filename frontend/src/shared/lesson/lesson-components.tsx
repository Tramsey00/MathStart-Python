import { useEffect, useId, useRef, useState, type ReactNode } from 'react';
import type { LessonSectionData, LessonTopic } from './lesson-types';

function ContentsIcon() {
  return <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true"><path d="M9 6h11M9 12h11M9 18h11M4 6h.01M4 12h.01M4 18h.01"/></svg>;
}

export type LessonBreadcrumb = { label: string; href?: string };

export function LessonHeading({ breadcrumbs, title, subtitle }: {
  breadcrumbs: readonly LessonBreadcrumb[]; title: ReactNode; subtitle?: ReactNode;
}) {
  return <header className="lesson-heading">
    <nav className="lesson-breadcrumbs" aria-label="Расположение темы"><ol>{breadcrumbs.map((item, index) => <li key={index}>
      {index > 0 && <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.4" aria-hidden="true"><path d="m6 4 4 4-4 4"/></svg>}
      {item.href ? <a href={item.href}>{item.label}</a> : <span>{item.label}</span>}
    </li>)}</ol></nav>
    <h1>{title}</h1>{subtitle && <p>{subtitle}</p>}
  </header>;
}

export function LessonContents({ sections, title, catalogueHref }: { sections: readonly LessonSectionData[]; title: string; catalogueHref: string }) {
  const [enhanced, setEnhanced] = useState(false);
  useEffect(() => setEnhanced(true), []);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(sections[0]?.id);
  const dialog = useRef<HTMLDialogElement>(null);
  const identity = useId();

  useEffect(() => {
    let frame = 0;
    const update = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const current = [...sections].reverse().find(section => {
          const element = document.getElementById(section.id);
          return element && element.getBoundingClientRect().top <= 160;
        });
        setActive(current?.id ?? sections[0]?.id);
      });
    };
    update();
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('scroll', update);
      window.removeEventListener('resize', update);
    };
  }, [sections]);

  useEffect(() => {
    const panel = dialog.current;
    if (!panel) return;
    if (open) {
      panel.showModal();
      const previous = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      return () => { document.body.style.overflow = previous; };
    }
    if (panel.open) panel.close();
  }, [open]);

  return <>
    <nav className="lesson-static-contents" aria-label="Разделы урока" hidden={enhanced}><details><summary>Содержание урока</summary><ol>{sections.map(section => <li key={section.id}><a href={`#${section.id}`}>{section.title}</a></li>)}</ol></details></nav>
    <aside className="lesson-rail" aria-label="Навигация по уроку">
      <button className="lesson-contents-trigger" type="button" aria-label="Содержание урока" title="Содержание урока" aria-haspopup="dialog" aria-expanded={open} aria-controls={identity} onClick={() => setOpen(true)}>
        <ContentsIcon/><span>Содержание</span>
      </button>
    </aside>
    <dialog ref={dialog} id={identity} className="lesson-contents-panel" aria-label="Содержание урока" aria-describedby={`${identity}-title`} onCancel={event => { event.preventDefault(); setOpen(false); }} onClose={() => setOpen(false)} onKeyDown={event => {
      if (event.key !== 'Tab') return;
      const controls = event.currentTarget.querySelectorAll<HTMLElement>('button,a[href]');
      const first = controls[0], last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    }} onClick={event => {
      if (event.target !== event.currentTarget) return;
      const box = event.currentTarget.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) setOpen(false);
    }}>
      <div className="lesson-panel-rail"><button className="lesson-panel-close" type="button" aria-label="Закрыть содержание" onClick={() => setOpen(false)} autoFocus><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg></button></div>
      <div className="lesson-panel-body"><div className="lesson-contents-context"><a href={catalogueHref}><svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M16 10H4m5-5-5 5 5 5"/></svg>К темам раздела</a></div>
      <h2 id={`${identity}-title`}>{title}</h2>
      <nav aria-label="Содержание урока">{sections.map((section, index) => <a key={section.id} href={`#${section.id}`} aria-current={section.id === active ? 'location' : undefined} onClick={() => {
        setActive(section.id);
        setOpen(false);
        requestAnimationFrame(() => document.getElementById(section.id)?.focus({ preventScroll: true }));
      }}><span className="lesson-contents-index" aria-hidden="true">{index + 1}.</span><span>{section.title}</span></a>)}</nav>
      </div>
    </dialog>
  </>;
}
export function LessonNote({ children }: { children: ReactNode }) { return <aside className="lesson-note">{children}</aside>; }
export function WorkedExample({ children }: { children: ReactNode }) { return <div className="worked-example">{children}</div>; }
export function SelfCheck({ question, kind, children }: { question: ReactNode; kind: 'answer' | 'solution'; children: ReactNode }) {
  return <div className="self-check"><LessonDisclosure kind={kind} question={question}>{children}</LessonDisclosure></div>;
}
export function LessonDisclosure({ kind, question, children }: { kind: 'answer' | 'solution'; question?: ReactNode; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [enhanced, setEnhanced] = useState(false);
  useEffect(() => setEnhanced(true), []);
  const identity = useId();
  return <div className="lesson-reveal" data-kind={kind} data-open={open} data-enhanced={enhanced}>
    {question && <div className="lesson-question-copy">{question}</div>}
    <button className="lesson-answer-toggle" type="button" aria-controls={identity} aria-expanded={open} onClick={() => setOpen(current => !current)}>Ответ и решение</button>
    <div className="lesson-reveal-expander" id={identity} aria-hidden={enhanced && !open} inert={enhanced && !open}>
      <div className="lesson-reveal-clip"><div className="lesson-reveal-content">{children}</div></div>
    </div>
  </div>;
}
export function LessonNavigation({ previous, next, href, catalogueHref }: {
  previous: LessonTopic | null; next: LessonTopic | null; href: (topic: LessonTopic) => string; catalogueHref: string;
}) {
  return <nav className="lesson-navigation" aria-label="Переход между темами"><div className="lesson-page-controls">
    {previous && <a className="lesson-previous" href={href(previous)} rel="prev" aria-label={`Предыдущая тема: ${previous.title}`}><span className="lesson-direction"><svg viewBox="0 0 20 20" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="M16 10H4m5-5-5 5 5 5"/></svg>Предыдущая тема</span></a>}
    {next && <a className="lesson-next" href={href(next)} rel="next" aria-label={`Следующая тема: ${next.title}`}><span className="lesson-direction">Следующая тема<svg viewBox="0 0 20 20" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="M4 10h12m-5-5 5 5-5 5"/></svg></span></a>}
    </div><a className="lesson-back" href={catalogueHref}>Все темы раздела</a></nav>;
}
