#!/usr/bin/env python3
import json,os,sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN=open(os.path.join(R,"backend/scripts/run_hero_skill_kit_validator_suite.py")).read()
for v in ["validate_v108_postqa_invariant_suite_relocatable.py","validate_v108_postqa_invariant_preview_no_simulate.py","validate_v108_postqa_invariant_preview_no_rewards_affinity.py","validate_v108_postqa_invariant_story_no_qa_autoresolve_player_facing.py","validate_v108_postqa_invariant_lobby_no_fake_team_launch.py","validate_v108_postqa_invariant_lobby_launch_context_to_combat.py","validate_v108_postqa_invariant_no_generate_enemy_player_facing.py","validate_v108_postqa_invariant_no_bot_default_startup.py","validate_v108_postqa_invariant_mutation_endpoint_watchlist.py","validate_v108_postqa_invariant_server_scope_false_positive.py"]:
    assert v in RUN, f"runtime invariant missing: {v}"
for r in ["validate_mega_release_acceleration_61_v108_postqa_rollup.py","validate_mega_release_acceleration_62_v108_postqa_a2_rollup.py","validate_mega_release_acceleration_63_v108_postqa_b_rollup.py","validate_mega_release_acceleration_64_v108_postqa_c_rollup.py","validate_mega_release_acceleration_65_v108_postqa_d_rollup.py","validate_mega_release_acceleration_66_v108_authoritative_pre_rollup.py","validate_mega_release_acceleration_67_v108_authoritative_runtime_rollup.py","validate_mega_release_acceleration_68_v108_authoritative_live_preconditions_rollup.py"]:
    assert r in RUN, f"rollup missing: {r}"
d=json.load(open(os.path.join(R,"data/design/v109_server_isolation/v109_runtime_invariant_preservation_v1.json")))
chg=d.get("validator_count_change",{})
assert chg.get("deleted",0)==0 and chg.get("silently_deleted",0)==0 and chg.get("weakened",0)==0
print("[v109 RUNTIME_INVARIANT_PRESERVATION] OK runtime=10 rollups=8 deleted=0 weakened=0")
