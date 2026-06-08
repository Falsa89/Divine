#!/usr/bin/env python3
# Pack 82 - ROLLUP: aggrega tutti i 11 track validator.
import os, json, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend/scripts')
tracks = [
    'validate_v110_pack_82_baseline_multirun.py',
    'validate_v110_pack_82_dual_read_psp_lookup.py',
    'validate_v110_pack_82_server_player_progress_sot.py',
    'validate_v110_pack_82_psp_namespace_audit.py',
    'validate_v110_pack_82_runtime_smoke_real_migrated_user.py',
    'validate_v110_pack_82_fresh_start_invariant.py',
    'validate_v110_pack_82_zero_db_writes.py',
    'validate_v110_pack_82_live_readiness_update.py',
    'validate_v110_pack_82_md5_rebase.py',
    'validate_v110_pack_82_gate_invariant_preservation.py',
    'validate_v110_pack_82_final_3run_suite.py',
]
fails = []
for t in tracks:
    p = os.path.join(SCRIPTS, t)
    rc = subprocess.run([sys.executable, p], capture_output=True, text=True, timeout=60)
    if rc.returncode != 0:
        fails.append((t, rc.stdout.strip() + '\n' + rc.stderr.strip()))
if fails:
    for t, msg in fails:
        print(f'FAIL TRACK {t}: {msg}')
    sys.exit(1)
S = os.path.join(R, 'data/design/v110_pack_82_psp_dual_read_compat/v110_pack_82_psp_dual_read_compat_summary_v1.json')
d = json.load(open(S))
sf = d.get('safety_flags', {})
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','production_apply_executed','production_db_writes','reward_live','progress_live','legacy_cleanup_executed','physical_psp_normalization_executed','copy_s1_to_s2_roster','copy_s1_to_s2_level','copy_s1_to_s2_progress','copy_s1_to_s2_team','account_wide_player_level_as_final_server_level','account_wide_roster_as_final_server_roster','false_filter_applied_true','hardcoded_s1_silent_player_facing_fallback','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','approval_flags_changed_to_yes_for_pack_82','postqa_d_gates_unlocked'):
    assert sf.get(k) is False, f'safety flag {k} must be false'
v = d.get('verdict','')
assert 'MEGA_RELEASE_ACCELERATION_82_PSP_USER_ID_DUAL_READ_COMPAT_AND_SERVER_PLAYER_PROGRESS_SOT' in v, f'verdict missing pack name: {v}'
print(f'[v110 MEGA_RELEASE_ACCELERATION_82_PSP_DUAL_READ_COMPAT_ROLLUP] OK tracks=11/11 verdict={v}')
