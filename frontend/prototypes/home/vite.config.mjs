import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';
import { dirname, resolve, join } from 'node:path';
import { readdirSync, readFileSync } from 'node:fs';

const root = dirname(fileURLToPath(import.meta.url));
const repository = resolve(root, '../../..');
function catalogue() {
  const source = JSON.parse(readFileSync(join(repository, 'site_content/catalog.json'), 'utf8'));
  const topics = [];
  function visit(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      if (entry.isDirectory()) visit(path);
      else if (entry.name === 'lesson.json') {
        const { page } = JSON.parse(readFileSync(path, 'utf8'));
        if (page.is_published && page.page_type === 'topic') topics.push({
          title: page.title, slug: page.slug, grade: page.grade,
          subject: page.subject, section: page.section, order: page.order,
        });
      }
    }
  }
  visit(join(repository, 'curriculum'));
  return { ...source, topics: topics.sort((a, b) => a.order - b.order || a.slug.localeCompare(b.slug)) };
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
