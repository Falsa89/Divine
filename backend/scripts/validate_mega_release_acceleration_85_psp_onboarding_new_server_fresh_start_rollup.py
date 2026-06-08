#!/usr/bin/env python3
import os, json, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend/scripts')
tracks = [
    'validate_v110_pack_85_baseline_verification.py',
    'validate_v110_pack_85_canonical_fresh_start_sot.py',
    'validate_v110_pack_85_route_map_and_ensure_implementation.py',
    'validate_v110_pack_85_user_heroes_integration.py',
    'validate_v110_pack_85_lobby_integration.py',
    'validate_v110_pack_85_runtime_smoke_fresh_start.py',
    'validate_v110_pack_85_data_invariants.py',
    'validate_v110_pack_85_rollback_cleanup_strategy.py',
    'validate_v110_pack_85_live_readiness_update.py',
    'validate_v110_pack_85_gate_invariant_preservation.py',
    'validate_v110_pack_85_final_3run_suite.py',
]
fails = []
for t in tracks:
    rc = subprocess.run([sys.executable, os.path.join(SCRIPTS, t)], capture_output=True, text=True, timeout=60)
    if rc.returncode != 0:
        fails.append((t, rc.stdout.strip() + '\n' + rc.stderr.strip()))
if fails:
    for t, msg in fails: print(f'FAIL TRACK {t}: {msg}')
    sys.exit(1)
d = json.load(open(os.path.join(R, 'data/design/v110_pack_85_psp_onboarding/v110_pack_85_psp_onboarding_summary_v1.json')))
sf = d.get('safety_flags', {})
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','production_apply_executed','bulk_psp_apply','physical_normalization_executed_in_this_pack','destructive_migration','delete_of_real_psp','premium_grant','reward_live','progress_live','legacy_cleanup_executed','user_heroes_creation_not_authorized_in_this_pack','player_level_mutation_on_existing_psp','copy_s1_to_s2','account_wide_player_level_as_final_server_level','account_wide_roster_as_final_server_roster','postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live'):
    assert sf.get(k) is False, f'safety {k} must be false'
v = d.get('verdict','')
assert 'MEGA_RELEASE_ACCELERATION_85_PSP_ONBOARDING_NEW_SERVER_FRESH_START' in v
print(f'[v110 MEGA_RELEASE_ACCELERATION_85_PSP_ONBOARDING_NEW_SERVER_FRESH_START_ROLLUP] OK tracks=11/11 verdict={v}')
