#!/usr/bin/env python3
# Track H: rollback drill REALE (no dry-run).
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_psp_full_staging/v110_full_staging_rollback_drill_v1.json")
d = json.load(open(F))
assert d.get("rollback_drill_executed") is True
assert d.get("rollback_dry_run_only") is False, "il pack 75 richiede rollback REALE, no dry-run"
assert d.get("target_db") == "divine_waifus_staging_clone"
assert d.get("psp_after_rollback") == 0
assert d.get("user_heroes_with_server_id_after_rollback") == 0
assert d.get("rollback_restored_pre_apply_signature") is True
assert d.get("production_rollback_executed") is False
assert d.get("source_db_writes_during_rollback") == 0
assert d.get("psp_deleted", 0) > 0
sf = d.get("safety_flags", {})
assert sf.get("db_write_to_production") is False
assert sf.get("rollback_executed_on_production") is False
assert sf.get("fake_PASS") is False
print(f"[v110 FULL_STAGING_ROLLBACK_DRILL] OK real_rollback psp_deleted={d.get('psp_deleted')}")
