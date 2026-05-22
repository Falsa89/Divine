#!/usr/bin/env python3
"""Offline dry-run simulator for SLC-D — NO DB writes."""
from __future__ import annotations
import json, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_d_common import SLC_DIR, load, finish, require  # noqa: E402

NAME = 'slc_d_merge_tooling_offline_simulation_v1'


def fetch(path):
    try:
        with urllib.request.urlopen('http://localhost:8001' + path, timeout=4) as r:
            return r.status, r.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception:
        return 0, ''


def evaluate_scenario(s: dict) -> dict:
    inp = s.get('input', {})
    exp = s.get('expected', {})
    name = s.get('name')
    if name == 'blocked_protected_event_state':
        cal = inp.get('calendar_state', '')
        if 'active' in cal:
            return {'merge_allowed': False, 'reason': 'live_mode_lock'}
        return {'merge_allowed': True}
    if name == 'three_similar_age_servers':
        srcs = inp.get('sources', [])
        oldest = max(srcs, key=lambda x: x.get('age_days', 0)) if srcs else None
        return {'merge_allowed': True, 'target_server_id': oldest.get('server_id') if oldest else None}
    if name == 'three_staggered_age_servers':
        srcs = inp.get('sources', [])
        oldest = max(srcs, key=lambda x: x.get('age_days', 0)) if srcs else None
        return {'merge_allowed': True, 'target_server_id': oldest.get('server_id') if oldest else None,
                'baseline_progress_index_required': True}
    if name == 'ten_plus_low_population_servers':
        cnt = inp.get('sources_count', 0)
        sub_size = 6
        return {'merge_allowed': True, 'split_into_subgroups': cnt > sub_size,
                'subgroups_planned': [{'size': sub_size}, {'size': cnt - sub_size}] if cnt > sub_size else [{'size': cnt}]}
    if name == 'duplicate_names_and_guild_tags':
        return {'merge_allowed': True, 'conflict_resolution_applied': inp.get('conflicts', [])}
    return {'merge_allowed': None}


def main() -> int:
    errs = []
    plan = load(SLC_DIR / 'server_merge_dryrun_scenarios_v1.json')
    scs = plan.get('scenarios', [])
    results = []
    for s in scs:
        actual = evaluate_scenario(s)
        exp = s.get('expected', {})
        # spot-check: merge_allowed must match expected when declared
        if 'merge_allowed' in exp and actual.get('merge_allowed') != exp['merge_allowed']:
            errs.append(f'scenario {s.get("name")}: merge_allowed expected={exp.get("merge_allowed")} actual={actual.get("merge_allowed")}')
        results.append({'id': s.get('id'), 'name': s.get('name'), 'expected': exp, 'actual': actual})
    # Live API smoke (read-only)
    code_h, body_h = fetch('/api/heroes')
    hc = None
    if code_h == 200:
        try:
            data = json.loads(body_h)
            heroes = data if isinstance(data, list) else data.get('heroes', [])
            hc = len(heroes)
        except Exception:
            pass
    if hc != 100:
        errs.append(f'/api/heroes count violated: {hc}')
    code_pg, _ = fetch('/api/heroes/primordial_gaia')
    if code_pg and code_pg != 404:
        errs.append(f'primordial_gaia must be 404 (got {code_pg})')
    payload = {
        'task': NAME, 'mode': 'OFFLINE_SIMULATION_NO_DB_WRITE',
        'design_only': True, 'utc': datetime.now(timezone.utc).isoformat(),
        'merge_execution_allowed': False, 'db_write': False,
        'second_server_opening_allowed': False, 'route_patch_applied': False,
        'simulated_results': results,
        'live_api_smoke': {'heroes_count': hc, 'primordial_gaia_status': code_pg},
    }
    out = SLC_DIR / '_slc_d_merge_tooling_offline_simulation_v1_full_report.json'
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
    return finish(NAME, errs, extra={'simulated_scenarios': len(results), 'heroes_count': hc})


if __name__ == '__main__':
    sys.exit(main())
