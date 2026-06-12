#!/usr/bin/env python3
"""Pack 109 — Story/Battle preview/staging RC audit.

Verifica che `routes/combat.py` non venga chiamato in live e che nessun
file Pack 109 invochi `/api/battle/simulate`.
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for f in (
    'backend/scripts/smoke_v110_pack_109_closed_alpha_rc_global_e2e.py',
    'backend/routes/playable_loop_map.py',
    'backend/routes/guild_strict.py',
    'backend/routes/tower_strict.py',
    'backend/routes/economy_strict.py',
    'backend/routes/controlled_rewards.py',
    'backend/routes/competitive_guards.py',
):
    p = os.path.join(R, f)
    if not os.path.exists(p): continue
    c = open(p).read()
    assert '/api/battle/simulate' not in c, f'{f}: battle simulate live call forbidden'
    assert 'battle_engine' not in c, f'{f}: battle_engine import forbidden'
print('[v110 PACK_109_STORY_BATTLE_PREVIEW_STAGING_RC] OK no_battle_simulate_live no_battle_engine_import')
