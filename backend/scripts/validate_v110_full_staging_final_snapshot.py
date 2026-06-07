#!/usr/bin/env python3
# Track I: snapshot finale dopo rollback.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_psp_full_staging/v110_full_staging_final_snapshot_v1.json")
d = json.load(open(F))
assert d.get("staging_psp_post_rollback") == 0
assert d.get("staging_user_heroes_with_server_id_post_rollback") == 0
assert d.get("read_only_for_source") is True
ck = d.get("staging_checksum_post_rollback", {})
for coll in ("users", "user_heroes", "player_server_profiles", "wallets"):
    cd = ck.get(coll)
    assert cd is not None and "sha256" in cd, coll
sf = d.get("safety_flags", {})
assert sf.get("db_write_to_production") is False
assert sf.get("fake_PASS") is False
print("[v110 FULL_STAGING_FINAL_SNAPSHOT] OK post-rollback signature restored")
