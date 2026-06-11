#!/usr/bin/env python3
"""Pack 104 — Gate / runtime invariant preservation (Packs 84-103 untouched)."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# tower_strict.py invariato sui contratti Pack 103
tw = open(os.path.join(R, 'backend/routes/tower_strict.py')).read()
assert 'TOWER_FLOOR_CLAIM_ENABLED' in tw
assert 'tower_floor_completion_claim' in tw
assert 'PACK_103_USER_TEST_MARKER' in tw
# combat.py mantiene il quarantena legacy
cb = open(os.path.join(R, 'backend/routes/combat.py')).read()
assert '_pack_101_tower_legacy_block_or_raise()' in cb
assert 'TOWER_LEGACY_QUARANTINED' in cb
# Daily quest claim mantiene la canonical map post-Pack-103
dqc = open(os.path.join(R, 'backend/routes/daily_quest_claim.py')).read()
assert '"daily_quest_2": "REAL_COMPLETION_EVENT_READY_VIA_TOWER_CLEAR"' in dqc
# Daily quest events mantiene il mapping Pack 103
dqe = open(os.path.join(R, 'backend/utils/daily_quest_events.py')).read()
assert '"tower_floor_clear_success": "daily_quest_2"' in dqe
# Reward source registry: tower_floor_completion_claim ancora presente
import sys
sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY
assert 'tower_floor_completion_claim' in REWARD_SOURCE_REGISTRY
assert REWARD_SOURCE_REGISTRY['tower_floor_completion_claim']['live'] is True
print('[v110 PACK_104_GATE_INVARIANT_PRESERVATION] OK pack_101_tower_strict_preserved pack_103_tower_floor_completion_preserved pack_100_daily_quest_2_canonical_preserved')
