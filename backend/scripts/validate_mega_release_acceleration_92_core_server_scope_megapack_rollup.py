#!/usr/bin/env python3
import os, json, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend/scripts')
tracks = [
    'validate_v110_pack_92_baseline_multirun.py',
    'validate_v110_pack_92_core_route_schema_audit.py',
    'validate_v110_pack_92_core_server_scope_sot.py',
    'validate_v110_pack_92_currency_wallet_loader_split.py',
    'validate_v110_pack_92_story_progress_loader_scope.py',
    'validate_v110_pack_92_equipment_loader_scope.py',
    'validate_v110_pack_92_frontend_server_id_sweep.py',
    'validate_v110_pack_92_frontend_static_regression_guard.py',
    'validate_v110_pack_92_runtime_guard_smoke.py',
    'validate_v110_pack_92_future_migration_write_path_plan.py',
    'validate_v110_pack_92_data_invariants.py',
    'validate_v110_pack_92_cleanup_rollback_strategy.py',
    'validate_v110_pack_92_live_readiness_update.py',
    'validate_v110_pack_92_md5_rebase.py',
    'validate_v110_pack_92_gate_invariant_preservation.py',
    'validate_v110_pack_92_final_multirun_suite.py',
]
fails = []
for t in tracks:
    rc = subprocess.run([sys.executable, os.path.join(SCRIPTS, t)], capture_output=True, text=True, timeout=120)
    if rc.returncode != 0:
        fails.append((t, (rc.stdout or '').strip() + '\n' + (rc.stderr or '').strip()))
if fails:
    for t, msg in fails:
        print(f'FAIL TRACK {t}: {msg}')
    sys.exit(1)
d = json.load(open(os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_summary_v1.json')))
sf = d.get('safety_flags', {})
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','schema_migration_executed','backfill_executed','production_user_db_writes','unmarked_test_writes','broad_db_writes','currency_write_promotion','story_progress_write_promotion','equipment_write_promotion','reward_live','progress_live','premium_grant','currency_grant','s1_to_s2_copy','copy_s1_to_s2_inventory','account_wide_fallback_for_server_bound_data','silent_s1_fallback','hardcoded_s1_in_writes','false_filter_applied_true','legacy_cleanup_executed','destructive_migration','delete_of_real_data','player_level_mutation','user_heroes_cross_server_mutation','team_route_regression','postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live'):
    assert sf.get(k) is False, f'safety {k} must be false'
es = d.get('explicit_statements', {})
for k in ('inventory_pack_91_preserved','no_broad_db_writes','no_reward_progress_live','no_release_readiness_claim','currency_loader_split_real','story_loader_real_server_scoped_read','equipment_loader_honest_deferred_blocker'):
    assert es.get(k) is True, k
assert es.get('frontend_user_heroes_server_id_sweep_completed_or_blockers') in ('COMPLETED','BLOCKERS')
v = d.get('verdict', '')
assert 'MEGA_RELEASE_ACCELERATION_92_CORE_SERVER_SCOPE_MEGAPACK' in v
print(f'[v110 MEGA_RELEASE_ACCELERATION_92_CORE_SERVER_SCOPE_MEGAPACK_ROLLUP] OK tracks={len(tracks)}/{len(tracks)} verdict={v}')
