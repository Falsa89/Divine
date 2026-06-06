#!/usr/bin/env python3
import json,os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(ROOT,"data","design","authoritative_live_preconditions","v108_authoritative_rollback_plan_v1.json")))
assert len(d.get("backup_collections_required",[]))>=6
assert len(d.get("kill_flags",[]))>=4
for f in d.get("kill_flags",[]):
    assert f.get("flip_to") is False
assert d.get("executed_in_this_pack") is False
assert d.get("db_writes_in_this_pack")==0
assert d.get("ledger_replay_handling")
assert d.get("partial_reward_write_rollback")
assert d.get("progress_rollback")
assert d.get("db_snapshot_plan")
assert len(d.get("smoke_test_plan",[]))>=3
assert len(d.get("abort_conditions",[]))>=4
for k in ("rollback_executed","db_writes","fake_PASS","validator_weakening","release_readiness_claimed"):
    assert d.get("safety_flags",{}).get(k) is False
DOC=os.path.join(ROOT,"docs","divine","108_AUTHORITATIVE_ROLLBACK_PLAN.md")
assert os.path.isfile(DOC)
print("[v108_AUTHORITATIVE_ROLLBACK_PLAN] OK backups>=6 kill_flags>=4 executed=false")
sys.exit(0)
