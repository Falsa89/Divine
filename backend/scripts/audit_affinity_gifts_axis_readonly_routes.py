#!/usr/bin/env python3
"""
AXIS-F — Audit: read-only affinity gifts axis routes.

Verifies the GET-only routes added to /app/backend/routes/affinity_gifts.py:
- GET /api/affinity/gifts/by-faction/greek -> 200, design_only payload
- GET /api/affinity/gifts/by-faction/tides -> 404 (deferred_not_live)
- GET /api/affinity/gifts/by-faction/borea -> 404 (forbidden alias)
- GET /api/affinity/gifts/by-element/dark -> 200, alias_applied=false
- GET /api/affinity/gifts/by-element/darkness -> 200, alias_applied=true,
  canonical=='dark'
- GET /api/affinity/gifts/by-element/tides -> 404 (axis_type_mismatch)
- Mutation methods (POST/PUT/PATCH/DELETE) on these routes -> 405
- /api/affinity/gifts and /summary still 200 (regression)
- envelope.read_only=true, .db_write=false, .gift_spend_enabled=false

Read-only. NO DB / runtime / catalog mutation.
"""
from __future__ import annotations
import json
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


def _http(path: str, method: str = 'GET', body: dict | None = None) -> tuple[int, dict | None]:
    payload = None
    headers = {}
    if body is not None:
        payload = json.dumps(body).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
    req = Request(API + path, data=payload, method=method, headers=headers)
    try:
        with urlopen(req, timeout=6) as resp:
            try:
                return resp.status, json.loads(resp.read().decode('utf-8'))
            except Exception:
                return resp.status, None
    except HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode('utf-8'))
        except Exception:
            return e.code, None
    except URLError:
        return -1, None


# 1) by-faction
code, body = _http('/affinity/gifts/by-faction/greek')
record('by_faction_greek_200', code == 200, f'got {code}')
if isinstance(body, dict):
    record('by_faction_greek_design_only',
           body.get('design_only') is True, '')
    record('by_faction_greek_runtime_attached_false',
           body.get('runtime_attached') is False, '')
    env = body.get('safety_envelope') or {}
    record('by_faction_greek_envelope_read_only',
           env.get('read_only') is True, '')
    record('by_faction_greek_envelope_db_write_false',
           env.get('db_write') is False, '')
    record('by_faction_greek_envelope_gift_spend_disabled',
           env.get('gift_spend_enabled') is False, '')
    record('by_faction_greek_count_ge_1',
           isinstance(body.get('count'), int) and body['count'] >= 1, '')

code, body = _http('/affinity/gifts/by-faction/tides')
record('by_faction_tides_404', code == 404, f'got {code}')
if isinstance(body, dict):
    record('by_faction_tides_message_deferred',
           'deferred_not_live' in str(body.get('detail', '')).lower(), '')

code, _ = _http('/affinity/gifts/by-faction/borea')
record('by_faction_borea_404', code == 404, f'got {code}')

code, _ = _http('/affinity/gifts/by-faction/greek_borea')
record('by_faction_greek_borea_404', code == 404, f'got {code}')

code, _ = _http('/affinity/gifts/by-faction/primordial_gaia')
record('by_faction_primordial_gaia_404', code == 404, f'got {code}')

# 2) by-element
code, body = _http('/affinity/gifts/by-element/dark')
record('by_element_dark_200', code == 200, f'got {code}')
if isinstance(body, dict):
    record('by_element_dark_canonical_dark',
           body.get('canonical') == 'dark', '')
    record('by_element_dark_alias_applied_false',
           body.get('alias_applied') is False, '')
    record('by_element_dark_design_only',
           body.get('design_only') is True, '')
    record('by_element_dark_count_ge_1',
           isinstance(body.get('count'), int) and body['count'] >= 1, '')

code, body = _http('/affinity/gifts/by-element/darkness')
record('by_element_darkness_200', code == 200, f'got {code}')
if isinstance(body, dict):
    record('by_element_darkness_alias_applied_true',
           body.get('alias_applied') is True, '')
    record('by_element_darkness_canonical_dark',
           body.get('canonical') == 'dark', '')

code, body = _http('/affinity/gifts/by-element/tides')
record('by_element_tides_404', code == 404, f'got {code}')
if isinstance(body, dict):
    record('by_element_tides_axis_type_mismatch',
           'axis_type_mismatch' in str(body.get('detail', '')).lower(), '')

# 3) Mutation methods must be 405 (or 404/422)
for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
    code, _ = _http('/affinity/gifts/by-faction/greek', method=method, body={})
    record(f'mutation_blocked:{method}_by_faction_greek',
           code in (405, 404, 422, 415, -1), f'got {code}')
    code, _ = _http('/affinity/gifts/by-element/dark', method=method, body={})
    record(f'mutation_blocked:{method}_by_element_dark',
           code in (405, 404, 422, 415, -1), f'got {code}')

# 4) Regression GETs
code, _ = _http('/affinity/gifts')
record('regression_gifts_200', code == 200, f'got {code}')
code, _ = _http('/affinity/gifts/summary')
record('regression_gifts_summary_200', code == 200, f'got {code}')


print('=' * 70)
print('AXIS-F — Read-Only Affinity Gifts Axis Routes Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
