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
    const nav = await navigation(page);
    await nav.getByRole('group', { name: 'Выбор класса' }).getByRole('button', { name: `${grade} класс`, exact: true }).click();
    await expect(page.locator('.section-card').first()).toBeVisible();
    for (const button of await nav.locator('.subject-button').all()) {
      const name = (await button.innerText()).replace(/^[±ƒ△▥]\s*/, '').trim();
      await button.click();
      await expect(page.locator('h1')).toHaveText(name);
    }
    if (await page.getByRole('button', { name: 'Открыть меню' }).isVisible()) await page.keyboard.press('Escape');
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
test('inline grades stay visible and support mouse and keyboard selection', async ({ page }, testInfo) => {
  await page.goto('/');
  const nav = await navigation(page);
  const grades = nav.getByRole('group', { name: 'Выбор класса' });
  await expect(grades.getByRole('button')).toHaveCount(6);
  for (const button of await grades.getByRole('button').all()) await expect(button).toBeVisible();
  await expect(grades.getByRole('button', { name: '7 класс', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await page.screenshot({ path: resolve(here, `../../.cache/home-${testInfo.project.name}-grade-picker.png`) });
  const fifth = grades.getByRole('button', { name: '5 класс', exact: true });
  await fifth.click();
  await expect(fifth).toHaveAttribute('aria-pressed', 'true');
  await expect(fifth).toBeFocused();
  await expect(page.locator('h1')).toHaveText('Математика');
  await page.keyboard.press('Tab');
  const sixth = grades.getByRole('button', { name: '6 класс', exact: true });
  await expect(sixth).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(sixth).toHaveAttribute('aria-pressed', 'true');
  await expect(page.locator('.subject-kicker')).toContainText('6 класс');
  await grades.getByRole('button', { name: '10 класс', exact: true }).click();
  await expect(page.locator('h1')).toHaveText('Алгебра');
  if (await page.getByRole('button', { name: 'Открыть меню' }).isVisible()) {
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog', { name: 'Навигация' })).not.toBeVisible();
    await expect(page.locator('.mobile-grade-selector').getByRole('button', { name: '10 класс', exact: true })).toHaveAttribute('aria-pressed', 'true');
  }
  await expect(page.locator('.prototype-label, .sidebar-tip, .other-subjects, .page-footer')).toHaveCount(0);
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
  await expect(page.getByRole('heading', { level: 2, name: /^Найденные темы/ })).toBeVisible();
  await search.fill('несуществующая-тема-zzzz');
  await expect(page.getByRole('heading', { name: 'Пока ничего не нашлось' })).toBeVisible();
  await page.getByRole('button', { name: 'Сбросить поиск' }).click();
  await expect(search).toBeFocused();
  const filter = page.getByRole('textbox', { name: 'Найти раздел' });
  const idleBorder = await page.locator('.section-filter').evaluate(element => getComputedStyle(element).borderColor);
  await filter.click();
  expect(await page.locator('.section-filter').evaluate(element => getComputedStyle(element).outlineStyle)).toBe('none');
  await page.keyboard.press('Tab');
  await page.keyboard.press('Shift+Tab');
  await expect(filter).toBeFocused();
  expect(await page.locator('.section-filter').evaluate(element => getComputedStyle(element).borderColor)).not.toBe(idleBorder);
  await filter.fill('многочлен');
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
test('shared illustration replaces removed labels and section hover leaves appearance unchanged', async ({ page }) => {
  await page.goto('/');
  const picture = page.locator('svg.math-illustration');
  await expect(picture).toHaveCount(1);
  await expect(picture).toBeVisible();
  const bounds = await picture.boundingBox();
  expect(bounds!.width).toBeGreaterThan(200);
  await expect(page.locator('.lesson-preview, .hero-tags, .nav-active-dot')).toHaveCount(0);
  await expect(page.locator('.breadcrumbs, .nav-home, .count-badge')).toHaveCount(0);
  await expect(page.getByText('ТВОЁ ОБУЧЕНИЕ', { exact: true })).toHaveCount(0);
  await expect(page.getByRole('heading', { level: 2, name: 'С чего начнём?', exact: true })).toBeVisible();
  await expect(page.locator('.hero')).not.toContainText('разделов');
  await expect(page.getByText('Открыть раздел', { exact: true })).toHaveCount(0);
  const section = page.locator('.section-card').first();
  for (const dark of [false, true]) {
    if (dark) await page.getByRole('button', { name: 'Включить тёмную тему' }).click();
    await page.locator('h1').hover();
    const before = await section.evaluate(element => {
      const style = getComputedStyle(element);
      return [style.backgroundColor, style.borderBottomColor, style.boxShadow, style.color];
    });
    await section.hover();
    const after = await section.evaluate(element => {
      const style = getComputedStyle(element);
      return [style.backgroundColor, style.borderBottomColor, style.boxShadow, style.color];
    });
    expect(after).toEqual(before);
  }
  await noOverflow(page);
});
