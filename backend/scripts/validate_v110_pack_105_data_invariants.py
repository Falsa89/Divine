#!/usr/bin/env python3
"""Pack 105 — Data invariants + Pack 104 source preservation."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY, FORBIDDEN_REWARD_TYPES, ALLOWED_SOFT_CURRENCIES

# Pack 104 sources ancora presenti e live.
for src_id in ('shop_buy_strict_claim','soul_forge_retire_strict_claim',
               'equipment_equip_strict_claim','equipment_unequip_strict_claim'):
    assert src_id in REWARD_SOURCE_REGISTRY, f'pack 104 source removed: {src_id}'
    assert REWARD_SOURCE_REGISTRY[src_id]['live'] is True

# Pack 105 sources idempotent.
for src_id in ('equipment_upgrade_strict_claim','forge_craft_strict_claim','equipment_fusion_strict_claim'):
    assert REWARD_SOURCE_REGISTRY[src_id]['idempotency'] == 'mandatory'

assert 'gems' in FORBIDDEN_REWARD_TYPES
assert 'gems' not in ALLOWED_SOFT_CURRENCIES

# Static check on economy_strict.py.
src = open(os.path.join(R, 'backend/routes/economy_strict.py')).read()
assert 'FORBIDDEN_REWARD_TYPES' in src
assert 'PREMIUM_GRANT_BLOCKED' in src or '_PremiumGrantBlocked' in src
assert 'INSUFFICIENT_MATERIAL' in src
assert 'INSUFFICIENT_SOFT_CURRENCY' in src
assert 'EQUIPMENT_MAX_LEVEL_REACHED' in src
assert 'EQUIPMENT_MAX_RARITY_REACHED' in src
assert 'FODDER_NOT_OWNED_ON_SERVER' in src
assert 'FODDER_SLOT_MISMATCH' in src
assert 'FODDER_RARITY_MISMATCH' in src
assert 'BASE_EQUIPMENT_CANNOT_BE_FODDER' in src

print('[v110 PACK_105_DATA_INVARIANTS] OK pack_104_sources_preserved pack_105_idempotency_mandatory gems_forbidden insufficient_blockers_present fusion_safeguards_present')
