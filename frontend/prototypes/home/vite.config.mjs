import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';
import { dirname, resolve, join } from 'node:path';
import { readdirSync, readFileSync } from 'node:fs';
import { quadraticSlug, readQuadraticLesson } from './lesson-source.mjs';
import { quadraticRoute } from '../../src/shared/routing/material-routes.mjs';

const root = dirname(fileURLToPath(import.meta.url));
const repository = resolve(root, '../../..');
function lessonRoutesMiddleware(request, response, next) {
  const [pathname, ...query] = (request.url ?? '').split('?');
  const search = query.length ? `?${query.join('?')}` : '';
  if (['/quadratic.html', `/${quadraticSlug}`, `/${quadraticSlug}/`, `${quadraticRoute.path}/`].includes(pathname)) {
    response.writeHead(302, { Location: quadraticRoute.path + search });
    response.end();
    return;
  }
  if (pathname === quadraticRoute.path) request.url = '/quadratic.html' + search;
  next();
}
function catalogue() {
  const source = JSON.parse(readFileSync(join(repository, 'site_content/catalog.json'), 'utf8'));
  const topics = [];
  function visit(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      if (entry.isDirectory()) visit(path);
      else if (entry.name === 'lesson.json') {
        const { page } = JSON.parse(readFileSync(path, 'utf8'));
        if (page.is_published && page.page_type === 'topic') {
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
  return { ...source, topics };
}

export default defineConfig({
  root,
  cacheDir: resolve(repository, 'frontend/.cache/home-prototype-vite'),
  esbuild: { jsx: 'automatic' },
  plugins: [{
    name: 'mathstart-readonly-prototype-catalogue',
    resolveId(id) { if (['virtual:mathstart-catalogue', 'virtual:mathstart-quadratic'].includes(id)) return '\0' + id.slice('virtual:'.length); },
    load(id) {
      if (id === '\0mathstart-catalogue') return `export default ${JSON.stringify(catalogue())}`;
      if (id === '\0mathstart-quadratic') return `export default ${JSON.stringify(readQuadraticLesson(repository, catalogue()))}`;
    },
    configureServer(server) {
      server.middlewares.use(lessonRoutesMiddleware);
    },
    configurePreviewServer(server) { server.middlewares.use(lessonRoutesMiddleware); },
  }],
  server: { host: '127.0.0.1', port: 5173, strictPort: true },
  preview: { host: '127.0.0.1', port: 5173, strictPort: true },
  build: {
    outDir: resolve(repository, 'frontend/.cache/home-prototype-build'), emptyOutDir: true,
    rollupOptions: { input: { home: join(root, 'index.html'), materials: join(root, 'materials.html'), quadratic: join(root, 'quadratic.html') } },
  },
});
