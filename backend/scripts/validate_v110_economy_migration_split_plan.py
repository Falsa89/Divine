#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_migration/v110_economy_migration_split_plan_v1.json")))
r = d.get("split_rules", {})
assert isinstance(r.get("soft_currencies_server_scoped"), list) and len(r["soft_currencies_server_scoped"]) >= 2
assert isinstance(r.get("hard_currencies_account_global"), list) and len(r["hard_currencies_account_global"]) >= 1
assert isinstance(r.get("premium_currencies_account_global"), list) and len(r["premium_currencies_account_global"]) >= 1
for k in ("per_user_total_premium_before_after_must_match", "per_user_total_hard_before_after_must_match", "duplication_forbidden", "premium_grant_forbidden"):
    assert d.get("audit_rules", {}).get(k) is True, f"audit {k}"
assert d.get("applied_in_this_pack") is False
assert d.get("db_writes") == 0
for k in ("premium_grant", "currency_duplication", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False, f"econ safety {k}"
print("[v110 ECONOMY_MIGRATION_SPLIT_PLAN] OK soft_server_scoped hard_premium_account_global applied=false")
