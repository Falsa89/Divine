#!/usr/bin/env python3
"""SLC-F dry-run simulator (NO DB writes). Executes the scenarios declared in
slc_f_dry_run_simulation_plan_v1.json + live API smoke for the catalog
endpoints, and records the resolution outcome per scenario without
performing any mutation."""
from __future__ import annotations
import json, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_f_common import SLC_DIR, load, finish, require  # noqa: E402

NAME = 'slc_f_route_patch_dryrun_simulation_v1'


def fetch(path: str, timeout: float = 4.0):
    try:
        with urllib.request.urlopen('http://localhost:8001' + path, timeout=timeout) as r:
            return r.status, r.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception:
        return 0, ''


def simulate_resolution(s: dict) -> dict:
    """Pure-function simulation of the active server resolver."""
    inp = s.get('input', {})
    exp = s.get('expected', {})
    res = {}
    server_status = inp.get('server_status')
    if server_status == 'merged':
        return {'http_status': 308, 'redirect_to': inp.get('merge_target_server_id'), 'resolution_source': 'merged_redirect'}
    if server_status == 'archived':
        return {'http_status': 410, 'reason': 'server_archived', 'resolution_source': 'archived_reject'}
    if inp.get('x_server_id_header') and inp.get('x_server_id_header') != inp.get('stored_active_server_id'):
        # mismatch -> 403
        return {'http_status': 403, 'reason': 'forbidden_server', 'resolution_source': 'x_server_id_header'}
    if inp.get('x_server_id_header'):
        return {'resolved_server_id': inp['x_server_id_header'], 'resolution_source': 'x_server_id_header'}
    if inp.get('stored_active_server_id'):
        return {'resolved_server_id': inp['stored_active_server_id'], 'resolution_source': 'stored_active_server_id'}
    if inp.get('compatibility_window') is False:
        return {'http_status': 423, 'reason': 'no_active_server'}
    # default legacy s1
    return {'resolved_account_id': inp.get('user_id'), 'resolved_server_id': 's1', 'resolution_source': 'default_legacy_server_id_s1', 'creates_profile': False}


def main() -> int:
    errs = []
    plan = load(SLC_DIR / 'slc_f_dry_run_simulation_plan_v1.json')
    scenarios = plan.get('scenarios', [])
    require(len(scenarios) >= 10, f'plan must contain >=10 scenarios (got {len(scenarios)})', errs)
    results = []
    for s in scenarios:
        if s.get('name') == 'global_catalog_route_unchanged':
            code, body = fetch('/api/heroes')
            heroes_count = None
            borea_in_list = None
            try:
                data = json.loads(body) if body else []
                heroes = data if isinstance(data, list) else data.get('heroes', [])
                heroes_count = len(heroes)
                borea_in_list = any((h.get('id') or '').lower() in ('borea', 'greek_borea', 'primordial_gaia') for h in heroes if isinstance(h, dict))
            except Exception:
                pass
            actual = {'http_status': code, 'heroes_count': heroes_count, 'borea_in_list': borea_in_list}
            if heroes_count != 100 or borea_in_list:
                errs.append(f'scenario {s.get("id")}: /api/heroes invariant violated: {actual}')
        elif s.get('name') == 'borea_catalog_only_baseline_unchanged':
            code, _ = fetch('/api/heroes/borea')
            actual = {'http_status': code, 'baseline': 'catalog_only_inert' if code == 200 else 'unexpected'}
            # baseline is 200; SLC-F must NOT mutate this. We only record.
        elif s.get('name') == 'primordial_gaia_404_invariant':
            code, _ = fetch('/api/heroes/primordial_gaia')
            actual = {'http_status': code}
            if code != 404:
                errs.append(f'scenario {s.get("id")}: primordial_gaia must be 404 (got {code})')
        elif s.get('name') == 'af2n_cap_50000_invariant_after_patch':
            af2n = Path('/app/backend/routes/affinity_gift_spend.py')
            src = af2n.read_text() if af2n.exists() else ''
            actual = {'cap_preserved': '50000' in src, 'allowlist_preserved': '2500' in src}
            if not actual['cap_preserved']:
                errs.append(f'scenario {s.get("id")}: AF2-N cap 50000 marker missing')
        else:
            actual = simulate_resolution(s)
        results.append({'id': s.get('id'), 'name': s.get('name'), 'expected': s.get('expected'), 'actual': actual})

    payload = {
        'task_origin': 'SLC-F-DRY-RUN-SIMULATION', 'version': 'v1', 'mode': 'DRY_RUN_NO_DB_WRITE',
        'design_only': True, 'utc': datetime.now(timezone.utc).isoformat(),
        'route_patch_applied': False, 'db_write': False, 'second_server_opening_allowed': False,
        'simulated_results': results,
        'safety': {'no_db_write': True, 'no_runtime_change': True, 'borea_safe': True},
    }
    out = SLC_DIR / '_slc_f_route_patch_dryrun_simulation_v1_full_report.json'
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
    return finish(NAME, errs, extra={'simulated_scenarios': len(results), 'route_patch_applied': False})


if __name__ == '__main__':
    sys.exit(main())
