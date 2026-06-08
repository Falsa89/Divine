#!/usr/bin/env python3
import os, json, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend/scripts')
tracks = [
    'validate_v110_pack_87_baseline_multirun.py',
    'validate_v110_pack_87_starter_flow_sot.py',
    'validate_v110_pack_87_route_and_legacy_starter_audit.py',
    'validate_v110_pack_87_starter_config.py',
    'validate_v110_pack_87_backend_starter_claim_endpoint.py',
    'validate_v110_pack_87_team_initialization.py',
    'validate_v110_pack_87_frontend_onboarding_integration.py',
    'validate_v110_pack_87_server_ui_copy_cleanup.py',
    'validate_v110_pack_87_runtime_smoke_e2e.py',
    'validate_v110_pack_87_data_invariants.py',
    'validate_v110_pack_87_cleanup_rollback_strategy.py',
    'validate_v110_pack_87_live_readiness_update.py',
    'validate_v110_pack_87_md5_rebase.py',
    'validate_v110_pack_87_gate_invariant_preservation.py',
    'validate_v110_pack_87_final_multirun_suite.py',
]
fails = []
for t in tracks:
    rc = subprocess.run([sys.executable, os.path.join(SCRIPTS, t)], capture_output=True, text=True, timeout=120)
    if rc.returncode != 0:
        fails.append((t, (rc.stdout or '').strip() + '\n' + (rc.stderr or '').strip()))
if fails:
    for t, msg in fails: print(f'FAIL TRACK {t}: {msg}')
    sys.exit(1)
d = json.load(open(os.path.join(R, 'data/design/v110_pack_87_server_scoped_starter_flow/v110_pack_87_summary_v1.json')))
sf = d.get('safety_flags', {})
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','production_apply_executed','bulk_psp_apply','physical_normalization_executed_in_this_pack','destructive_migration','delete_of_real_psp','premium_grant','reward_live','progress_live','legacy_cleanup_executed','starter_heroes_account_wide_grant','copy_s1_to_s2','account_wide_player_level_as_final_server_level','account_wide_roster_as_final_server_roster','postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','user_heroes_creation_from_register','premium_or_5star_or_6star_starter','borea_or_premium_hero_in_starter','inventory_grant_in_starter','equipment_grant_in_starter','currency_grant_in_starter','story_reward_grant_in_starter','team_overwrite_existing','player_level_mutation'):
    assert sf.get(k) is False, f'safety {k} must be false'
es = d.get('explicit_statements', {})
for k in ('starter_heroes_are_server_scoped','no_account_wide_starter_user_heroes','new_server_starts_level_1','no_s1_to_s2_copy','no_premium_currency_equipment_story_rewards','reward_progress_live_off','legacy_cleanup_not_executed'):
    assert es.get(k) is True, f'explicit statement {k} must be true'
v = d.get('verdict','')
assert 'MEGA_RELEASE_ACCELERATION_87_SERVER_SCOPED_STARTER_FLOW_AND_SERVER_UI_COPY_CLEANUP' in v
print(f'[v110 MEGA_RELEASE_ACCELERATION_87_SERVER_SCOPED_STARTER_FLOW_ROLLUP] OK tracks={len(tracks)}/{len(tracks)} verdict={v}')
