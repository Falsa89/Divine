"""AF2-N Stage3 Locust low-impact load test — V19.

Safe scenario: mostly read-only + non-allowlist 423 + Borea 404 rejects.
NO fresh spend tasks. NO uncontrolled ledger growth.
Run via: run_af2n_stage3_locust_low_impact.py (orchestrator).
"""
import uuid, random
from locust import HttpUser, task, between, events


class StageLowImpactUser(HttpUser):
    wait_time = between(0.05, 0.2)

    @task(40)
    def health(self):
        self.client.get('/api/health', name='/api/health')

    @task(15)
    def canary_status(self):
        self.client.get('/api/affinity/gift-spend/canary-status', name='/api/affinity/gift-spend/canary-status')

    @task(10)
    def heroes(self):
        self.client.get('/api/heroes', name='/api/heroes')

    @task(10)
    def affinity_gifts_catalog(self):
        self.client.get('/api/affinity/gifts', name='/api/affinity/gifts')

    @task(15)
    def non_allowlist_post(self):
        body = {
            'gift_id': 'gift_test_001',
            'hero_id': 'greek_zeus',
            'quantity': 1,
            'idempotency_key': 'v19lc' + uuid.uuid4().hex[:10],
            'user_id': 'unauth_v19lc_' + str(random.randint(0, 9999)),
        }
        with self.client.post('/api/affinity/gift-spend', json=body,
                              name='POST gift-spend [non-allowlist expect 423]',
                              catch_response=True) as r:
            if r.status_code == 423: r.success()
            else: r.failure(f'expected 423 got {r.status_code}')

    @task(8)
    def borea_post(self):
        body = {
            'gift_id': 'gift_test_001',
            'hero_id': random.choice(['borea','greek_borea','primordial_gaia']),
            'quantity': 1,
            'idempotency_key': 'v19lcB' + uuid.uuid4().hex[:10],
            'user_id': 'stage3_qa_001',
        }
        with self.client.post('/api/affinity/gift-spend', json=body,
                              name='POST gift-spend [Borea expect 404]',
                              catch_response=True) as r:
            if r.status_code == 404: r.success()
            else: r.failure(f'expected 404 got {r.status_code}')

    @task(2)
    def idempotent_replay_known_key(self):
        # Replay a known historical key for stage1_qa_001 (v16live001ai),
        # which is idempotent and produces no state change.
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
                except Exception: r.failure('200 but non-JSON body')
            else:
                r.failure(f'expected 200 got {r.status_code}')
