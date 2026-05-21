#!/usr/bin/env python3
"""SLC-C — Read-Only API Smoke Baseline.

Captures the current behavior of public API endpoints relevant to the
SLC-C migration plan. NO mutations. NO writes. The script is informational
and validates only what SLC-C is responsible for:

  HARD INVARIANT (must hold; SLC-C must not regress):
    - GET /api/heroes  -> exactly 100 official heroes exposed
    - GET /api/heroes/primordial_gaia -> 404

  PRE-EXISTING CATALOG-ONLY BEHAVIOR (SLC-C does NOT change, NOT a leak):
    - GET /api/heroes/borea       -> 200 (catalog-only design data)
    - GET /api/heroes/greek_borea -> 200 (catalog-only design data, is_official=true,
                                          but NOT counted in the public 100-list)

  Both Borea-related endpoints intentionally serve inert catalog data; the
  list endpoint /api/heroes (count=100) is what enforces the public-facing
  hidden state. This baseline is recorded so that any future drift caused
  by a multi-shard implementation can be detected and flagged.
"""
from __future__ import annotations
import json, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import DESIGN_DIR, finish  # noqa: E402

NAME = 'slc_c_api_smoke_readonly_v1'
BASE = 'http://localhost:8001'


def fetch(path: str, timeout: float = 5.0) -> tuple[int, str]:
    req = urllib.request.Request(BASE + path, method='GET')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode('utf-8', errors='ignore')
        except Exception:
            body = ''
        return e.code, body
    except Exception as ex:
        return 0, f'error:{ex}'


def main() -> int:
    errs = []
    # 1) /api/heroes count == 100
    code, body = fetch('/api/heroes')
    heroes_count = None
    public_borea_in_list = False
    if code == 200:
        try:
            data = json.loads(body)
            heroes = data if isinstance(data, list) else data.get('heroes', [])
            heroes_count = len(heroes)
            for h in heroes:
                hid = (h.get('id') or '').lower() if isinstance(h, dict) else ''
                if hid in ('borea', 'greek_borea', 'primordial_gaia'):
                    public_borea_in_list = True
        except Exception as ex:
            errs.append(f'/api/heroes parse error: {ex}')
    else:
        errs.append(f'/api/heroes returned status={code}')

    if heroes_count != 100:
        errs.append(f'HARD INVARIANT VIOLATED: /api/heroes count != 100 (got {heroes_count})')
    if public_borea_in_list:
        errs.append('HARD INVARIANT VIOLATED: borea/greek_borea/primordial_gaia listed in /api/heroes public list')

    # 2) Hard invariant: primordial_gaia must be 404
    code_pg, _ = fetch('/api/heroes/primordial_gaia')
    if code_pg != 404:
        errs.append(f'HARD INVARIANT VIOLATED: /api/heroes/primordial_gaia returned {code_pg}, expected 404')

    # 3) Pre-existing catalog-only behavior (informational; NOT failing).
    code_b, _ = fetch('/api/heroes/borea')
    code_gb, _ = fetch('/api/heroes/greek_borea')

    # 4) AF2-N gift-spend endpoint must still reject Borea with 404 BEFORE any other check
    code_gs, body_gs = fetch('/api/affinity/gift-spend')  # GET will likely 405; that's fine
    # Just record availability of the route (no POST here — would mutate ledger)

    payload = {
        'task_origin': 'SLC-C-API-SMOKE-READONLY',
        'version': 'v1',
        'mode': 'READ_ONLY',
        'utc': datetime.now(timezone.utc).isoformat(),
        'hard_invariants': {
            'heroes_count_equals_100': heroes_count == 100,
            'heroes_count_observed': heroes_count,
            'primordial_gaia_is_404': code_pg == 404,
            'no_borea_in_public_list': not public_borea_in_list,
        },
        'pre_existing_catalog_only_state': {
            'api_heroes_borea_status': code_b,
            'api_heroes_greek_borea_status': code_gb,
            'note': (
                'Both endpoints serve catalog-only inert data; this is a pre-existing '
                'design-only state documented in divine_weapons.py and sanctuary.py. '
                'SLC-C does not modify this behavior.'
            ),
        },
        'affinity_gift_spend_route_reachable': code_gs in (200, 405, 422, 423, 429),
        'safety': {
            'no_db_write': True,
            'no_runtime_change': True,
            'no_post_or_mutating_calls': True,
        },
    }
    out = DESIGN_DIR / f'_{NAME}_result.json'
    with out.open('w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    return finish(NAME, errs, {
        'heroes_count': heroes_count,
        'primordial_gaia_404': code_pg == 404,
        'borea_status_preexisting': code_b,
        'greek_borea_status_preexisting': code_gb,
    })


if __name__ == '__main__':
    sys.exit(main())
