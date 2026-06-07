#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_limited_psp_apply_result_v1.json")))
assert d.get("limited_apply_executed") is False
assert d.get("production_apply_executed") is False, "production apply MUST be false"
assert d.get("db_writes") == 0
assert d.get("psp_inserts_in_this_pack") == 0
assert d.get("user_heroes_updates_in_this_pack") == 0
assert d.get("status")
for k in ("limited_apply_executed", "production_apply_executed", "db_write", "destructive_migration", "premium_grant", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 LIMITED_PSP_APPLY_RESULT] OK status={d['status']} limited_apply_executed=false production_apply_executed=false")
