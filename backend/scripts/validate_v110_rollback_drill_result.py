#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_rollback_drill_result_v1.json")))
assert d.get("rollback_drill_executed") is False, "rollback drill must NOT be claimed executed if it wasn't"
assert d.get("production_rollback_executed") is False
assert d.get("db_writes") == 0
assert d.get("rollback_dry_run_executed") in (True, False)
for k in ("rollback_drill_executed", "db_write", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 ROLLBACK_DRILL_RESULT] OK status={d.get('status')} drill_executed=false dry_run_executed={d.get('rollback_dry_run_executed')}")
