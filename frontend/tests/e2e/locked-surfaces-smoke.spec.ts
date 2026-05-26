import { test, expect } from '@playwright/test';

// PROJECT_BETA_TESTING_AUTOMATION_HARNESS Track E
// Locked surfaces smoke: lock/preparation text must be visible AND no live
// buy/claim/craft labels.

const LOCKED_SURFACES: { route: string; mustContainAny?: string[] }[] = [
  { route: '/shop',       mustContainAny: ['REVISIONE', 'PREPARAZIONE', 'LOCKED', 'lock'] },
  { route: '/item-shop',  mustContainAny: ['REVISIONE', 'PREPARAZIONE', 'LOCKED', 'lock'] },
  { route: '/battlepass', mustContainAny: ['REVISIONE', 'PREPARAZIONE', 'LOCKED', 'lock'] },
  { route: '/vip',        mustContainAny: ['REVISIONE', 'PREPARAZIONE', 'LOCKED', 'lock'] },
  { route: '/exclusive',  mustContainAny: ['legacy', 'archiviata', 'LOCKED', 'lock'] },
];

// Tokens that MUST NOT appear on any locked screen, because they imply live action.
const FORBIDDEN_LIVE_LABELS = [
  'COMPRA ORA',
  'ACQUISTA',
  'CRAFT NOW',
  'FORGIA SUBITO',
];

for (const { route, mustContainAny = [] } of LOCKED_SURFACES) {
  test(`locked surface ${route} shows lock and no live action`, async ({ page }) => {
    await page.goto(route, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2500);
    const text = await page.evaluate(() => document.body.innerText || '');
    expect(text.length, `${route} body must not be blank`).toBeGreaterThan(20);
    if (mustContainAny.length) {
      const ok = mustContainAny.some(s => text.toLowerCase().includes(s.toLowerCase()));
      expect(ok, `${route} expected one of ${mustContainAny.join('|')} in body, got: ${text.slice(0, 200)}`).toBeTruthy();
    }
    for (const forbidden of FORBIDDEN_LIVE_LABELS) {
      expect(text, `${route} must not display live action label: ${forbidden}`).not.toContain(forbidden);
    }
  });
}
