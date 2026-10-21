import { test, expect, type Page } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
const here = dirname(fileURLToPath(import.meta.url));
async function noOverflow(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
}
test('all grades and subjects remain usable, including long Russian headings', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Алгебра.');
  for (const grade of [5, 6, 7, 8, 9, 10]) {
    await page.getByRole('group', { name: 'Выбор класса' }).getByRole('button', { name: `${grade} класс`, exact: true }).click();
    await expect(page.locator('.section-card').first()).toBeVisible();
    const subjects = page.locator('.sidebar .subject-button');
    if (await page.getByRole('button', { name: 'Открыть меню' }).isVisible()) {
      await page.getByRole('button', { name: 'Открыть меню' }).click();
      const menu = page.getByRole('dialog', { name: 'Навигация' });
      for (const button of await menu.locator('.subject-button').all()) {
        const name = (await button.innerText()).replace(/^[±ƒ△▥]\s*/, '').trim();
        await button.click();
        await expect(page.locator('h1')).toHaveText(`${name}.`);
      }
      await page.keyboard.press('Escape');
    } else {
      for (const button of await subjects.all()) {
        const name = (await button.innerText()).replace(/^[±ƒ△▥]\s*/, '').trim();
        await button.click();
        await expect(page.locator('h1')).toHaveText(`${name}.`);
      }
    }
    await noOverflow(page);
  }
  expect(errors).toEqual([]);
});
test('section dialog has real topic links, keyboard dismissal and restored focus', async ({ page }) => {
  await page.goto('/');
  const card = page.locator('.section-card').first();
  await card.click();
  const dialog = page.getByRole('dialog', { name: 'Математические модели' });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole('link')).toHaveCount(5);
  await expect(dialog.getByRole('link').first()).toHaveAttribute('href', /^http:\/\/127\.0\.0\.1:8121\/[a-z0-9-]+\/$/);
  await page.keyboard.press('Escape');
  await expect(dialog).not.toBeVisible();
  await expect(card).toBeFocused();
  await noOverflow(page);
});
test('global search, empty results, clear and section filter work', async ({ page }) => {
  await page.goto('/');
  const search = page.getByRole('textbox', { name: 'Поиск по всем темам' });
  await search.fill('дроби');
  await expect(page.locator('.result-row').first()).toBeVisible();
  await expect(page.getByRole('heading', { level: 2 }).first()).toContainText('Найденные темы');
  await search.fill('несуществующая-тема-zzzz');
  await expect(page.getByRole('heading', { name: 'Пока ничего не нашлось' })).toBeVisible();
  await page.getByRole('button', { name: 'Сбросить поиск' }).click();
  await expect(search).toBeFocused();
  await page.getByRole('textbox', { name: 'Найти раздел' }).fill('многочлен');
  await expect(page.locator('.section-card')).toHaveCount(2);
  await noOverflow(page);
});
test('both themes load local fonts and produce review screenshots', async ({ page }, testInfo) => {
  const failures: string[] = [];
  page.on('requestfailed', request => failures.push(request.url()));
  await page.goto('/');
  await page.evaluate(() => document.fonts.ready);
  expect(await page.evaluate(() => document.fonts.check('500 14px Inter', 'Математика Algebra'))).toBe(true);
  await noOverflow(page);
  await page.screenshot({ path: resolve(here, `../../.cache/home-${testInfo.project.name}-light.png`), fullPage: true });
  await page.getByRole('button', { name: 'Включить тёмную тему' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
  await page.screenshot({ path: resolve(here, `../../.cache/home-${testInfo.project.name}-dark.png`), fullPage: true });
  await page.getByRole('button', { name: 'Включить светлую тему' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
  expect(failures).toEqual([]);
});
