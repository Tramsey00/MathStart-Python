import { test, expect, type Locator } from '@playwright/test';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

async function coefficient(input: Locator, value: number) {
  await input.evaluate((node, next) => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(node, String(next));
    node.dispatchEvent(new Event('input', { bubbles: true }));
  }, value);
}

test('lesson keeps the article, answers, anchors and adjacent navigation', async ({ page }, info) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto('/materials/8-algebra-32');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Квадратичная функция y = ax² + bx + c');
  await expect(page.locator('.lesson-section')).toHaveCount(8);
  await expect(page.locator('.self-check')).toHaveCount(10);
  await expect(page.locator('.ms-quadratic-svg')).toHaveCount(2);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await expect(page.locator('.lesson-previous')).toHaveAttribute('href', 'http://127.0.0.1:8121/kak-postroit-grafik-funkczii-y-fx-m-n/');
  await expect(page.locator('.lesson-next')).toHaveAttribute('href', 'http://127.0.0.1:8121/reshenie-kvadratnyh-uravnenij-s-pomoshhyu-grafikov-funkczij/');
  await expect(page.getByRole('heading', { name: 'Паспорт параболы за пять действий' })).toHaveCount(0);
  await expect(page.getByRole('heading', { name: 'Далее', exact: true })).toHaveCount(0);
  const trigger = page.getByRole('button', { name: 'Содержание урока', exact: true });
  const panel = page.getByRole('dialog', { name: 'Содержание урока' });
  await expect(panel).not.toBeVisible();
  await trigger.click();
  await expect(panel).toBeVisible();
  await panel.getByRole('navigation', { name: 'Содержание урока' }).getByRole('link', { name: 'Самопроверка', exact: true }).click();
  await expect(page).toHaveURL(/#lesson-section-8$/);
  await expect(panel).not.toBeVisible();
  await expect(page.locator('#lesson-section-8')).toBeFocused();
  const headingTop = await page.locator('#lesson-section-8').evaluate(node => node.getBoundingClientRect().top);
  expect(headingTop).toBeGreaterThan(75);
  expect(headingTop).toBeLessThanOrEqual(160);
  const answer = page.locator('.self-check').first();
  const question = answer.locator('.lesson-question-copy');
  const toggle = answer.getByRole('button', { name: 'Ответ и решение' });
  const expander = answer.locator('.lesson-reveal-expander');
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await expect(expander).toHaveAttribute('aria-hidden', 'true');
  await expect(expander).toHaveAttribute('inert', '');
  await expect(question).toBeVisible();
  await question.click();
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await toggle.focus();
  await page.keyboard.press('Enter');
  await expect(toggle).toHaveAttribute('aria-expanded', 'true');
  await expect(expander).toHaveAttribute('aria-hidden', 'false');
  await expect(expander).not.toHaveAttribute('inert', '');
  await expect(expander.locator('.lesson-reveal-content')).toContainText('a = 3, b = −7, c = 2');
  await page.keyboard.press('Enter');
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await expect(expander).toHaveAttribute('aria-hidden', 'true');
  await expect(expander).toHaveAttribute('inert', '');
  expect(await page.locator('.worked-example,.lesson-note').evaluateAll(nodes => nodes.every(node => getComputedStyle(node).borderLeftWidth === '0px'))).toBe(true);
  expect(errors).toEqual([]);
});

test('canonical lesson route survives aliases, query strings, fragments and reloads', async ({ page }) => {
  const aliases = [
    '/quadratic.html?audit=1&source=test#lesson-section-8',
    '/kvadratichnaya-funkcziya-y-ax2-bx-c?audit=1&source=test#lesson-section-8',
    '/kvadratichnaya-funkcziya-y-ax2-bx-c/?audit=1&source=test#lesson-section-8',
    '/materials/8-algebra-32/?audit=1&source=test#lesson-section-8',
  ];
  for (const alias of aliases) {
    await page.goto(alias);
    await expect(page).toHaveURL(/\/materials\/8-algebra-32\?audit=1&source=test#lesson-section-8$/);
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Квадратичная функция y = ax² + bx + c');
  }
  await page.reload();
  await expect(page).toHaveURL(/\/materials\/8-algebra-32\?audit=1&source=test#lesson-section-8$/);
  await expect(page.locator('#lesson-section-8')).toBeVisible();
  await page.goto('/materials.html');
  await page.getByLabel('Поиск по всем темам').fill('Квадратичная функция y = ax² + bx + c');
  await page.getByRole('link', { name: /Квадратичная функция y = ax² \+ bx \+ c/ }).click();
  await expect(page).toHaveURL(/\/materials\/8-algebra-32$/);
});

test('contents panel traps focus, closes on Escape/backdrop and marks the current section', async ({ page }, info) => {
  await page.goto('/quadratic.html');
  const trigger = page.getByRole('button', { name: 'Содержание урока', exact: true });
  const panel = page.getByRole('dialog', { name: 'Содержание урока' });
  await trigger.focus();
  await page.keyboard.press('Enter');
  await expect(panel).toBeVisible();
  await expect(panel.getByRole('navigation', { name: 'Содержание урока' }).getByRole('link')).toHaveCount(8);
  const panelBox = await panel.boundingBox();
  expect(panelBox!.y).toBe(0);
  expect(panelBox!.height).toBe(page.viewportSize()!.height);
  await expect(panel.getByRole('button', { name: 'Закрыть содержание' })).toBeFocused();
  await panel.getByRole('link').last().focus();
  await page.keyboard.press('Tab');
  await expect(panel.getByRole('button', { name: 'Закрыть содержание' })).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(panel).not.toBeVisible();
  await expect(trigger).toBeFocused();
  await page.locator('#theory').evaluate(node => node.scrollIntoView({ block: 'start' }));
  await trigger.click();
  await expect(panel.locator('a[aria-current="location"]')).toHaveAttribute('href', '#theory');
  await expect(panel).toHaveCSS('opacity', '1');
  await page.screenshot({ path: info.outputPath('contents-open.png'), animations: 'disabled' });
  for (let cycle = 0; cycle < 8; cycle++) {
    await trigger.focus();
    await page.keyboard.press('Enter');
    await expect(panel).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(panel).not.toBeVisible();
    await expect(trigger).toBeFocused();
  }
  await trigger.focus();
  await page.keyboard.press('Enter');
  if (page.viewportSize()!.width > 420) await page.mouse.click(page.viewportSize()!.width - 10, 220);
  else await panel.getByRole('button', { name: 'Закрыть содержание' }).click();
  await expect(panel).not.toBeVisible();
  expect(await page.evaluate(() => document.body.style.overflow)).toBe('');
});

test('React graph updates mathematics and resets, including the linear case', async ({ page }, info) => {
  await page.goto('/quadratic.html#interactive-lab');
  const lab = page.locator('.quadratic-lab');
  await expect(lab.locator('.quadratic-current')).toHaveText('y = x² − 4x + 3');
  await expect(lab.locator('dd').nth(1)).toHaveText('V(2; −1)');
  await expect(lab.locator('td[data-x="-2"]')).toHaveText('15');
  const a = lab.getByRole('slider', { name: /Коэффициент a/ });
  await a.focus();
  await page.keyboard.press('ArrowRight');
  await expect(a).toHaveValue('1.1');
  await expect(lab.locator('.quadratic-current')).toHaveText('y = 1,1x² − 4x + 3');
  await coefficient(a, 0);
  await expect(lab.locator('dd').first()).toHaveText('Линейная функция');
  await expect(lab.locator('dd').nth(5)).toHaveText('x = 0,75');
  await coefficient(lab.getByRole('slider', { name: /Коэффициент b/ }), 0);
  await coefficient(lab.getByRole('slider', { name: /Коэффициент c/ }), 0);
  await expect(lab.locator('dd').first()).toHaveText('Постоянная функция');
  await expect(lab.locator('dd').nth(2)).toHaveText('Любая прямая x = k');
  await expect(lab.locator('dd').nth(5)).toHaveText('Любое действительное x');
  await lab.getByRole('button', { name: 'Сбросить коэффициенты' }).click();
  await expect(a).toHaveValue('1');
  await expect(lab.locator('dd').nth(5)).toHaveText('x₁ = 1, x₂ = 3');
  await a.press('End');
  await lab.getByRole('slider', { name: /Коэффициент b/ }).press('Home');
  await lab.getByRole('slider', { name: /Коэффициент c/ }).press('End');
  await lab.getByRole('button', { name: 'Сбросить коэффициенты' }).click();
  await page.waitForTimeout(80);
  await a.focus();
  await page.keyboard.press('ArrowRight');
  const interruptedA = await a.inputValue();
  await page.waitForTimeout(450);
  await expect(a).toHaveValue(interruptedA);
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await a.press('End');
  await lab.getByRole('button', { name: 'Сбросить коэффициенты' }).click();
  await expect(a).toHaveValue('1');
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  if (page.viewportSize()!.width >= 1200) {
    await page.setViewportSize({ width: page.viewportSize()!.width, height: 800 });
    await lab.evaluate(node => node.scrollIntoView({ block: 'start' }));
    for (const selector of ['.quadratic-plot', '.quadratic-properties', '.quadratic-values']) {
      const box = await lab.locator(selector).boundingBox();
      expect(box!.y, selector).toBeGreaterThanOrEqual(76);
      expect(box!.y + box!.height, selector).toBeLessThanOrEqual(800);
    }
    await page.screenshot({ path: info.outputPath('graph-with-values.png'), animations: 'disabled' });
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test('lesson keeps brand tokens and uses a flat local neutral surface in both modes', async ({ page }, info) => {
  await page.goto('/quadratic.html');
  const tokenNames = ['--primary', '--background', '--foreground', '--font-sans', '--font-serif', '--radius'];
  const tokens = () => page.evaluate(names => Object.fromEntries(names.map(name => [name, getComputedStyle(document.documentElement).getPropertyValue(name).trim()])), tokenNames);
  const lessonLight = await tokens();
  expect(await page.locator('.lesson-article,.worked-example,.lesson-note').evaluateAll(nodes => nodes.every(node => getComputedStyle(node).backgroundColor === 'rgba(0, 0, 0, 0)' && getComputedStyle(node).borderLeftWidth === '0px'))).toBe(true);
  await page.screenshot({ path: info.outputPath('lesson-top.png') });
  await page.goto('/materials.html');
  expect(await tokens()).toEqual(lessonLight);
  await page.goto('/quadratic.html');
  await page.getByRole('button', { name: 'Включить тёмную тему' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  const lessonDark = await tokens();
  await page.locator('#interactive-lab').scrollIntoViewIfNeeded();
  await page.screenshot({ path: info.outputPath('graph-dark.png') });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.goto('/materials.html');
  expect(await tokens()).toEqual(lessonDark);
});

test('refined lesson stays usable in both themes with adjacent titles available to assistive technology', async ({ page }, info) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto('/quadratic.html');
  for (const theme of ['light', 'dark']) {
    if (theme === 'dark') await page.getByRole('button', { name: 'Включить тёмную тему' }).click();
    const trigger = page.getByRole('button', { name: 'Содержание урока', exact: true });
    expect((await trigger.boundingBox())!.height).toBeGreaterThanOrEqual(44);
    await trigger.click();
    const panel = page.getByRole('dialog', { name: 'Содержание урока' });
    expect((await panel.boundingBox())!.width).toBeLessThanOrEqual(520);
    const close = await panel.getByRole('button', { name: 'Закрыть содержание' }).boundingBox();
    expect(close!.width + 0.01).toBeGreaterThanOrEqual(44);
    expect(close!.height + 0.01).toBeGreaterThanOrEqual(44);
    await panel.getByRole('link', { name: 'Самопроверка', exact: true }).focus();
    await page.screenshot({ path: info.outputPath(`contents-${theme}.png`), animations: 'disabled' });
    await page.keyboard.press('Enter');
    await expect(page.locator('#lesson-section-8')).toBeFocused();
    for (const check of await page.locator('.self-check').all()) {
      const summary = check.getByRole('button', { name: 'Ответ и решение' });
      expect((await summary.boundingBox())!.height).toBeGreaterThanOrEqual(33);
      await expect(check.locator('.lesson-question-copy')).toBeVisible();
      await check.locator('.lesson-question-copy').click();
      await expect(summary).toHaveAttribute('aria-expanded', 'false');
      await summary.focus();
      await page.keyboard.press('Space');
      await expect(summary).toHaveAttribute('aria-expanded', 'true');
      await expect(check.locator('.lesson-reveal-expander')).toHaveAttribute('aria-hidden', 'false');
      await expect(check.locator('.lesson-reveal-expander')).not.toHaveAttribute('inert', '');
      await expect(check.locator('.lesson-reveal-content')).toBeVisible();
      await page.keyboard.press('Space');
      await expect(summary).toHaveAttribute('aria-expanded', 'false');
      await expect(check.locator('.lesson-reveal-expander')).toHaveAttribute('aria-hidden', 'true');
      await expect(check.locator('.lesson-reveal-expander')).toHaveAttribute('inert', '');
    }
    await page.locator('.self-check .lesson-answer-toggle').first().click();
    await page.locator('#lesson-section-8').evaluate(node => node.scrollIntoView({ block: 'start' }));
    await page.screenshot({ path: info.outputPath(`self-check-${theme}.png`) });
    await page.locator('.self-check .lesson-answer-toggle').first().click();
    const navigation = page.getByRole('navigation', { name: 'Переход между темами' });
    for (const selector of ['.lesson-previous', '.lesson-next']) {
      const link = navigation.locator(selector);
      const title = await link.getAttribute('aria-label');
      expect(title).toMatch(/^(Предыдущая|Следующая) тема: .+/);
      await expect(link.locator('.lesson-topic-title')).toHaveCount(0);
      await expect(link).toBeVisible();
      expect(await link.evaluate(node => node.scrollWidth <= node.clientWidth)).toBe(true);
    }
    await navigation.locator('.lesson-previous').focus();
    await page.keyboard.press('Tab');
      await expect(navigation.locator('.lesson-next')).toBeFocused();
    await expect(navigation.locator('.lesson-next')).toHaveCSS('outline-style', 'solid');
    await page.screenshot({ path: info.outputPath(`navigation-${theme}.png`) });
    await expect(navigation.locator('.lesson-previous')).toHaveAttribute('href', 'http://127.0.0.1:8121/kak-postroit-grafik-funkczii-y-fx-m-n/');
    await expect(navigation.locator('.lesson-next')).toHaveAttribute('href', 'http://127.0.0.1:8121/reshenie-kvadratnyh-uravnenij-s-pomoshhyu-grafikov-funkczij/');
    await page.route('http://127.0.0.1:8121/**', route => route.fulfill({ status: 200, contentType: 'text/html', body: '<title>Navigation intercepted</title>' }));
    await navigation.locator('.lesson-previous').focus();
    await page.keyboard.press('Enter');
    await expect(page).toHaveURL('http://127.0.0.1:8121/kak-postroit-grafik-funkczii-y-fx-m-n/');
    await page.goto('/materials/8-algebra-32');
    const nextNavigation = page.getByRole('navigation', { name: 'Переход между темами' });
    await nextNavigation.locator('.lesson-next').focus();
    await page.keyboard.press('Enter');
    await expect(page).toHaveURL('http://127.0.0.1:8121/reshenie-kvadratnyh-uravnenij-s-pomoshhyu-grafikov-funkczij/');
    await page.goto('/materials/8-algebra-32');
    await page.unroute('http://127.0.0.1:8121/**');
    await page.locator('.quadratic-lab').evaluate(node => node.scrollIntoView({ block: 'start' }));
    for (const slider of await page.getByRole('slider').all()) {
      expect((await slider.boundingBox())!.height).toBeGreaterThanOrEqual(44);
    }
    await page.getByRole('slider', { name: 'Коэффициент a' }).focus();
    await page.keyboard.press('ArrowRight');
    await expect(page.getByRole('slider', { name: 'Коэффициент a' })).toHaveValue('1.1');
    await page.getByRole('button', { name: 'Сбросить коэффициенты' }).click();
    const resolveLessonToken = (token: string) => page.evaluate(name => {
      const probe = document.createElement('span');
      probe.style.color = `var(${name})`;
      document.body.append(probe);
      const color = getComputedStyle(probe).color;
      probe.remove();
      return color;
    }, token);
    expect(await page.locator('.legend-root').evaluate(node => getComputedStyle(node).color))
      .toBe(await resolveLessonToken('--lesson-accent-text'));
    expect(await page.locator('.plot-root').first().evaluate(node => getComputedStyle(node).stroke))
      .toBe(await resolveLessonToken('--lesson-accent'));
    // Stress real toolbar wrapping and values without changing mathematical behavior.
    await page.getByRole('slider', { name: 'Коэффициент a' }).press('End');
    await page.getByRole('slider', { name: 'Коэффициент b' }).press('Home');
    await page.getByRole('slider', { name: 'Коэффициент c' }).press('End');
    await expect(page.locator('.quadratic-current')).toHaveText('y = 4x² − 10x + 10');
    expect(await page.locator('.quadratic-toolbar').evaluate(node => node.scrollWidth <= node.clientWidth)).toBe(true);
    await page.getByRole('button', { name: 'Сбросить коэффициенты' }).click();
    await page.locator('.quadratic-lab').evaluate(node => node.scrollIntoView({ block: 'start' }));
    await page.screenshot({ path: info.outputPath(`lab-${theme}.png`) });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  }
  expect(errors).toEqual([]);
});

test('authored diagrams stay static and the point probe uses its keyboard slider', async ({ page }, info) => {
  await page.goto('/quadratic.html');
  for (const theme of ['light', 'dark']) {
    if (theme === 'dark') await page.getByRole('button', { name: 'Включить тёмную тему' }).click();
    for (const diagram of await page.locator('.lesson-diagram').all()) {
      const svg = diagram.locator('svg');
      const original = await svg.evaluate(node => node.outerHTML);
      await expect(diagram.getByRole('button')).toHaveCount(0);
      expect(await svg.evaluate(node => node.outerHTML)).toBe(original);
      expect(await svg.evaluate(node => node.getBoundingClientRect().width <= node.parentElement!.clientWidth + 1)).toBe(true);
    }
    const formula = page.locator('.lesson-vertex-formula');
    await expect(formula).toHaveText('y = a(x − x₀)² + y₀');
    await expect(formula).toHaveCSS('color', await page.locator('.ms-quadratic-formula-main').first().evaluate(node => getComputedStyle(node).color));
    expect(parseFloat(await formula.evaluate(node => getComputedStyle(node).fontSize))).toBeGreaterThan(20);
    await formula.scrollIntoViewIfNeeded();
    await page.screenshot({ path: info.outputPath(`vertex-formula-${theme}.png`) });
    const probe = page.getByRole('slider', { name: 'Абсцисса исследуемой точки x' });
    await probe.focus();
    await probe.press('ArrowRight');
    await expect(probe).toHaveValue('0.1');
    await expect(probe).toHaveAttribute('aria-valuetext', 'x = 0,1; y = 2,61');
    await probe.press('End');
    await expect(probe).toHaveAttribute('aria-valuetext', 'x = 10; y = 63');
    await expect(page.locator('.quadratic-probe-outside')).toBeVisible();
    await probe.press('Home');
    await expect(probe).toHaveAttribute('aria-valuetext', 'x = −10; y = 143');
    await page.getByRole('button', { name: 'Сбросить коэффициенты' }).click();
    await expect(probe).toHaveValue('0');
    await page.locator('.quadratic-plot svg').scrollIntoViewIfNeeded();
    const plot = await page.locator('.quadratic-plot svg').boundingBox();
    await page.mouse.move(plot!.x + plot!.width * (48 + 13 / 20 * 504) / 580, plot!.y + plot!.height / 2);
    await expect(probe).toHaveValue('0');
    await page.mouse.down();
    await page.mouse.up();
    await expect(probe).toHaveValue('0');
    await page.mouse.move(0, 0);
    await expect(probe).toHaveValue('0');
    await page.getByRole('button', { name: 'Сбросить коэффициенты' }).click();
    await expect(page.locator('.quadratic-probe')).not.toContainText('Наведите');
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  }
});

test('touch only selects a point on the native slider', async ({ browser, page }, info) => {
  const context = await browser.newContext({ viewport: page.viewportSize()!, hasTouch: true });
  const touch = await context.newPage();
  try {
    for (const theme of ['light', 'dark']) {
      // A fresh document cancels momentum scrolling from the preceding touch run.
      await touch.goto('http://127.0.0.1:5173/quadratic.html');
      if (theme === 'dark') await touch.getByRole('button', { name: 'Включить тёмную тему' }).click();
      const probe = touch.getByRole('slider', { name: 'Абсцисса исследуемой точки x' });
      const svg = touch.locator('.quadratic-plot svg');
      await svg.scrollIntoViewIfNeeded();
      const box = await svg.boundingBox();
      await touch.touchscreen.tap(box!.x + box!.width * (48 + 12 / 20 * 504) / 580, box!.y + box!.height / 2);
      await expect(probe).toHaveValue('0');
      await expect(touch.locator('.plot-probe')).toBeVisible();
      await probe.scrollIntoViewIfNeeded();
      const sliderBox = await probe.boundingBox();
      await probe.tap({ position: { x: sliderBox!.width / 2, y: sliderBox!.height / 2 } });
      await expect(probe).toHaveValue('0');
      await expect(probe).toHaveAttribute('aria-valuetext', 'x = 0; y = 3');
      const diagram = touch.locator('.lesson-diagram').first();
      await expect(diagram.getByRole('button')).toHaveCount(0);
    }
  } finally { await context.close(); }
});

test('real Chrome page zoom 200% preserves reflow and lesson controls', async ({ playwright, page }, info) => {
  const profile = info.outputPath('zoom-profile');
  mkdirSync(join(profile, 'Default'), { recursive: true });
  // Chromium ChromeZoomLevelPrefs: default partition key "x", logarithmic zoom level.
  // https://github.com/chromium/chromium/blob/main/chrome/browser/ui/zoom/chrome_zoom_level_prefs.cc
  writeFileSync(join(profile, 'Default', 'Preferences'), JSON.stringify({ partition: { default_zoom_level: { x: Math.log(2) / Math.log(1.2) } } }));
  const context = await playwright.chromium.launchPersistentContext(profile, { channel: 'chrome', headless: true, viewport: null,
    args: [`--window-size=${Math.max(720, page.viewportSize()!.width)},1000`] });
  try {
    const zoomed = context.pages()[0]!;
    const cdp = await context.newCDPSession(zoomed);
    // Playwright's default viewport clip assumes 100% page zoom. Capture the
    // compositor surface directly so the whole zoomed viewport is visible.
    const capture = async (name: string) => {
      const screenshot = await cdp.send('Page.captureScreenshot', { format: 'png', fromSurface: true });
      writeFileSync(info.outputPath(name), Buffer.from(screenshot.data, 'base64'));
    };
    await zoomed.goto('http://127.0.0.1:5173/quadratic.html');
    const dimensions = await zoomed.evaluate(() => ({ dpr: devicePixelRatio, outer: outerWidth, inner: innerWidth }));
    expect(dimensions.dpr).toBeCloseTo(2, 2);
    expect(dimensions.outer / dimensions.inner).toBeGreaterThan(1.9);
    for (const theme of ['light', 'dark']) {
      if (theme === 'dark') await zoomed.getByRole('button', { name: 'Включить тёмную тему' }).click();
      await zoomed.evaluate(() => window.scrollTo(0, 0));
      await capture(`zoom-200-top-${theme}.png`);
      const contentsTrigger = zoomed.getByRole('button', { name: 'Содержание урока', exact: true });
      await contentsTrigger.focus();
      await zoomed.keyboard.press('Enter');
      const contentsLink = zoomed.getByRole('link', { name: 'Самопроверка', exact: true });
      await contentsLink.focus();
      await zoomed.keyboard.press('Enter');
      const answerToggle = zoomed.locator('.self-check .lesson-answer-toggle').first();
      await answerToggle.focus();
      await zoomed.keyboard.press('Enter');
      await expect(answerToggle).toHaveAttribute('aria-expanded', 'true');
      await expect(answerToggle.locator('..').locator('.lesson-reveal-expander')).toHaveAttribute('aria-hidden', 'false');
      await zoomed.keyboard.press('Enter');
      await expect(answerToggle).toHaveAttribute('aria-expanded', 'false');
      const probe = zoomed.getByRole('slider', { name: 'Абсцисса исследуемой точки x' });
      await probe.press('ArrowRight');
      await expect(probe).toHaveValue('0.1');
      const reset = zoomed.getByRole('button', { name: 'Сбросить коэффициенты' });
      await reset.focus();
      await zoomed.keyboard.press('Enter');
      const enlarge = zoomed.locator('.lesson-diagram').first().getByRole('button');
      if (await enlarge.isVisible()) {
        await enlarge.press('Enter');
        await expect(enlarge).toHaveAttribute('aria-pressed', 'true');
        await enlarge.press('Enter');
      }
      await zoomed.locator('.lesson-vertex-formula').scrollIntoViewIfNeeded();
      await capture(`zoom-200-formula-${theme}.png`);
      await zoomed.locator('.quadratic-lab').evaluate(node => node.scrollIntoView({ block: 'start' }));
      await capture(`zoom-200-lab-${theme}.png`);
      expect(await zoomed.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    }
  } finally { await context.close(); }
});
