#!/usr/bin/env python3
"""Pack 105 — Gate / runtime invariant preservation (Pack 84-104 untouched)."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY

# Pack 103 source ancora presente.
assert 'tower_floor_completion_claim' in REWARD_SOURCE_REGISTRY
assert REWARD_SOURCE_REGISTRY['tower_floor_completion_claim']['live'] is True
# Pack 104 sources ancora live.
for s in ('shop_buy_strict_claim','soul_forge_retire_strict_claim','equipment_equip_strict_claim','equipment_unequip_strict_claim'):
    assert REWARD_SOURCE_REGISTRY[s]['live'] is True
# tower_strict.py invariato sui contratti Pack 103.
tw = open(os.path.join(R, 'backend/routes/tower_strict.py')).read()
assert 'TOWER_FLOOR_CLAIM_ENABLED' in tw
assert 'tower_floor_completion_claim' in tw
assert 'PACK_103_USER_TEST_MARKER' in tw
# combat.py mantiene il quarantena legacy.
cb = open(os.path.join(R, 'backend/routes/combat.py')).read()
assert '_pack_101_tower_legacy_block_or_raise()' in cb
assert 'TOWER_LEGACY_QUARANTINED' in cb
# Daily quest claim mantiene Pack 103 canonical.
dqc = open(os.path.join(R, 'backend/routes/daily_quest_claim.py')).read()
assert '"daily_quest_2": "REAL_COMPLETION_EVENT_READY_VIA_TOWER_CLEAR"' in dqc
# Pack 104 sources nel codice.
es = open(os.path.join(R, 'backend/routes/economy_strict.py')).read()
assert 'SHOP_BUY_STRICT_ENABLED' in es
assert 'SOUL_FORGE_RETIRE_STRICT_ENABLED' in es
assert 'EQUIPMENT_STRICT_WRITES_ENABLED' in es
print('[v110 PACK_105_GATE_INVARIANT_PRESERVATION] OK pack_101_pack_103_pack_104_endpoints_kill_switches_preserved')
