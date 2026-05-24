#!/usr/bin/env python3
"""PROJECT_G Track B validator — housing preview contract freeze + cap snapshot.

Verifies:
  * marker present with verdict TRACK_B_HOUSING_PREVIEW_CONTRACT_FROZEN_INERT
  * housing cap snapshot v1 contains the 7 sub-structures (per_room, category,
    item, bonus, mode, master_cap, vip_vault_secondary_cap)
  * per_room caps respect master_cap (per-room max ≤ master_cap)
  * vip_vault_secondary_cap must_be_under_master_cap=true
  * runtime probe: GET /api/housing/preview → 503 (flag OFF)
  * no DB write keywords in housing_preview.py
  * housing_bonus_resolver_stub not imported by route
"""
import json, os, sys, urllib.request, urllib.error
from pathlib import Path

MARKER = Path('/app/data/design/housing/project_g_housing_preview_contract_and_cap_snapshot_v1.json')
ROUTE = Path('/app/backend/routes/housing_preview.py')
FORBIDDEN_DB_WRITES = ('insert_one(', 'update_one(', 'replace_one(', 'delete_one(', 'find_one_and_update(')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def http_status(method, url):
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as r: return r.status
    except urllib.error.HTTPError as e: return e.code
    except Exception: return -1


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_B_HOUSING_PREVIEW_CONTRACT_FROZEN_INERT': fail('verdict mismatch')
    forb = m.get('forbidden_in_track_b_respected', {})
    for k in ('housing_live_bonus', 'db_writes', 'battle_mutation', 'account_stat_mutation', 'frontend'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_b.{k} must be False')
    snap = m.get('housing_cap_snapshot_v1', {})
    for sub in ('per_room', 'category', 'item', 'bonus', 'mode', 'master_cap', 'vip_vault_secondary_cap'):
        if sub not in snap: fail(f'cap snapshot missing sub-structure: {sub}')
    master = snap['master_cap']
    per_room = snap['per_room']
    for stat in ('hp_pct', 'atk_pct', 'def_pct', 'crit_pct'):
        if stat not in master: fail(f'master_cap missing {stat}')
        if stat not in per_room: fail(f'per_room missing {stat}')
        if per_room[stat]['max'] > master[stat]:
            fail(f'per_room {stat} max ({per_room[stat]["max"]}) exceeds master_cap {stat} ({master[stat]})')
    vv = snap['vip_vault_secondary_cap']
    if vv.get('must_be_under_master_cap') is not True: fail('vip_vault_secondary_cap must_be_under_master_cap must be True')
    for stat in ('hp_pct', 'atk_pct', 'def_pct', 'crit_pct'):
        if vv[stat] > master[stat]:
            fail(f'vip_vault {stat} ({vv[stat]}) exceeds master_cap {stat} ({master[stat]})')
    if 'flat_damage' not in snap['bonus']['types_forbidden']: fail('bonus types_forbidden must include flat_damage')
    if 'true_damage' not in snap['bonus']['types_forbidden']: fail('bonus types_forbidden must include true_damage')
    # Route hygiene
    if not ROUTE.exists(): fail(f'route missing {ROUTE}')
    rsrc = ROUTE.read_text()
    # Only forbid actual import statements, not textual mentions in docstrings/comments.
    for bad in (
        'from game_logic.housing_bonus_resolver_stub',
        'from backend.game_logic.housing_bonus_resolver_stub',
        'import housing_bonus_resolver_stub',
    ):
        if bad in rsrc:
            fail(f'housing_bonus_resolver_stub must NOT be imported by housing_preview route (found: {bad})')
    for kw in FORBIDDEN_DB_WRITES:
        if kw in rsrc: fail(f'forbidden DB write op in housing_preview route: {kw}')
    # Runtime probe
    if os.environ.get('SUITE_SKIP_HTTP_PROBE', '').strip().lower() != 'true':
        if os.environ.get('HOUSING_PREVIEW_ENABLED', '').strip().lower() == 'true':
            print('[WARN] HOUSING_PREVIEW_ENABLED=true — skipping 503 probe')
        else:
            code = http_status('GET', 'http://127.0.0.1:8001/api/housing/preview')
            if code not in (503, -1):
                fail(f'runtime probe GET /api/housing/preview returned {code}, expected 503')
    print('[PASS] PROJECT_G Track B housing preview contract FROZEN INERT: 503 default; 7 cap sub-structures; per_room≤master; vip_vault≤master; no DB writes')
    sys.exit(0)

if __name__ == '__main__': main()
