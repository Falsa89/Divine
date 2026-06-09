#!/usr/bin/env python3
import os, json, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend/scripts')
tracks = [
    'validate_v110_pack_91_baseline_multirun.py',
    'validate_v110_pack_91_frontend_mutation_consumer_audit.py',
    'validate_v110_pack_91_selected_server_source_adoption.py',
    'validate_v110_pack_91_item_shop_frontend_migration.py',
    'validate_v110_pack_91_inventory_use_exp_frontend_migration.py',
    'validate_v110_pack_91_skill_upgrade_frontend_migration.py',
    'validate_v110_pack_91_backend_regression_guard.py',
    'validate_v110_pack_91_real_mutating_smoke_e2e.py',
    'validate_v110_pack_91_frontend_static_regression_guard.py',
    'validate_v110_pack_91_data_invariants.py',
    'validate_v110_pack_91_cleanup_rollback.py',
    'validate_v110_pack_91_live_readiness_update.py',
    'validate_v110_pack_91_md5_rebase.py',
    'validate_v110_pack_91_gate_invariant_preservation.py',
    'validate_v110_pack_91_final_multirun_suite.py',
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
d = json.load(open(os.path.join(R, 'data/design/v110_pack_91_inventory_frontend_consumer_and_smoke/v110_pack_91_summary_v1.json')))
sf = d.get('safety_flags', {})
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','schema_migration_executed','backfill_executed','production_user_db_writes','unmarked_test_writes','account_wide_inventory_write','hardcoded_s1_in_writes','frontend_mutation_without_server_id','silent_s1_fallback','copy_s1_to_s2_inventory','currencies_db_writes','story_db_writes','equipment_db_writes','reward_live','progress_live','premium_grant','currency_grant','legacy_cleanup_executed','destructive_migration','delete_of_real_data','player_level_mutation','user_heroes_cross_server_mutation','team_route_regression','postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live'):
    assert sf.get(k) is False, f'safety {k} must be false'
es = d.get('explicit_statements', {})
for k in ('frontend_inventory_mutations_pass_server_id','no_account_wide_inventory_writes','no_production_user_db_writes','reward_progress_live_off','legacy_cleanup_not_executed'):
    assert es.get(k) is True, k
assert es.get('real_mutating_smoke_executed_or_blocked_honestly') in ('EXECUTED','BLOCKED_HONESTLY')
v = d.get('verdict', '')
assert 'MEGA_RELEASE_ACCELERATION_91_INVENTORY_FRONTEND_CONSUMER_MIGRATION_AND_MUTATING_SMOKE' in v
print(f'[v110 MEGA_RELEASE_ACCELERATION_91_INVENTORY_FRONTEND_CONSUMER_MIGRATION_AND_MUTATING_SMOKE_ROLLUP] OK tracks={len(tracks)}/{len(tracks)} verdict={v}')
