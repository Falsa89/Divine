#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_pre_smoke_db_snapshot_v1.json")
assert os.path.isfile(P)
d = json.load(open(P))
assert d.get("snapshot_kind") == "pre_smoke"
assert d.get("read_only") is True
assert d.get("db_writes") == 0
counts = d.get("counts", {})
for k in ("users", "player_server_profiles", "user_heroes", "team_formation", "user_inventory", "user_equipment", "bots", "migration_logs"):
    assert k in counts, f"missing count {k}"
assert d.get("safety_flags", {}).get("db_write") is False
print(f"[v110 PRE_SMOKE_DB_SNAPSHOT] OK read_only=true mongo_reachable={d.get('mongo_reachable')}")
