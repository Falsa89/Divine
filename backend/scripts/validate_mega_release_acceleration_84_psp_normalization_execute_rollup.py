#!/usr/bin/env python3
import os, json, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend/scripts')
tracks = [
    'validate_v110_pack_84_baseline_verification.py',
    'validate_v110_pack_84_approval_proof.py',
    'validate_v110_pack_84_pin_verification.py',
    'validate_v110_pack_84_pre_write_snapshot.py',
    'validate_v110_pack_84_backup_confirmation.py',
    'validate_v110_pack_84_real_execute_script_realization.py',
    'validate_v110_pack_84_execute_result.py',
    'validate_v110_pack_84_idempotency_rerun.py',
    'validate_v110_pack_84_post_namespace_audit.py',
    'validate_v110_pack_84_runtime_smoke.py',
    'validate_v110_pack_84_server_lifecycle_preservation.py',
    'validate_v110_pack_84_rollback_readiness.py',
    'validate_v110_pack_84_zero_mutation_and_live_readiness.py',
    'validate_v110_pack_84_final_3run_and_gate_preservation.py',
]
fails = []
for t in tracks:
    rc = subprocess.run([sys.executable, os.path.join(SCRIPTS, t)], capture_output=True, text=True, timeout=60)
    if rc.returncode != 0:
        fails.append((t, rc.stdout.strip() + '\n' + rc.stderr.strip()))
if fails:
    for t, msg in fails: print(f'FAIL TRACK {t}: {msg}')
    sys.exit(1)
d = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_execute/v110_psp_normalization_execute_summary_v1.json')))
sf = d.get('safety_flags', {})
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','production_apply_executed','destructive_migration_beyond_user_id_normalization','reward_live','progress_live','legacy_cleanup_executed','psp_apply_executed','user_heroes_mutation','player_level_mutation','copy_s1_to_s2','new_server_psp_creation','postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','writes_outside_psp_user_id_normalization'):
    assert sf.get(k) is False, f'safety flag {k} must be false'
assert sf.get('physical_psp_normalization_executed') is True
assert sf.get('physical_psp_normalization_authorized') is True
v = d.get('verdict','')
assert 'MEGA_RELEASE_ACCELERATION_84_PSP_USER_ID_PHYSICAL_NORMALIZATION_EXECUTE' in v
print(f'[v110 MEGA_RELEASE_ACCELERATION_84_PSP_NORMALIZATION_EXECUTE_ROLLUP] OK tracks=14/14 verdict={v}')
