// Explicit dev-mode smoke only; never runs as part of npm test or CI.
import { chromium, request } from '@playwright/test';
import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { createHash } from 'node:crypto';
const root = resolve('..');
const origin = 'http://127.0.0.1:8131';
const results = { origin, routes: {}, websocketOrigins: [], checks: [] };
const api = await request.newContext({ baseURL: origin });
const browser = await chromium.launch({ channel: 'chrome' });
const page = await browser.newPage();
const errors = [];
page.on('pageerror', error => errors.push(error.message));
page.on('websocket', socket => { results.websocketOrigins.push(new URL(socket.url()).origin); });
const digest = raw => createHash('sha256').update(raw).digest('hex');
async function temporaryEdit(path, edit, observe) {
  const before = await readFile(path);
  const after = Buffer.from(edit(before.toString('utf8')));
  if (before.equals(after)) throw Error('Temporary probe did not change source');
  await writeFile(path, after);
  try { await observe(); }
  finally {
    if (!(await readFile(path)).equals(after)) throw Error('Concurrent source change; refusing to overwrite it');
    await writeFile(path, before);
    if (digest(await readFile(path)) !== digest(before)) throw Error('Source restoration failed');
  }
}
try {
  for (const path of ['/', '/materials', '/materials/8-algebra-32', '/materials/7-algebra-8']) {
    const response = await api.get(path, { timeout: 45000 });
    results.routes[path] = response.status();
    if (response.status() !== 200) throw Error('Development page failed: ' + path + ' ' + response.status());
  }
  const grades = await api.get('/api/v1/grades/');
  if (grades.status() !== 200) throw Error('Same-origin API proxy failed: ' + grades.status());
  results.checks.push('same-origin-fastapi-api');
  const account = await api.get('/account/');
  if (account.status() !== 200 || !account.headers()['cache-control']?.includes('no-store')) throw Error('Private shell did not stay on FastAPI');
  results.checks.push('private-shell-remains-fastapi-no-store');
  const alias = await api.get('/materials.html?from=dev', { maxRedirects: 0 });
  if (alias.status() !== 301 || alias.headers().location !== '/materials?from=dev') throw Error('Canonical alias proxy failed');
  results.checks.push('canonical-alias-preserves-query');
  await page.goto(origin + '/materials/7-algebra-8', { waitUntil: 'networkidle' });
  await page.locator('.lesson-heading').waitFor();
  await temporaryEdit(resolve(root, 'frontend/src/shared/lesson/lesson.css'),
    text => text + '\n.lesson-contents-panel { --mathstart-hmr-probe: ready; }\n',
    async () => {
      await page.waitForFunction(() => getComputedStyle(document.querySelector('.lesson-contents-panel')).getPropertyValue('--mathstart-hmr-probe').trim() === 'ready');
      results.checks.push('css-update-without-manual-reload');
    });
  await temporaryEdit(resolve(root, 'frontend/src/shared/lesson/lesson-components.tsx'),
    text => text.replace('<header className="lesson-heading">', '<header className="lesson-heading" data-hmr-probe="ready">'),
    async () => {
      await page.locator('.lesson-heading[data-hmr-probe="ready"]').waitFor();
      results.checks.push('react-update-without-manual-reload');
    });
  await page.waitForFunction(() => !document.querySelector('.lesson-heading')?.hasAttribute('data-hmr-probe'));
  const view = JSON.parse(await readFile(resolve(root, 'var/local/dev/public-view.json'), 'utf8'));
  const legacy = Object.entries(view.routes).find(([, item]) => !item.public_design && item.page.renderer_version !== 'react-v1');
  if (!legacy) throw Error('Expected mixed legacy/React scope for this smoke');
  const oldPage = await api.get(legacy[0]);
  if (oldPage.status() !== 200 || (await oldPage.text()).includes('/@vite/client')) throw Error('Legacy page was incorrectly hydrated by Vite');
  results.checks.push('legacy-document-remains-fastapi');
  const linear = view.routes['/materials/7-algebra-8'];
  const source = resolve(root, linear.page.source.path, '../content.json');
  const marker = ' DEV_CONTENT_REFRESH_PROBE';
  await temporaryEdit(source, text => { const doc = JSON.parse(text); doc.subtitle += marker; return JSON.stringify(doc, null, 2) + '\n'; }, async () => {
    await page.waitForFunction(marker => document.querySelector('.lesson-heading > p')?.textContent.includes(marker), marker);
    const published = await api.get('/api/v1/content/pages/' + linear.page.slug + '/');
    if (published.status() !== 200) throw Error('Published topic API status: ' + published.status());
    if ((await published.text()).includes(marker)) throw Error('Dev content leaked into published API');
    results.checks.push('content-auto-refresh-with-published-api-isolation');
  });
  await page.waitForFunction(marker => !document.querySelector('.lesson-heading > p')?.textContent.includes(marker), marker);
  if (errors.length) throw Error('Browser errors: ' + errors.join('; '));
  if (!results.websocketOrigins.length || results.websocketOrigins.some(value => value !== 'ws://127.0.0.1:8131')) throw Error('HMR escaped the browser origin');
  results.checks.push('websocket-on-8131', 'temporary-sources-restored');
  await writeFile(resolve(root, 'var/local/dev/hmr-smoke.json'), JSON.stringify(results, null, 2));
  console.log('PASS: 4 pages, API proxy, CSS/React/content refresh, same-origin WebSocket; probe sources restored');
} finally { await page.close(); await browser.close(); await api.dispose(); }
