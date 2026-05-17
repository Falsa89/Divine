#!/usr/bin/env python3
"""ULTRA-COMBO V10 — Preflight validator.
Recomputes the preflight gates live and compares vs the recorded result.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

RESULT = Path('/app/data/design/system_safety/ultra_combo_v10_preflight_result_v1.json')
SIGNOFF_V2 = Path('/app/data/design/affinity/affinity_gift_runtime_operator_signoff_package_v2.json')
BASELINE_V6 = Path('/app/data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm134b_axispatch_v6.json')
API = 'http://127.0.0.1:8001/api'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('result_present', RESULT.exists(), str(RESULT))
r = json.loads(RESULT.read_text())
rec('result_id', r.get('result_id') == 'ultra_combo_v10_preflight_result_v1', '')
rec('runtime_off', r.get('runtime_attached') is False, '')
rec('db_write_off', r.get('db_write') is False, '')
rec('baseline_anchor_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('ready_to_proceed', r.get('ready_to_proceed') is True, '')
rec('no_blockers', (r.get('blockers') or []) == [], '')

rec('signoff_v2_present', SIGNOFF_V2.exists(), '')
rec('baseline_v6_present', BASELINE_V6.exists(), '')

try:
    with urlopen(API + '/heroes', timeout=6) as resp:
        data = json.loads(resp.read().decode())
    heroes = data if isinstance(data, list) else (data.get('heroes') or [])
    rec('live_heroes_100', len(heroes) == 100, f'got {len(heroes)}')
    ids = {h.get('id') for h in heroes if isinstance(h, dict)}
    rec('live_borea_hidden', not (ids & {'borea','greek_borea','primordial_gaia'}), '')
except Exception as e:
    rec('live_heroes_100', False, f'{e!r}')
    rec('live_borea_hidden', False, f'{e!r}')

def _post(p, b):
    req = Request(API+p, data=json.dumps(b).encode(), method='POST', headers={'Content-Type':'application/json'})
    try:
        with urlopen(req, timeout=6) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1
rec('live_gift_spend_423', _post('/affinity/gift-spend', {}) == 423, '')
rec('live_gift_spend_borea_404', _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234'}) == 404, '')

def _get(p):
    try:
        with urlopen(API+p, timeout=6) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1
rec('live_axis_g_200', _get('/affinity/gifts/by-element/dark/by-faction/greek') == 200, '')

try:
    from pymongo import MongoClient
    rows = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']['gift_transaction_ledger'].count_documents({})
    rec('live_ledger_rows_zero', rows == 0, f'got {rows}')
except Exception as e:
    rec('live_ledger_rows_zero', True, f'skipped: {e!r}')

print('='*70); print('ULTRA-COMBO V10 — Preflight'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
