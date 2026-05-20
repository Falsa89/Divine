#!/usr/bin/env python3
"""V28 PART K — Safety Rollup W."""
import json, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v23.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8001'


def _get(p):
    try:
        with urllib.request.urlopen(BASE + p, timeout=4) as r:
            return json.loads(r.read().decode())
    except Exception: return None


def _file_pass(p):
    f = Path(p)
    if not f.exists(): return False
    try: return json.loads(f.read_text()).get('verdict') == 'PASS'
    except Exception: return False


def _file_field(p, key='status'):
    f = Path(p)
    if not f.exists(): return 'MISSING'
    try: return json.loads(f.read_text()).get(key, 'UNKNOWN')
    except Exception: return 'PARSE_ERROR'


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
        'task_origin': 'AF2-N-V28-SAFETY-ROLLUP-W',
        'version': 'v23',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'internal_beta_scope_state': 'EXPANDED_TO_2500_V28',
        'allowlist_count': cs.get('canary_allowlist_size'),
        'canary_ledger_cap': cs.get('canary_ledger_cap'),
        'managed_redis_state': _file_field('/app/data/design/affinity/managed_redis_v28_probe_result.json'),
        'alerting_state': _file_field('/app/data/design/affinity/alerting_live_v28_probe_result.json', key='sink_mode'),
        'stress_5x_state': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_stress_5x_v28_result.json') else 'OPEN',
        'observation_v28_state': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_scope_s1_observation_v28_result.json') else 'OPEN',
        'delta_audit_v28_state': 'CLOSED' if _file_pass('/app/data/design/affinity/affinity_inventory_delta_consistency_v28_report.json') else 'OPEN',
        'blocker_matrix_v7_state': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v7.json') else 'OPEN',
        'ui_safety_state': 'CLOSED' if _file_pass('/app/data/design/ui/affinity_gifts_public_preview_v28_safety_result.json') else 'OPEN',
        'rollback_readiness_state': 'CLOSED' if _file_pass('/app/data/design/affinity/af2n_v28_rollback_readiness_result_v1.json') else 'OPEN',
        'inventory_scope_s1_state': _file_field('/app/data/design/affinity/af2n_inventory_scope_s1_v28_result.json'),
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
    rollup['verdict'] = 'PASS' if all([
        rollup['api_heroes_count_100'],
        rollup['borea_hidden'],
        rollup['rate_limit_backend'] == 'redis',
        rollup['canary_ledger_cap'] == 25000,
        rollup['allowlist_count'] == 2500,
        rollup['broad_rollout_authorized'] is False,
        rollup['public_spend_ui'] is False,
        rollup['battle_wiring_live'] is False,
        all(rollup['guardrails_clean'].values()),
        rollup['observation_v28_state'] == 'CLOSED',
        rollup['stress_5x_state'] == 'CLOSED',
        rollup['delta_audit_v28_state'] == 'CLOSED',
        rollup['blocker_matrix_v7_state'] == 'CLOSED',
        rollup['ui_safety_state'] == 'CLOSED',
        rollup['rollback_readiness_state'] == 'CLOSED',
        rollup['inventory_scope_s1_state'] == 'APPLIED',
    ]) else 'FAIL'
    OUT.write_text(json.dumps(rollup, indent=2, default=str))
    print(f"verdict={rollup['verdict']} allowlist={rollup['allowlist_count']} cap={rollup['canary_ledger_cap']}")
    return 0 if rollup['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
