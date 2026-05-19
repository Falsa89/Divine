"""V23 — Stage4 Locust with rate-limit emphasis (Redis-backed).

Mix: status / replay / non-allowlist / heavy burst from rotating users
     / Borea / capped fresh.
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
            _FRESH_USED += 1; return True
    return False


class Stage4RateLimitUser(HttpUser):
    wait_time = between(0.3, 1.2)

    @task(20)
    def canary_status(self):
        with self.client.get('/api/affinity/gift-spend/canary-status', name='canary_status', catch_response=True) as r:
            if r.status_code == 200: r.success()
            else: r.failure(f'{r.status_code}')

    @task(30)
    def non_allowlist(self):
        uid = f'locust_unauth_v23_{int(time.time()*1000)}_{random.randint(0,99)}'
        body = {'gift_id':'x','hero_id':'greek_zeus','quantity':1,
                'idempotency_key':f'locust_unauth_v23_{uid}','user_id':uid}
        with self.client.post('/api/affinity/gift-spend', json=body, name='unauth_spend', catch_response=True) as r:
            if r.status_code in (423, 429): r.success()
            else: r.failure(f'{r.status_code}')

    @task(25)
    def burst_rotating(self):
        # 10 different burst pools to exercise Redis ZSET
        pool = random.randint(0, 9)
        uid = f'locust_burstv23_pool_{pool}'
        body = {'gift_id':'x','hero_id':'greek_zeus','quantity':1,
                'idempotency_key': f'locust_burstv23_{int(time.time()*1000)}_{random.randint(0,9999)}',
                'user_id': uid}
        with self.client.post('/api/affinity/gift-spend', json=body, name='burst_rotating', catch_response=True) as r:
            if r.status_code in (423, 429): r.success()
            else: r.failure(f'{r.status_code}')

    @task(15)
    def replay_known(self):
        body = {'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,
                'idempotency_key':'tx_canary_replay_locust_v23','user_id':'stage3_qa_001'}
        with self.client.post('/api/affinity/gift-spend', json=body, name='replay_spend', catch_response=True) as r:
            if r.status_code in (200, 423, 429): r.success()
            else: r.failure(f'{r.status_code}')

    @task(3)
    def borea_probe(self):
        body = {'gift_id':'x','hero_id':'borea','quantity':1,
                'idempotency_key': f'locust_borea_v23_{time.time()}','user_id':'stage4_qa_001'}
        with self.client.post('/api/affinity/gift-spend', json=body, name='borea_probe', catch_response=True) as r:
            if r.status_code == 404: r.success()
            else: r.failure(f'{r.status_code}')

    @task(5)
    def fresh_capped(self):
        if not _take_fresh_slot(): self.canary_status(); return
        uid = f'stage4_qa_{random.randint(1, 500):03d}'
        body = {'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,
                'idempotency_key': f'locust_fresh_v23_{int(time.time()*1000)}_{uid}','user_id':uid}
        with self.client.post('/api/affinity/gift-spend', json=body, name='fresh_spend_capped', catch_response=True) as r:
            if r.status_code in (200, 423, 429): r.success()
            else: r.failure(f'{r.status_code}')
