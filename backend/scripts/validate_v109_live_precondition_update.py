#!/usr/bin/env python3
import json,os,sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,"data/design/v109_server_isolation/v109_live_precondition_update_v1.json")))
still_blocked=d.get("preconditions_still_blocked_after_v109",[])
for b in ("server_id_filter_applied","real_player_team_source","psp_migration_readiness","legacy_cleanup_readiness"):
    assert b in still_blocked, f"missing still_blocked precondition: {b}"
assert d.get("live_overall_ready") is False
assert d.get("preconditions_now_pass_after_v109")==[]
print("[v109 LIVE_PRECONDITION_UPDATE] OK live_overall_ready=false no_false_promotions")
