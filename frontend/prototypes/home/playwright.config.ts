import { defineConfig } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
export default defineConfig({
  testDir: here,
  testMatch: ['home.spec.ts', 'landing.spec.ts'],
  outputDir: resolve(here, '../../.cache/home-prototype-test-results'),
  reporter: [['list'], ['json', { outputFile: resolve(here, '../../.cache/home-prototype-results.json') }]],
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 45_000,
  use: { baseURL: 'http://127.0.0.1:5173', channel: 'chrome', screenshot: 'only-on-failure' },
  projects: [360, 768, 1440, 1920].map(width => ({ name: `chrome-${width}`, use: { viewport: { width, height: width === 360 ? 800 : 1000 } } })),
  webServer: {
    command: `"${process.execPath}" "${resolve(here, '../../node_modules/vite/bin/vite.js')}" --config "${resolve(here, 'vite.config.mjs')}"`,
    url: 'http://127.0.0.1:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
  },
});
