// AF2-L-K6-PREP — K6 disabled-endpoint probe (SAFE / DESIGN-ONLY)
//
// PURPOSE: prepare a real k6 load-test asset that exercises the disabled
// `/api/affinity/gift-spend` endpoint and verifies it returns HTTP 423.
// NO real gift spend is performed. The endpoint MUST remain disabled.
//
// Usage (when k6 is installed AND the user explicitly approves a live run):
//   k6 run --vus 50 --duration 30s /app/loadtests/affinity_gift_spend_disabled.k6.js
//
// SAFETY:
//   - This script ONLY POSTs payloads to a disabled endpoint.
//   - The script ASSERTS the response is 423; any 200 means runtime
//     incorrectly activated and the test fails immediately.
//   - No DB write is possible — the endpoint short-circuits.
//   - Borea aliases are tested separately and expected to return 404.

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 50,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
    'checks{kind:disabled}': ['rate==1.0'],
    'checks{kind:borea}':    ['rate==1.0'],
  },
};

const BASE = __ENV.BASE_URL || 'http://127.0.0.1:8001/api';

const DISABLED_PAYLOADS = [
  {},
  { gift_id: 'gift_x', hero_id: 'greek_zeus', quantity: 1, idempotency_key: 'abcdef1234567890' },
  { gift_id: 'gift_x', hero_id: 'greek_zeus', quantity: 1 },
  { gift_id: 'gift_x', hero_id: 'greek_zeus', quantity: 1, idempotency_key: 'duplicate_key_001' },
  { gift_id: 'gift_x', hero_id: 'greek_zeus', quantity: -1, idempotency_key: 'abcdef1234567890' },
  { gift_id: 'gift_x', hero_id: 'greek_zeus', quantity: 9999999, idempotency_key: 'abcdef1234567890' },
];

const BOREA_PAYLOADS = [
  { gift_id: 'x', hero_id: 'borea', quantity: 1, idempotency_key: 'abcd1234efgh' },
  { gift_id: 'x', hero_id: 'greek_borea', quantity: 1, idempotency_key: 'abcd1234efgh' },
  { gift_id: 'x', hero_id: 'primordial_gaia', quantity: 1, idempotency_key: 'abcd1234efgh' },
];

export default function () {
  // 80% of VU iterations target the disabled endpoint with normal payloads
  if (Math.random() < 0.8) {
    const body = DISABLED_PAYLOADS[Math.floor(Math.random() * DISABLED_PAYLOADS.length)];
    const r = http.post(
      `${BASE}/affinity/gift-spend`,
      JSON.stringify(body),
      { headers: { 'Content-Type': 'application/json' }, tags: { kind: 'disabled' } }
    );
    check(r, { 'disabled returns 423': (res) => res.status === 423 }, { kind: 'disabled' });
  } else {
    const body = BOREA_PAYLOADS[Math.floor(Math.random() * BOREA_PAYLOADS.length)];
    const r = http.post(
      `${BASE}/affinity/gift-spend`,
      JSON.stringify(body),
      { headers: { 'Content-Type': 'application/json' }, tags: { kind: 'borea' } }
    );
    check(r, { 'borea alias returns 404': (res) => res.status === 404 }, { kind: 'borea' });
  }
  sleep(0.05);
}
