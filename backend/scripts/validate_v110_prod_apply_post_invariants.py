#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_apply_execute/v110_prod_apply_post_invariants_v1.json")
d = json.load(open(F))
assert d.get("all_invariants_ok") is True
checks = d.get("checks", {})
for k in ("psp_total_matches_users_in_plan", "psp_with_target_server_geq_users_in_plan",
          "valid_profile_ids_format", "unique_user_id_server_id_pair",
          "users_count_unchanged_or_grew_organically", "user_heroes_count_not_reduced",
          "team_formation_count_unchanged", "wallets_unchanged",
          "battle_pass_unchanged", "vip_data_unchanged", "shop_purchases_unchanged",
          "gacha_history_unchanged", "story_progress_unchanged",
          "psp_v110_apply_marked_matches_inserts",
          "no_legacy_delete", "no_premium_grant", "no_currency_duplication",
          "no_reward_live_enabled", "no_progress_live_enabled"):
    assert checks.get(k, {}).get("ok") is True, k
sf = d.get("safety_flags", {})
for k in ("premium_grant", "currency_duplication", "fake_PASS", "release_readiness_claimed"):
    assert sf.get(k) is False, k
print("[v110 PROD_APPLY_POST_INVARIANTS] OK all invariants verified")
