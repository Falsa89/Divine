#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_staging_backup_execution_result_v1.json")))
assert d.get("backup_executed") is False
assert d.get("db_writes") == 0
assert d.get("fs_writes_during_backup") == 0
assert d.get("status")
for k in ("backup_executed", "db_write", "production_db_smoke", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 STAGING_BACKUP_EXECUTION] OK status={d['status']} backup_executed=false db_writes=0")
