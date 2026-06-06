#!/usr/bin/env python3
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUNNER = os.path.join(ROOT, "backend", "scripts", "run_hero_skill_kit_validator_suite.py")
rt = open(RUNNER).read()
for v in ["validate_v108_postqa_invariant_suite_relocatable.py","validate_v108_postqa_invariant_preview_no_simulate.py","validate_v108_postqa_invariant_preview_no_rewards_affinity.py","validate_v108_postqa_invariant_story_no_qa_autoresolve_player_facing.py","validate_v108_postqa_invariant_lobby_no_fake_team_launch.py","validate_v108_postqa_invariant_lobby_launch_context_to_combat.py","validate_v108_postqa_invariant_no_generate_enemy_player_facing.py","validate_v108_postqa_invariant_no_bot_default_startup.py","validate_v108_postqa_invariant_mutation_endpoint_watchlist.py","validate_v108_postqa_invariant_server_scope_false_positive.py"]:
    assert v in rt, f"runtime invariant missing in runner: {v}"
for r in ["validate_mega_release_acceleration_61_v108_postqa_rollup.py","validate_mega_release_acceleration_62_v108_postqa_a2_rollup.py","validate_mega_release_acceleration_63_v108_postqa_b_rollup.py","validate_mega_release_acceleration_64_v108_postqa_c_rollup.py","validate_mega_release_acceleration_65_v108_postqa_d_rollup.py","validate_mega_release_acceleration_66_v108_authoritative_pre_rollup.py"]:
    assert r in rt, f"rollup missing in runner: {r}"
P = os.path.join(ROOT, "data", "design", "authoritative_runtime", "v108_authoritative_runtime_invariant_preservation_v1.json")
d = json.load(open(P))
chg = d.get("validator_count_change", {})
assert chg.get("deleted", 0) == 0
assert chg.get("silently_deleted", 0) == 0
assert chg.get("weakened", 0) == 0
print("[v108_AUTHORITATIVE_RUNTIME INVARIANT_PRESERVATION] OK runtime=10 rollups=6 deleted=0 weakened=0")
sys.exit(0)
