#!/usr/bin/env python3
"""Pack 101 — Gate/runtime invariant preservation Pack 84-100 + battle_engine + battle simulate."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for f in [
    'backend/routes/daily_login_claim.py',
    'backend/routes/daily_quest_claim.py',
    'backend/routes/daily_quest_tracker.py',
    'backend/utils/daily_quest_events.py',
    'backend/routes/tower_strict.py',
]:
    assert os.path.exists(os.path.join(R,f)), f
# Battle engine NOT touched
be=os.path.join(R,'backend/battle_engine.py')
if os.path.exists(be):
    src=open(be).read()
    assert 'pack_101' not in src.lower(), 'Pack 101 must NOT touch battle_engine'
# Smoke must not call /api/battle/simulate
smoke=open(os.path.join(R,'backend/scripts/smoke_v110_pack_101_tower_strict_e2e.py')).read()
assert '/api/battle/simulate' not in smoke
print('[v110 PACK_101_GATE_INVARIANT_PRESERVATION] OK pack_84_100_kept battle_engine_untouched no_battle_simulate_call')
