import { test, expect, type Locator, type Page } from '@playwright/test';

type ContrastSample = { foreground: string; background: string; ratio: number };

async function contrast(locator: Locator): Promise<ContrastSample> {
  return locator.evaluate((element) => {
    const probe = document.createElement('span');
    probe.style.position = 'fixed';
    probe.style.visibility = 'hidden';
    document.body.append(probe);
    const channels = (value: string) => {
      probe.style.color = `color-mix(in srgb, ${value} 100%, transparent)`;
      const converted = getComputedStyle(probe).color;
      const rgb = converted.match(/rgba?\(([^)]+)\)/);
      if (rgb) {
        const values = rgb[1].split(/[ ,/]+/).filter(Boolean).map(Number);
        return [values[0] / 255, values[1] / 255, values[2] / 255, values[3] ?? 1];
      }
      const srgb = converted.match(/color\(srgb\s+([^)]+)\)/);
      if (srgb) {
        const values = srgb[1].split(/[ ,/]+/).filter(Boolean).map(Number);
        return [values[0], values[1], values[2], values[3] ?? 1];
      }
      throw new Error(`Could not convert computed CSS color to sRGB: ${converted}`);
    };
    const linear = (channel: number) => channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
    const luminance = ([r, g, b]: readonly number[]) => .2126 * linear(r) + .7152 * linear(g) + .0722 * linear(b);
    const over = (top: readonly number[], bottom: readonly number[]) => {
      const alpha = top[3];
      return [0, 1, 2, 3].map(index => index === 3 ? alpha + bottom[3] * (1 - alpha) : top[index] * alpha + bottom[index] * (1 - alpha)) as [number, number, number, number];
    };
    let background: readonly number[] = [1, 1, 1, 1];
    const ancestors: Element[] = [];
    for (let node: Element | null = element; node; node = node.parentElement) ancestors.unshift(node);
    for (const node of ancestors) {
      const color = channels(getComputedStyle(node).backgroundColor);
      if (color[3] > 0) background = over(color, background);
    }
    const foreground = channels(getComputedStyle(element).color);
    const paintedForeground = foreground[3] < 1 ? over(foreground, background) : foreground;
    const a = luminance(paintedForeground);
    const b = luminance(background);
    const ratio = (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
    probe.remove();
    return { foreground: getComputedStyle(element).color, background: `rgb(${background.slice(0, 3).map(channel => Math.round(channel * 255)).join(', ')})`, ratio };
  });
}

async function passes(locator: Locator, label: string, minimum = 4.5) {
  await expect(locator).toBeVisible();
  const sample = await contrast(locator);
  expect(sample.ratio, `${label}: ${sample.foreground} on ${sample.background}`).toBeGreaterThanOrEqual(minimum);
}

async function openLesson(page: Page, theme: 'light' | 'dark') {
  await page.goto('/quadratic.html');
  await expect(page.locator('.lesson-preview-page')).toBeVisible();
  if (theme === 'dark') await page.locator('.lesson-theme-toggle').click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', theme);
  await page.waitForTimeout(180);
}

for (const theme of ['light', 'dark'] as const) {
  test(`lesson text meets WCAG AA across settled ${theme} surfaces and interaction states`, async ({ page }) => {
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await openLesson(page, theme);

    const footer = page.locator('.lesson-footer');
    await passes(footer.locator('.lesson-footer-brand p'), `${theme} footer description`);
    await passes(footer.locator('.lesson-copyright'), `${theme} copyright`);

    const headerLink = page.locator('.lesson-header-nav a').first();
    await passes(headerLink, `${theme} header link`);
    await headerLink.hover();
    await passes(headerLink, `${theme} header link hover`);
    const login = page.locator('.lesson-login');
    await passes(login, `${theme} header action icon`, 3);
    await login.hover();
    await passes(login, `${theme} header action icon hover`, 3);

    const footerLink = footer.locator('a').first();
    await passes(footerLink, `${theme} footer link`);
    await footerLink.hover();
    await passes(footerLink, `${theme} footer link hover`);
    const gradeLink = footer.locator('.lesson-footer-grades a').first();
    await gradeLink.hover();
    await passes(gradeLink, `${theme} footer grade link hover`);

    const next = page.locator('.lesson-next .lesson-direction');
    await next.scrollIntoViewIfNeeded();
    await passes(next, `${theme} next-topic button`);
    await next.hover();
    await passes(next, `${theme} next-topic button hover`);

    const answer = page.locator('.lesson-answer-toggle').first();
    await answer.scrollIntoViewIfNeeded();
    await passes(answer, `${theme} answer button`);
    await answer.hover();
    await passes(answer, `${theme} answer button hover`);
    await answer.click();
    await expect(answer).toHaveAttribute('aria-expanded', 'true');
    await passes(answer, `${theme} open answer button`);

    const reset = page.locator('.quadratic-reset');
    await reset.scrollIntoViewIfNeeded();
    await passes(reset, `${theme} graph reset`);
    await reset.hover();
    await passes(reset, `${theme} graph reset hover`);

    if (theme === 'dark') {
      await passes(page.locator('.quadratic-current'), 'dark graph formula', 3);
      await passes(page.locator('.coefficient-control output').first(), 'dark coefficient output');
      await passes(page.locator('.quadratic-legend .legend-curve'), 'dark graph legend');
      await passes(page.locator('.quadratic-legend .legend-root'), 'dark root legend');
    }
  });
}
