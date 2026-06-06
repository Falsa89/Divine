#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
s = json.load(open(os.path.join(R, "data/design/v110_psp_migration/v110_player_server_profiles_schema_v1.json")))
p = json.load(open(os.path.join(R, "data/design/v110_psp_migration/v110_psp_index_plan_v1.json")))
assert s.get("collection_name") == "player_server_profiles"
assert s.get("collection_created_in_this_pack") is False
assert s.get("primary_key") == ["user_id", "server_id"]
assert isinstance(s.get("fields"), list) and len(s["fields"]) >= 10
assert p.get("indexes_created_in_this_pack") is False
assert isinstance(p.get("indexes_planned"), list) and len(p["indexes_planned"]) >= 3
for idx in p["indexes_planned"]:
    assert idx.get("name") and idx.get("keys")
for k in ("index_created_in_this_pack", "db_write", "fake_PASS"):
    assert p.get("safety_flags", {}).get(k) is False, f"index safety {k}"
print(f"[v110 PSP_SCHEMA_AND_INDEX_PLAN] OK fields={len(s['fields'])} indexes_planned={len(p['indexes_planned'])}")
