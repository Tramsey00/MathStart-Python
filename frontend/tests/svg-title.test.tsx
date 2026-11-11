import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { act } from 'react';
import { renderToString } from 'react-dom/server';
import { hydrateRoot } from 'react-dom/client';
import { describe, expect, it, vi } from 'vitest';
import { LessonPage } from '../src/shared/lesson/lesson-page';
import { LessonSource } from '../src/shared/lesson/source-renderer';
import type { LessonDocument, LessonNode } from '../src/shared/lesson/lesson-types';
const root = resolve('..');
const topics = JSON.parse(readFileSync(resolve(root, 'docs/tasks/ms-t005-migration-map.json'), 'utf8')).topics
  .filter((t: { proposed_path: string }) => ['/materials/7-geometry-8', '/materials/7-geometry-9'].includes(t.proposed_path)) as { slug: string; source: string }[];
const parse = (html: string) => new DOMParser().parseFromString(html, 'text/html');
const svgMarkup = (n: Element) => n.outerHTML.replace(/<!--.*?-->/gs, '');
describe('authored SVG title preservation', () => {
  it('renders multiple title text fragments literally, retaining its ID and accessible name', () => {
    const nodes: LessonNode[] = [{ kind: 'figure', tag: 'svg', attrs: { role: 'img', 'aria-labelledby': 'fixture-title' }, children: [
      {kind:'element',tag:'title',attrs:{id:'fixture-title'},children:[{kind:'text',text:' A & '},{kind:'text',text:'B < C '}]},
    ] }];
    const output = parse(renderToString(<LessonSource nodes={nodes}/>));
    expect(output.querySelector('svg title')?.textContent).toBe(' A & B < C ');
    expect(output.querySelector('svg')?.getAttribute('aria-labelledby')).toBe('fixture-title');
    expect(output.querySelector('title')?.namespaceURI).toBe('http://www.w3.org/2000/svg');
  });
  it.each(topics)('retains complete SVG structures and title references: $slug', topic => {
    const lesson = JSON.parse(readFileSync(resolve(root, topic.source, 'content.json'), 'utf8')) as LessonDocument;
    const before = parse(readFileSync(resolve(root, topic.source, 'body.html'), 'utf8'));
    const after = parse(renderToString(<LessonPage document={lesson} navigation={{previous:null,next:null}} gradeLinks={[]}/>));
    for (const section of lesson.sections) {
      const source = before.getElementById(section.id)!;
      const rendered = after.getElementById(section.id)!;
      expect([...rendered.querySelectorAll('svg')].map(svgMarkup)).toEqual([...source.querySelectorAll('svg')].map(svgMarkup));
      for (const title of source.querySelectorAll('svg title')) {
        expect(title.textContent).not.toBe('');
        expect(after.getElementById(title.id)?.textContent).toBe(title.textContent);
      }
    }
    expect(after.body.textContent).not.toContain('[object Object]');
  });
  it.each(topics)('hydrates SVG titles without replacement or recovery: $slug', async topic => {
    vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true);
    const lesson = JSON.parse(readFileSync(resolve(root, topic.source, 'content.json'), 'utf8')) as LessonDocument;
    const content = <LessonPage document={lesson} navigation={{previous:null,next:null}} gradeLinks={[]}/>;
    const host = document.createElement('div'); host.innerHTML = renderToString(content); document.body.append(host);
    const titles = [...host.querySelectorAll('svg title')];
    const labels = titles.map(t => t.textContent); const errors: unknown[] = [];
    let hydration: ReturnType<typeof hydrateRoot> | undefined;
    try {
      await act(async () => { hydration = hydrateRoot(host, content, {onRecoverableError:e=>errors.push(e)}); });
      expect(errors).toEqual([]);
      expect([...host.querySelectorAll('svg title')]).toEqual(titles);
      expect(titles.map(t=>t.textContent)).toEqual(labels);
    } finally { await act(async()=>hydration?.unmount()); host.remove(); vi.unstubAllGlobals(); }
  });
});
