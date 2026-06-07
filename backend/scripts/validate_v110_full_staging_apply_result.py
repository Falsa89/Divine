#!/usr/bin/env python3
# Track D: full apply (no limit) sul clone.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_psp_full_staging/v110_full_staging_apply_result_v1.json")
d = json.load(open(F))
assert d.get("target_db") == "divine_waifus_staging_clone"
assert d.get("source_db") == "divine_waifus"
assert d.get("apply_executed") is True
assert d.get("limit_used") is None, "il pack 75 NON deve usare --limit"
assert d.get("target_server_id") == "s1"
assert d.get("production_apply_executed") is False
assert d.get("production_db_writes") == 0
assert d.get("source_db_writes") == 0
assert d.get("psp_profiles_inserted", 0) > 0, "full apply deve inserire >=1 PSP"
assert d.get("no_premium_grant") is True
assert d.get("no_deletes") is True
assert d.get("no_reward_live") is True
assert d.get("no_progress_live") is True
assert d.get("migration_batch_id") == "v110_psp_apply_v1"
assert d.get("users_selected") == d.get("psp_profiles_inserted") + d.get("psp_profiles_upserted")
print(f"[v110 FULL_STAGING_APPLY_RESULT] OK inserted={d.get('psp_profiles_inserted')} users={d.get('users_selected')}")
