import { createElement, type CSSProperties, type ReactNode } from 'react';
import { LessonDisclosure, LessonNote, SelfCheck, WorkedExample } from './lesson-components';
import { QuadraticGraph } from './quadratic-graph';
import { LessonDiagram } from './lesson-diagram';
import type { LessonNode } from './lesson-types';
import { LinearGraph } from '../../features/lesson-interactives/linear-graph';

function inlineStyle(value: string): CSSProperties {
  return Object.fromEntries(value.split(';').filter(part => part.includes(':')).map(part => {
    const index = part.indexOf(':');
    return [part.slice(0, index).trim().replace(/-([a-z])/g, (_, letter: string) => letter.toUpperCase()), part.slice(index + 1).trim()];
  }));
}
const propNames: Record<string, string> = { class: 'className', for: 'htmlFor', colspan: 'colSpan', rowspan: 'rowSpan', tabindex: 'tabIndex' };
export function LessonSource({ nodes }: { nodes: readonly LessonNode[] }) {
  return <>{nodes.map((node, index) => renderNode(node, index))}</>;
}
function renderNode(node: LessonNode, key: number): ReactNode {
  if (node.kind === 'text') return node.text;
  if (node.kind === 'graph') return <QuadraticGraph key={key}/>;
  if (node.kind === 'interactive') {
    const interactives = { linear: LinearGraph };
    const Interactive = interactives[node.name];
    if (!Interactive) throw Error('Unsupported lesson interactive');
    return <Interactive key={key} id={node.id}/>;
  }
  if (node.kind === 'selfCheck') return <div key={key} id={node.attrs.id}><SelfCheck kind={node.disclosure} question={<LessonSource nodes={node.question}/>}><LessonSource nodes={node.answer}/></SelfCheck></div>;
  const classes = (node.attrs.class ?? '').split(/\s+/);
  // React rejects indentation text inside table structure; it is not academic content.
  const childNodes = ['table', 'thead', 'tbody', 'tfoot', 'tr', 'colgroup'].includes(node.tag)
    ? node.children.filter(child => child.kind !== 'text' || child.text.trim()) : node.children;
  const body = <LessonSource nodes={childNodes}/>;
  if (classes.includes('ms-task')) {
    const answer = node.children.find(child => child.kind === 'element' && (child.attrs.class ?? '').split(/\s+/).includes('ms-answer'));
    if (answer?.kind !== 'element') throw Error('Self-check answer missing');
    const summary = answer.children.find(child => child.kind === 'element' && child.tag === 'summary');
    const solution = summary?.kind === 'element' && summary.children.some(child => child.kind === 'text' && child.text.includes('решение'));
    const question = node.children.filter(child => child !== answer).flatMap(child => child.kind === 'element' && child.tag === 'p' ? child.children : [child]);
    return <SelfCheck key={key} kind={solution ? 'solution' : 'answer'} question={<LessonSource nodes={question}/>}><LessonSource nodes={answer.children.filter(child => child !== summary)}/></SelfCheck>;
  }
  if (classes.includes('ms-answer')) {
    const summary = node.children.find(child => child.kind === 'element' && child.tag === 'summary');
    const isSolution = summary?.kind === 'element' && summary.children.some(child => child.kind === 'text' && child.text.includes('решение'));
    return <LessonDisclosure key={key} kind={isSolution ? 'solution' : 'answer'}><LessonSource nodes={node.children.filter(child => child !== summary)}/></LessonDisclosure>;
  }
  if (classes.includes('ms-rule-box')) {
    const first = node.children.findIndex(child => child.kind === 'text' && child.text.trim());
    const formula = node.children[first];
    if (formula?.kind === 'text' && formula.text.trim() === 'y = a(x − x₀)² + y₀') {
      let start = first + 1;
      while (start < node.children.length) {
        const child = node.children[start];
        if (!child) break;
        if (child.kind === 'text' ? !child.text.trim() : child.kind === 'element' && child.tag === 'br') start++;
        else break;
      }
      return <LessonNote key={key}><span className="ms-quadratic-formula-main lesson-vertex-formula">{formula.text}</span><LessonSource nodes={node.children.slice(start)}/></LessonNote>;
    }
  }
  if (node.kind === 'note' || classes.includes('ms-note') || classes.includes('ms-rule-box')) return <div key={key} id={node.attrs.id}><LessonNote>{body}</LessonNote></div>;
  if (node.kind === 'example' || classes.includes('ms-math-box') || classes.includes('ms-example')) return <div key={key} id={node.attrs.id}><WorkedExample>{body}</WorkedExample></div>;
  const props: Record<string, unknown> = { key };
  for (const [name, value] of Object.entries(node.attrs)) {
    if (name === 'style') { props.style = inlineStyle(value); continue; }
    const property = propNames[name] ?? (name.startsWith('aria-') || name.startsWith('data-') ? name : name.replace(/-([a-z])/g, (_, letter: string) => letter.toUpperCase()));
    props[property] = ['open', 'hidden', 'disabled'].includes(name) ? true : value;
  }
  const tag = classes.includes('ms-quadratic-steps') ? 'ol' : classes.includes('ms-quadratic-step') ? 'li' : node.tag;
  if (['br', 'hr', 'img', 'input', 'wbr'].includes(tag)) return createElement(tag, props);
  if (tag === 'table') return <div className="lesson-table-scroll" key={key}>{createElement(tag, props, body)}</div>;
  if (node.kind === 'figure' || classes.includes('ms-quadratic-svg')) return <LessonDiagram key={key} label={node.attrs['aria-label'] ?? 'Учебная схема'}>{createElement(tag, props, body)}</LessonDiagram>;
  return createElement(tag, props, body);
}
