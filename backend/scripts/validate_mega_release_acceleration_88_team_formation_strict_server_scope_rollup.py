#!/usr/bin/env python3
import os, json, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend/scripts')
tracks = [
    'validate_v110_pack_88_baseline_multirun.py',
    'validate_v110_pack_88_team_formation_source_audit.py',
    'validate_v110_pack_88_strict_team_route_implementation.py',
    'validate_v110_pack_88_starter_team_compatibility.py',
    'validate_v110_pack_88_frontend_team_consumer_check.py',
    'validate_v110_pack_88_runtime_smoke_e2e.py',
    'validate_v110_pack_88_account_wide_fallback_guard.py',
    'validate_v110_pack_88_core_loader_promotion_prep.py',
    'validate_v110_pack_88_data_invariants.py',
    'validate_v110_pack_88_cleanup_rollback_strategy.py',
    'validate_v110_pack_88_live_readiness_update.py',
    'validate_v110_pack_88_md5_rebase.py',
    'validate_v110_pack_88_gate_invariant_preservation.py',
    'validate_v110_pack_88_final_multirun_suite.py',
]
fails = []
for t in tracks:
    rc = subprocess.run([sys.executable, os.path.join(SCRIPTS, t)], capture_output=True, text=True, timeout=120)
    if rc.returncode != 0:
        fails.append((t, (rc.stdout or '').strip() + '\n' + (rc.stderr or '').strip()))
if fails:
    for t, msg in fails: print(f'FAIL TRACK {t}: {msg}')
    sys.exit(1)
d = json.load(open(os.path.join(R, 'data/design/v110_pack_88_team_formation_strict_server_scope/v110_pack_88_summary_v1.json')))
sf = d.get('safety_flags', {})
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','account_wide_team_fallback_with_server_id','writes_to_users_team_formation_in_server_scoped_flow','fake_team','fallback_global_roster_or_team','overwrite_existing_team','copy_s1_to_s2','inventory_currency_story_equipment_mutation','bulk_psp_apply','physical_normalization_executed_in_this_pack','destructive_migration','delete_of_real_data','reward_live','progress_live','premium_grant','player_level_mutation','postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','legacy_cleanup_executed'):
    assert sf.get(k) is False, f'safety {k} must be false'
es = d.get('explicit_statements', {})
for k in ('no_account_wide_team_fallback_with_server_id','no_users_team_formation_writes_in_server_scoped_flow','pack_87_starter_team_preserved','reward_progress_live_off','legacy_cleanup_not_executed'):
    assert es.get(k) is True, f'explicit statement {k} must be true'
v = d.get('verdict','')
assert 'MEGA_RELEASE_ACCELERATION_88_TEAM_FORMATION_STRICT_SERVER_SCOPE_AND_CORE_LOADER_PROMOTION_PREP' in v
print(f'[v110 MEGA_RELEASE_ACCELERATION_88_TEAM_FORMATION_STRICT_SERVER_SCOPE_ROLLUP] OK tracks={len(tracks)}/{len(tracks)} verdict={v}')
