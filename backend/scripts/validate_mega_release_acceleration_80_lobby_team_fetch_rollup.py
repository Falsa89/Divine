#!/usr/bin/env python3
# Pack 80 — ROLLUP: aggrega tutti i 12 track validator.
import os, json, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend/scripts')
tracks = [
    'validate_v110_lobby_team_fetch_baseline_multirun.py',
    'validate_v110_lobby_team_fetch_route_usage_map.py',
    'validate_v110_pre_battle_lobby_team_fetch_implementation.py',
    'validate_v110_team_formation_route_hardening.py',
    'validate_v110_real_team_source_runtime_smoke.py',
    'validate_v110_core_loader_promotion_batch.py',
    'validate_v110_story_lobby_combat_payload_update.py',
    'validate_v110_lobby_team_fetch_zero_mutation_preservation.py',
    'validate_v110_lobby_team_fetch_live_readiness_update.py',
    'validate_v110_lobby_team_fetch_md5_rebase.py',
    'validate_v110_lobby_team_fetch_gate_invariant_preservation.py',
    'validate_v110_lobby_team_fetch_final_multirun_suite.py',
]
fails = []
for t in tracks:
    p = os.path.join(SCRIPTS, t)
    rc = subprocess.run([sys.executable, p], capture_output=True, text=True, timeout=30)
    if rc.returncode != 0:
        fails.append((t, rc.stdout.strip() + '\n' + rc.stderr.strip()))
if fails:
    for t, msg in fails:
        print(f'FAIL TRACK {t}: {msg}')
    sys.exit(1)
S = os.path.join(R, 'data/design/v110_pack_80_lobby_fetch/v110_pack_80_lobby_fetch_summary_v1.json')
d = json.load(open(S))
sf = d.get('safety_flags', {})
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','production_apply_executed','production_db_writes','reward_live','progress_live','legacy_cleanup_executed','false_filter_applied_true','fake_team_as_real','fake_enemy_as_authored','3_slot_placeholder_player_facing','hardcoded_s1_silent_player_facing_fallback','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','approval_flags_changed_to_yes_for_pack_80','postqa_d_gates_unlocked'):
    assert sf.get(k) is False, f'safety flag {k} must be false'
v = d.get('verdict','')
assert 'MEGA_RELEASE_ACCELERATION_80_LOBBY_TEAM_FETCH_AND_CORE_LOADER_PROMOTION' in v, f'verdict missing pack name: {v}'
print(f'[v110 MEGA_RELEASE_ACCELERATION_80_LOBBY_TEAM_FETCH_ROLLUP] OK tracks=12/12 verdict={v}')
