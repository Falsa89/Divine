#!/usr/bin/env python3
import json,os,sys,importlib.util
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(ROOT,"data","design","authoritative_live_preconditions","v108_authoritative_live_reward_progress_blocker_result_v1.json")))
for c in ("AUTHORITATIVE_LIVE_REWARD_PRECONDITIONS_NOT_MET","AUTHORITATIVE_LIVE_PROGRESS_PRECONDITIONS_NOT_MET","AUTHORITATIVE_LIVE_IDEMPOTENCY_REQUIRED","AUTHORITATIVE_LIVE_SERVER_FILTER_REQUIRED","AUTHORITATIVE_LIVE_ROLLBACK_REQUIRED"):
    assert c in d.get("block_codes_defined",[])
ff=d.get("env_flags_default_off",{})
for k in ("REWARD_LIVE_ENABLED","PROGRESS_LIVE_ENABLED","BATTLE_LAUNCH_AUTHORITATIVE_ENABLED"):
    assert ff.get(k) is False
assert d.get("live_enabled_in_this_pack") is False
# verify adapter raises HTTPException with each code
A=os.path.join(ROOT,"backend","utils","authoritative_idempotency_ledger.py")
spec=importlib.util.spec_from_file_location("adp",A); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from fastapi import HTTPException
cases=[
    ({},"AUTHORITATIVE_LIVE_REWARD_PRECONDITIONS_NOT_MET"),
    ({"reward_preconditions_pass":True},"AUTHORITATIVE_LIVE_PROGRESS_PRECONDITIONS_NOT_MET"),
    ({"reward_preconditions_pass":True,"progress_preconditions_pass":True},"AUTHORITATIVE_LIVE_IDEMPOTENCY_REQUIRED"),
    ({"reward_preconditions_pass":True,"progress_preconditions_pass":True,"idempotency_present":True},"AUTHORITATIVE_LIVE_SERVER_FILTER_REQUIRED"),
    ({"reward_preconditions_pass":True,"progress_preconditions_pass":True,"idempotency_present":True,"server_filter_applied":True},"AUTHORITATIVE_LIVE_ROLLBACK_REQUIRED"),
]
for precond, expected in cases:
    try:
        m.check_live_preconditions(precond)
        raise AssertionError(f"did not raise for {precond}")
    except HTTPException as e:
        assert e.detail.get("code")==expected, f"got {e.detail.get('code')}, expected {expected}"
print("[v108_AUTHORITATIVE_LIVE_REWARD_PROGRESS_BLOCKER] OK 5_codes blocked all_flags_off live_enabled=false")
sys.exit(0)
