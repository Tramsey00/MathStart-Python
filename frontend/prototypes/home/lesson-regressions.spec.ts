import { test, expect } from '@playwright/test';

test('fresh catalogue navigation has no missing favicon or browser errors', async ({ page }) => {
  const errors: string[] = [];
  const failed: string[] = [];
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  page.on('pageerror', error => errors.push(error.message));
  page.on('response', response => { if (response.status() >= 400) failed.push(`${response.status()} ${response.url()}`); });
  await page.goto('/materials.html?grade=8-klass&subject=algebra');
  await expect(page.locator('link[rel=icon]')).toHaveAttribute('href', 'data:,');
  await page.locator('#topic-search').fill('Квадратичная функция');
  const link = page.locator('.search-results a').filter({ hasText: 'Квадратичная функция y = ax² + bx + c' });
  await expect(link).toHaveAttribute('href', '/materials/8-algebra-32');
  await link.click();
  await expect(page).toHaveURL(/\/materials\/8-algebra-32$/);
  await expect(page.locator('.self-check')).toHaveCount(10);
  await page.reload();
  await expect(page.locator('.lesson-section')).toHaveCount(8);
  // Allow the browser's automatic favicon request to be observed in a fresh context.
  await page.waitForTimeout(300);
  expect(failed).toEqual([]);
  expect(errors).toEqual([]);
});

test('touch scrolling and explicit cancellation preserve x, then a confirmed tap selects', async ({ browser, page }, info) => {
  const context = await browser.newContext({ baseURL: 'http://127.0.0.1:5173', viewport: page.viewportSize()!, hasTouch: true });
  const touch = await context.newPage();
  const cdp = await context.newCDPSession(touch);
  try {
    for (const theme of ['light', 'dark']) {
      await touch.goto('/materials/8-algebra-32');
      if (theme === 'dark') await touch.getByRole('button', { name: 'Включить тёмную тему' }).click();
      const svg = touch.locator('.quadratic-plot svg');
      const probe = touch.getByRole('slider', { name: 'Абсцисса исследуемой точки x' });
      await expect(probe).toHaveValue('0');
      await expect(svg).toHaveCSS('touch-action', 'pan-y');
      await svg.evaluate(node => node.scrollIntoView({ block: 'center', behavior: 'instant' }));
      const box = (await svg.boundingBox())!;
      const x = box.x + box.width * .75, y = box.y + box.height * .65;
      const beforeScroll = await touch.evaluate(() => scrollY);
      await svg.evaluate(node => {
        node.setAttribute('data-cancel-count', '0');
        node.addEventListener('pointercancel', () => node.setAttribute('data-cancel-count', String(Number(node.getAttribute('data-cancel-count')) + 1)));
      });
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] });
      for (let step = 1; step <= 8; step++) {
        await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x, y: y - step * 12 }] });
        await touch.waitForTimeout(20);
      }
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
      await expect.poll(() => touch.evaluate(() => scrollY)).toBeGreaterThan(beforeScroll);
      await expect(svg).toHaveAttribute('data-cancel-count', '1');
      await expect(probe).toHaveValue('0');

      await svg.evaluate(node => node.scrollIntoView({ block: 'center', behavior: 'instant' }));
      const afterBox = (await svg.boundingBox())!;
      const point = { x: afterBox.x + afterBox.width * .65, y: afterBox.y + afterBox.height / 2 };
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [point] });
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchCancel', touchPoints: [] });
      await expect(svg).toHaveAttribute('data-cancel-count', '2');
      await expect(probe).toHaveValue('0');
      await touch.touchscreen.tap(point.x, point.y);
      await expect.poll(async () => Number(await probe.inputValue())).toBeGreaterThan(1);
      const selected = await probe.inputValue();
      await touch.mouse.move(afterBox.x + afterBox.width * .8, point.y);
      await expect(probe).toHaveValue(selected);
      await touch.screenshot({ path: info.outputPath(`touch-cancel-recovery-${theme}.png`) });
      expect(await touch.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    }
  } finally { await context.close(); }
});
