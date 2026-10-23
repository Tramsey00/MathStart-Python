// Build-only adapter for the first lesson. The authored curriculum stays canonical.
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { parseFragment } from 'parse5';
import { quadraticRoute } from '../../src/shared/routing/material-routes.mjs';

export const quadraticSlug = quadraticRoute.slug;
const relative = 'curriculum/8-klass/algebra/06-kvadratichnaya-funkciya-y-ax2-funkciya-y-k-x/06-kvadratichnaya-funkcziya-y-ax2-bx-c';
const attributes = node => Object.fromEntries((node.attrs ?? []).map(a => [a.name, a.value]));
const hasClass = (node, name) => (attributes(node).class ?? '').split(/\s+/).includes(name);
const children = node => node.childNodes ?? [];
const text = node => node.nodeName === '#text' ? node.value : children(node).map(text).join('');

function convert(node) {
  if (node.nodeName === '#text') return { kind: 'text', text: node.value };
  if (!node.tagName) return null;
  const attrs = attributes(node);
  if (['script', 'iframe', 'object', 'style'].includes(node.tagName)) throw Error('Unsupported active lesson markup');
  if (Object.keys(attrs).some(key => /^on/i.test(key))) throw Error('Inline lesson handlers are not supported');
  if (attrs.href && !/^(?:\/|#|https?:\/\/)/.test(attrs.href)) throw Error('Unsupported lesson link');
  // The real graph is owned by React; its authored fallback is kept as a source reference.
  if (attrs.id === 'ms-quadratic-lab-660') return { kind: 'graph' };
  if (['ms-nav', 'ms-quadratic-number', 'ms-next-topic'].some(name => hasClass(node, name))) return null;
  return {
    kind: 'element', tag: node.tagName, attrs,
    children: children(node).map(convert).filter(Boolean),
  };
}

export function readQuadraticLesson(repository, catalogue) {
  const directory = join(repository, relative);
  const metadata = JSON.parse(readFileSync(join(directory, 'lesson.json'), 'utf8')).page;
  if (metadata.slug !== quadraticSlug || !metadata.is_published) throw Error('Unexpected pilot lesson');
  const html = readFileSync(join(directory, 'body.html'), 'utf8');
  const root = children(parseFragment(html)).find(node => hasClass(node, 'ms-lesson-page'));
  if (!root) throw Error('Missing authored lesson');
  const hero = children(root).find(node => hasClass(node, 'ms-hero'));
  const subtitle = children(hero).find(node => hasClass(node, 'ms-subtitle'));
  const authoredSections = children(root).filter(node => node.tagName === 'section' && !hasClass(node, 'ms-hero'));
  if (authoredSections.length !== 9) throw Error('Pilot section inventory changed; review the source adapter');
  // User removed the repeated recap and "Далее" on 2026-10-23.
  // Keep the authored source intact; only the preview projection omits them.
  const sections = authoredSections.filter(section => attributes(section).id !== 'lesson-section-9').map(section => {
    const heading = children(section).find(node => node.tagName === 'h2');
    if (!heading || !attributes(section).id) throw Error('Missing lesson heading/anchor');
    return { id: attributes(section).id, title: text(heading).trim().replace(/^\d+\.\s*/, ''),
      nodes: children(section).filter(node => node !== heading).map(convert).filter(Boolean) };
  });
  const topics = catalogue.topics.filter(topic => topic.grade === metadata.grade && topic.subject === metadata.subject && topic.section === metadata.section)
    .sort((a, b) => a.order - b.order || a.slug.localeCompare(b.slug));
  const position = topics.findIndex(topic => topic.slug === metadata.slug);
  if (position < 0) throw Error('Pilot missing from published catalogue');
  return { ...metadata, subtitle: text(subtitle).replace(/\s+/g, ' ').trim(), sections,
    previous: topics[position - 1] ?? null, next: topics[position + 1] ?? null };
}
