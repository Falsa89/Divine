#!/usr/bin/env python3
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "authoritative_runtime", "v108_authoritative_runtime_baseline_multirun_v1.json")
d = json.load(open(P))
SENT = "PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_BATTLE_RUNTIME_STAGING_NO_REWARD_LIVE"
assert d.get("sentinel") == SENT
assert d.get("deterministic") is True
assert d.get("required_fail") == 0
assert d.get("miss") == 0
assert d.get("optional_fail", 999) <= d.get("optional_fail_target_overall_max", 30)
ri = d.get("runtime_invariant_validators_v108_postqa_a", {})
assert ri.get("observed_count") == 10 and ri.get("status") == "PASS"
assert d.get("postqa_d_gates_preserved") is True
assert d.get("authoritative_pre_preserved") is True
for k in ("fake_PASS","validator_weakening","silent_validator_deletion","release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False
print("[v108_AUTHORITATIVE_RUNTIME BASELINE_MULTIRUN] OK runs=3 deterministic required=0 miss=0 optional=22")
sys.exit(0)
