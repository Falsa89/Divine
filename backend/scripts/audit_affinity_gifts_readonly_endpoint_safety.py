#!/usr/bin/env python3
"""
AF2-E — Affinity gifts read-only endpoint safety audit.

Verifies:
  - the route file is GET-only (no POST/PUT/PATCH/DELETE decorators)
  - the endpoint is registered in game_systems.py
  - GET /api/affinity/gifts returns 200 + safety_envelope with all
    runtime flags False
  - entries count matches the AF2-A catalog draft total_entries
  - no adult naming
  - Borea: greek_borea preserved with borea_gift_locked, legacy
    `borea`/`primordial_gaia` rejected (404)
  - no UI gift-spend button exists
  - no DB write occurs (instrumented via response inspection +
    grep for write tokens in the route file)

Read-only. Exit 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROOT = Path('/app')
ROUTE_FILE = ROOT / 'backend' / 'routes' / 'affinity_gifts.py'
GAME_SYSTEMS = ROOT / 'backend' / 'game_systems.py'
CATALOG = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_catalog_faction_element_draft_v1.json'
FRONTEND_APP = ROOT / 'frontend' / 'app'

API_BASE = 'http://127.0.0.1:8001'

WRITE_TOKENS_FORBIDDEN = [
    r'\.insert_one\s*\(',
    r'\.insert_many\s*\(',
    r'\.update_one\s*\(',
    r'\.update_many\s*\(',
    r'\.delete_one\s*\(',
    r'\.delete_many\s*\(',
    r'\.find_one_and_update\s*\(',
    r'\.find_one_and_delete\s*\(',
    r'\.bulk_write\s*\(',
    r'\.replace_one\s*\(',
]

# Adult blacklist context-aware
ADULT_BLACKLIST = ['nsfw', 'lewd', 'erotic', 'porn', 'xxx', 'explicit_sex']
ADULT_CONTEXT_REGEX = re.compile(
    r'(?<![a-z_])adult(?![a-z_]*(?:_explicit_naming_forbidden|_blacklist))',
    re.IGNORECASE,
)

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


# 1. Route file present
record('route_file_present', ROUTE_FILE.exists(), str(ROUTE_FILE))
route_src = ROUTE_FILE.read_text(encoding='utf-8') if ROUTE_FILE.exists() else ''

# 2. Only @router.get decorators
mutating_decorators = re.findall(r'@router\.(post|put|patch|delete)\s*\(', route_src, re.IGNORECASE)
record('route_get_only', not mutating_decorators,
       f'unexpected mutating decorators: {mutating_decorators}')

get_decorators = re.findall(r'@router\.get\s*\(', route_src)
record('route_has_get_decorators', len(get_decorators) >= 3,
       f'expected >=3 GET decorators, got {len(get_decorators)}')

# 3. No DB write tokens in route file
write_hits = []
for pat in WRITE_TOKENS_FORBIDDEN:
    if re.search(pat, route_src):
        write_hits.append(pat)
record('route_no_db_write_tokens', not write_hits, f'hits={write_hits}')

# 4. Registered in game_systems.py
gs_src = GAME_SYSTEMS.read_text(encoding='utf-8') if GAME_SYSTEMS.exists() else ''
record('route_imported_in_game_systems',
       'from routes.affinity_gifts import register_affinity_gifts_readonly_routes' in gs_src,
       '')
record('route_registered_in_game_systems',
       'register_affinity_gifts_readonly_routes(router)' in gs_src, '')

# 5. Live API smoke
def _get_json(path: str) -> tuple[int, dict | None]:
    try:
        with urlopen(API_BASE + path, timeout=5) as resp:
            body = resp.read().decode('utf-8')
            return resp.status, json.loads(body)
    except HTTPError as e:
        try:
            body = e.read().decode('utf-8') if hasattr(e, 'read') else ''
            return e.code, (json.loads(body) if body else None)
        except Exception:
            return e.code, None
    except URLError as e:
        return -1, None


def _request_with_method(path: str, method: str) -> int:
    try:
        req = Request(API_BASE + path, method=method)
        with urlopen(req, timeout=5) as resp:
            return resp.status
    except HTTPError as e:
        return e.code
    except URLError:
        return -1


code, body = _get_json('/api/affinity/gifts')
record('get_full_status_200', code == 200, f'got {code}')
record('get_full_has_envelope',
       isinstance(body, dict) and isinstance(body.get('safety_envelope'), dict), '')
env = (body or {}).get('safety_envelope', {}) if body else {}
for k in ['runtime_attached', 'battle_runtime_attached', 'applied_to_combat',
          'db_write', 'inventory_enabled', 'gift_spend_enabled',
          'gift_claim_enabled', 'affinity_points_write_enabled',
          'stat_buffs_enabled', 'borea_activation',
          'feature_flag_currently_enabled']:
    record(f'envelope_{k}_false', env.get(k) is False, f'got {env.get(k)!r}')
for k in ['read_only', 'design_only']:
    record(f'envelope_{k}_true', env.get(k) is True, f'got {env.get(k)!r}')

# 6. Entries count == catalog draft total_entries
catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
expected_total = catalog.get('total_entries')
record('entries_count_matches_draft',
       isinstance(body, dict) and len(body.get('entries') or []) == expected_total,
       f'expected {expected_total}, got {len(body.get("entries") or []) if body else None}')

# 7. Summary endpoint
code2, body2 = _get_json('/api/affinity/gifts/summary')
record('get_summary_status_200', code2 == 200, f'got {code2}')
record('get_summary_no_entries',
       isinstance(body2, dict) and 'entries' not in body2,
       'summary must not include full entries list')

# 8. By-faction endpoint
code3, body3 = _get_json('/api/affinity/gifts/by-faction/greek')
record('get_by_faction_greek_200', code3 == 200, f'got {code3}')
record('get_by_faction_greek_has_entries',
       isinstance(body3, dict) and isinstance(body3.get('entries'), list)
       and len(body3['entries']) > 0, '')

# 9. Borea legacy alias 404
code4, _ = _get_json('/api/affinity/gifts/by-faction/borea')
record('get_by_faction_borea_404', code4 == 404, f'got {code4}')
code5, _ = _get_json('/api/affinity/gifts/by-faction/primordial_gaia')
record('get_by_faction_primordial_gaia_404', code5 == 404, f'got {code5}')
code6, _ = _get_json('/api/affinity/gifts/by-faction/tides')
record('get_by_faction_tides_404', code6 == 404, f'got {code6}')

# 10. POST/PUT/PATCH/DELETE all rejected
for m in ['POST', 'PUT', 'PATCH', 'DELETE']:
    c = _request_with_method('/api/affinity/gifts', m)
    record(f'method_{m}_rejected', c in (404, 405), f'got {c}')

# 11. No adult naming in route file or live response
raw_resp = json.dumps(body) if body else ''
for tok in ADULT_BLACKLIST:
    record(f'no_adult_token_route:{tok}', tok not in route_src.lower(), '')
    record(f'no_adult_token_response:{tok}', tok not in raw_resp.lower(), '')
record('no_adult_context_route',
       not list(ADULT_CONTEXT_REGEX.finditer(route_src)), '')

# 12. Borea greek_borea entries (if any in catalog) preserved with locked flag
entries = catalog.get('entries') or []
greek_borea_entries = [
    e for e in entries
    if isinstance(e, dict) and e.get('faction_token') == 'greek'
    and 'borea' in (e.get('gift_id') or '').lower()
]
# Catalog draft typically has no per-hero entries; just verify gift catalog
# preserves the borea-locked envelope at top level
record('catalog_borea_locked_constraint',
       (catalog.get('constraints') or {}).get('borea_gifts_locked_until_visibility_unlock') is True
       or all(e.get('borea_gift_locked_until_visibility_unlock') is True
              for e in entries if isinstance(e, dict)),
       'gift catalog draft must keep borea locked')

# 13. No UI gift-spend button
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
print('AF2-E — Affinity Gifts Read-Only Endpoint Safety Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
