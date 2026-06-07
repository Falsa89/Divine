#!/usr/bin/env python3
# Track G: balance/economy audit.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_psp_full_staging/v110_full_staging_balance_economy_audit_v1.json")
d = json.load(open(F))
assert d.get("premium_grants_in_apply") == 0
assert d.get("hard_currency_grants_in_apply") == 0
assert d.get("soft_currency_duplications") == 0
assert d.get("negative_balances_in_psp") == 0
assert d.get("battlepass_mutated") is False
assert d.get("vip_mutated") is False
assert d.get("shop_mutated") is False
assert d.get("gacha_mutated") is False
assert d.get("economy_unchanged_post_apply") is True
sf = d.get("safety_flags", {})
for k in ("premium_grant", "currency_duplication", "battlepass_mutation",
          "vip_mutation", "shop_mutation", "gacha_mutation", "fake_PASS"):
    assert sf.get(k) is False, k
print("[v110 FULL_STAGING_BALANCE_ECONOMY_AUDIT] OK no premium/currency mutation")
