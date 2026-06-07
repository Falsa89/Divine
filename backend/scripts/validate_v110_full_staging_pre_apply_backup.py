#!/usr/bin/env python3
# Track C: backup/snapshot pre-apply su clone.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_psp_full_staging/v110_full_staging_pre_apply_backup_v1.json")
d = json.load(open(F))
assert d.get("target_db") == "divine_waifus_staging_clone"
assert d.get("backup_present") is True
assert d.get("staging_pre_apply_snapshot")
assert d.get("staging_pre_apply_checksum")
assert d.get("source_pre_apply_snapshot")
ck = d.get("staging_pre_apply_checksum", {})
for coll in ("users", "user_heroes", "player_server_profiles", "wallets"):
    cd = ck.get(coll)
    assert cd is not None and "sha256" in cd and len(cd["sha256"]) == 64, coll
sf = d.get("safety_flags", {})
assert sf.get("db_write") is False
assert sf.get("destructive") is False
assert sf.get("fake_PASS") is False
print("[v110 FULL_STAGING_PRE_APPLY_BACKUP] OK snapshot+checksum")
