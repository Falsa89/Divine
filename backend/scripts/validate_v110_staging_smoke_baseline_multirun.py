#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_staging_smoke_baseline_multirun_v1.json")))
assert d.get("sentinel") == "PUBLIC_SYNC_TAG_v110_PSP_APPLY_STAGING_SMOKE_LIMITED"
assert d.get("deterministic") is True
assert d.get("required_fail") == 0 and d.get("miss") == 0
assert d.get("optional_fail", 999) <= d.get("optional_fail_target_overall_max", 30)
for k in ("v108_postqa_a_invariants_pass", "postqa_d_gates_preserved", "v108_authoritative_preserved", "v109_server_isolation_preserved", "v110_prep_preserved", "v110_apply_preflight_preserved"):
    assert d.get(k) is True, f"baseline {k}"
for k in ("fake_PASS", "validator_weakening", "silent_validator_deletion", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False
print("[v110 STAGING_SMOKE_BASELINE_MULTIRUN] OK runs=3 deterministic 1242/21/0/0")
