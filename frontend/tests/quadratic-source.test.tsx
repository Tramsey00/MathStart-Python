import { readFileSync, readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { readQuadraticLesson } from '../prototypes/home/lesson-source.mjs';
import { LessonSource } from '../src/shared/lesson/source-renderer';

const repository = resolve(process.cwd(), '..');
const directory = resolve(repository, 'curriculum/8-klass/algebra/06-kvadratichnaya-funkciya-y-ax2-funkciya-y-k-x');
const topics = readdirSync(directory).map(name => JSON.parse(readFileSync(resolve(directory, name, 'lesson.json'), 'utf8')).page);
const source = new DOMParser().parseFromString(readFileSync(resolve(directory, '06-kvadratichnaya-funkcziya-y-ax2-bx-c/body.html'), 'utf8'), 'text/html');
const lesson = readQuadraticLesson(repository, { topics });
const normalize = (value: string | null) => (value ?? '').replace(/\s+/g, ' ').trim();
function academicText(root: Node) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const text: string[] = [];
  while (walker.nextNode()) {
    const value = normalize(walker.currentNode.textContent);
    if (value) text.push(value);
  }
  return text.join(' ');
}

describe('canonical quadratic lesson adapter', () => {
  it('preserves academic text in all retained sections outside the lab and changed disclosure controls', () => {
    for (const section of lesson.sections) {
      const original = source.getElementById(section.id)!.cloneNode(true) as Element;
      original.querySelectorAll('h2,#ms-quadratic-lab-660,.ms-nav,.ms-quadratic-number,.ms-answer summary').forEach(node => node.remove());
      const rendered = new DOMParser().parseFromString(renderToStaticMarkup(<LessonSource nodes={section.nodes}/>), 'text/html');
      rendered.querySelector('[data-react-quadratic]')?.remove();
      rendered.querySelectorAll('.lesson-answer-toggle,.lesson-reveal-action,.lesson-diagram-tools,.lesson-diagram-help').forEach(node => node.remove());
      expect(academicText(rendered.body), section.id).toBe(academicText(original));
    }
  });
  it('retains all self-checks, authored drawings, worked calculations and table cells', () => {
    const rendered = new DOMParser().parseFromString(renderToStaticMarkup(<>{lesson.sections.map(section => <LessonSource key={section.id} nodes={section.nodes}/>)}</>), 'text/html');
    expect(lesson.sections).toHaveLength(8);
    expect(rendered.querySelectorAll('.self-check')).toHaveLength(10);
    expect(rendered.querySelectorAll('.self-check details')).toHaveLength(0);
    expect(rendered.querySelectorAll('.self-check .lesson-answer-toggle')).toHaveLength(10);
    expect(rendered.querySelectorAll('.self-check .lesson-reveal-expander')).toHaveLength(10);
    expect(source.querySelectorAll('.ms-math-box')).toHaveLength(7);
    expect(rendered.querySelectorAll('.worked-example')).toHaveLength(8);
    const snapshots = (document: Document, selector: string) => [...document.querySelectorAll(selector)].map(node => normalize(node.textContent));
    const answers = [...source.querySelectorAll('.ms-answer')].map(node => {
      const copy = node.cloneNode(true) as Element;
      copy.querySelector('summary')!.remove();
      return academicText(copy);
    });
    expect([...rendered.querySelectorAll('.lesson-reveal-content')].map(academicText)).toEqual(answers);
    expect([...rendered.querySelectorAll('math')].map(node => node.outerHTML)).toEqual([...source.querySelectorAll('math')].map(node => node.outerHTML));
    expect(snapshots(rendered, '.ms-values-table td,.ms-values-table th')).toEqual(snapshots(source, '.ms-values-table td,.ms-values-table th'));
    expect([...rendered.querySelectorAll('.ms-quadratic-svg')].map(node => node.outerHTML)).toEqual([...source.querySelectorAll('.ms-quadratic-svg')].map(node => node.outerHTML));
  });
  it('omits exactly the recap section and its next-topic teaser at the user’s request', () => {
    const authored = [...source.querySelectorAll('.ms-lesson-page > section:not(.ms-hero)')].map(node => node.id);
    expect(authored).toHaveLength(9);
    expect(lesson.sections.map(section => section.id)).toEqual(authored.filter(id => id !== 'lesson-section-9'));
    const preview = JSON.stringify(lesson.sections);
    expect(preview).not.toContain('Паспорт параболы');
    expect(preview).not.toContain('ms-next-topic');
  });
  it('takes adjacent lessons from the authored section ordering', () => {
    expect(lesson.previous?.slug).toBe('kak-postroit-grafik-funkczii-y-fx-m-n');
    expect(lesson.next?.slug).toBe('reshenie-kvadratnyh-uravnenij-s-pomoshhyu-grafikov-funkczij');
  });
});
