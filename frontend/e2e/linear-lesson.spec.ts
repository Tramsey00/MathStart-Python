import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
const data = JSON.parse(readFileSync(process.env.MATHSTART_PUBLIC_VIEW!, 'utf8'));
const canonical = Object.keys(data.routes).find(path => data.routes[path].page.renderer_version === 'react-v1')!;
const oldPath = canonical ? `/${data.routes[canonical].page.slug}/` : '';

test('linear pilot uses Content canonical, reload, Back and preserved anchors', async ({ page, request }) => {
  expect(canonical).toBe('/materials/7-algebra-1');
  const redirect = await request.get(oldPath + '?from=pilot', { maxRedirects: 0 });
  expect(redirect.status()).toBe(301); expect(redirect.headers().location).toBe(canonical + '?from=pilot');
  const errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto(oldPath + '?from=pilot#theory');
  await expect(page).toHaveURL(new RegExp('/materials/7-algebra-1\\?from=pilot#theory$'));
  await expect(page.locator('#theory')).toBeVisible();
  await page.reload(); await expect(page.locator('#theory')).toBeVisible();
  await expect(page.locator('.lesson-section')).toHaveCount(13);
  await expect(page.locator('.self-check')).toHaveCount(13);
  await expect(page.locator('.lesson-section table')).toHaveCount(4);
  await expect(page.locator('.lesson-diagram svg')).toHaveCount(3);
  await page.getByRole('button', { name: 'Содержание урока', exact: true }).click();
  await expect(page.getByRole('dialog', { name: 'Содержание урока', exact: true })).toBeVisible();
  await page.getByRole('dialog').getByRole('link', { name: /Экспресс-анализ/ }).click();
  await expect(page).toHaveURL(/#lesson-section-13$/);
  await page.goBack(); await expect(page).toHaveURL(/#theory$/);
  await page.locator('.lesson-back').click(); await expect(page).toHaveURL(/7-klass-algebra\/$/);
  await page.goBack(); await expect(page.locator('[data-react-linear]')).toHaveCount(1);
  expect(errors).toEqual([]);
});

test('linear graph keyboard, answers, reset and responsive themes use shared controls', async ({ page }) => {
  await page.goto(canonical);
  const lab = page.locator('[data-react-linear]');
  const k = lab.getByRole('slider', { name: 'Коэффициент k' });
  await k.focus(); await k.press('Home'); await expect(k).toHaveValue('-3');
  await expect(lab.locator('.quadratic-current')).toHaveText('y = −3x');
  await expect(lab.locator('.quadratic-properties')).toContainText('убывает');
  const b = lab.getByRole('slider', { name: 'Коэффициент b' }); await b.focus(); await b.press('End'); await expect(b).toHaveValue('6');
  await expect(lab.locator('.quadratic-properties')).toContainText('(2; 0)');
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await lab.getByRole('button', { name: 'Сбросить значения' }).click(); await expect(k).toHaveValue('1'); await expect(b).toHaveValue('0');
  const answer = page.locator('.self-check').first().getByRole('button', { name: 'Ответ и решение' });
  await answer.click(); await expect(answer).toHaveAttribute('aria-expanded', 'true');
  await answer.click(); await expect(answer).toHaveAttribute('aria-expanded', 'false');
  await page.getByRole('button', { name: 'Включить тёмную тему' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await page.reload(); await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
  await page.getByRole('button', { name: 'Включить светлую тему' }).click();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
});

test('linear pilot article, solutions, SVG and contents are usable without JavaScript', async ({ browser, baseURL }) => {
  const context = await browser.newContext({ javaScriptEnabled: false, baseURL: baseURL! });
  const page = await context.newPage(); await page.goto(canonical);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(data.routes[canonical].page.title);
  await expect(page.locator('.lesson-section')).toHaveCount(13);
  await page.locator('.lesson-static-contents summary').click();
  await page.locator('.lesson-static-contents').getByRole('link', { name: /Экспресс-анализ/ }).click();
  await expect(page).toHaveURL(/#lesson-section-13$/);
  await expect(page.locator('.self-check .lesson-reveal-expander').first()).toBeVisible();
  await expect(page.locator('.lesson-diagram svg')).toHaveCount(3);
  await context.close();
});

test('linear graph touch tap and scrolling cancellation preserve the selected point', async ({ browser, baseURL }) => {
  const context = await browser.newContext({ hasTouch: true, viewport: { width: 360, height: 800 }, baseURL: baseURL! });
  const page = await context.newPage(); await page.goto(canonical);
  const graph = page.locator('[data-react-linear] svg').first(); await graph.scrollIntoViewIfNeeded();
  const bounds = (await graph.boundingBox())!;
  await page.touchscreen.tap(bounds.x + bounds.width * .7, bounds.y + bounds.height * .5);
  const probe = page.getByRole('slider', { name: 'Абсцисса исследуемой точки x' });
  await expect(probe).not.toHaveValue('0'); const before = await probe.inputValue();
  await graph.dispatchEvent('pointerdown', { pointerId: 11, pointerType: 'touch', isPrimary: true, button: 0, clientX: 100, clientY: 100 });
  await graph.dispatchEvent('pointermove', { pointerId: 11, pointerType: 'touch', clientX: 100, clientY: 150 });
  await graph.dispatchEvent('pointercancel', { pointerId: 11, pointerType: 'touch' });
  await expect(probe).toHaveValue(before);
  await context.close();
});
