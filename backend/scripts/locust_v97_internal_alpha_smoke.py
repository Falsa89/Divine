#!/usr/bin/env python3
"""
v97 — Locust smoke test script for internal alpha load profile.

Low-impact: 10 users, 2/sec spawn, 30s duration.

USAGE:
    pip install locust
    locust -f backend/scripts/locust_v97_internal_alpha_smoke.py \
        --host=http://localhost:8001 --users 10 --spawn-rate 2 --run-time 30s --headless

Note: NON eseguito in container automaticamente; questo file definisce il profilo.

Safety:
- No reward/score live mutation
- No production broadcast
- Token rotation rispettata
"""
import os
import random

try:
    from locust import HttpUser, task, between
except ImportError:
    HttpUser = object
    def task(weight):
        def deco(f):
            return f
        return deco
    def between(a, b):
        return None

class InternalAlphaSmokeUser(HttpUser):  # type: ignore
    wait_time = between(1, 3)

    def on_start(self):
        # Guest login per ottenere il token
        r = self.client.post('/api/auth/guest', json={'alias_hint': f'load_{random.randint(1000, 9999)}'})
        if r.status_code == 200:
            data = r.json()
            self.token = data.get('token')
            self.refresh_token = data.get('refresh_token')
        else:
            self.token = None
            self.refresh_token = None

    def _auth_headers(self):
        return {'Authorization': f'Bearer {self.token}'} if self.token else {}

    @task(3)
    def get_me(self):
        self.client.get('/api/auth/me', headers=self._auth_headers())

    @task(2)
    def get_formation(self):
        self.client.get('/api/team/get-formation', headers=self._auth_headers())

    @task(1)
    def provider_status(self):
        self.client.get('/api/auth/provider-status')

    @task(1)
    def encounter_catalog(self):
        self.client.get('/api/encounter-source/catalog')

    @task(1)
    def live_mode_catalog(self):
        self.client.get('/api/live-mode/catalog')

    @task(1)
    def avatar_catalog(self):
        self.client.get('/api/avatar-placeholder/catalog')

    @task(1)
    def refresh_rotation(self):
        if self.refresh_token:
            r = self.client.post('/api/auth/refresh', json={'refresh_token': self.refresh_token})
            if r.status_code == 200:
                d = r.json()
                self.token = d.get('token', self.token)
                self.refresh_token = d.get('refresh_token', self.refresh_token)
