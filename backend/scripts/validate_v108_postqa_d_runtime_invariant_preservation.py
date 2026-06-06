#!/usr/bin/env python3
"""v108_POSTQA_D - Track G runtime invariant preservation validator.
Verifica che i 10 runtime invariant validators v108_POSTQA_A + i 4 rollup
POSTQA siano referenziati nel runner e che nessuno sia stato silenziosamente cancellato.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUNNER = os.path.join(ROOT, "backend", "scripts", "run_hero_skill_kit_validator_suite.py")
rt = open(RUNNER).read()

REQUIRED_RUNTIME = [
    "validate_v108_postqa_invariant_suite_relocatable.py",
    "validate_v108_postqa_invariant_preview_no_simulate.py",
    "validate_v108_postqa_invariant_preview_no_rewards_affinity.py",
    "validate_v108_postqa_invariant_story_no_qa_autoresolve_player_facing.py",
    "validate_v108_postqa_invariant_lobby_no_fake_team_launch.py",
    "validate_v108_postqa_invariant_lobby_launch_context_to_combat.py",
    "validate_v108_postqa_invariant_no_generate_enemy_player_facing.py",
    "validate_v108_postqa_invariant_no_bot_default_startup.py",
    "validate_v108_postqa_invariant_mutation_endpoint_watchlist.py",
    "validate_v108_postqa_invariant_server_scope_false_positive.py",
]
missing = [v for v in REQUIRED_RUNTIME if v not in rt]
assert not missing, f"runtime invariant validators missing in runner: {missing}"

REQUIRED_ROLLUPS = [
    "validate_mega_release_acceleration_61_v108_postqa_rollup.py",
    "validate_mega_release_acceleration_62_v108_postqa_a2_rollup.py",
    "validate_mega_release_acceleration_63_v108_postqa_b_rollup.py",
    "validate_mega_release_acceleration_64_v108_postqa_c_rollup.py",
]
rmissing = [r for r in REQUIRED_ROLLUPS if r not in rt]
assert not rmissing, f"postqa rollups missing in runner: {rmissing}"

P = os.path.join(ROOT, "data", "design", "postqa", "v108_postqa_d_runtime_invariant_preservation_v1.json")
d = json.load(open(P))
chg = d.get("validator_count_change", {})
assert chg.get("deleted", 0) == 0
assert chg.get("silently_deleted", 0) == 0
assert chg.get("weakened", 0) == 0
print("[v108_POSTQA_D RUNTIME_INVARIANT_PRESERVATION] OK runtime=10 rollups=4 deleted=0 weakened=0")
sys.exit(0)
