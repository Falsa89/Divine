#!/usr/bin/env python3
"""
AF2-G — POST /api/affinity/gift-spend skeleton safety audit.

Verifies:
  - route file exists and has a @router.post decorator on /affinity/gift-spend
  - no DB write tokens (insert_/update_/delete_/bulk_/replace_)
  - no motor / pymongo / db / database imports in the new route file
  - flag default OFF; common truthy variants (true/1/yes/on/TRUE) do NOT enable
  - POST with empty body returns 423 + canonical disabled envelope
  - POST with valid-looking payload returns 423 + db_write=false envelope
  - POST with hero_id in {'borea','primordial_gaia','greek_borea'} returns 404 BEFORE the disabled envelope
  - GET /api/affinity/gift-spend rejected (405)
  - GET /api/affinity/gifts still 200 (no regression)
  - no UI gift-spend button in frontend/app
"""
from __future__ import annotations
import json
import os
import re
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROOT = Path('/app')
ROUTE_FILE = ROOT / 'backend' / 'routes' / 'affinity_gift_spend.py'
GAME_SYSTEMS = ROOT / 'backend' / 'game_systems.py'
FRONTEND_APP = ROOT / 'frontend' / 'app'

API_BASE = 'http://127.0.0.1:8001'

WRITE_TOKENS = [
    r'\.insert_one\s*\(', r'\.insert_many\s*\(',
    r'\.update_one\s*\(', r'\.update_many\s*\(',
    r'\.delete_one\s*\(', r'\.delete_many\s*\(',
    r'\.bulk_write\s*\(', r'\.replace_one\s*\(',
    r'\.find_one_and_update\s*\(', r'\.find_one_and_delete\s*\(',
]
DB_IMPORTS = [
    r'^\s*(import|from)\s+motor',
    r'^\s*(import|from)\s+pymongo',
    r'^\s*from\s+server\s+import\s+db',
    r'^\s*from\s+database\s+import',
]

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


# 1. Route file present + structure
record('route_file_present', ROUTE_FILE.exists(), str(ROUTE_FILE))
src = ROUTE_FILE.read_text(encoding='utf-8') if ROUTE_FILE.exists() else ''
record('route_has_post_decorator',
       bool(re.search(r'@router\.post\s*\(\s*["\']\/affinity\/gift-spend', src)),
       'expected @router.post("/affinity/gift-spend")')

# 2. No write tokens
write_hits = [p for p in WRITE_TOKENS if re.search(p, src)]
record('route_no_db_write_tokens', not write_hits, f'hits={write_hits}')

# 3. No DB-ish imports
db_imp_hits = [p for p in DB_IMPORTS if re.search(p, src, re.MULTILINE)]
record('route_no_db_imports', not db_imp_hits, f'hits={db_imp_hits}')

# 4. Flag handling: default OFF, only allowlisted truthy
sys.path.insert(0, str(ROOT / 'backend'))
try:
    from routes import affinity_gift_spend as mod  # type: ignore
    os.environ.pop('AFFINITY_GIFT_RUNTIME_ENABLED', None)
    record('flag_default_off', mod.is_affinity_gift_runtime_enabled() is False, '')
    for t in ['true', '1', 'yes', 'on', 'TRUE', 'True', 'enabled']:
        os.environ['AFFINITY_GIFT_RUNTIME_ENABLED'] = t
        record(f'flag_truthy_rejected:{t}',
               mod.is_affinity_gift_runtime_enabled() is False,
               f'token "{t}" must not enable')
    os.environ.pop('AFFINITY_GIFT_RUNTIME_ENABLED', None)
except Exception as e:
    record('module_import', False, f'{e!r}')

# 5. Registered in game_systems.py
gs_src = GAME_SYSTEMS.read_text(encoding='utf-8') if GAME_SYSTEMS.exists() else ''
record('registered_in_game_systems',
       'register_affinity_gift_spend_skeleton_routes(router)' in gs_src, '')

# 6. Live API smoke
def _post(path: str, body: dict | None) -> tuple[int, dict | None]:
    payload = json.dumps(body).encode('utf-8') if body is not None else b''
    req = Request(
        API_BASE + path,
        data=payload,
        method='POST',
        headers={'Content-Type': 'application/json'},
    )
    try:
        with urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        try:
            body = e.read().decode('utf-8') if hasattr(e, 'read') else ''
            return e.code, (json.loads(body) if body else None)
        except Exception:
            return e.code, None
    except URLError:
        return -1, None


def _req(path: str, method: str) -> int:
    try:
        req = Request(API_BASE + path, method=method)
        with urlopen(req, timeout=5) as resp:
            return resp.status
    except HTTPError as e:
        return e.code
    except URLError:
        return -1


# Empty body -> 423
code, body = _post('/api/affinity/gift-spend', {})
record('empty_body_status_423', code == 423, f'got {code}')
if isinstance(body, dict):
    env = body.get('safety_envelope') or {}
    for k in ['enabled', 'runtime_attached', 'db_write', 'inventory_write',
              'affinity_points_write', 'stat_buffs_enabled',
              'gift_spend_executed', 'feature_flag_currently_enabled']:
        record(f'empty_envelope_{k}_false', env.get(k) is False, f'got {env.get(k)!r}')
    record('empty_envelope_idempotency_required',
           env.get('idempotency_required') is True, '')
    record('empty_envelope_no_borea_activation',
           env.get('no_borea_activation') is True, '')

# Valid payload -> 423 + db_write false
code, body = _post('/api/affinity/gift-spend', {
    'gift_id': 'gift.greek.water', 'hero_id': 'greek_athena',
    'quantity': 1, 'idempotency_key': 'abcd1234efgh',
})
record('valid_payload_status_423', code == 423, f'got {code}')
if isinstance(body, dict):
    env = body.get('safety_envelope') or {}
    record('valid_envelope_db_write_false', env.get('db_write') is False, '')
    record('valid_envelope_gift_spend_executed_false',
           env.get('gift_spend_executed') is False, '')
    record('valid_shape_ok_preview',
           (body.get('shape_validation_preview') or {}).get('shape_ok') is True, '')

# Borea aliases -> 404 BEFORE envelope
for alias in ['borea', 'primordial_gaia', 'greek_borea']:
    code, body = _post('/api/affinity/gift-spend', {
        'gift_id': 'gift.x', 'hero_id': alias,
        'quantity': 1, 'idempotency_key': 'abcd1234efgh',
    })
    record(f'borea_alias_404:{alias}', code == 404, f'got {code}')

# Method GET on /gift-spend rejected
code = _req('/api/affinity/gift-spend', 'GET')
record('get_on_gift_spend_rejected', code in (404, 405), f'got {code}')

# Method PUT/PATCH/DELETE rejected
for m in ['PUT', 'PATCH', 'DELETE']:
    code = _req('/api/affinity/gift-spend', m)
    record(f'method_{m}_rejected', code in (404, 405, 422),
           f'got {code}')

# 7. GET /api/affinity/gifts still 200 (no regression from AF2-E)
try:
    with urlopen(API_BASE + '/api/affinity/gifts', timeout=5) as resp:
        record('regression_gifts_get_200', resp.status == 200, f'got {resp.status}')
except Exception as e:
    record('regression_gifts_get_200', False, f'{e!r}')

# 8. No UI gift-spend button
ui_hits = []
if FRONTEND_APP.exists():
    for tsx in FRONTEND_APP.rglob('*.tsx'):
        if not tsx.is_file():
            continue
        t = tsx.read_text(encoding='utf-8', errors='ignore')
        for pat in [r'gift[_-]?spend[_-]?button',
                    r'spend[_-]?gift[_-]?button',
                    r'claim[_-]?gift[_-]?button']:
            if re.search(pat, t, re.IGNORECASE):
                ui_hits.append(f'{tsx}:{pat}')
record('no_ui_gift_spend_button', not ui_hits, f'hits={ui_hits}')


print('=' * 70)
print('AF2-G — Affinity Gift-Spend POST Skeleton Safety Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
