import { test, expect, type Page } from '@playwright/test';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
const here = dirname(fileURLToPath(import.meta.url));
async function noOverflow(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
}
test('homepage connects each class and subject to the approved catalogue', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('У каждого ответа');
  await expect(page.getByRole('banner').getByRole('link', { name: 'Войти', exact: true })).toHaveAttribute('href', 'http://127.0.0.1:8121/account/');
  const grades = page.getByRole('group', { name: 'Выбор класса на главной' });
  for (const grade of [5, 6, 7, 8, 9, 10]) {
    await grades.getByRole('button', { name: `${grade} класс`, exact: true }).click();
    await expect(grades.getByRole('button', { name: `${grade} класс`, exact: true })).toHaveAttribute('aria-pressed', 'true');
    const subjects = page.getByRole('navigation', { name: 'Предметы выбранного класса' }).getByRole('link');
    expect(await subjects.count()).toBeGreaterThan(0);
    for (const subject of await subjects.all()) await expect(subject).toHaveAttribute('href', new RegExp(`^/materials.html\\?grade=${grade}-klass&subject=`));
    await noOverflow(page);
  }
  await page.getByRole('contentinfo').getByRole('link', { name: '6 класс', exact: true }).click();
  await expect(page).toHaveURL(/materials.html\?grade=6-klass/);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Математика');
  await expect(page.locator('.section-card p')).toHaveCount(0);
  await page.getByRole('banner').getByRole('link', { name: 'MathStart — главная' }).click();
  await expect(page).toHaveURL(/\/$/);
  await page.goto('/materials.html?grade=8-klass&subject=geometriya');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Геометрия');
  await page.goto('/materials.html?grade=unknown&subject=unknown');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Алгебра');
  expect(errors).toEqual([]);
});
test('square demonstration preserves exact mathematics and supports keyboard interaction', async ({ page }) => {
  await page.goto('/');
  const range = page.getByRole('slider', { name: /Измени/ });
  await expect(page.locator('.example-numbers')).toHaveText('(4 + 2)² = 16 + 16 + 4 = 36');
  await range.focus();
  await page.keyboard.press('ArrowRight');
  await expect(range).toHaveValue('3');
  await expect(page.locator('.example-numbers')).toHaveText('(4 + 3)² = 16 + 24 + 9 = 49');
  await page.keyboard.press('End');
  await expect(page.locator('.example-numbers')).toContainText('= 64');
  await page.keyboard.press('Home');
  await expect(page.locator('.example-numbers')).toContainText('= 25');
  const split = page.getByRole('button', { name: 'Разобрать квадрат' });
  const before = await page.locator('.square-piece').first().getAttribute('style');
  await split.click();
  await expect(page.getByRole('button', { name: 'Собрать квадрат' })).toHaveAttribute('aria-pressed', 'true');
  expect(await page.locator('.square-piece').first().getAttribute('style')).not.toBe(before);
  if (!await page.evaluate(() => matchMedia('(prefers-reduced-motion: reduce)').matches)) {
    expect(await page.locator('.square-piece').first().evaluate(element => getComputedStyle(element).transitionDuration)).toBe('0.24s');
  }
  await expect(page.locator('.example-numbers')).toContainText('= 25');
  await page.getByRole('button', { name: 'Собрать квадрат' }).click();
  await expect(split).toHaveAttribute('aria-pressed', 'false');
  await split.focus();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('button', { name: 'Собрать квадрат' })).toHaveAttribute('aria-pressed', 'true');
  expect(await page.locator('.square-piece').first().evaluate(element => getComputedStyle(element).transitionDuration)).toBe('0s');
  await noOverflow(page);
});
test('light dark and reduced motion remain readable and produce review screenshots', async ({ page }, testInfo) => {
  const failures: string[] = [];
  page.on('requestfailed', request => failures.push(request.url()));
  await page.goto('/');
  await page.evaluate(() => document.fonts.ready);
  for (const target of [page.getByRole('slider'), page.getByRole('button', { name: 'Разобрать квадрат' }), page.getByRole('banner').getByRole('link', { name: 'Войти', exact: true })]) {
    expect((await target.boundingBox())!.height).toBeGreaterThanOrEqual(44);
  }
  for (const mode of ['light', 'dark']) {
    if (mode === 'dark') await page.getByRole('button', { name: 'Включить тёмную тему' }).click();
    await expect(page.locator('html')).toHaveAttribute('data-theme', mode);
    await page.getByRole('contentinfo').scrollIntoViewIfNeeded();
    await page.getByRole('heading', { level: 1 }).scrollIntoViewIfNeeded();
    await page.waitForFunction(() => document.getAnimations().every(animation => animation.playState === 'finished'));
    await noOverflow(page);
    await page.screenshot({ path: resolve(here, `../../.cache/landing-${testInfo.project.name}-${mode}.png`), fullPage: true });
  }
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.getByRole('button', { name: 'Разобрать квадрат' }).click();
  expect(await page.locator('.square-piece').first().evaluate(element => getComputedStyle(element).transitionDuration)).toBe('0s');
  expect(await page.locator('h1').evaluate(element => getComputedStyle(element).animationName)).toBe('none');
  await page.getByRole('link', { name: 'Открыть весь каталог' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await noOverflow(page);
  expect(failures).toEqual([]);
});
