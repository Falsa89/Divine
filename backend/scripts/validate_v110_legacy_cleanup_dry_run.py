#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(R, "data/design/v110_psp_migration/v110_legacy_cleanup_dry_run_result_v1.json")
assert os.path.isfile(P), "legacy cleanup dry-run JSON missing"
d = json.load(open(P))
assert d.get("read_only") is True
assert d.get("db_writes") == 0
assert d.get("delete_executed") is False
for k in ("db_write", "delete", "destructive_migration", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False, f"legacy safety {k}"
assert "findings" in d
print(f"[v110 LEGACY_CLEANUP_DRY_RUN] OK read_only=true delete=0 findings_keys={len(d['findings'])}")
