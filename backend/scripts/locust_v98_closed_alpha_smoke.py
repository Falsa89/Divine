#!/usr/bin/env python3
"""
v98 — Locust Closed Alpha Smoke (expanded vs v97).
USAGE: locust -f backend/scripts/locust_v98_closed_alpha_smoke.py --host=http://localhost:8001 --users 20 --spawn-rate 4 --run-time 60s --headless
"""
import random
try:
    from locust import HttpUser, task, between
except ImportError:
    HttpUser=object
    def task(w):
        def deco(f): return f
        return deco
    def between(a,b): return None

class ClosedAlphaSmokeUser(HttpUser):  # type: ignore
    wait_time = between(1,3)
    def on_start(self):
        r = self.client.post('/api/auth/guest',json={'alias_hint':f'load_{random.randint(1000,9999)}'})
        if r.status_code==200:
            d=r.json(); self.token=d.get('token'); self.refresh_token=d.get('refresh_token')
        else:
            self.token=None; self.refresh_token=None
    def _h(self): return {'Authorization':f'Bearer {self.token}'} if self.token else {}
    @task(3)
    def me(self): self.client.get('/api/auth/me',headers=self._h())
    @task(2)
    def formation(self): self.client.get('/api/team/get-formation',headers=self._h())
    @task(1)
    def provider(self): self.client.get('/api/auth/provider-status')
    @task(1)
    def data_export(self): self.client.get('/api/auth/data-export',headers=self._h())
    @task(1)
    def privacy(self): self.client.get('/api/auth/privacy-status',headers=self._h())
    @task(1)
    def admin_actors(self): self.client.get('/api/admin/server-actors/status')
    @task(1)
    def encounter(self): self.client.get('/api/encounter-source/catalog')
    @task(1)
    def live_mode(self): self.client.get('/api/live-mode/catalog')
    @task(1)
    def avatar(self): self.client.get('/api/avatar-placeholder/catalog')
    @task(1)
    def refresh(self):
        if self.refresh_token:
            r=self.client.post('/api/auth/refresh',json={'refresh_token':self.refresh_token})
            if r.status_code==200:
                d=r.json(); self.token=d.get('token',self.token); self.refresh_token=d.get('refresh_token',self.refresh_token)
