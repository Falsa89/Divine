#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_staging_clone/v110_staging_clone_backup_result_v1.json")))
assert d.get("backup_executed") is True
assert d.get("db_writes") == 0
assert d.get("method")
masked = d.get("secrets_masked_plan", [])
for s in ("password", "oauth_token", "iap_receipt_token"):
    assert any(s in m for m in masked), f"masked plan must include {s}"
shas = d.get("sha256_manifest_per_collection", {})
assert isinstance(shas, dict) and len(shas) >= 1
for k in ("db_write", "production_db_smoke", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 STAGING_CLONE_BACKUP_RESULT] OK method={d['method']} collections={len(shas)} db_writes=0")
