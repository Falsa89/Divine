#!/usr/bin/env python3
"""v95 — Validator: Read-Only Catalog Endpoints Runtime.

Verifica che backend/routes/v95_readonly_catalog.py esista, sia registrato in
backend/server.py, e che gli endpoint /api/encounter-source/catalog,
/api/encounter-source/get, /api/live-mode/catalog, /api/avatar-placeholder/catalog
rispondano 200 con campo v95_readonly=True e db_writes=0.
"""
import os, sys, json
import urllib.request, urllib.error
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
failures = []

router_path = os.path.join(ROOT, 'backend', 'routes', 'v95_readonly_catalog.py')
if not os.path.isfile(router_path):
    failures.append('router file missing: backend/routes/v95_readonly_catalog.py')

server_path = os.path.join(ROOT, 'backend', 'server.py')
with open(server_path, 'r', encoding='utf-8') as f:
    src = f.read()
if 'v95_readonly_catalog' not in src or 'include_router(v95_readonly_catalog_router)' not in src:
    failures.append('server.py does not include v95_readonly_catalog router')

BASE = os.environ.get('V95_BASE_URL', 'http://localhost:8001')
endpoints = [
    '/api/encounter-source/catalog',
    '/api/encounter-source/get?mode=story',
    '/api/live-mode/catalog',
    '/api/avatar-placeholder/catalog',
]
for ep in endpoints:
    try:
        with urllib.request.urlopen(BASE + ep, timeout=5) as r:
            if r.status != 200:
                failures.append(f'{ep} status={r.status}')
                continue
            d = json.loads(r.read().decode('utf-8'))
            if d.get('v95_readonly') is not True or d.get('db_writes') != 0:
                failures.append(f'{ep} missing v95_readonly/db_writes flags')
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
        failures.append(f'{ep} error: {e}')

if failures:
    print('FAIL — v95 readonly catalog endpoints:')
    for x in failures:
        print(' -', x)
    sys.exit(1)
print('PASS — v95 readonly catalog endpoints runtime active')
sys.exit(0)
