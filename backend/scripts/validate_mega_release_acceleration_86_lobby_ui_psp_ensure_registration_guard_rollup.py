#!/usr/bin/env python3
import os, json, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend/scripts')
tracks = [
    'validate_v110_pack_86_baseline_multirun.py',
    'validate_v110_pack_86_route_ui_map.py',
    'validate_v110_pack_86_lobby_psp_ensure_integration.py',
    'validate_v110_pack_86_register_starter_legacy_guard.py',
    'validate_v110_pack_86_backend_ensure_route_hardening.py',
    'validate_v110_pack_86_user_heroes_team_after_ui_ensure.py',
    'validate_v110_pack_86_runtime_smoke_e2e.py',
    'validate_v110_pack_86_data_invariants.py',
    'validate_v110_pack_86_cleanup_rollback_strategy.py',
    'validate_v110_pack_86_live_readiness_update.py',
    'validate_v110_pack_86_md5_rebase.py',
    'validate_v110_pack_86_gate_invariant_preservation.py',
    'validate_v110_pack_86_final_multirun_suite.py',
]
fails = []
for t in tracks:
    rc = subprocess.run([sys.executable, os.path.join(SCRIPTS, t)], capture_output=True, text=True, timeout=60)
    if rc.returncode != 0:
        fails.append((t, (rc.stdout or '').strip() + '\n' + (rc.stderr or '').strip()))
if fails:
    for t, msg in fails: print(f'FAIL TRACK {t}: {msg}')
    sys.exit(1)
d = json.load(open(os.path.join(R, 'data/design/v110_pack_86_lobby_psp_ensure/v110_pack_86_summary_v1.json')))
sf = d.get('safety_flags', {})
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','production_apply_executed','bulk_psp_apply','physical_normalization_executed_in_this_pack','destructive_migration','delete_of_real_psp','premium_grant','reward_live','progress_live','legacy_cleanup_executed','starter_heroes_grant','starter_flow_approved','copy_s1_to_s2','account_wide_player_level_as_final_server_level','account_wide_roster_as_final_server_roster','postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','user_heroes_creation_from_register'):
    assert sf.get(k) is False, f'safety {k} must be false'
es = d.get('explicit_statements', {})
for k in ('no_global_starter_user_heroes_from_register','new_server_starts_level_1','no_s1_to_s2_copy','reward_live_off','progress_live_off','legacy_cleanup_not_executed'):
    assert es.get(k) is True, f'explicit statement {k} must be true'
v = d.get('verdict','')
assert 'MEGA_RELEASE_ACCELERATION_86_LOBBY_UI_PSP_ENSURE_AND_REGISTRATION_STARTER_LEGACY_GUARD' in v
print(f'[v110 MEGA_RELEASE_ACCELERATION_86_LOBBY_UI_PSP_ENSURE_AND_REGISTRATION_STARTER_LEGACY_GUARD_ROLLUP] OK tracks={len(tracks)}/{len(tracks)} verdict={v}')
