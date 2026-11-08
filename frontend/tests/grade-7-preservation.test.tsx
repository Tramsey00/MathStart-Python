import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { renderToString } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { LessonPage } from '../src/shared/lesson/lesson-page';
import type { LessonDocument } from '../src/shared/lesson/lesson-types';
import { materialPathForSlug } from '../src/shared/routing/material-routes.mjs';
const root = resolve('..');
const load = (path: string) => JSON.parse(readFileSync(resolve(root, path), 'utf8'));
const map = load('docs/tasks/ms-t005-migration-map.json') as { topics: { slug: string; source: string; status: string; canonical_path: string | null; source_files: Record<string, string>; excluded_sections: { id: string | null }[] }[] };
type MathOverride = { slug: string; source: string; changes: { start: number; end: number; old: string; mathml: string; section: string }[] };
const mathOverrides = load('docs/tasks/ms-t005-mathml-overrides.json') as { topics: MathOverride[] };
const normalize = (text: string | null) => (text ?? '').replace(/\s/gu, '').replaceAll('-', '−');
const parse = (html: string) => new DOMParser().parseFromString(html, 'text/html');
// Authored SVG comments are not geometry or academic labels; React adds its own boundary comments.
const svgMarkup = (node: Element) => node.outerHTML.replace(/<!--.*?-->/gs, '');

describe('MS-T005 source preservation and explicit route assignments', () => {
  it('accounts for exactly the 75 original grade-7 identities and preserves every frozen source', () => {
    const inventory = load('docs/tasks/lesson-inventory.json').topics.filter((t: {grade: string}) => t.grade === '7-klass');
    expect(map.topics.map(t => t.slug).sort()).toEqual(inventory.map((t: {slug: string}) => t.slug).sort());
    expect(map.topics).toHaveLength(75);
    for (const topic of map.topics) for (const [file, sha] of Object.entries(topic.source_files)) {
      expect(createHash('sha256').update(readFileSync(resolve(root, topic.source, file))).digest('hex'), topic.slug + '/' + file).toBe(sha);
    }
    const paths = load('site_content/material-routes.json').assignments.flatMap((r: { grade: number; subject: string; number: number; aliases?: string[] }) => [`/materials/${r.grade}-${r.subject}-${r.number}`, ...(r.aliases ?? [])]);
    expect(new Set(paths).size).toBe(paths.length);
  });
  it('preserves every authored numerator/denominator and exact MathML fraction structure', () => {
    const mathematicalText = (s: string) => normalize(s).replace(/[²³₁₂]/gu, c => ({'²':'2','³':'3','₁':'1','₂':'2'}[c]!));
    for (const topic of mathOverrides.topics) {
      const original = readFileSync(resolve(root, topic.source, 'body.html'), 'utf8');
      const active = map.topics.find(t => t.slug === topic.slug)!;
      const rendered = ['MIGRATED', 'PREPARED_BLOCKED_URL'].includes(active.status)
        ? parse(renderToString(<LessonPage document={load(topic.source + '/content.json')} navigation={{previous:null,next:null}} gradeLinks={[]}/>)) : null;
      for (const change of topic.changes) {
        expect(original.slice(change.start, change.end)).toBe(change.old);
        const before = parse(change.old); const after = parse(change.mathml);
        const fraction = after.querySelector('math > mfrac')!;
        expect(fraction.children).toHaveLength(2);
        expect(mathematicalText(fraction.children[0]!.textContent!)).toBe(mathematicalText(before.querySelector('.ms-num')!.textContent!));
        expect(mathematicalText(fraction.children[1]!.textContent!)).toBe(mathematicalText(before.querySelector('.ms-den')!.textContent!));
        if (rendered) expect([...rendered.getElementById(change.section)!.querySelectorAll('mfrac')].some(n => svgMarkup(n) === svgMarkup(fraction))).toBe(true);
      }
    }
  });
  for (const topic of map.topics.filter(t => t.status === 'MIGRATED')) {
    it(`preserves the visible academic content, SVG, tables, answers and anchors: ${topic.slug}`, () => {
      let sourceHtml = readFileSync(resolve(root, topic.source, 'body.html'), 'utf8');
      const authoredMath = mathOverrides.topics.find(t => t.slug === topic.slug);
      for (const change of [...(authoredMath?.changes ?? [])].reverse()) {
        expect(sourceHtml.slice(change.start, change.end)).toBe(change.old);
        sourceHtml = sourceHtml.slice(0, change.start) + change.mathml + sourceHtml.slice(change.end);
      }
      const source = parse(sourceHtml);
      const lesson = load(topic.source + '/content.json') as LessonDocument;
      const rendered = parse(renderToString(<LessonPage document={lesson} navigation={{previous: null, next: null}} gradeLinks={[]}/>));
      expect(materialPathForSlug(topic.slug)).toBe(topic.canonical_path);
      expect(load(topic.source + '/lesson.json').renderer_version).toBe('react-v1');
      for (const section of lesson.sections) {
        const before = source.getElementById(section.id)!.cloneNode(true) as Element;
        before.querySelectorAll('summary,.ms-nav,.ms-lesson-nav,.ms-quadratic-number,.ms-next-topic').forEach(n => n.remove());
        before.querySelector('h2')!.textContent = section.title;
        const after = rendered.getElementById(section.id)!;
        const academic = after.cloneNode(true) as Element;
        academic.querySelectorAll('.lesson-answer-toggle').forEach(n => n.remove());
        expect(normalize(academic.textContent), section.id).toBe(normalize(before.textContent));
        expect([...after.querySelectorAll('td,th')].map(n => normalize(n.textContent))).toEqual([...before.querySelectorAll('td,th')].map(n => normalize(n.textContent)));
        expect([...after.querySelectorAll('svg')].map(svgMarkup)).toEqual([...before.querySelectorAll('svg')].map(svgMarkup));
        for (const node of [before, ...before.querySelectorAll('[id]')]) if (node.id) expect(rendered.getElementById(node.id), node.id).not.toBeNull();
        expect([...after.querySelectorAll('a[href]')].map(n => n.getAttribute('href'))).toEqual([...before.querySelectorAll('a[href]')].map(n => n.getAttribute('href')));
      }
      for (const section of topic.excluded_sections) if (section.id) expect(rendered.getElementById(section.id)).toBeNull();
      expect(rendered.querySelector('.ms-nav,.ms-lesson-nav')).toBeNull();
      expect(rendered.querySelectorAll('.lesson-navigation')).toHaveLength(1);
      expect(rendered.querySelector('.lesson-diagram button')).toBeNull();
    });
  }
});
