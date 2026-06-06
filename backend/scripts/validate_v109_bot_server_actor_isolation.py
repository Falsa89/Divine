#!/usr/bin/env python3
import json,os,sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,"data/design/v109_server_isolation/v109_bot_server_actor_isolation_v1.json")))
assert d.get("bots_default_disabled") is True
assert d.get("bots_server_scope_required") is True
assert d.get("bots_runtime_promoted") is False
assert d.get("live_ready") is False
print("[v109 BOT_SERVER_ACTOR_ISOLATION] OK bots_default_disabled=true")
