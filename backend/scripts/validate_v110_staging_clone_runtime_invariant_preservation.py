#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN = open(os.path.join(R, "backend/scripts/run_hero_skill_kit_validator_suite.py")).read()
for v in ["validate_v108_postqa_invariant_suite_relocatable.py", "validate_v108_postqa_invariant_no_bot_default_startup.py", "validate_v108_postqa_invariant_mutation_endpoint_watchlist.py"]:
    assert v in RUN, f"runtime invariant missing: {v}"
for r in ["validate_mega_release_acceleration_69_v109_server_isolation_rollup.py", "validate_mega_release_acceleration_70_v110_psp_prep_rollup.py", "validate_mega_release_acceleration_71_v110_apply_preflight_rollup.py", "validate_mega_release_acceleration_72_v110_psp_apply_staging_smoke_rollup.py"]:
    assert r in RUN, f"rollup missing: {r}"
d = json.load(open(os.path.join(R, "data/design/v110_staging_clone/v110_staging_clone_runtime_invariant_preservation_v1.json")))
chg = d.get("validator_count_change", {})
assert chg.get("deleted", 0) == 0 and chg.get("silently_deleted", 0) == 0 and chg.get("weakened", 0) == 0
assert d.get("preserved_runtime_invariant_validators_v108_postqa_a") == 10
assert len(d.get("preserved_rollups", [])) == 12
print("[v110 STAGING_CLONE_RUNTIME_INVARIANT_PRESERVATION] OK runtime=10 rollups=12 deleted=0 weakened=0")
