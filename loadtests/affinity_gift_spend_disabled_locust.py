"""AF2-L-K6-PREP — Locust disabled-endpoint probe (SAFE / DESIGN-ONLY).

PURPOSE: mirror of the k6 script for teams using locust. Hits the disabled
`/api/affinity/gift-spend` endpoint and asserts HTTP 423 (or 404 for Borea
aliases). Never performs a real gift spend.

Usage:
    locust -f /app/loadtests/affinity_gift_spend_disabled_locust.py \\
        --host http://127.0.0.1:8001 -u 50 -r 10 -t 30s --headless

Safety guarantees:
    - endpoint is hard-disabled; no DB write reachable.
    - failures raise immediately if any 200 is observed.
"""
import random
from locust import HttpUser, task, between, events

DISABLED_PAYLOADS = [
    {},
    {"gift_id": "gift_x", "hero_id": "greek_zeus", "quantity": 1,
     "idempotency_key": "abcdef1234567890"},
    {"gift_id": "gift_x", "hero_id": "greek_zeus", "quantity": 1},
    {"gift_id": "gift_x", "hero_id": "greek_zeus", "quantity": 1,
     "idempotency_key": "duplicate_key_001"},
    {"gift_id": "gift_x", "hero_id": "greek_zeus", "quantity": -1,
     "idempotency_key": "abcdef1234567890"},
]
BOREA_PAYLOADS = [
    {"gift_id": "x", "hero_id": "borea", "quantity": 1, "idempotency_key": "abcd1234efgh"},
    {"gift_id": "x", "hero_id": "greek_borea", "quantity": 1, "idempotency_key": "abcd1234efgh"},
    {"gift_id": "x", "hero_id": "primordial_gaia", "quantity": 1, "idempotency_key": "abcd1234efgh"},
]


class AffinityGiftSpendDisabledUser(HttpUser):
    wait_time = between(0.05, 0.15)

    @task(8)
    def disabled_post(self):
        body = random.choice(DISABLED_PAYLOADS)
        with self.client.post('/api/affinity/gift-spend',
                              json=body, catch_response=True,
                              name='disabled_endpoint') as r:
            if r.status_code == 423:
                r.success()
            else:
                r.failure(f'expected 423 disabled, got {r.status_code}')

    @task(2)
    def borea_alias_post(self):
        body = random.choice(BOREA_PAYLOADS)
        with self.client.post('/api/affinity/gift-spend',
                              json=body, catch_response=True,
                              name='borea_alias') as r:
            if r.status_code == 404:
                r.success()
            else:
                r.failure(f'expected 404 borea alias, got {r.status_code}')


@events.test_stop.add_listener
def _on_test_stop(environment, **kwargs):
    stats = environment.stats
    fail = stats.total.num_failures
    if fail:
        print(f'AF2-L-K6-PREP locust: {fail} failures observed')
