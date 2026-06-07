#!/usr/bin/env python3
# Pack 76 Track G: expected production diff.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_preflight/v110_expected_prod_apply_diff_v1.json")
d = json.load(open(F))
assert d.get("target_db") == "divine_waifus"
assert d.get("target_server_id") == "s1"
ei = d.get("expected_inserts", {})
eu = d.get("expected_updates", {})
ed = d.get("expected_deletes", {})
assert isinstance(ei.get("player_server_profiles"), int)
assert ei["player_server_profiles"] >= 1
assert isinstance(eu.get("user_heroes_server_id_set"), int)
assert isinstance(eu.get("team_formation_server_id_set"), int)
assert isinstance(eu.get("user_equipment_server_id_set"), int)
assert ed == {} or len(ed) == 0
assert d.get("users_count_must_remain_unchanged") is True
assert d.get("user_heroes_count_must_not_decrease") is True
assert d.get("no_premium_currency_grant_expected") is True
assert d.get("no_soft_currency_duplication_expected") is True
assert d.get("no_negative_balance_expected") is True
assert d.get("no_legacy_collection_deletion_expected") is True
assert d.get("no_reward_live_enablement_expected") is True
assert d.get("no_progress_live_enablement_expected") is True
inv = d.get("invariants", {})
for k in ("psp_total_post_apply_equals_users_in_scope",
          "psp_with_target_server_equals_users_in_scope",
          "unique_user_id_server_id_pair",
          "psp_v110_apply_marked_equals_psp_inserted"):
    assert inv.get(k) is True, k
assert inv.get("valid_profile_id_regex") == "^[a-f0-9]+:s1$"
sf = d.get("safety_flags", {})
for k in ("destructive", "production_apply_executed", "fake_PASS"):
    assert sf.get(k) is False, k
print(f"[v110 EXPECTED_PROD_APPLY_DIFF] OK psp_inserts={ei.get('player_server_profiles')} total_writes={d.get('expected_total_db_writes_if_executed')}")
