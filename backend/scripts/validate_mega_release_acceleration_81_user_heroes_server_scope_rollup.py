#!/usr/bin/env python3
# Pack 81 - ROLLUP: aggrega tutti i 14 track validator (Track 16 - validators + runner integration).
import os, json, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend/scripts')
tracks = [
    'validate_v110_pack_81_baseline_multirun.py',
    'validate_v110_pack_81_canonical_sot_consolidation.py',
    'validate_v110_pack_81_user_heroes_route_map.py',
    'validate_v110_pack_81_user_heroes_server_id_psp_promotion.py',
    'validate_v110_pack_81_frontend_roster_consumers_update.py',
    'validate_v110_pack_81_inventory_loader_scoping.py',
    'validate_v110_pack_81_currencies_loader_split.py',
    'validate_v110_pack_81_story_progress_loader_scoping.py',
    'validate_v110_pack_81_equipment_refs_build_consistency.py',
    'validate_v110_pack_81_user_heroes_runtime_smoke.py',
    'validate_v110_pack_81_zero_mutation_preservation.py',
    'validate_v110_pack_81_live_readiness_update.py',
    'validate_v110_pack_81_md5_rebase.py',
    'validate_v110_pack_81_gate_invariant_preservation.py',
    'validate_v110_pack_81_final_multirun_suite.py',
]
fails = []
for t in tracks:
    p = os.path.join(SCRIPTS, t)
    rc = subprocess.run([sys.executable, p], capture_output=True, text=True, timeout=45)
    if rc.returncode != 0:
        fails.append((t, rc.stdout.strip() + '\n' + rc.stderr.strip()))
if fails:
    for t, msg in fails:
        print(f'FAIL TRACK {t}: {msg}')
    sys.exit(1)
S = os.path.join(R, 'data/design/v110_pack_81_user_heroes_server_scope/v110_pack_81_user_heroes_server_scope_summary_v1.json')
d = json.load(open(S))
sf = d.get('safety_flags', {})
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','production_apply_executed','production_db_writes','reward_live','progress_live','legacy_cleanup_executed','false_filter_applied_true','user_heroes_treated_as_account_wide_final_source','global_roster_fallback_as_final_player_facing_source','hardcoded_s1_silent_player_facing_fallback','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','approval_flags_changed_to_yes_for_pack_81','postqa_d_gates_unlocked'):
    assert sf.get(k) is False, f'safety flag {k} must be false'
v = d.get('verdict','')
assert 'MEGA_RELEASE_ACCELERATION_81_USER_HEROES_SERVER_SCOPE_AND_CORE_LOADERS_PROMOTION' in v, f'verdict missing pack name: {v}'
print(f'[v110 MEGA_RELEASE_ACCELERATION_81_USER_HEROES_SERVER_SCOPE_ROLLUP] OK tracks=15/15 verdict={v}')
