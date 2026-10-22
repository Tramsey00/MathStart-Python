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
  await page.goto('/materials.html');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Алгебра');
  for (const grade of [5, 6, 7, 8, 9, 10]) {
    const nav = await navigation(page);
    await nav.getByRole('group', { name: 'Выбор класса' }).getByRole('button', { name: `${grade} класс`, exact: true }).click();
    await expect(page.locator('.section-card').first()).toBeVisible();
    for (const button of await nav.locator('.subject-button').all()) {
      const name = (await button.innerText()).replace(/^[±ƒ△▥]\s*/, '').trim();
      await button.click();
      await expect(page.locator('h1')).toHaveText(name);
      await expect(page.locator('.section-card p')).toHaveCount(0);
      expect(await page.locator('.section-card').evaluateAll(cards => cards.every(card => {
        const title = card.querySelector('h3')!;
        const bounds = card.getBoundingClientRect();
        const titleBounds = title.getBoundingClientRect();
        return bounds.height >= 44 && title.scrollHeight <= title.clientHeight + 1
          && titleBounds.left >= bounds.left && titleBounds.right <= bounds.right + 1;
      }))).toBe(true);
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
  await page.goto('/materials.html');
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
  await page.goto('/materials.html');
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
test('section dialog has real topic links, keyboard dismissal and restored focus', async ({ page }, testInfo) => {
  await page.goto('/materials.html');
  const card = page.locator('.section-card').first();
  await card.click();
  const dialog = page.getByRole('dialog', { name: 'Математические модели' });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole('link')).toHaveCount(5);
  await expect(dialog.getByRole('listitem')).toHaveCount(5);
  await expect(dialog.locator('.topic-index').first()).toHaveText('1');
  await expect(dialog.getByText('Читать', { exact: true })).toHaveCount(0);
  await expect(dialog.getByRole('heading', { name: 'Темы раздела' })).toBeVisible();
  await expect(dialog.getByRole('link').first()).toHaveAttribute('href', /^http:\/\/127\.0\.0\.1:8121\/[a-z0-9-]+\/$/);
  expect(await dialog.evaluate(element => element.scrollWidth <= element.clientWidth)).toBe(true);
  await page.screenshot({ path: resolve(here, `../../.cache/home-${testInfo.project.name}-dialog.png`) });
  await dialog.getByRole('button', { name: 'Закрыть раздел' }).click();
  await expect(card).toBeFocused();
  await card.click();
  await dialog.getByRole('heading', { name: 'Темы раздела' }).click();
  await expect(dialog).toBeVisible();
  const bounds = (await dialog.boundingBox())!;
  const outside = { x: Math.max(2, bounds.x - 8), y: bounds.y + bounds.height / 2 };
  await page.mouse.move(bounds.x + bounds.width / 2, bounds.y + 12);
  await page.mouse.down();
  await page.mouse.move(outside.x, outside.y);
  await page.mouse.up();
  await expect(dialog).toBeVisible();
  await page.mouse.click(outside.x, outside.y);
  await expect(dialog).not.toBeVisible();
  await expect(card).toBeFocused();
  await card.click();
  await page.keyboard.press('Escape');
  await expect(dialog).not.toBeVisible();
  await expect(card).toBeFocused();
  const nav = await navigation(page);
  await nav.getByRole('group', { name: 'Выбор класса' }).getByRole('button', { name: '8 класс', exact: true }).click();
  if (await page.getByRole('button', { name: 'Открыть меню' }).isVisible()) await page.keyboard.press('Escape');
  await page.locator('.section-card').first().click();
  const longDialog = page.getByRole('dialog', { name: 'Алгебраические дроби. Арифметические операции над алгебраическими дробями', exact: true });
  await expect(longDialog).toBeVisible();
  await expect(longDialog.getByRole('listitem')).toHaveCount(7);
  expect(await longDialog.evaluate(element => element.scrollWidth <= element.clientWidth)).toBe(true);
  await longDialog.getByRole('link').last().focus();
  await expect(longDialog.getByRole('link').last()).toBeInViewport();
  await page.screenshot({ path: resolve(here, `../../.cache/home-${testInfo.project.name}-dialog-long.png`) });
  await page.keyboard.press('Escape');
  await page.locator('.section-card').first().click();
  await expect(longDialog.getByRole('link').first()).toBeInViewport();
  await page.keyboard.press('Escape');
  await noOverflow(page);
});
test('global search, empty results, clear and section filter work', async ({ page }, testInfo) => {
  await page.goto('/materials.html');
  const search = page.getByRole('textbox', { name: 'Поиск по всем темам' });
  await search.fill('дроби');
  await expect(page.locator('.result-row').first()).toBeVisible();
  await expect(page.locator('.result-grade').first()).toContainText(/класс · /);
  await expect(page.getByRole('heading', { level: 2, name: /^Найденные темы/ })).toBeVisible();
  await page.getByRole('button', { name: 'Очистить поиск', exact: true }).click();
  await expect(search).toHaveValue('');
  await expect(search).toBeFocused();
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
  await expect(page.locator('.section-card .card-number').first()).toHaveText('6');
  await page.getByRole('button', { name: 'Очистить фильтр разделов' }).click();
  await expect(filter).toHaveValue('');
  await expect(filter).toBeFocused();
  await expect(page.locator('.section-card')).toHaveCount(7);
  await filter.fill('многочлен');
  await page.keyboard.press('Escape');
  await expect(filter).toHaveValue('');
  await filter.fill('несуществующий-раздел-zzzz');
  await expect(page.getByRole('heading', { name: 'Таких разделов нет' })).toBeVisible();
  await expect(page.locator('.section-card')).toHaveCount(0);
  await page.screenshot({ path: resolve(here, `../../.cache/home-${testInfo.project.name}-empty.png`), fullPage: true });
  await page.getByRole('button', { name: 'Показать все разделы' }).click();
  await expect(filter).toBeFocused();
  await expect(filter).toHaveValue('');
  await expect(page.locator('.section-card')).toHaveCount(7);
  await noOverflow(page);
});
test('both themes load local fonts and produce review screenshots', async ({ page }, testInfo) => {
  const failures: string[] = [];
  page.on('requestfailed', request => failures.push(request.url()));
  await page.goto('/materials.html');
  await page.evaluate(() => document.fonts.ready);
  expect(await page.evaluate(() => [...document.fonts].some(face => face.family === 'Outfit' && face.status === 'loaded'))).toBe(true);
  expect(await page.evaluate(() => [...document.fonts].some(face => face.family === 'Merriweather' && face.status === 'loaded'))).toBe(true);
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
  await page.goto('/materials.html');
  const picture = page.locator('svg.math-illustration');
  await expect(picture).toHaveCount(1);
  await expect(picture).toBeVisible();
  const bounds = await picture.boundingBox();
  expect(bounds!.width).toBeGreaterThan(200);
  await expect(page.locator('.lesson-preview, .hero-tags, .nav-active-dot')).toHaveCount(0);
  await expect(page.locator('.breadcrumbs, .nav-home, .count-badge')).toHaveCount(0);
  await expect(page.getByText('ТВОЁ ОБУЧЕНИЕ', { exact: true })).toHaveCount(0);
  await expect(page.getByRole('link', { name: 'О проекте', exact: true })).toHaveCount(0);
  await expect(page.locator('.brand')).toHaveText('MathStart');
  await expect(page.getByText('Темы', { exact: true })).toHaveCount(0);
  await expect(page.getByText('Читать', { exact: true })).toHaveCount(0);
  await expect(page.locator('.brand-mark, .hero-note, .card-arrow')).toHaveCount(0);
  await expect(page.getByRole('heading', { level: 2, name: 'С чего начнём?', exact: true })).toBeVisible();
  await expect(page.locator('.hero')).not.toContainText('разделов');
  await expect(page.getByText('Открыть раздел', { exact: true })).toHaveCount(0);
  for (const target of [page.locator('.brand'), picture.locator('text').first()]) {
    await target.scrollIntoViewIfNeeded();
    const box = (await target.boundingBox())!;
    await page.mouse.move(box.x + 1, box.y + box.height / 2);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width - 1, box.y + box.height / 2, { steps: 8 });
    expect(await page.evaluate(() => window.getSelection()?.toString())).toBe('');
    // Release outside the link so this gesture checks selection, not home navigation.
    await page.mouse.move(box.x + box.width + 12, box.y + box.height / 2);
    await page.mouse.up();
    expect(await page.evaluate(() => window.getSelection()?.toString())).toBe('');
  }
  const description = page.locator('.hero-copy>p');
  await description.dblclick({ position: { x: 30, y: 10 } });
  expect(await page.evaluate(() => window.getSelection()?.toString().length)).toBeGreaterThan(0);
  await page.evaluate(() => window.getSelection()?.removeAllRanges());
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
