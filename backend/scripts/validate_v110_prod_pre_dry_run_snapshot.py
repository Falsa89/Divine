#!/usr/bin/env python3
# Pack 76 Track C: snapshot pre dry-run su produzione (read-only).
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_preflight/v110_prod_pre_dry_run_snapshot_v1.json")
d = json.load(open(F))
assert d.get("target_db") == "divine_waifus"
assert d.get("source_db_writes_during_snapshot") == 0
assert d.get("production_db_writes_during_snapshot") == 0
snap = d.get("snapshot", {})
ck = d.get("checksum", {})
for k in ("users", "user_heroes", "team_formation", "user_equipment",
          "player_server_profiles", "wallets"):
    assert k in snap, k
    assert ck.get(k, {}).get("sha256") and len(ck[k]["sha256"]) == 64, k
sf = d.get("safety_flags", {})
assert sf.get("db_write") is False
assert sf.get("destructive") is False
assert sf.get("fake_PASS") is False
print(f"[v110 PROD_PRE_DRY_RUN_SNAPSHOT] OK users={snap.get('users')} psp={snap.get('player_server_profiles')}")
