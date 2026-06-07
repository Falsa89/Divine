#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_execute/v110_final_staging_snapshot_v1.json")))
assert d.get("staging_psp_post_rollback") == 0, "after rollback, staging PSP must be 0"
assert d.get("staging_user_heroes_with_server_id_post_rollback") == 0
assert d.get("read_only_for_source") is True
for k in ("db_write_to_production", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 FINAL_STAGING_SNAPSHOT] OK staging_psp_post_rollback=0 user_heroes_with_server_id_post_rollback=0")
