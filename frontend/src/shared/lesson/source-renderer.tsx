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
type ElementNode = Extract<LessonNode, { tag: string }>;
type SourceContext = { inExample: boolean; inDiagram: boolean; preserveMarkup: boolean };
const defaultContext: SourceContext = { inExample: false, inDiagram: false, preserveMarkup: false };
function isElement(node: LessonNode): node is ElementNode { return 'tag' in node; }
function hasClass(node: LessonNode, name: string): boolean {
  return isElement(node) && (node.attrs.class ?? '').split(/\s+/).includes(name);
}
function nodeText(node: LessonNode): string {
  return node.kind === 'text' ? node.text : isElement(node) ? node.children.map(nodeText).join('') : '';
}
function containsSvg(node: LessonNode): boolean {
  return isElement(node) && (node.tag === 'svg' || node.children.some(containsSvg));
}
function isDiagramContainer(node: LessonNode): boolean {
  return isElement(node) && (node.tag === 'figure' || hasClass(node, 'ms-figure') || hasClass(node, 'ms-quadratic-figure')) && containsSvg(node);
}
function hasRetainedContent(node: LessonNode): boolean {
  if (node.kind === 'text') return !!node.text.trim();
  if (!isElement(node)) return true;
  return !!node.attrs.id || !!node.attrs.role || !!node.attrs['aria-label'] ||
    !['p', 'div', 'span', 'strong', 'b', 'em', 'i', 'br'].includes(node.tag) || node.children.some(hasRetainedContent);
}
function isBlock(node: LessonNode): boolean {
  return !isElement(node) ? node.kind !== 'text' :
    ['p', 'div', 'h2', 'h3', 'h4', 'ul', 'ol', 'table', 'figure'].includes(node.tag);
}
function compactFlow(nodes: readonly LessonNode[]): readonly LessonNode[] {
  const retained = nodes.filter(node => !(isElement(node) && node.tag === 'p' && !hasRetainedContent(node)));
  return retained.filter((node, index) => {
    if (!isElement(node) || node.tag !== 'br' || node.attrs.id) return true;
    const previous = retained.slice(0, index).reverse().find(candidate => candidate.kind !== 'text' || candidate.text.trim());
    const next = retained.slice(index + 1).find(candidate => candidate.kind !== 'text' || candidate.text.trim());
    return !!previous && !!next && !isBlock(previous) && !isBlock(next) && !(isElement(previous) && previous.tag === 'br');
  });
}
function isExampleHeading(node: LessonNode): boolean {
  return isElement(node) && ['h3', 'h4'].includes(node.tag) && /^Пример(?:\s+\d+)?[.\s:]/u.test(nodeText(node).trim());
}
function endsExample(node: LessonNode): boolean {
  return isDiagramContainer(node) || node.kind === 'figure' || node.kind === 'graph' || node.kind === 'interactive' || node.kind === 'selfCheck' ||
    (isElement(node) && ['h2', 'h3', 'h4', 'svg'].includes(node.tag)) || node.kind === 'note' || hasClass(node, 'ms-rule-box');
}
export function LessonSource({ nodes, context = defaultContext }: { nodes: readonly LessonNode[]; context?: SourceContext }) {
  const flow = context.preserveMarkup ? nodes : compactFlow(nodes);
  const rendered: ReactNode[] = [];
  for (let index = 0; index < flow.length; index++) {
    const node = flow[index]!;
    if (!context.inExample && !context.preserveMarkup && isExampleHeading(node)) {
      let end = index + 1;
      while (end < flow.length && !endsExample(flow[end]!)) end++;
      rendered.push(<WorkedExample key={index}>{flow.slice(index, end).map((child, childIndex) =>
        renderNode(child, childIndex, { ...context, inExample: true }))}</WorkedExample>);
      index = end - 1;
    } else {
      rendered.push(renderNode(node, index, context));
    }
  }
  return <>{rendered}</>;
}
function renderNode(node: LessonNode, key: number, context: SourceContext): ReactNode {
  if (node.kind === 'text') return node.text;
  if (node.kind === 'graph') return <QuadraticGraph key={key}/>;
  if (node.kind === 'interactive') {
    const interactives = { linear: LinearGraph, quadratic: QuadraticGraph };
    const Interactive = interactives[node.name];
    if (!Interactive) throw Error('Unsupported lesson interactive');
    return <Interactive key={key} id={node.id}/>;
  }
  if (node.kind === 'selfCheck') return <SelfCheck key={key} id={node.attrs.id} kind={node.disclosure} question={<LessonSource nodes={node.question}/>}><LessonSource nodes={node.answer}/></SelfCheck>;
  const classes = (node.attrs.class ?? '').split(/\s+/);
  // React rejects indentation text inside table structure; it is not academic content.
  const childNodes = ['table', 'thead', 'tbody', 'tfoot', 'tr', 'colgroup'].includes(node.tag)
    ? node.children.filter(child => child.kind !== 'text' || child.text.trim()) : node.children;
  const childContext = { ...context, preserveMarkup: context.preserveMarkup || ['svg', 'math'].includes(node.tag) };
  const body = <LessonSource nodes={childNodes} context={childContext}/>;
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
  // Legacy ms-math-box can be ordinary theory; only actual examples receive a frame.
  if (node.kind === 'example' && !context.inExample && !classes.includes('ms-math-box') && !classes.includes('ms-example')) return <div key={key} id={node.attrs.id}><WorkedExample>{body}</WorkedExample></div>;
  const props: Record<string, unknown> = { key };
  for (const [name, value] of Object.entries(node.attrs)) {
    if (name === 'style') { props.style = inlineStyle(value); continue; }
    const property = propNames[name] ?? (name.startsWith('aria-') || name.startsWith('data-') ? name : name.replace(/-([a-z])/g, (_, letter: string) => letter.toUpperCase()));
    props[property] = ['open', 'hidden', 'disabled'].includes(name) ? true : value;
  }
  const tag = classes.includes('ms-quadratic-steps') ? 'ol' : classes.includes('ms-quadratic-step') ? 'li' : node.tag;
  if (tag === 'math') {
    props.className = [...new Set([...classes.filter(Boolean), 'lesson-math'])].join(' ');
    props.xmlns = 'http://www.w3.org/1998/Math/MathML';
  }
  if (['br', 'hr', 'img', 'input', 'wbr'].includes(tag)) return createElement(tag, props);
  if (tag === 'table') return <div className="lesson-table-scroll" key={key}>{createElement(tag, props, body)}</div>;
  if (!context.inDiagram && isDiagramContainer(node)) {
    const caption = node.children.find(child => hasClass(child, 'ms-figure-title') || hasClass(child, 'ms-quadratic-figure-title') || (isElement(child) && child.tag === 'figcaption'));
    const label = node.attrs['aria-label'] ?? ((caption && nodeText(caption).trim()) || 'Учебная схема');
    const style = inlineStyle(node.attrs.style ?? '');
    const existingFrame = [style.border, style.borderWidth].some(value => value !== undefined && !/^(?:0(?:px)?|none)(?:\s|$)/.test(String(value).trim()));
    props.className = `${String(props.className ?? '')} lesson-figure-source`.trim();
    return createElement(tag, props, <LessonDiagram label={label} frame={!existingFrame}>
      <LessonSource nodes={childNodes} context={{ ...childContext, inDiagram: true }}/>
    </LessonDiagram>);
  }
  if (node.kind === 'figure' || classes.includes('ms-quadratic-svg')) {
    const drawing = createElement(tag, props, body);
    return context.inDiagram ? drawing : <LessonDiagram key={key} label={node.attrs['aria-label'] ?? 'Учебная схема'}>{drawing}</LessonDiagram>;
  }
  return createElement(tag, props, body);
}
