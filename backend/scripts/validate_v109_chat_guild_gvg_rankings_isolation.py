#!/usr/bin/env python3
import json,os,sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,"data/design/v109_server_isolation/v109_chat_guild_gvg_rankings_isolation_v1.json")))
sys_=d.get("systems",[])
assert len(sys_)>=5
for s in sys_:
    assert s.get("contract_server_scope_required") is True
    assert s.get("live_ready") is False
assert d.get("isolation_live_ready") is False
assert d.get("isolation_live_claim") is False
print(f"[v109 CHAT_GUILD_GVG_RANKINGS_ISOLATION] OK systems={len(sys_)} live_ready=false")
