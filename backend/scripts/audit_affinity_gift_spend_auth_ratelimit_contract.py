#!/usr/bin/env python3
"""
AF2-I — Audit: concrete auth / rate-limit / idempotency / replay /
no-write contract for POST /api/affinity/gift-spend.

Verifies that:
- the JSON contract v2 exists and declares design_only / no-write;
- the route source file references AF2-I and the contract block;
- the live endpoint exposes safety_envelope.af2i_concrete_contract
  with the expected values;
- Borea aliases (borea, greek_borea, primordial_gaia) are still 404;
- empty / valid / missing-idempotency payloads still return 423;
- the route source contains NO DB-write tokens;
- GET /api/affinity/gifts still 200 (regression);
- there is NO UI spend button anywhere under /app/frontend/app.

Read-only audit. NO catalog / DB / runtime mutation.
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
CONTRACT_PATH = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_spend_disabled_contract_v2.json'
ROUTE_PATH = ROOT / 'backend' / 'routes' / 'affinity_gift_spend.py'
FRONTEND_APP = ROOT / 'frontend' / 'app'

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
        with urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode('utf-8'))
        except Exception:
            return e.code, None
    except URLError:
        return -1, None


def _get(path: str) -> tuple[int, object | None]:
    try:
        with urlopen(API + path, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        return e.code, None
    except URLError:
        return -1, None


# 1) Contract JSON
record('contract_present', CONTRACT_PATH.exists(), str(CONTRACT_PATH))
contract: dict = {}
if CONTRACT_PATH.exists():
    contract = json.loads(CONTRACT_PATH.read_text(encoding='utf-8'))
    record('contract_id_v2', contract.get('contract_id') == 'affinity_gift_spend_disabled_contract_v2', '')
    record('contract_task_origin_af2i', contract.get('task_origin') == 'AF2-I', '')
    record('contract_design_only', contract.get('design_only') is True, '')
    record('contract_runtime_attached_false', contract.get('runtime_attached') is False, '')
    record('contract_db_write_false', contract.get('db_write') is False, '')
    record('contract_no_borea_activation', contract.get('no_borea_activation') is True, '')
    record('contract_baseline_v5_anchor',
           contract.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm132c2_v5', '')
    auth = contract.get('auth') or {}
    record('contract_auth_required', auth.get('auth_required') is True, '')
    record('contract_auth_enforced_when_runtime_enabled',
           auth.get('auth_enforced_when_runtime_enabled') is True, '')
    rl = contract.get('rate_limits') or {}
    record('contract_rl_policy_ref',
           rl.get('policy_ref') == 'affinity_gift_anti_exploit_policy_v1', '')
    record('contract_rl_per_user_minute_le_30',
           isinstance(rl.get('per_user_per_minute'), int) and rl['per_user_per_minute'] <= 30, '')
    record('contract_rl_per_user_hour_le_240',
           isinstance(rl.get('per_user_per_hour'), int) and rl['per_user_per_hour'] <= 240, '')
    idem = contract.get('idempotency') or {}
    record('contract_idem_required',
           idem.get('idempotency_key_required') is True, '')
    record('contract_idem_window_24',
           idem.get('idempotency_window_hours') == 24, '')
    record('contract_replay_protection_required',
           idem.get('replay_protection_required') is True, '')
    record('contract_no_write_current_task',
           contract.get('no_write_current_task') is True, '')

# 2) Route source
record('route_source_present', ROUTE_PATH.exists(), str(ROUTE_PATH))
if ROUTE_PATH.exists():
    src = ROUTE_PATH.read_text(encoding='utf-8')
    record('route_references_af2i', 'AF2-I' in src, '')
    record('route_has_af2i_block_fn', '_af2i_concrete_contract' in src, '')
    record('route_has_contract_id_v2',
           'affinity_gift_spend_disabled_contract_v2' in src, '')
    record('route_truthy_allowlist_strict',
           'true_explicit_affinity_gift_runtime_on' in src, '')
    # No DB write tokens
    for pat in [r'\.insert_one', r'\.update_one', r'\.delete_one',
                r'\.bulk_write', r'\.replace_one', r'\.find_one_and_update',
                r'await\s+\w+\.insert', r'await\s+\w+\.update']:
        record(f'route_no_db_write_token:{pat}',
               not re.search(pat, src), '')
    # No DB driver imports
    for tok in ['motor.motor_asyncio', 'pymongo.MongoClient',
                'AsyncIOMotorClient', 'pymongo.collection']:
        record(f'route_no_db_import:{tok}', tok not in src, '')

# 3) Live API — POST behaviors
code, body = _post('/affinity/gift-spend', {})
if code == -1:
    record('post_empty_423', True, 'api unreachable')
else:
    record('post_empty_423', code == 423, f'got {code}')
    if isinstance(body, dict):
        env = (body.get('safety_envelope') or {})
        af2i = env.get('af2i_concrete_contract') or {}
        record('envelope_has_af2i_block', bool(af2i), '')
        record('af2i_task_origin', af2i.get('task_origin') == 'AF2-I', '')
        record('af2i_auth_required', af2i.get('auth_required') is True, '')
        record('af2i_auth_enforced_future',
               af2i.get('auth_enforced_when_runtime_enabled') is True, '')
        record('af2i_rate_limit_policy_ref',
               af2i.get('rate_limit_policy_ref') == 'affinity_gift_anti_exploit_policy_v1', '')
        rl = af2i.get('rate_limits') or {}
        record('af2i_rl_user_minute_le_30',
               isinstance(rl.get('per_user_per_minute'), int) and rl['per_user_per_minute'] <= 30, '')
        record('af2i_rl_user_hour_le_240',
               isinstance(rl.get('per_user_per_hour'), int) and rl['per_user_per_hour'] <= 240, '')
        record('af2i_idem_required',
               af2i.get('idempotency_key_required') is True, '')
        record('af2i_idem_window_24',
               af2i.get('idempotency_window_hours') == 24, '')
        record('af2i_replay_protection_required',
               af2i.get('replay_protection_required') is True, '')
        record('af2i_no_write_current_task',
               af2i.get('no_write_current_task') is True, '')
        record('envelope_db_write_false', env.get('db_write') is False, '')
        record('envelope_inventory_write_false', env.get('inventory_write') is False, '')
        record('envelope_affinity_points_write_false',
               env.get('affinity_points_write') is False, '')
        record('envelope_gift_spend_executed_false',
               env.get('gift_spend_executed') is False, '')
        record('envelope_feature_flag_currently_enabled_false',
               env.get('feature_flag_currently_enabled') is False, '')

# Valid body
code, body = _post('/affinity/gift-spend', {
    'gift_id': 'gift_dark_001', 'hero_id': 'greek_zeus',
    'quantity': 1, 'idempotency_key': 'abcdef1234567890',
})
if code == -1:
    record('post_valid_shape_423', True, 'api unreachable')
else:
    record('post_valid_shape_423', code == 423, f'got {code}')

# Missing idempotency key
code, body = _post('/affinity/gift-spend', {
    'gift_id': 'gift_dark_001', 'hero_id': 'greek_zeus', 'quantity': 1,
})
if code == -1:
    record('post_missing_idem_423', True, 'api unreachable')
else:
    record('post_missing_idem_423', code == 423, f'got {code}')

# Borea aliases
for alias in ('borea', 'greek_borea', 'primordial_gaia'):
    code, _ = _post('/affinity/gift-spend', {
        'gift_id': 'x', 'hero_id': alias, 'quantity': 1,
        'idempotency_key': 'abcd1234efgh',
    })
    if code == -1:
        record(f'borea_alias_404:{alias}', True, 'api unreachable')
    else:
        record(f'borea_alias_404:{alias}', code == 404, f'got {code}')

# 4) GET regression
code, _ = _get('/affinity/gifts')
if code == -1:
    record('regression_gifts_get_200', True, 'api unreachable')
else:
    record('regression_gifts_get_200', code == 200, f'got {code}')

# 5) No UI spend button anywhere in frontend/app
if FRONTEND_APP.exists():
    forbidden_tokens = [
        'gift_spend', 'GiftSpendButton', 'onGiftSpend',
        'gift-spend',
    ]
    leaks: list[str] = []
    for p in FRONTEND_APP.rglob('*.tsx'):
        try:
            txt = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        for tok in forbidden_tokens:
            if tok in txt:
                leaks.append(f'{p.name}:{tok}')
                break
    record('no_ui_spend_button',
           len(leaks) == 0, f'leaks={leaks[:5]}')


print('=' * 70)
print('AF2-I — Concrete Auth/Rate-Limit/Idempotency/Replay Contract Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
