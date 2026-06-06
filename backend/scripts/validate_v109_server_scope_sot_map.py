#!/usr/bin/env python3
import json,os,sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,"data/design/v109_server_isolation/v109_server_scope_sot_map_v1.json")))
assert d.get("sentinel")=="PUBLIC_SYNC_TAG_v109_SERVER_ISOLATION_AND_SERVER_ID_FILTER_PROMOTION"
ents=d.get("entities",[])
assert len(ents)>=12
for e in ents:
    assert e.get("current_scope") and e.get("target_scope")
assert d.get("migration_executed_in_this_pack") is False
assert d.get("destructive_migration") is False
print(f"[v109 SERVER_SCOPE_SOT_MAP] OK entities={len(ents)} migration_executed=false")
