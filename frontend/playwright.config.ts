import { defineConfig, devices } from '@playwright/test';

// PROJECT_BETA_TESTING_AUTOMATION_HARNESS Track E
// Smoke harness for Expo Web preview. Stable URL is the preview URL exposed by
// EXPO_PUBLIC_API_URL (relative /api) + the kubernetes ingress at "/". Locally
// we hit http://localhost:3000 because the same metro dev server serves the web
// bundle there. CI/preview override via env BETA_BASE_URL.
const BASE_URL = process.env.BETA_BASE_URL || 'http://localhost:3000';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: [
    ['list'],
    ['json', { outputFile: 'test-results/beta-smoke-report.json' }],
  ],
  outputDir: 'test-results',
  use: {
    baseURL: BASE_URL,
    headless: true,
    viewport: { width: 390, height: 844 },
    ignoreHTTPSErrors: true,
    screenshot: 'only-on-failure',
    video: 'off',
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'mobile-chromium-390x844',
      use: { ...devices['Pixel 5'], viewport: { width: 390, height: 844 } },
    },
  ],
});
