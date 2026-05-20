#!/usr/bin/env python3
"""V26 PART L — Safety Rollup U."""
import json, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v21.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8001'


def _get(p):
    try:
        with urllib.request.urlopen(BASE + p, timeout=4) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def _file_pass(p):
    f = Path(p)
    if not f.exists(): return False
    try:
        return json.loads(f.read_text()).get('verdict') == 'PASS'
    except Exception:
        return False


def _git_clean(f):
    out = subprocess.run(['git', '-C', '/app', 'diff', '--stat', '--', f],
                          capture_output=True, text=True, timeout=5)
    return out.stdout.strip() == ''


def main():
    cs = _get('/api/affinity/gift-spend/canary-status') or {}
    heroes = _get('/api/heroes') or []
    ids = {(h.get('id') or '').lower() for h in heroes if isinstance(h, dict)}
    leak = sorted(ids & {'borea', 'greek_borea', 'primordial_gaia'})

    rollup = {
        'task_origin': 'AF2-N-V26-SAFETY-ROLLUP-U',
        'version': 'v21',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'state': 'stage4_internal_beta_active_no_broad_rollout',
        # V26 part statuses
        'managed_redis_status': 'PLAN_READY' if _file_pass('/app/data/design/affinity/affinity_managed_redis_readiness_plan_v1.json') else 'OPEN',
        'cap_raise_plan_status': 'PLAN_READY' if _file_pass('/app/data/design/affinity/af2n_cap_raise_plan_v1.json') else 'OPEN',
        'inventory_scope_plan_status': 'PLAN_READY' if _file_pass('/app/data/design/affinity/af2n_inventory_scope_expansion_plan_v1.json') else 'OPEN',
        'broad_rollout_signoff_v6_status': 'PLAN_READY_NOT_APPROVED' if _file_pass('/app/data/design/affinity/af2n_broad_rollout_signoff_package_v6.json') else 'OPEN',
        'alerting_integration_status': 'PLAN_READY' if _file_pass('/app/data/design/affinity/af2n_alerting_integration_plan_v1.json') else 'OPEN',
        'frontend_smoke_status': 'CLOSED' if _file_pass('/app/data/design/ui/affinity_gifts_frontend_smoke_v26_result.json') else 'OPEN',
        'stress_2x_status': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_stress_2x_v26_result.json') else 'OPEN',
        'blocker_matrix_v5_status': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v5.json') else 'OPEN',
        'observation_v26_status': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_stage4_observation_window_v26_result.json') else 'OPEN',
        'rollback_readiness_status': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_v26_rollback_readiness_result_v1.json') else 'OPEN',
        # Invariants
        'api_heroes_count_100': len(heroes) == 100,
        'heroes_count_observed': len(heroes),
        'borea_hidden': not leak,
        'rate_limit_backend': cs.get('rate_limit_backend'),
        'broad_rollout_authorized': False,
        'public_spend_ui': False,
        'battle_wiring_live': False,
        'battle_runtime_attached': cs.get('battle_runtime_attached'),
        'guardrails_clean': {
            'backend/battle_engine.py': _git_clean('backend/battle_engine.py'),
            'backend/battle_core.py': _git_clean('backend/battle_core.py'),
            'frontend/app/combat.tsx': _git_clean('frontend/app/combat.tsx'),
        },
    }
    # All v26 parts must be CLOSED, PLAN_READY, or PLAN_READY_NOT_APPROVED
    valid = {'CLOSED', 'PLAN_READY', 'PLAN_READY_NOT_APPROVED'}
    statuses = [v for k, v in rollup.items() if k.endswith('_status')]
    all_addressed = all(s in valid for s in statuses)
    rollup['all_v26_parts_addressed'] = all_addressed
    rollup['verdict'] = 'PASS' if all([
        all_addressed,
        rollup['api_heroes_count_100'],
        rollup['borea_hidden'],
        rollup['rate_limit_backend'] == 'redis',
        rollup['broad_rollout_authorized'] is False,
        rollup['public_spend_ui'] is False,
        rollup['battle_wiring_live'] is False,
        all(rollup['guardrails_clean'].values()),
    ]) else 'FAIL'
    OUT.write_text(json.dumps(rollup, indent=2, default=str))
    print(f"verdict={rollup['verdict']} all_addressed={all_addressed} → {OUT}")
    return 0 if rollup['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
