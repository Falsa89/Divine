#!/usr/bin/env python3
import os, json, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend/scripts')
tracks=[
    'validate_v110_pack_89_baseline_multirun.py',
    'validate_v110_pack_89_inventory_route_schema_audit.py',
    'validate_v110_pack_89_inventory_sot.py',
    'validate_v110_pack_89_inventory_data_audit.py',
    'validate_v110_pack_89_inventory_feasibility_gate.py',
    'validate_v110_pack_89_route_guard_or_promotion_result.py',
    'validate_v110_pack_89_future_migration_backfill_plan.py',
    'validate_v110_pack_89_backup_rollback_preflight.py',
    'validate_v110_pack_89_frontend_inventory_consumer_check.py',
    'validate_v110_pack_89_runtime_smoke_e2e.py',
    'validate_v110_pack_89_data_invariants.py',
    'validate_v110_pack_89_live_readiness_update.py',
    'validate_v110_pack_89_md5_rebase.py',
    'validate_v110_pack_89_gate_invariant_preservation.py',
    'validate_v110_pack_89_final_multirun_suite.py',
]
fails=[]
for t in tracks:
    rc=subprocess.run([sys.executable, os.path.join(SCRIPTS,t)], capture_output=True, text=True, timeout=120)
    if rc.returncode != 0:
        fails.append((t, (rc.stdout or '').strip()+'\n'+(rc.stderr or '').strip()))
if fails:
    for t,msg in fails: print(f'FAIL TRACK {t}: {msg}')
    sys.exit(1)
d=json.load(open(os.path.join(R, 'data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_summary_v1.json')))
sf=d.get('safety_flags',{})
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','inventory_schema_migration_executed','inventory_backfill_executed','inventory_db_writes','currencies_db_writes','story_db_writes','equipment_db_writes','false_filter_applied_true','account_wide_inventory_leak_in_server_scoped_path','copy_s1_to_s2_inventory','premium_grant','currency_grant','reward_live','progress_live','legacy_cleanup_executed','destructive_migration','delete_of_real_data','player_level_mutation','user_heroes_mutation','team_route_regression','postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live'):
    assert sf.get(k) is False, f'safety {k} must be false'
es=d.get('explicit_statements',{})
for k in ('no_inventory_db_writes','no_false_filter_applied_true','reward_progress_live_off','legacy_cleanup_not_executed'):
    assert es.get(k) is True
assert 'RUNTIME_PROMOTED' in es.get('inventory_runtime_promoted_or_deferred','')
v=d.get('verdict','')
assert 'MEGA_RELEASE_ACCELERATION_89_INVENTORY_PSP_SCOPED_LOADER_PROMOTION' in v
print(f'[v110 MEGA_RELEASE_ACCELERATION_89_INVENTORY_PSP_SCOPED_ROLLUP] OK tracks={len(tracks)}/{len(tracks)} verdict={v}')
