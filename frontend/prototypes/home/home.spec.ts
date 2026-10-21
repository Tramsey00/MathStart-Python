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
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Алгебра');
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
        await expect(page.locator('h1')).toHaveText(name);
      }
      await page.keyboard.press('Escape');
    } else {
      for (const button of await subjects.all()) {
        const name = (await button.innerText()).replace(/^[±ƒ△▥]\s*/, '').trim();
        await button.click();
        await expect(page.locator('h1')).toHaveText(name);
      }
    }
    await noOverflow(page);
  }
  expect(errors).toEqual([]);
});
async function navigation(page: Page) {
  if (await page.getByRole('button', { name: 'Открыть меню' }).isVisible()) {
    await page.getByRole('button', { name: 'Открыть меню' }).click();
    return page.getByRole('dialog', { name: 'Навигация' });
  }
  return page.locator('.sidebar');
}
test('subject list collapses without changing the selected subject', async ({ page }) => {
  await page.goto('/');
  const nav = await navigation(page);
  const algebra = nav.getByRole('button', { name: 'Алгебра', exact: true });
  await expect(algebra).toHaveAttribute('aria-expanded', 'true');
  await algebra.click();
  await expect(algebra).toHaveAttribute('aria-expanded', 'false');
  await expect(nav.getByRole('button', { name: 'Математические модели', exact: true })).not.toBeVisible();
  await expect(page.locator('h1')).toHaveText('Алгебра');
  await algebra.click();
  await expect(nav.getByRole('button', { name: 'Математические модели', exact: true })).toBeVisible();
  await nav.getByRole('button', { name: 'Геометрия', exact: true }).click();
  await expect(algebra).toHaveAttribute('aria-expanded', 'false');
  await expect(page.locator('h1')).toHaveText('Геометрия');
  await noOverflow(page);
});
test('grade picker supports dismissal, focus return and real grade changes', async ({ page }, testInfo) => {
  await page.goto('/');
  const nav = await navigation(page);
  const trigger = nav.getByRole('button', { name: /^Выбрать класс:/ });
  await trigger.click();
  await expect(trigger).toHaveAttribute('aria-expanded', 'true');
  await expect(nav.locator('.grade-picker-panel button')).toHaveCount(6);
  await expect(nav.locator('.grade-picker-panel').getByRole('button', { name: '7 класс', exact: true })).toBeFocused();
  await page.screenshot({ path: resolve(here, `../../.cache/home-${testInfo.project.name}-grade-picker.png`) });
  await page.keyboard.press('Escape');
  await expect(trigger).toHaveAttribute('aria-expanded', 'false');
  await expect(trigger).toBeFocused();
  await expect(nav).toBeVisible();
  await trigger.click();
  await trigger.click();
  await expect(trigger).toHaveAttribute('aria-expanded', 'false');
  await trigger.click();
  await nav.getByText('ТВОЁ ОБУЧЕНИЕ', { exact: true }).click();
  await expect(trigger).toHaveAttribute('aria-expanded', 'false');
  await trigger.click();
  await nav.locator('.grade-picker-panel').getByRole('button', { name: '5 класс', exact: true }).click();
  await expect(trigger).toHaveAccessibleName('Выбрать класс: 5 класс');
  await expect(trigger).toHaveAttribute('aria-expanded', 'false');
  await expect(trigger).toBeFocused();
  await expect(page.locator('h1')).toHaveText('Математика');
  await trigger.click();
  await page.keyboard.press('Shift+Tab');
  await page.keyboard.press('Shift+Tab');
  await expect(trigger).toHaveAttribute('aria-expanded', 'false');
  await noOverflow(page);
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
