import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { act } from 'react';
import { renderToString } from 'react-dom/server';
import { hydrateRoot } from 'react-dom/client';
import { describe, expect, it, vi } from 'vitest';
import { convertLesson } from '../scripts/convert-lesson.mjs';
import { LessonPage } from '../src/shared/lesson/lesson-page';
import type { LessonDocument } from '../src/shared/lesson/lesson-types';

const directory = resolve('../curriculum/7-klass/algebra/02-linejnaya-funkciya-y-kx-b/03-linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii');
const document = JSON.parse(readFileSync(directory + '/content.json', 'utf8')) as LessonDocument;
const source = new DOMParser().parseFromString(readFileSync(directory + '/body.html', 'utf8'), 'text/html');
const page = <LessonPage document={document} navigation={{ previous: null, next: null }} gradeLinks={[]}/>;
const normalize = (s: string | null) => (s ?? '').replace(/\s+/g, ' ').trim();

describe('linear lesson document preservation and SSG', () => {
  it('is the complete reviewed conversion, including all source sections and academic blocks', () => {
    expect(document).toEqual(convertLesson(directory));
    expect(document.sections).toHaveLength(13);
    const rendered = new DOMParser().parseFromString(renderToString(page), 'text/html');
    expect(rendered.querySelectorAll('.self-check')).toHaveLength(13);
    expect(rendered.querySelectorAll('.lesson-section table')).toHaveLength(4);
    expect(rendered.querySelectorAll('.lesson-diagram svg')).toHaveLength(3);
    for (const section of document.sections) {
      const before = source.getElementById(section.id)!.cloneNode(true) as HTMLElement;
      // Replaced UI is not academic prose. Keep the authored observation below it.
      const lab = before.querySelector('#ms-linear-lab-723');
      if (lab) lab.replaceWith(...Array.from(lab.querySelectorAll(':scope > p')));
      before.querySelectorAll('summary').forEach(node => node.remove());
      const after = rendered.getElementById(section.id)!.cloneNode(true) as HTMLElement;
      after.querySelectorAll('.linear-lab,.lesson-answer-toggle,.lesson-diagram-tools,.lesson-diagram-help').forEach(node => node.remove());
      expect(normalize(after.textContent).replace(/\s/g, ''), section.id).toBe(normalize(before.textContent).replace(/\s/g, ''));
      expect([...after.querySelectorAll('td,th')].map(n => normalize(n.textContent))).toEqual([...before.querySelectorAll('td,th')].map(n => normalize(n.textContent)));
    }
    const svgBefore = [...source.querySelectorAll('section .ms-svg')];
    const svgAfter = [...rendered.querySelectorAll('.lesson-diagram svg')];
    svgBefore.forEach((svg, i) => expect(svgAfter[i]!.outerHTML).toBe(svg.outerHTML));
    for (const node of source.querySelectorAll('[id]')) expect(rendered.getElementById(node.id), node.id).not.toBeNull();
  });
  it('hydrates the existing article even with a saved dark theme, without replacing content', async () => {
    vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true);
    const host = globalThis.document.createElement('div');
    host.innerHTML = renderToString(page);
    globalThis.document.body.append(host);
    localStorage.setItem('mathstart-mode', 'dark');
    const section = host.querySelector('#theory');
    const errors: unknown[] = [];
    let root: ReturnType<typeof hydrateRoot>;
    await act(async () => { root = hydrateRoot(host, page, { onRecoverableError: error => errors.push(error) }); });
    expect(errors).toEqual([]);
    expect(host.querySelector('#theory')).toBe(section);
    expect(globalThis.document.documentElement.dataset.theme).toBe('dark');
    await act(async () => root!.unmount()); host.remove(); localStorage.clear(); vi.unstubAllGlobals();
  });
});
