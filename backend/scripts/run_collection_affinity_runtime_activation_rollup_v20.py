#!/usr/bin/env python3
"""V25 PART K — Safety Rollup T."""
import json, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v20.json')
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
        'task_origin': 'AF2-N-V25-SAFETY-ROLLUP-T',
        'version': 'v20',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'state': 'stage4_internal_beta_active_no_broad_rollout',
        'redis_ops_recovery_status': 'CLOSED' if _file_pass('/app/data/design/affinity/redis_rate_limit_ops_recovery_result_v1.json') else 'OPEN',
        'redis_restart_drill_status': 'CLOSED' if _file_pass('/app/data/design/affinity/redis_rate_limit_restart_drill_v25_result.json') else 'OPEN',
        'fail_open_alerting_status': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_fail_open_alerting_contract_v1.json') else 'OPEN',
        'support_runbook_status': 'CLOSED' if Path('/app/docs/divine/85_AF2N_STAGE4_SUPPORT_RUNBOOK_V25.md').exists() else 'OPEN',
        'economy_stress_status': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_economy_stress_10x_simulation_v25_result.json') else 'OPEN',
        'blocker_matrix_v4_status': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v4.json') else 'OPEN',
        'observation_v25_status': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_stage4_observation_window_v25_result.json') else 'OPEN',
        'rollback_readiness_status': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_v25_rollback_readiness_result_v1.json') else 'OPEN',
        'ui_safety_status': 'CLOSED' if _file_pass('/app/data/design/ui/affinity_gifts_public_preview_v25_safety_result.json') else 'OPEN',
        # Invariants
        'api_heroes_count_100': len(heroes) == 100,
        'heroes_count_observed': len(heroes),
        'borea_hidden': not leak,
        'borea_leak_aliases': leak,
        'rate_limit_backend': cs.get('rate_limit_backend'),
        'runtime_attached': cs.get('runtime_attached'),
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
    statuses = [v for k, v in rollup.items() if k.endswith('_status')]
    all_closed = all(s == 'CLOSED' for s in statuses)
    rollup['all_v25_parts_closed'] = all_closed
    rollup['verdict'] = 'PASS' if all([
        all_closed,
        rollup['api_heroes_count_100'],
        rollup['borea_hidden'],
        rollup['rate_limit_backend'] == 'redis',
        rollup['battle_wiring_live'] is False,
        rollup['broad_rollout_authorized'] is False,
        rollup['public_spend_ui'] is False,
        all(rollup['guardrails_clean'].values()),
    ]) else 'FAIL'
    OUT.write_text(json.dumps(rollup, indent=2, default=str))
    print(f"verdict={rollup['verdict']} all_v25_closed={all_closed} → {OUT}")
    return 0 if rollup['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
