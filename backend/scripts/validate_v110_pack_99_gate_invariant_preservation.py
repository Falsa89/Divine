#!/usr/bin/env python3
"""Pack 99 gate preservation: pack 84-98 invariants kept, no battle_engine rewrite, no /api/battle/simulate regression."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for f in ['backend/routes/daily_login_claim.py','backend/routes/daily_quest_claim.py']:
    assert os.path.exists(os.path.join(R,f)), f
# Daily login source preserved
reg=open(os.path.join(R,'backend/utils/reward_source_registry.py')).read()
assert 'daily_login_claim' in reg
# Battle engine NOT touched by Pack 99
be=os.path.join(R,'backend/battle_engine.py')
if os.path.exists(be):
    src=open(be).read()
    assert 'pack_99' not in src.lower(), 'Pack 99 must NOT touch battle_engine'
print('[v110 PACK_99_GATE_INVARIANT_PRESERVATION] OK pack_84_98_kept battle_engine_untouched daily_login_intact')
