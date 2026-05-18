"""V22 — Stage4 Extended Locust file (low-impact).

More traffic mix than V21:
 - canary-status polling 25%
 - non-allowlist 35%
 - replay 25%
 - rate-limit bursts 10%
 - fresh capped 5%
Fresh spend budget capped at 5 globally.
"""
import time, threading, random
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


class Stage4ExtendedUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(25)
    def canary_status(self):
        with self.client.get('/api/affinity/gift-spend/canary-status', name='canary_status', catch_response=True) as r:
            if r.status_code == 200: r.success()
            else: r.failure(f'expected 200 got {r.status_code}')

    @task(35)
    def non_allowlist_spend(self):
        uid = f'locust_unauth_{int(time.time()*1000)}_{random.randint(0,99)}'
        body = {'gift_id':'x','hero_id':'greek_zeus','quantity':1,
                'idempotency_key': f'locust_unauth_{uid}', 'user_id': uid}
        with self.client.post('/api/affinity/gift-spend', json=body, name='unauth_spend', catch_response=True) as r:
            if r.status_code in (423, 429): r.success()
            else: r.failure(f'expected 423/429 got {r.status_code}')

    @task(25)
    def replay_known(self):
        body = {'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,
                'idempotency_key':'tx_canary_replay_locust_v22','user_id':'stage3_qa_001'}
        with self.client.post('/api/affinity/gift-spend', json=body, name='replay_spend', catch_response=True) as r:
            if r.status_code in (200, 423, 429): r.success()
            else: r.failure(f'expected 200/423/429 got {r.status_code}')

    @task(10)
    def burst_same_user(self):
        uid = 'locust_burst_v22_shared'
        body = {'gift_id':'x','hero_id':'greek_zeus','quantity':1,
                'idempotency_key': f'locust_burst_v22_{int(time.time()*1000)}_{random.randint(0,9999)}',
                'user_id': uid}
        with self.client.post('/api/affinity/gift-spend', json=body, name='burst_same_user', catch_response=True) as r:
            if r.status_code in (423, 429): r.success()
            else: r.failure(f'expected 423/429 got {r.status_code}')

    @task(3)
    def borea_probe(self):
        body = {'gift_id':'x','hero_id':'borea','quantity':1,
                'idempotency_key': f'locust_borea_{time.time()}','user_id':'stage4_qa_001'}
        with self.client.post('/api/affinity/gift-spend', json=body, name='borea_probe', catch_response=True) as r:
            if r.status_code == 404: r.success()
            else: r.failure(f'expected 404 got {r.status_code}')

    @task(5)
    def fresh_stage4_spend_capped(self):
        if not _take_fresh_slot():
            self.canary_status(); return
        uid = f'stage4_qa_{random.randint(1, 500):03d}'
        body = {'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,
                'idempotency_key': f'locust_fresh_v22_{int(time.time()*1000)}_{uid}','user_id':uid}
        with self.client.post('/api/affinity/gift-spend', json=body, name='fresh_spend_capped', catch_response=True) as r:
            if r.status_code in (200, 423, 429): r.success()
            else: r.failure(f'expected 200/423/429 got {r.status_code}')
