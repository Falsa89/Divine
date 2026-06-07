#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_server_filter_team_source/zero_mutation_economy_preservation_v1.json")
d = json.load(open(F))
for k in ("psp_inserted_in_pack_78", "psp_deleted_in_pack_78",
          "user_heroes_modified_in_pack_78", "team_formation_modified_in_pack_78",
          "user_equipment_modified_in_pack_78", "wallets_modified_in_pack_78",
          "battle_pass_modified_in_pack_78", "vip_modified_in_pack_78",
          "shop_modified_in_pack_78", "gacha_modified_in_pack_78",
          "premium_grant_in_pack_78", "soft_currency_duplication_in_pack_78",
          "production_db_writes_in_pack_78"):
    assert d.get(k) == 0, k
assert d.get("legacy_cleanup_in_pack_78") is False
sf = d.get("safety_flags", {})
for k in ("production_db_writes", "destructive_migration", "delete",
          "premium_grant", "currency_duplication", "reward_live",
          "progress_live", "legacy_cleanup_executed",
          "battle_pass_mutated", "vip_mutated", "shop_mutated",
          "gacha_mutated", "fake_PASS"):
    assert sf.get(k) is False, k
print("[v110 ZERO_MUTATION_ECONOMY_PRESERVATION] OK 0 writes 0 mutations")
