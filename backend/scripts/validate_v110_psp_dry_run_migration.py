#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(R, "data/design/v110_psp_migration/v110_psp_dry_run_result_v1.json")
assert os.path.isfile(P), "PSP dry-run JSON missing (run dry_run_v110_psp_migration.py first)"
d = json.load(open(P))
assert d.get("read_only") is True
assert d.get("db_writes") == 0
assert d.get("apply_executed") is False
assert d.get("applied_in_this_pack") is False
for k in ("db_write", "destructive_migration", "delete", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False, f"psp dry-run safety {k}"
assert "counts" in d and "estimated_apply_writes" in d
print(f"[v110 PSP_DRY_RUN_MIGRATION] OK read_only=true db_writes=0 mongo_reachable={d.get('mongo_reachable')}")
