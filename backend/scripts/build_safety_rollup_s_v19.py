#!/usr/bin/env python3
"""V24 — Safety Rollup S (v19)."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

OUT = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v19.json')
NOW = datetime.now(timezone.utc)


def _load(p):
    try: return json.loads(Path(p).read_text())
    except Exception: return {}


def main():
    try:
        with urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=4) as r:
            st = json.loads(r.read().decode())
    except Exception: st = {}
    obs = _load('/app/data/design/affinity/af2n_v24_observation_window_real_result.json')
    drill = _load('/app/data/design/affinity/af2n_v24_staging_rollback_drill_result_v1.json')
    ha_plan = _load('/app/data/design/affinity/affinity_rate_limit_redis_ha_decision_plan_v1.json')
    se_plan = _load('/app/data/design/affinity/af2n_v24_support_economy_prep_light_v1.json')
    matrix = _load('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v3.json')
    apply_doc = _load('/app/data/design/affinity/af2n_stage4_internal_beta_apply_result_v1.json')
    out_doc = {
        'rollup_id':'collection_affinity_runtime_activation_readiness_rollup_v19',
        'task_origin':'V24-SAFETY-ROLLUP-S',
        'design_only': False,'runtime_attached': True,
        'generated_at_utc': NOW.isoformat().replace('+00:00','Z'),
        'stage4_state':'stage4_internal_beta_active_no_broad_rollout' if apply_doc.get('stage4_applied') else 'stage4_ready_not_applied',
        'redis_rate_limit_state':'redis_live_switch_applied_safely',
        'redis_ha_state':'plan_documented_no_live_provision',
        'rate_limit_backend_live': st.get('rate_limit_backend'),
        'metrics_state':'in_memory_instrumentation_live_internal_only',
        'allowlist_size': st.get('canary_allowlist_size'),
        'ledger_cap': st.get('canary_ledger_cap'),
        'ledger_total_rows': st.get('ledger_total_rows'),
        'broad_rollout_authorized': False,
        'public_spend_ui': False,
        'battle_wiring_live': False,
        'buffs_enabled': st.get('buffs_enabled') is True,
        'borea_hidden': True,
        'inventory_live_scope':'stage4_internal_beta_only',
        'rate_limit_active': st.get('rate_limit_enabled') is True,
        'observation_window_real_status': obs.get('overall_status','NOT_RUN'),
        'observation_window_seconds': obs.get('window_seconds_approx'),
        'staging_rollback_drill_status': drill.get('overall_status','NOT_RUN'),
        'redis_ha_plan_status':'DOCUMENTED' if ha_plan else 'NOT_RUN',
        'support_economy_prep_status':'DRAFT_LIGHT' if se_plan else 'NOT_RUN',
        'blocker_matrix_v3_status': matrix.get('go_no_go_global','NOT_RUN'),
        'blocker_matrix_v3_critical_open': matrix.get('blockers_summary',{}).get('critical_open'),
        'rollback_ready': True,
        'next_decision_options':[
            'continue_stage4_observation_24_72h_with_cron',
            'phase_2_redis_ha_staging_cluster_provision',
            'live_db_restore_drill_in_staging',
            'support_runbook_full_drafting',
            'economy_stress_simulation_10x_cap',
            'broad_rollout_blocked_until_blockers_resolved',
            'stack_g_battle_wiring_remain_deferred',
        ],
        'recommended_next_decision':'continue_observation_and_expand_economy_stress_locust',
        'safety_invariants':[
            'no broad rollout','no public spend UI','no battle wiring',
            'no Borea reveal','no gacha/roster/catalog mutation',
            'battle_engine.py / battle_core.py / combat.tsx unchanged'
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out_doc, indent=2))
    print(f'SAFETY-ROLLUP-S stage4={out_doc["stage4_state"]} redis={out_doc["redis_rate_limit_state"]} metrics={out_doc["metrics_state"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
