#!/usr/bin/env python3
# Track J: prova immutabilità DB sorgente/produzione locale.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_psp_full_staging/v110_full_staging_source_prod_immutability_v1.json")
d = json.load(open(F))
assert d.get("source_db") == "divine_waifus"
assert d.get("source_unchanged_at_count_level") is True
assert d.get("source_psp_present") == 0
# user_heroes con server_id sul source possono essere presenti da pack precedenti (es. v109 server isolation).
# La prova di immutabilità del Pack 75 è source_db_writes_during_pack_75 == 0 e count-level unchanged.
assert isinstance(d.get("source_user_heroes_with_server_id"), int)
assert d.get("source_migration_logs_v110_count") == 0
assert d.get("source_marker_present") is False
assert d.get("source_db_writes_during_pack_75") == 0
assert d.get("production_apply_executed") is False
assert d.get("legacy_cleanup_executed") is False
assert d.get("reward_live_enabled") is False
assert d.get("progress_live_enabled") is False
sf = d.get("safety_flags", {})
for k in ("production_db_writes", "db_write_to_source", "destructive_source_op",
          "delete_on_source", "premium_grant", "fake_PASS"):
    assert sf.get(k) is False, k
print("[v110 FULL_STAGING_SOURCE_PROD_IMMUTABILITY] OK source untouched")
