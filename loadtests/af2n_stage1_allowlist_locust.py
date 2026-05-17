"""AF2-N-STAGE1-K6-LIVE — Locust fallback (NOT executed today, locust binary not installed)."""
from locust import HttpUser, task, between


class AF2NStage1User(HttpUser):
    wait_time = between(0.05, 0.1)
    host = 'http://127.0.0.1:8001'

    @task(2)
    def health(self):
        with self.client.get('/api/health', catch_response=True) as r:
            if r.status_code != 200: r.failure(f'health={r.status_code}')

    @task(2)
    def heroes(self):
        with self.client.get('/api/heroes', catch_response=True) as r:
            if r.status_code != 200: r.failure(f'heroes={r.status_code}')

    @task(2)
    def canary_status(self):
        with self.client.get('/api/affinity/gift-spend/canary-status', catch_response=True) as r:
            if r.status_code != 200: r.failure(f'status={r.status_code}')

    @task(3)
    def spend_empty(self):
        with self.client.post('/api/affinity/gift-spend', json={}, catch_response=True) as r:
            if r.status_code != 423: r.failure(f'empty={r.status_code}')

    @task(3)
    def spend_borea(self):
        with self.client.post('/api/affinity/gift-spend', json={
            'gift_id': 'x', 'hero_id': 'borea', 'quantity': 1,
            'idempotency_key': 'abcd1234efgh', 'user_id': 'user_canary_001'
        }, catch_response=True) as r:
            if r.status_code != 404: r.failure(f'borea={r.status_code}')

    @task(3)
    def spend_nonal(self):
        with self.client.post('/api/affinity/gift-spend', json={
            'gift_id': 'x', 'hero_id': 'greek_zeus', 'quantity': 1,
            'idempotency_key': 'rndrndlocust',  # locust may rotate via user_id
            'user_id': 'unauth_user_xxx',
        }, catch_response=True) as r:
            if r.status_code != 423: r.failure(f'nonal={r.status_code}')

    @task(3)
    def spend_replay(self):
        with self.client.post('/api/affinity/gift-spend', json={
            'gift_id': 'gift_test_001', 'hero_id': 'greek_zeus', 'quantity': 1,
            'idempotency_key': 'canary_idem_0001', 'user_id': 'user_canary_001'
        }, catch_response=True) as r:
            if r.status_code != 200: r.failure(f'replay={r.status_code}')
