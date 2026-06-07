#!/usr/bin/env python3
# Track F: post-apply invariants.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_psp_full_staging/v110_full_staging_post_apply_invariants_v1.json")
d = json.load(open(F))
assert d.get("all_invariants_ok") is True
assert d.get("db_writes") == "ONLY_STAGING_CLONE"
checks = d.get("checks", {})
for k in ("psp_count_matches_users_selected", "psp_with_target_server_matches",
          "valid_profile_ids_format", "unique_account_server_pair",
          "users_count_unchanged", "user_heroes_count_not_reduced",
          "no_team_size_drift", "no_legacy_delete", "no_premium_grant",
          "no_currency_duplication", "no_soft_currency_loss_outside_policy",
          "no_reward_live_enabled", "no_progress_live_enabled",
          "psp_v110_apply_marked_equals_psp_total"):
    assert checks.get(k, {}).get("ok") is True, k
sf = d.get("safety_flags", {})
assert sf.get("premium_grant") is False
assert sf.get("currency_duplication") is False
assert sf.get("fake_PASS") is False
assert sf.get("release_readiness_claimed") is False
print("[v110 FULL_STAGING_POST_APPLY_INVARIANTS] OK all invariants")
