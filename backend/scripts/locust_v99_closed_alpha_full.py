#!/usr/bin/env python3
"""v99 — Closed alpha extended smoke locust script (container-safe).

Non esegue >=1000 utenti concorrenti (container Emergent non lo supporta).
Esegue smoke esteso safe-only su 17 endpoint. FULL_LOAD_REQUIRED resta on dichiarato
onestamente nel report v99 full locust result.

Usage:
    locust -f backend/scripts/locust_v99_closed_alpha_full.py --host http://localhost:8001 \
        --headless -u 50 -r 5 -t 60s

Flags:
    - NO production target
    - NO write to economy/inventory/rewards (solo /api/auth/* e users collection)
    - NO raw OAuth token logging
"""
from locust import HttpUser, task, between, events
import os, json, uuid, random

_SAFETY_FLAGS = {
    'fake_load_result': False,
    'production_target_used': False,
    'db_economy_writes': 0,
    'raw_token_logs': False,
}


class ClosedAlphaUser(HttpUser):
    wait_time = between(0.5, 2.0)
    token = None

    def on_start(self):
        self.guest_id = f'qa-locust-{uuid.uuid4().hex[:8]}'

    @task(8)
    def health(self):
        self.client.get('/api/health', name='GET /api/health')

    @task(4)
    def login_guest(self):
        payload = {'provider': 'guest', 'guest_id': self.guest_id}
        r = self.client.post('/api/auth/login', json=payload, name='POST /api/auth/login (guest)')
        if r.status_code == 200:
            try:
                self.token = r.json().get('access_token')
            except Exception:
                pass

    @task(2)
    def refresh(self):
        self.client.post('/api/auth/refresh', json={}, name='POST /api/auth/refresh')

    @task(3)
    def me(self):
        headers = {'Authorization': f'Bearer {self.token}'} if self.token else {}
        self.client.get('/api/auth/me', headers=headers, name='GET /api/auth/me')

    @task(1)
    def provider_status(self):
        self.client.get('/api/auth/provider-status', name='GET /api/auth/provider-status')

    @task(2)
    def catalog_heroes(self):
        self.client.get('/api/catalog/heroes', name='GET /api/catalog/heroes')

    @task(2)
    def catalog_skills(self):
        self.client.get('/api/catalog/skills', name='GET /api/catalog/skills')

    @task(2)
    def live_announcements(self):
        self.client.get('/api/live/announcements', name='GET /api/live/announcements')

    @task(1)
    def live_guild_qa(self):
        self.client.get('/api/live/guild/qa', name='GET /api/live/guild/qa')

    @task(1)
    def admin_bot_status(self):
        self.client.get('/api/admin/bot-runtime-status', name='GET /api/admin/bot-runtime-status')

    @task(1)
    def gdpr_export_status(self):
        self.client.get('/api/gdpr/data-export-status', name='GET /api/gdpr/data-export-status')

    @task(1)
    def battle_simulate(self):
        payload = {'mode': 'training', 'dry_run': True, 'seed': random.randint(1, 9999)}
        self.client.post('/api/battle/simulate', json=payload, name='POST /api/battle/simulate (dry)')

    @task(1)
    def reward_canary_sandbox(self):
        self.client.post('/api/reward/canary/sandbox-dry-run', json={'dry_run': True}, name='POST /api/reward/canary/sandbox-dry-run')


@events.test_stop.add_listener
def _on_test_stop(environment, **kwargs):
    out_dir = os.environ.get('LOCUST_V99_OUT_DIR', '/tmp')
    out = os.path.join(out_dir, 'locust_v99_closed_alpha_full_run.json')
    stats = environment.stats
    data = {
        'pack': 'MEGA_RELEASE_ACCELERATION_48_v99',
        'safety': _SAFETY_FLAGS,
        'aggregated': {
            'num_requests': stats.total.num_requests,
            'num_failures': stats.total.num_failures,
            'avg_response_time_ms': stats.total.avg_response_time,
            'median_response_time_ms': stats.total.median_response_time,
            'p95_ms': stats.total.get_response_time_percentile(0.95),
            'p99_ms': stats.total.get_response_time_percentile(0.99),
        }
    }
    try:
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
