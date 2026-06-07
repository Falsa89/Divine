#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_execute/v110_rollback_drill_v1.json")))
assert d.get("rollback_drill_executed") is True
assert d.get("rollback_dry_run_only") is False
assert d.get("production_rollback_executed") is False, "production rollback MUST be false"
assert d.get("target_db") == "divine_waifus_staging_clone"
assert d.get("psp_deleted", 0) > 0, "rollback drill should have deleted at least one PSP"
assert d.get("rollback_restored_pre_apply_signature") is True, "rollback MUST restore pre-apply signature"
for k in ("db_write_to_production", "rollback_executed_on_production", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 ROLLBACK_DRILL_EXECUTE] OK psp_deleted={d.get('psp_deleted')} restored_pre_apply=true production_rollback=false")
