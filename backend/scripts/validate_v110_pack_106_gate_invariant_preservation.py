#!/usr/bin/env python3
"""Pack 106 — Gate / runtime invariant preservation (Pack 84-105 untouched)."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY

for s in ('tower_floor_completion_claim','shop_buy_strict_claim','soul_forge_retire_strict_claim',
          'equipment_equip_strict_claim','equipment_unequip_strict_claim',
          'equipment_upgrade_strict_claim','forge_craft_strict_claim','equipment_fusion_strict_claim'):
    assert s in REWARD_SOURCE_REGISTRY, f'pack <= 105 source removed: {s}'
    assert REWARD_SOURCE_REGISTRY[s]['live'] is True

tw = open(os.path.join(R, 'backend/routes/tower_strict.py')).read()
assert 'TOWER_FLOOR_CLAIM_ENABLED' in tw
assert 'tower_floor_completion_claim' in tw
cb = open(os.path.join(R, 'backend/routes/combat.py')).read()
assert '_pack_101_tower_legacy_block_or_raise()' in cb
es = open(os.path.join(R, 'backend/routes/economy_strict.py')).read()
assert 'SHOP_BUY_STRICT_ENABLED' in es
assert 'EQUIPMENT_UPGRADE_STRICT_ENABLED' in es
assert 'FORGE_CRAFT_STRICT_ENABLED' in es
assert 'EQUIPMENT_FUSION_STRICT_ENABLED' in es
print('[v110 PACK_106_GATE_INVARIANT_PRESERVATION] OK pack_101_103_104_105_endpoints_kill_switches_preserved')
