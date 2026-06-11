#!/usr/bin/env python3
"""Pack 103 - Gate invariant preservation."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for f in ['backend/routes/tower_strict.py','backend/data/tower_floor_catalog_v1.py','backend/routes/daily_login_claim.py','backend/routes/daily_quest_claim.py','backend/routes/daily_quest_tracker.py','backend/utils/daily_quest_events.py','backend/utils/reward_source_registry.py']:
    assert os.path.exists(os.path.join(R,f)), f
be=os.path.join(R,'backend/battle_engine.py')
if os.path.exists(be):
    assert 'pack_103' not in open(be).read().lower()
smoke=open(os.path.join(R,'backend/scripts/smoke_v110_pack_103_tower_execute_e2e.py')).read()
assert '/api/battle/simulate' not in smoke
print('[v110 PACK_103_GATE_INVARIANT_PRESERVATION] OK')
