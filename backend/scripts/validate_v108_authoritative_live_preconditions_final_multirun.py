#!/usr/bin/env python3
import json,os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P=os.path.join(ROOT,"data","design","authoritative_live_preconditions","v108_authoritative_live_preconditions_final_multirun_v1.json")
assert os.path.isfile(P), "final multirun result not generated yet; run rollup standalone first"
d=json.load(open(P))
SENT="PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_LIVE_PRECONDITIONS_AND_IDEMPOTENCY_LEDGER"
assert d.get("sentinel")==SENT
assert d.get("deterministic") is True
assert d.get("required_fail_final")==0
assert d.get("miss_final")==0
opt=d.get("optional_fail_final",999); tmax=d.get("optional_fail_target_max",30)
assert opt<=tmax
print(f"[v108_AUTHORITATIVE_LIVE_PRECONDITIONS_FINAL_MULTIRUN] OK required=0 miss=0 optional={opt} target_max={tmax}")
sys.exit(0)
