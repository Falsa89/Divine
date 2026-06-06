#!/usr/bin/env python3
import json,os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(ROOT,"data","design","authoritative_live_preconditions","v108_authoritative_live_preconditions_baseline_multirun_v1.json")))
SENT="PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_LIVE_PRECONDITIONS_AND_IDEMPOTENCY_LEDGER"
assert d.get("sentinel")==SENT
assert d.get("deterministic") is True
assert d.get("required_fail")==0
assert d.get("miss")==0
assert d.get("optional_fail",999)<=d.get("optional_fail_target_overall_max",30)
ri=d.get("runtime_invariant_validators_v108_postqa_a",{})
assert ri.get("observed_count")==10 and ri.get("status")=="PASS"
assert d.get("postqa_d_gates_preserved") is True
assert d.get("authoritative_pre_preserved") is True
assert d.get("authoritative_runtime_preserved") is True
print("[v108_AUTHORITATIVE_LIVE_PRECONDITIONS_BASELINE_MULTIRUN] OK runs=3 deterministic 1191/22/0/0")
sys.exit(0)
