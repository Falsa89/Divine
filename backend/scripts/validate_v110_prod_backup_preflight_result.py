#!/usr/bin/env python3
# Pack 76 Track E: backup preflight manifest+checksum.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_preflight/v110_prod_backup_preflight_result_v1.json")
d = json.load(open(F))
assert d.get("backup_level") in ("MANIFEST_AND_CHECKSUM_ONLY", "PHYSICAL_BACKUP_EXECUTED")
assert d.get("backup_present") is True
assert d.get("restore_capable") is True
assert d.get("target_db") == "divine_waifus"
assert d.get("secret_export_avoided") is True
assert d.get("production_db_writes_during_preflight") == 0
manifest = d.get("manifest", {})
assert isinstance(manifest, dict)
for coll in ("users", "user_heroes", "player_server_profiles", "wallets",
             "battle_pass", "vip_data", "environment_markers"):
    m = manifest.get(coll)
    assert m is not None, coll
    assert "sha256" in m and len(m["sha256"]) == 64, coll
assert isinstance(d.get("manifest_sha256"), str) and len(d["manifest_sha256"]) == 64
sf = d.get("safety_flags", {})
for k in ("raw_secret_export", "destructive", "db_write_to_production", "fake_PASS"):
    assert sf.get(k) is False, k
print(f"[v110 PROD_BACKUP_PREFLIGHT] OK level={d.get('backup_level')} manifest_sha256={d['manifest_sha256'][:12]}...")
