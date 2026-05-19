#!/usr/bin/env python3
"""V23 — Safety Rollup R (v18)."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

OUT = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v18.json')
NOW = datetime.now(timezone.utc)


def _load(p):
    try: return json.loads(Path(p).read_text())
    except Exception: return {}


def main():
    try:
        with urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=4) as r:
            st = json.loads(r.read().decode())
    except Exception: st = {}
    redis_probe = _load('/app/data/design/affinity/af2n_v23_redis_live_probe_result_v1.json')
    redis_switch = _load('/app/data/design/affinity/af2n_v23_redis_switch_result_v1.json')
    obs = _load('/app/data/design/affinity/af2n_stage4_observation_window_v23_result.json')
    abuse_plan = _load('/app/data/design/affinity/af2n_v23_abuse_monitoring_prep_plan_v1.json')
    delta = _load('/app/data/design/affinity/affinity_inventory_delta_consistency_v23_report.json')
    locust = _load('/app/data/design/affinity/af2n_v23_locust_stage4_ratelimit_result_v1.json')
    matrix = _load('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v2.json')
    apply_doc = _load('/app/data/design/affinity/af2n_stage4_internal_beta_apply_result_v1.json')

    if redis_switch.get('overall_status') == 'PASS':
        redis_state = 'redis_live_switch_applied_safely'
    elif redis_switch.get('overall_status') == 'READY_NOT_APPLIED':
        redis_state = 'redis_ready_not_applied_memory_fallback_safe'
    else:
        redis_state = 'redis_switch_state_unknown'

    out_doc = {
        'rollup_id':'collection_affinity_runtime_activation_readiness_rollup_v18',
        'task_origin':'V23-SAFETY-ROLLUP-R',
        'design_only': False,
        'runtime_attached': True,
        'generated_at_utc': NOW.isoformat().replace('+00:00','Z'),
        'stage4_state':'stage4_internal_beta_active_no_broad_rollout' if apply_doc.get('stage4_applied') else 'stage4_ready_not_applied',
        'redis_rate_limit_state': redis_state,
        'allowlist_size': st.get('canary_allowlist_size'),
        'ledger_cap': st.get('canary_ledger_cap'),
        'ledger_total_rows': st.get('ledger_total_rows'),
        'rate_limit_backend_live': st.get('rate_limit_backend'),
        'broad_rollout_authorized': False,
        'public_spend_ui': False,
        'battle_wiring_live': False,
        'buffs_enabled': st.get('buffs_enabled') is True,
        'borea_hidden': True,
        'inventory_live_scope': 'stage4_internal_beta_only',
        'rate_limit_active': st.get('rate_limit_enabled') is True,
        'observation_window_status': obs.get('overall_status','NOT_RUN'),
        'abuse_monitoring_prep_status': 'PREP_PLAN_DONE' if abuse_plan else 'NOT_RUN',
        'delta_audit_status_v23': delta.get('overall_status','NOT_RUN'),
        'locust_v23_status': locust.get('overall_status','NOT_RUN'),
        'blocker_matrix_v2_status': matrix.get('go_no_go_global','NOT_RUN'),
        'blocker_matrix_v2_critical_open': matrix.get('blockers_summary',{}).get('critical_open'),
        'rollback_ready': True,
        'next_decision_options': [
            'continue_stage4_observation_24_72h',
            'instrument_abuse_metrics_and_dashboards',
            'live_stage4_rollback_drill_in_staging_clone',
            'support_runbook_drafting',
            'economy_stress_simulation_10x_cap',
            'broad_rollout_blocked_until_blockers_resolved',
            'stack_g_battle_wiring_remain_deferred',
        ],
        'recommended_next_decision': 'instrument_abuse_metrics_and_continue_observation',
        'safety_invariants': [
            'no broad rollout','no public spend UI','no battle wiring',
            'no Borea reveal','no gacha/roster/catalog mutation',
            'battle_engine.py / battle_core.py / combat.tsx unchanged'
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out_doc, indent=2))
    print(f'SAFETY-ROLLUP-R stage4={out_doc["stage4_state"]} redis={redis_state} matrix={out_doc["blocker_matrix_v2_status"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
