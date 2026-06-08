#!/usr/bin/env python3
# Pack 83 - ROLLUP.
import os, json, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend/scripts')
tracks = [
    'validate_v110_pack_83_baseline_verification.py',
    'validate_v110_pack_83_psp_namespace_audit.py',
    'validate_v110_pack_83_deterministic_normalization_mapping.py',
    'validate_v110_pack_83_production_dry_run_diff.py',
    'validate_v110_pack_83_backup_preflight_manifest.py',
    'validate_v110_pack_83_rollback_plan_and_script.py',
    'validate_v110_pack_83_future_execute_script_safety.py',
    'validate_v110_pack_83_approval_gate_matrix.py',
    'validate_v110_pack_83_server_lifecycle_preservation.py',
    'validate_v110_pack_83_runtime_smoke_read_only.py',
    'validate_v110_pack_83_zero_mutation_preservation.py',
    'validate_v110_pack_83_live_readiness_update.py',
    'validate_v110_pack_83_gate_invariant_preservation.py',
    'validate_v110_pack_83_final_3run_suite.py',
]
fails = []
for t in tracks:
    p = os.path.join(SCRIPTS, t)
    rc = subprocess.run([sys.executable, p], capture_output=True, text=True, timeout=60)
    if rc.returncode != 0:
        fails.append((t, rc.stdout.strip() + '\n' + rc.stderr.strip()))
if fails:
    for t, msg in fails: print(f'FAIL TRACK {t}: {msg}')
    sys.exit(1)
S = os.path.join(R, 'data/design/v110_psp_normalization_preflight/v110_psp_normalization_preflight_summary_v1.json')
d = json.load(open(S))
sf = d.get('safety_flags', {})
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','production_apply_executed','production_db_writes','reward_live','progress_live','legacy_cleanup_executed','physical_psp_normalization_executed','psp_apply_executed','user_heroes_mutation','player_level_mutation','copy_s1_to_s2','new_server_psp_creation','postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','approval_flags_changed_to_yes_for_pack_83'):
    assert sf.get(k) is False, f'safety flag {k} must be false'
v = d.get('verdict','')
assert 'MEGA_RELEASE_ACCELERATION_83_PSP_PHYSICAL_NORMALIZATION_PREFLIGHT' in v
print(f'[v110 MEGA_RELEASE_ACCELERATION_83_PSP_PHYSICAL_NORMALIZATION_PREFLIGHT_ROLLUP] OK tracks=14/14 verdict={v}')
