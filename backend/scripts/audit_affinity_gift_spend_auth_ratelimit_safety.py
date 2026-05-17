#!/usr/bin/env python3
"""
AF2-H — Auth/rate-limit/idempotency hardening metadata audit.

Verifies that the POST /api/affinity/gift-spend skeleton:
  - still has no Depends(get_current_user) wired today (no-write by design)
  - exposes future-runtime hardening metadata in the disabled envelope
  - documents auth_required_future=true, rate_limit_required_future=true,
    idempotency_required_future=true with sensible values
  - rate_limit per-user <=30/min and <=240/h
  - idempotency window >= 1h
  - still hard-disabled (HTTP 423) on valid payload
  - still 404 for borea / greek_borea hero_id
  - no DB write tokens / no motor/pymongo import
  - GET /api/affinity/gifts unaffected (regression 200)

Read-only. Exit 0 on PASS.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROOT = Path('/app')
ROUTE = ROOT / 'backend' / 'routes' / 'affinity_gift_spend.py'
API_BASE = 'http://127.0.0.1:8001'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


record('route_present', ROUTE.exists(), str(ROUTE))
src = ROUTE.read_text(encoding='utf-8') if ROUTE.exists() else ''

# 1. Future hardening metadata exposed
for tok in [
    'auth_required_future', 'auth_strategy_future',
    'rate_limit_required_future', 'rate_limit_per_user_per_minute_future',
    'rate_limit_per_user_per_hour_future', 'rate_limit_per_ip_per_minute_future',
    'rate_limit_burst_window_seconds_future', 'rate_limit_burst_max_future',
    'idempotency_required_future', 'idempotency_key_header_future',
    'idempotency_window_hours_future', 'idempotency_key_min_len',
    'idempotency_key_max_len', 'replay_protection_strategy_future',
    'transaction_integrity_required_future', 'transaction_strategy_future',
    'borea_visibility_gate_required_future',
]:
    record(f'metadata_present:{tok}', tok in src, f'token missing in route src')

# 2. No Depends(get_current_user) wired today (we mantain disabled-without-leak posture).
# Distinguish actual call usage (`= Depends(get_current_user)` or function param)
# from documentation string `"Depends(get_current_user)"`.
depends_usage = re.search(
    r'(=\s*Depends\(get_current_user\)|:\s*[A-Za-z_]+\s*=\s*Depends\(get_current_user\))',
    src,
)
record('no_depends_get_current_user_today', depends_usage is None,
       'Depends should NOT be wired in this task (no-write by design)')

# 3. No DB write tokens / no DB imports
for pat in [r'\.insert_one', r'\.update_one', r'\.delete_one',
            r'\.bulk_write', r'\.replace_one',
            r'^\s*(import|from)\s+motor',
            r'^\s*(import|from)\s+pymongo']:
    record(f'no_write_token:{pat}', not re.search(pat, src, re.MULTILINE),
           f'forbidden token found')

# 4. Live: HTTP 423 + envelope includes future_runtime_hardening
def _post(body: dict | None) -> tuple[int, dict | None]:
    payload = json.dumps(body or {}).encode('utf-8')
    req = Request(API_BASE + '/api/affinity/gift-spend', data=payload,
                  method='POST', headers={'Content-Type': 'application/json'})
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


code, body = _post({
    'gift_id': 'g1', 'hero_id': 'greek_athena',
    'quantity': 1, 'idempotency_key': 'abcd1234efgh',
})
record('valid_payload_423', code == 423, f'got {code}')
if isinstance(body, dict):
    env = body.get('safety_envelope') or {}
    fh = env.get('future_runtime_hardening') or {}
    record('envelope_has_future_hardening', isinstance(fh, dict) and fh, '')
    record('fh_auth_required_future', fh.get('auth_required_future') is True, '')
    record('fh_rate_limit_required_future',
           fh.get('rate_limit_required_future') is True, '')
    record('fh_idempotency_required_future',
           fh.get('idempotency_required_future') is True, '')
    record('fh_currently_enforced_false',
           fh.get('currently_enforced') is False, '')
    rpm = fh.get('rate_limit_per_user_per_minute_future')
    rph = fh.get('rate_limit_per_user_per_hour_future')
    record('fh_rate_limit_per_user_minute_le_30',
           isinstance(rpm, int) and rpm <= 30, f'got {rpm}')
    record('fh_rate_limit_per_user_hour_le_240',
           isinstance(rph, int) and rph <= 240, f'got {rph}')
    iw = fh.get('idempotency_window_hours_future')
    record('fh_idempotency_window_ge_1h',
           isinstance(iw, int) and iw >= 1, f'got {iw}')
    record('fh_borea_visibility_gate',
           fh.get('borea_visibility_gate_required_future') is True, '')
    # Core envelope flags unchanged
    for k in ['db_write', 'inventory_write', 'affinity_points_write',
              'gift_spend_executed', 'feature_flag_currently_enabled']:
        record(f'envelope_{k}_false', env.get(k) is False, '')

# 5. Borea aliases still 404
for alias in ['borea', 'greek_borea', 'primordial_gaia']:
    code, _ = _post({'gift_id': 'x', 'hero_id': alias, 'quantity': 1,
                     'idempotency_key': 'abcd1234efgh'})
    record(f'borea_alias_404:{alias}', code == 404, f'got {code}')

# 6. GET /api/affinity/gifts unaffected
try:
    with urlopen(API_BASE + '/api/affinity/gifts', timeout=5) as resp:
        record('regression_gifts_get_200', resp.status == 200, '')
except Exception as e:
    record('regression_gifts_get_200', False, f'{e!r}')


print('=' * 70)
print('AF2-H — Auth/Rate-Limit/Idempotency Hardening Safety Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
