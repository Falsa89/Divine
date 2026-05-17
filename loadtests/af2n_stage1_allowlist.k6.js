// AF2-N-STAGE1-K6-LIVE — k6 script (NOT executed today, k6 binary not installed)
// Targets only safe surfaces: 423/404/idempotent_replay. Avoids new ledger rows.
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
  },
};

const API = 'http://127.0.0.1:8001/api';

export default function () {
  // 1. health
  check(http.get(`${API}/health`), { 'health 200': (r) => r.status === 200 });
  // 2. heroes count = 100 (skipped detail check for perf)
  check(http.get(`${API}/heroes`), { 'heroes 200': (r) => r.status === 200 });
  // 3. canary-status
  check(http.get(`${API}/affinity/gift-spend/canary-status`), { 'status 200': (r) => r.status === 200 });
  // 4. empty POST -> 423
  check(
    http.post(`${API}/affinity/gift-spend`, '{}', { headers: { 'Content-Type': 'application/json' } }),
    { 'empty 423': (r) => r.status === 423 }
  );
  // 5. Borea -> 404
  check(
    http.post(`${API}/affinity/gift-spend`,
      JSON.stringify({ gift_id: 'x', hero_id: 'borea', quantity: 1, idempotency_key: 'abcd1234efgh', user_id: 'user_canary_001' }),
      { headers: { 'Content-Type': 'application/json' } }),
    { 'borea 404': (r) => r.status === 404 }
  );
  // 6. non-allowlist -> 423
  check(
    http.post(`${API}/affinity/gift-spend`,
      JSON.stringify({ gift_id: 'x', hero_id: 'greek_zeus', quantity: 1, idempotency_key: `rnd${__ITER}`, user_id: 'unauth_user_xxx' }),
      { headers: { 'Content-Type': 'application/json' } }),
    { 'nonal 423': (r) => r.status === 423 }
  );
  // 7. idempotent replay -> 200 no new row
  check(
    http.post(`${API}/affinity/gift-spend`,
      JSON.stringify({ gift_id: 'gift_test_001', hero_id: 'greek_zeus', quantity: 1, idempotency_key: 'canary_idem_0001', user_id: 'user_canary_001' }),
      { headers: { 'Content-Type': 'application/json' } }),
    { 'replay 200': (r) => r.status === 200 }
  );
  sleep(0.05);
}
