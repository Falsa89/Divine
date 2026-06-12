#!/usr/bin/env python3
"""MEGA_RELEASE_ACCELERATION_109 ROLLUP.

Verifica che TUTTI i validator Pack 109 esistano + smoke + report.
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIRED = (
    'validate_v110_pack_109_sot.py',
    'validate_v110_pack_109_pack_91_108_preservation.py',
    'validate_v110_pack_109_server_profile_isolation_audit.py',
    'validate_v110_pack_109_auth_logout_server_selection_audit.py',
    'validate_v110_pack_109_frontend_navigation_playable_loop_rc.py',
    'validate_v110_pack_109_story_battle_preview_staging_rc.py',
    'validate_v110_pack_109_tower_rc.py',
    'validate_v110_pack_109_daily_dailyquest_controlled_rewards_rc.py',
    'validate_v110_pack_109_economy_strict_rc.py',
    'validate_v110_pack_109_inventory_equipment_material_psp_rc.py',
    'validate_v110_pack_109_guild_rc.py',
    'validate_v110_pack_109_arena_pvp_event_rc.py',
    'validate_v110_pack_109_reward_ledger_idempotency_rc.py',
    'validate_v110_pack_109_forbidden_mutation_premium_iap_gacha_guard.py',
    'validate_v110_pack_109_mobile_qa_checklist.py',
    'validate_v110_pack_109_known_deferred_blocker_matrix.py',
    'validate_v110_pack_109_closed_alpha_gate_verdict.py',
    'validate_v110_pack_109_cleanup_rollback_artifacts.py',
    'validate_v110_pack_109_runtime_smoke_e2e.py',
    'smoke_v110_pack_109_closed_alpha_rc_global_e2e.py',
)
for s in REQUIRED:
    assert os.path.exists(os.path.join(R, 'backend/scripts', s)), f'missing: {s}'
rep = os.path.join(R, 'docs/divine/110_CLOSED_ALPHA_RC_SWEEP_RELEASE_GATE_FINAL_REPORT.md')
assert os.path.exists(rep), 'final report missing'
rep_low = open(rep).read().lower()
for t in ('pack 109', 'verdict', 'reward_live_general', 'release_readiness_claimed',
          'public_launch_ready', 'production_release_ready'):
    assert t in rep_low, f'final report token missing: {t}'
print('[MEGA_RELEASE_ACCELERATION_109_ROLLUP] OK nineteen_validators_present smoke_present final_report_present')
