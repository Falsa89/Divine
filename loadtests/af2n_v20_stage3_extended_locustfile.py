"""AF2-N V20 Locust EXTENDED low-impact load test.

Larger scenario than V19 but still read-only / replay / reject ONLY.
No fresh spend tasks. Designed for 10-20 users / 30-60s.
"""
import uuid, random
from locust import HttpUser, task, between


class LowImpactExtendedUser(HttpUser):
    wait_time = between(0.05, 0.25)

    @task(45)
    def health(self):
        self.client.get('/api/health', name='/api/health')

    @task(18)
    def canary_status(self):
        self.client.get('/api/affinity/gift-spend/canary-status', name='/api/affinity/gift-spend/canary-status')

    @task(12)
    def heroes(self):
        self.client.get('/api/heroes', name='/api/heroes')

    @task(10)
    def affinity_gifts_catalog(self):
        self.client.get('/api/affinity/gifts', name='/api/affinity/gifts')

    @task(18)
    def non_allowlist(self):
        body = {
            'gift_id': 'gift_test_001',
            'hero_id': random.choice(['greek_zeus','greek_hera','greek_apollo','greek_athena']),
            'quantity': 1,
            'idempotency_key': 'v20lc' + uuid.uuid4().hex[:10],
            'user_id': 'unauth_v20lc_' + str(random.randint(0, 9999)),
        }
        with self.client.post('/api/affinity/gift-spend', json=body,
                              name='POST gift-spend [non-allow expect 423]',
                              catch_response=True) as r:
            if r.status_code == 423: r.success()
            else: r.failure(f'expected 423 got {r.status_code}')

    @task(10)
    def borea_aliases(self):
        body = {
            'gift_id': 'gift_test_001',
            'hero_id': random.choice(['borea','greek_borea','primordial_gaia']),
            'quantity': 1,
            'idempotency_key': 'v20lcB' + uuid.uuid4().hex[:10],
            'user_id': 'stage3_qa_002',
        }
        with self.client.post('/api/affinity/gift-spend', json=body,
                              name='POST gift-spend [Borea expect 404]',
                              catch_response=True) as r:
            if r.status_code == 404: r.success()
            else: r.failure(f'expected 404 got {r.status_code}')

    @task(3)
    def idempotent_replay_known(self):
        body = {
            'gift_id': 'gift_test_001',
            'hero_id': 'greek_zeus',
            'quantity': 2,
            'idempotency_key': 'v16live001ai',
            'user_id': 'stage1_qa_001',
        }
        with self.client.post('/api/affinity/gift-spend', json=body,
                              name='POST gift-spend [idempotent replay expect 200]',
                              catch_response=True) as r:
            if r.status_code == 200:
                try:
                    if r.json().get('result') == 'idempotent_replay': r.success()
                    else: r.failure('200 but not idempotent_replay')
                except Exception: r.failure('200 but non-JSON')
            else: r.failure(f'expected 200 got {r.status_code}')
