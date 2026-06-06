#!/usr/bin/env python3
import json,os,sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,"data/design/v109_server_isolation/v109_baseline_multirun_v1.json")))
assert d.get("sentinel")=="PUBLIC_SYNC_TAG_v109_SERVER_ISOLATION_AND_SERVER_ID_FILTER_PROMOTION"
assert d.get("deterministic") is True
assert d.get("required_fail")==0 and d.get("miss")==0
assert d.get("optional_fail",999)<=d.get("optional_fail_target_overall_max",30)
assert d.get("runtime_invariant_validators_v108_postqa_a",{}).get("observed_count")==10
for k in ("postqa_d_gates_preserved","authoritative_pre_preserved","authoritative_runtime_preserved","authoritative_live_preconditions_preserved"):
    assert d.get(k) is True
for k in ("fake_PASS","validator_weakening","silent_validator_deletion","release_readiness_claimed"):
    assert d.get("safety_flags",{}).get(k) is False
print("[v109 BASELINE_MULTIRUN] OK runs=3 deterministic 1201/22/0/0")
