#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_apply_execute/v110_prod_apply_backup_confirmation_v1.json")
d = json.load(open(F))
assert d.get("backup_confirmed") is True
assert d.get("restore_capable") is True
assert isinstance(d.get("pinned_backup_manifest_sha256"), str)
assert isinstance(d.get("fresh_backup_manifest_sha256"), str)
assert len(d.get("fresh_backup_manifest_sha256")) == 64
sf = d.get("safety_flags", {})
assert sf.get("db_write_to_production") is False
assert sf.get("fake_PASS") is False
print(f"[v110 PROD_APPLY_BACKUP_CONFIRMATION] OK fresh_sha256={d['fresh_backup_manifest_sha256'][:12]}...")
