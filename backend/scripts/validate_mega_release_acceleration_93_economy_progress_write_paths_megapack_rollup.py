#!/usr/bin/env python3
import os, json, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend/scripts')
tracks = [
    'validate_v110_pack_93_baseline_multirun.py',
    'validate_v110_pack_93_write_path_audit.py',
    'validate_v110_pack_93_currency_write_guard.py',
    'validate_v110_pack_93_story_progress_write_guard.py',
    'validate_v110_pack_93_equipment_backfill_preflight.py',
    'validate_v110_pack_93_equipment_write_guard.py',
    'validate_v110_pack_93_reward_claim_ledger_design.py',
    'validate_v110_pack_93_frontend_write_consumer_guard.py',
    'validate_v110_pack_93_runtime_smoke_e2e.py',
    'validate_v110_pack_93_static_anti_account_wide_write_guard.py',
    'validate_v110_pack_93_data_invariants.py',
    'validate_v110_pack_93_cleanup_rollback.py',
    'validate_v110_pack_93_live_readiness_update.py',
    'validate_v110_pack_93_md5_rebase.py',
    'validate_v110_pack_93_gate_invariant_preservation.py',
    'validate_v110_pack_93_final_multirun_suite.py',
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
d = json.load(open(os.path.join(R, 'data/design/v110_pack_93_economy_progress_write_paths/v110_pack_93_summary_v1.json')))
sf = d.get('safety_flags', {})
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','production_user_db_writes','broad_db_writes','migration_executed','backfill_executed','legacy_cleanup_executed','destructive_migration','reward_live','progress_live','premium_grant','currency_grant','iap_store_payment_change','false_filter_applied_true','false_readiness','unmarked_test_writes','account_wide_writes_for_server_bound_data','s1_to_s2_copy','hardcoded_s1_in_writes','postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live'):
    assert sf.get(k) is False, f'safety {k} must be false'
es = d.get('explicit_statements', {})
for k in ('no_production_user_writes','no_reward_live_activation','no_migration_backfill_execute','pack_91_preserved','pack_92_preserved','currency_write_guard_implemented_test_only_safe','story_progress_write_honest_deferred_blocker','equipment_write_honest_deferred_blocker','reward_claim_ledger_design_pre_live_complete'):
    assert es.get(k) is True, k
v = d.get('verdict', '')
assert 'MEGA_RELEASE_ACCELERATION_93_ECONOMY_PROGRESS_WRITE_PATHS_MEGAPACK' in v
print(f'[v110 MEGA_RELEASE_ACCELERATION_93_ECONOMY_PROGRESS_WRITE_PATHS_MEGAPACK_ROLLUP] OK tracks={len(tracks)}/{len(tracks)} verdict={v}')
