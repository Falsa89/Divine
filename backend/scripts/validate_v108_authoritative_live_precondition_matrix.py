#!/usr/bin/env python3
import json,os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D=lambda n:json.load(open(os.path.join(ROOT,"data","design","authoritative_live_preconditions",n)))
SENT="PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_LIVE_PRECONDITIONS_AND_IDEMPOTENCY_LEDGER"
d=D("v108_authoritative_live_precondition_matrix_v1.json")
assert d.get("sentinel")==SENT
p=d.get("preconditions",[])
assert len(p)>=15, f"need >=15 preconditions, got {len(p)}"
ALLOWED={"PASS","BLOCKED","DESIGN_ONLY","NOT_READY"}
for pr in p:
    assert pr.get("current_status") in ALLOWED, f"bad status: {pr.get('current_status')}"
    assert pr.get("enforcement_location")
    assert pr.get("validator")
    assert pr.get("target_pack")
assert d.get("live_overall_ready") is False
for k in ("fake_PASS","validator_weakening","release_readiness_claimed","reward_live_enabled","progress_live_enabled"):
    assert d.get("safety_flags",{}).get(k) is False
print("[v108_AUTHORITATIVE_LIVE_PRECONDITION_MATRIX] OK preconditions="+str(len(p))+" live_overall_ready=false")
sys.exit(0)
