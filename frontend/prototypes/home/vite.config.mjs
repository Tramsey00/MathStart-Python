import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';
import { dirname, resolve, join } from 'node:path';
import { readdirSync, readFileSync } from 'node:fs';

const root = dirname(fileURLToPath(import.meta.url));
const repository = resolve(root, '../../..');
function catalogue() {
  const source = JSON.parse(readFileSync(join(repository, 'site_content/catalog.json'), 'utf8'));
  const topics = [];
  const bodies = new Map();
  function visit(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      if (entry.isDirectory()) visit(path);
      else if (entry.name === 'lesson.json') {
        const { page } = JSON.parse(readFileSync(path, 'utf8'));
        if (page.is_published && page.page_type === 'topic') {
          bodies.set(page.slug, join(directory, 'body.html'));
          topics.push({
          title: page.title, slug: page.slug, grade: page.grade,
          subject: page.subject, section: page.section, order: page.order,
          });
        }
      }
    }
  }
  visit(join(repository, 'curriculum'));
  topics.sort((a, b) => a.order - b.order || a.slug.localeCompare(b.slug));
  const previews = source.subjects.flatMap(subject => {
    const sections = source.sections.filter(section => section.grade === subject.grade && section.subject === subject.slug).sort((a, b) => a.order - b.order);
    const first = sections.flatMap(section => topics.filter(topic => topic.grade === subject.grade && topic.subject === subject.slug && topic.section === section.slug))[0];
    if (!first) return [];
    const html = readFileSync(bodies.get(first.slug), 'utf8');
    // A plain-text excerpt of the author's introduction, never executable HTML.
    const paragraph = [...html.matchAll(/<p\b([^>]*)>([\s\S]*?)<\/p>/gi)]
      .find(match => /\bms-subtitle\b/.test(match[1]))?.[2];
    if (!paragraph || /<(?:script|style|svg|math|iframe)\b/i.test(paragraph)) return [];
    const entities = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', ndash: '–', mdash: '—' };
    const excerpt = paragraph.replace(/<[^>]*>/g, ' ')
      .replace(/&(#x[\da-f]+|#\d+|amp|lt|gt|quot|apos|nbsp|ndash|mdash);/gi, (entity, code) => {
        if (!code.startsWith('#')) return entities[code.toLowerCase()] ?? entity;
        const point = code[1].toLowerCase() === 'x' ? parseInt(code.slice(2), 16) : Number(code.slice(1));
        return point > 0 && point <= 0x10ffff ? String.fromCodePoint(point) : ' ';
      }).replace(/\s+/g, ' ').trim();
    return excerpt ? [{ ...first, excerpt }] : [];
  });
  return { ...source, topics, previews };
}

export default defineConfig({
  root,
  cacheDir: resolve(repository, 'frontend/.cache/home-prototype-vite'),
  esbuild: { jsx: 'automatic' },
  plugins: [{
    name: 'mathstart-readonly-prototype-catalogue',
    resolveId(id) { if (id === 'virtual:mathstart-catalogue') return '\0mathstart-catalogue'; },
    load(id) { if (id === '\0mathstart-catalogue') return `export default ${JSON.stringify(catalogue())}`; },
  }],
  server: { host: '127.0.0.1', port: 5173, strictPort: true },
  preview: { host: '127.0.0.1', port: 5173, strictPort: true },
  build: { outDir: resolve(repository, 'frontend/.cache/home-prototype-build'), emptyOutDir: true },
});
