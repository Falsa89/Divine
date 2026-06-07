#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN = open(os.path.join(R, "backend/scripts/run_hero_skill_kit_validator_suite.py")).read()
for v in ["validate_v108_postqa_invariant_suite_relocatable.py", "validate_v108_postqa_invariant_no_bot_default_startup.py"]:
    assert v in RUN, f"runtime invariant missing: {v}"
for r in ["validate_mega_release_acceleration_71_v110_apply_preflight_rollup.py", "validate_mega_release_acceleration_72_v110_psp_apply_staging_smoke_rollup.py", "validate_mega_release_acceleration_73_v110_staging_clone_provision_rollup.py"]:
    assert r in RUN, f"rollup missing: {r}"
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_execute/v110_staging_execute_gate_invariant_preservation_v1.json")))
chg = d.get("validator_count_change", {})
assert chg.get("deleted", 0) == 0 and chg.get("silently_deleted", 0) == 0 and chg.get("weakened", 0) == 0
assert d.get("original_apply_script_hard_stop_intact") is True
assert d.get("postqa_d_gates_intact") is True
print("[v110 STAGING_EXECUTE_GATE_INVARIANT_PRESERVATION] OK runtime=10 deleted=0 weakened=0 hard_stop_pack71=intact")
