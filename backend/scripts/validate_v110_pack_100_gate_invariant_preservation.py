#!/usr/bin/env python3
"""Pack 100 — Gate / runtime invariant preservation (Pack 84-99, battle_engine, no battle simulate)."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for f in ['backend/routes/daily_login_claim.py','backend/routes/daily_quest_claim.py','backend/routes/daily_quest_tracker.py','backend/utils/daily_quest_events.py']:
    assert os.path.exists(os.path.join(R,f)), f
be=os.path.join(R,'backend/battle_engine.py')
if os.path.exists(be):
    src=open(be).read()
    assert 'pack_100' not in src.lower(), 'Pack 100 must NOT touch battle_engine'
# Smoke must not call /api/battle/simulate
smoke=open(os.path.join(R,'backend/scripts/smoke_v110_pack_100_daily_task_loop_e2e.py')).read()
assert '/api/battle/simulate' not in smoke, 'smoke must not call battle/simulate'
print('[v110 PACK_100_GATE_INVARIANT_PRESERVATION] OK pack_84_99_kept battle_engine_untouched no_battle_simulate_call')
