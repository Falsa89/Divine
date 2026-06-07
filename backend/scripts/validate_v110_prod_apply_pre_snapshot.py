#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_apply_execute/v110_prod_apply_pre_snapshot_v1.json")
d = json.load(open(F))
assert d.get("target_db") == "divine_waifus"
assert d.get("classification") == "PRODUCTION_LIKE_LOCAL_CONTAINER"
assert d.get("staging_clone_marker_on_target") is False
snap = d.get("snapshot_pre_apply", {})
assert isinstance(snap.get("users"), int) and snap.get("users") >= 1
assert isinstance(snap.get("player_server_profiles"), int)
assert isinstance(snap.get("user_heroes"), int)
sf = d.get("safety_flags", {})
assert sf.get("production_apply_executed") is False
assert sf.get("db_write") is False
assert sf.get("fake_PASS") is False
print(f"[v110 PROD_APPLY_PRE_SNAPSHOT] OK users={snap.get('users')} psp_pre={snap.get('player_server_profiles')}")
