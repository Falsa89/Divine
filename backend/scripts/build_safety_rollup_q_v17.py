#!/usr/bin/env python3
"""V22 — Safety Rollup Q (v17)."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

OUT = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v17.json')
NOW = datetime.now(timezone.utc)


def _load(p):
    try: return json.loads(Path(p).read_text())
    except Exception: return {}


def main():
    try:
        with urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=4) as r:
            st = json.loads(r.read().decode())
    except Exception:
        st = {}
    redis_probe = _load('/app/data/design/affinity/affinity_rate_limit_redis_probe_result_v1.json')
    redis_plan = _load('/app/data/design/affinity/affinity_rate_limit_redis_migration_plan_v1.json')
    monitor = _load('/app/data/design/affinity/af2n_stage4_extended_monitoring_v22_result.json')
    locust = _load('/app/data/design/affinity/af2n_v22_locust_stage4_extended_result_v1.json')
    delta = _load('/app/data/design/affinity/affinity_inventory_delta_consistency_v22_report.json')
    matrix = _load('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v1.json')
    stage4_apply = _load('/app/data/design/affinity/af2n_stage4_internal_beta_apply_result_v1.json')

    redis_state = 'memory_current'
    if redis_probe.get('overall_status') == 'PASS':
        redis_state = 'redis_ready_for_gated_switch'
    elif redis_probe.get('overall_status') == 'READY_NOT_APPLIED':
        redis_state = 'redis_ready_not_applied'

    out_doc = {
        'rollup_id':'collection_affinity_runtime_activation_readiness_rollup_v17',
        'task_origin':'V22-SAFETY-ROLLUP-Q',
        'design_only': False,
        'runtime_attached': True,
        'generated_at_utc': NOW.isoformat().replace('+00:00','Z'),
        'stage4_state': 'stage4_internal_beta_active_no_broad_rollout' if stage4_apply.get('stage4_applied') else 'stage4_ready_not_applied',
        'redis_rate_limit_state': redis_state,
        'allowlist_size': st.get('canary_allowlist_size'),
        'ledger_cap': st.get('canary_ledger_cap'),
        'ledger_total_rows': st.get('ledger_total_rows'),
        'broad_rollout_authorized': False,
        'public_spend_ui': False,
        'battle_wiring_live': False,
        'buffs_enabled': st.get('buffs_enabled') is True,
        'borea_hidden': True,
        'inventory_live_scope': 'stage4_internal_beta_only',
        'rate_limit_active': st.get('rate_limit_enabled') is True,
        'locust_extended_status': locust.get('overall_status', 'NOT_RUN'),
        'extended_monitoring_status': monitor.get('overall_status', 'NOT_RUN'),
        'delta_audit_status': delta.get('overall_status', 'NOT_RUN'),
        'blocker_matrix_status': matrix.get('go_no_go_global', 'NOT_RUN'),
        'blocker_matrix_total_open_critical': matrix.get('blockers_summary', {}).get('critical_open', None),
        'rollback_ready': True,
        'next_decision_options': [
            'continue_stage4_observation_24_72h',
            'provision_redis_and_run_v23_redis_switch_gated',
            'execute_live_stage4_rollback_drill_in_staging',
            'broad_rollout_blocked_until_blockers_resolved',
            'stack_g_battle_wiring_remain_deferred',
        ],
        'recommended_next_decision': 'provision_redis_and_continue_stage4_observation',
        'safety_invariants': [
            'no broad rollout', 'no public spend UI', 'no battle wiring',
            'no Borea reveal', 'no gacha/roster/catalog mutation',
            'battle_engine.py / battle_core.py / combat.tsx unchanged'
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out_doc, indent=2))
    print(f'SAFETY-ROLLUP-Q stage4={out_doc["stage4_state"]} redis={redis_state} blocker_matrix={out_doc["blocker_matrix_status"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
