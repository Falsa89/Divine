#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_apply_execute/v110_prod_apply_execute_result_v1.json")
d = json.load(open(F))
assert d.get("target_db") == "divine_waifus"
assert d.get("target_server_id") == "s1"
assert d.get("cmd_returncode") == 0
assert d.get("script_status") == "APPLY_EXECUTED_PRODUCTION"
assert d.get("apply_executed") is True
assert d.get("production_apply_executed") is True
assert d.get("db_writes", 0) > 0
assert d.get("psp_inserted_in_this_run", 0) > 0
assert d.get("limit_used") is None
assert d.get("migration_source") == "v110_psp_apply_v1"
assert d.get("audit_collection") == "migration_logs"
assert d.get("no_premium_grant") is True
assert d.get("no_deletes") is True
assert d.get("no_reward_live") is True
assert d.get("no_progress_live") is True
assert d.get("no_legacy_cleanup") is True
assert d.get("no_gacha_mutation") is True
assert d.get("no_battle_pass_mutation") is True
assert d.get("no_vip_mutation") is True
assert d.get("no_shop_mutation") is True
sf = d.get("safety_flags", {})
assert sf.get("production_apply_executed") is True
assert sf.get("production_db_writes") is True
for k in ("destructive_migration", "delete", "premium_grant", "currency_duplication",
          "reward_live", "progress_live", "fake_PASS", "release_readiness_claimed",
          "legacy_cleanup_executed"):
    assert sf.get(k) is False, k
print(f"[v110 PROD_APPLY_EXECUTE_RESULT] OK psp_inserted={d.get('psp_inserted_in_this_run')} db_writes={d.get('db_writes')} production_apply_executed=true")
