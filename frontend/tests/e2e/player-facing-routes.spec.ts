import { test, expect } from '@playwright/test';

// PROJECT_BETA_TESTING_AUTOMATION_HARNESS Track E
// Player-facing core route smoke. The goal is NOT to drive deep flows; it is
// to assert that each player-facing route loads and renders something visible
// (no blank screen) on a mobile viewport.
const ROUTES = [
  '/treasury',
  '/economy',
  '/exclusive',
  '/gacha',
  '/artifacts-preview',
  '/shop',
  '/item-shop',
  '/battlepass',
  '/vip',
  '/servers',
  '/safe-previews',
  '/daily-hub',
];

for (const route of ROUTES) {
  test(`route ${route} renders something (no blank)`, async ({ page }) => {
    await page.goto(route, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2500);
    const bodyText = await page.evaluate(() => document.body.innerText || '');
    // 1) Body must have at least 20 chars of visible text.
    expect(bodyText.length, `body too short on ${route}: "${bodyText.slice(0, 200)}"`).toBeGreaterThan(20);
    // 2) Must not show a raw error banner like "Application error" alone.
    expect(bodyText.toLowerCase()).not.toContain('application error');
  });
}
