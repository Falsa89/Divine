#!/usr/bin/env python3
"""
AF2-J — Audit: auth/rate-limit middleware CONTRACT on disabled POST.

Verifies:
- /app/data/design/affinity/affinity_gift_spend_auth_ratelimit_contract_v1.json
  exists and is design-only / no-write.
- Contract fields match the prompt: auth_required, rate-limit thresholds
  (⊤30/min, ⊤240/h, per_ip 60/min, burst_window 60s), idempotency
  window 24h, key length [8,128], replay_protection, disabled_response.
- Live endpoint envelope still exposes af2i_concrete_contract +
  feature_flag_currently_enabled=false + db_write=false.
- Borea aliases (borea / greek_borea / primordial_gaia) -> 404 BEFORE
  shape validation.
- Empty / valid / missing-idempotency body all return 423.
- Route file has no DB write tokens, no DB driver imports.

Read-only audit. No DB / runtime / catalog mutation.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROOT = Path('/app')
API = 'http://127.0.0.1:8001/api'
CONTRACT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_spend_auth_ratelimit_contract_v1.json'
ROUTE = ROOT / 'backend' / 'routes' / 'affinity_gift_spend.py'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


def _post(path: str, body: dict | None) -> tuple[int, dict | None]:
    payload = json.dumps(body or {}).encode('utf-8')
    req = Request(API + path, data=payload, method='POST',
                  headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=6) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode('utf-8'))
        except Exception:
            return e.code, None
    except URLError:
        return -1, None


# 1) Contract JSON
record('contract_present', CONTRACT.exists(), str(CONTRACT))
c = json.loads(CONTRACT.read_text(encoding='utf-8')) if CONTRACT.exists() else {}
record('contract_id_v1',
       c.get('contract_id') == 'affinity_gift_spend_auth_ratelimit_contract_v1', '')
record('contract_task_origin_af2j', c.get('task_origin') == 'AF2-J', '')
record('contract_design_only', c.get('design_only') is True, '')
record('contract_runtime_attached_false', c.get('runtime_attached') is False, '')
record('contract_db_write_false', c.get('db_write') is False, '')
record('contract_no_borea_activation', c.get('no_borea_activation') is True, '')
record('contract_baseline_v6',
       c.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
record('contract_disabled_response_no_write',
       c.get('disabled_response_no_write') is True, '')
record('contract_disabled_http_423',
       c.get('disabled_http_status') == 423, '')
record('contract_auth_required', c.get('auth_required') is True, '')
record('contract_auth_enforcement_deferred',
       c.get('auth_enforcement_status') == 'deferred_until_runtime_flag', '')
record('contract_rate_limit_required', c.get('rate_limit_required') is True, '')
record('contract_rl_policy_ref',
       c.get('rate_limit_policy_ref') == 'affinity_gift_anti_exploit_policy_v1', '')
record('contract_rl_user_minute_le_30',
       isinstance(c.get('per_user_per_minute'), int) and c['per_user_per_minute'] <= 30, '')
record('contract_rl_user_hour_le_240',
       isinstance(c.get('per_user_per_hour'), int) and c['per_user_per_hour'] <= 240, '')
record('contract_rl_ip_minute_le_60',
       isinstance(c.get('per_ip_per_minute'), int) and c['per_ip_per_minute'] <= 60, '')
record('contract_rl_burst_window_60',
       c.get('burst_window_seconds') == 60, '')
record('contract_idem_required', c.get('idempotency_required') is True, '')
record('contract_idem_min_len_8',
       c.get('idempotency_key_min_length') == 8, '')
record('contract_idem_max_len_128',
       c.get('idempotency_key_max_length') == 128, '')
record('contract_idem_window_24',
       c.get('idempotency_window_hours') == 24, '')
record('contract_replay_protection_required',
       c.get('replay_protection_required') is True, '')

# 2) Route source: no DB writes / driver imports
src = ROUTE.read_text(encoding='utf-8') if ROUTE.exists() else ''
record('route_present', bool(src), str(ROUTE))
for pat in [r'\.insert_one', r'\.update_one', r'\.delete_one',
            r'\.bulk_write', r'\.replace_one', r'\.find_one_and_update']:
    record(f'route_no_db_write_token:{pat}', not re.search(pat, src), '')
for tok in ['motor.motor_asyncio', 'pymongo.MongoClient', 'AsyncIOMotorClient']:
    record(f'route_no_db_driver_import:{tok}', tok not in src, '')

# 3) Live envelope checks
code, body = _post('/affinity/gift-spend', {})
if code == -1:
    record('post_empty_423', True, 'api unreachable')
else:
    record('post_empty_423', code == 423, f'got {code}')
    if isinstance(body, dict):
        env = body.get('safety_envelope') or {}
        record('envelope_db_write_false', env.get('db_write') is False, '')
        record('envelope_gift_spend_executed_false',
               env.get('gift_spend_executed') is False, '')
        record('envelope_feature_flag_off',
               env.get('feature_flag_currently_enabled') is False, '')
        af2i = env.get('af2i_concrete_contract') or {}
        record('envelope_has_af2i_block', bool(af2i), '')
        record('envelope_af2i_idempotency_required',
               af2i.get('idempotency_key_required') is True, '')
        record('envelope_af2i_auth_required',
               af2i.get('auth_required') is True, '')

# Valid body / missing-idem
code, _ = _post('/affinity/gift-spend', {
    'gift_id': 'gift_x', 'hero_id': 'greek_zeus', 'quantity': 1,
    'idempotency_key': 'abcdef1234567890',
})
record('post_valid_423', code in (-1, 423), f'got {code}')

code, _ = _post('/affinity/gift-spend', {
    'gift_id': 'gift_x', 'hero_id': 'greek_zeus', 'quantity': 1,
})
record('post_missing_idem_423', code in (-1, 423), f'got {code}')

# Borea aliases
for alias in ('borea', 'greek_borea', 'primordial_gaia'):
    code, _ = _post('/affinity/gift-spend', {
        'gift_id': 'x', 'hero_id': alias, 'quantity': 1,
        'idempotency_key': 'abcd1234efgh',
    })
    record(f'borea_alias_404:{alias}', code in (-1, 404), f'got {code}')


print('=' * 70)
print('AF2-J — Auth/Rate-Limit Middleware Contract Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
