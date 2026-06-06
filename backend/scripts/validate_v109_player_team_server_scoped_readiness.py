#!/usr/bin/env python3
import json,os,sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,"data/design/v109_server_isolation/v109_player_team_server_scoped_readiness_v1.json")))
assert d.get("team_currently_server_scoped") is False
assert d.get("team_account_wide") is True
assert d.get("team_6_slot_supported") is True
assert d.get("team_fake_markers_blocked") is True
assert d.get("live_ready") is False
print("[v109 PLAYER_TEAM_SERVER_SCOPED_READINESS] OK live_ready=false honest")
