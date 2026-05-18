"""V21 — Stage4 Locust file (low-impact).

Mix: mostly replays/non-allowlist/status (90%), tiny fraction fresh spends (10%).
Caps total fresh spends via shared counter.
"""
import os, time, threading
from locust import HttpUser, task, between

_LOCK = threading.Lock()
_FRESH_BUDGET = 5
_FRESH_USED = 0


def _take_fresh_slot():
    global _FRESH_USED
    with _LOCK:
        if _FRESH_USED < _FRESH_BUDGET:
            _FRESH_USED += 1
            return True
    return False


class Stage4LowImpactUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(20)
    def canary_status(self):
        with self.client.get('/api/affinity/gift-spend/canary-status', name='canary_status', catch_response=True) as r:
            if r.status_code != 200:
                r.failure(f'expected 200 got {r.status_code}')
            else:
                r.success()

    @task(40)
    def non_allowlist_spend(self):
        uid = f'locust_unauth_{int(time.time()*1000)}'
        body = {'gift_id': 'x', 'hero_id': 'greek_zeus', 'quantity': 1,
                'idempotency_key': f'locust_unauth_{uid}', 'user_id': uid}
        with self.client.post('/api/affinity/gift-spend', json=body, name='unauth_spend', catch_response=True) as r:
            if r.status_code in (423, 429):
                r.success()
            else:
                r.failure(f'expected 423/429 got {r.status_code}')

    @task(30)
    def replay_known(self):
        body = {'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                'idempotency_key': 'tx_canary_replay_locust_known', 'user_id': 'stage3_qa_001'}
        with self.client.post('/api/affinity/gift-spend', json=body, name='replay_spend', catch_response=True) as r:
            if r.status_code in (200, 423, 429):
                r.success()
            else:
                r.failure(f'expected 200/423/429 got {r.status_code}')

    @task(2)
    def borea_probe(self):
        body = {'gift_id': 'x', 'hero_id': 'borea', 'quantity': 1,
                'idempotency_key': f'locust_borea_{time.time()}', 'user_id': 'stage3_qa_001'}
        with self.client.post('/api/affinity/gift-spend', json=body, name='borea_probe', catch_response=True) as r:
            if r.status_code == 404:
                r.success()
            else:
                r.failure(f'expected 404 got {r.status_code}')

    @task(8)
    def fresh_stage4_spend_capped(self):
        if not _take_fresh_slot():
            self.canary_status(); return
        import random
        uid = f'stage4_qa_{random.randint(1, 500):03d}'
        body = {'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                'idempotency_key': f'locust_fresh_{int(time.time()*1000)}_{uid}',
                'user_id': uid}
        with self.client.post('/api/affinity/gift-spend', json=body, name='fresh_spend_capped', catch_response=True) as r:
            if r.status_code in (200, 423, 429):
                r.success()
            else:
                r.failure(f'expected 200/423/429 got {r.status_code}')
