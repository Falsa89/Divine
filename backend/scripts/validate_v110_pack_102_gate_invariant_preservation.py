#!/usr/bin/env python3
"""Pack 102 — Gate / runtime invariant preservation (Pack 84-101 + battle_engine + no battle simulate)."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for f in [
    'backend/routes/daily_login_claim.py',
    'backend/routes/daily_quest_claim.py',
    'backend/routes/daily_quest_tracker.py',
    'backend/routes/tower_strict.py',
    'backend/data/tower_floor_catalog_v1.py',
    'backend/data/character_bible.py',
]:
    assert os.path.exists(os.path.join(R,f)), f
be=os.path.join(R,'backend/battle_engine.py')
if os.path.exists(be):
    src=open(be).read()
    assert 'pack_102' not in src.lower(), 'Pack 102 must NOT touch battle_engine'
smoke=open(os.path.join(R,'backend/scripts/smoke_v110_pack_102_tower_100_floor_catalog_e2e.py')).read()
assert '/api/battle/simulate' not in smoke
print('[v110 PACK_102_GATE_INVARIANT_PRESERVATION] OK pack_84_101_kept battle_engine_untouched no_battle_simulate_call')
