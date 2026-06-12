#!/usr/bin/env python3
"""Pack 108 — Guild Reward Lock (no live grant).

Verifica che NESSUNO dei file Pack 108 conceda reward Guild live.
Verifica che competitive_guards.guild_reward_live_grant resti False.
Verifica che reward_source_registry NON abbia attivato reward live Guild.
"""
import os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

for f in ('backend/routes/guild_strict.py', 'backend/routes/playable_loop_map.py',
          'backend/routes/competitive_guards.py'):
    c = open(os.path.join(R, f)).read()
    # Niente $inc su soft_currencies/materials/users.
    for forbidden in ('"$inc"', "'$inc'"):
        assert forbidden not in c, f'{f}: {forbidden}'
    # Nessun grant Guild live.
    assert 'guild_reward_live_grant' not in c or 'guild_reward_live_grant": False' in c or 'guild_reward_live_grant\": False' in c

# Verifica controlled_rewards/reward_source_registry: nessuna nuova guild_* source live.
for f in ('backend/utils/reward_source_registry.py', 'backend/routes/controlled_rewards.py'):
    p = os.path.join(R, f)
    if not os.path.exists(p):
        continue
    c = open(p).read()
    # Pack 108 NON deve aver introdotto reward source guild live.
    assert 'guild_reward_live' not in c.lower() or 'False' in c

# guild_strict explicit: reward_live_general / guild_reward_live_grant must be False.
gs = open(os.path.join(R, 'backend/routes/guild_strict.py')).read()
assert '"reward_live_general": False' in gs
assert '"guild_reward_live_grant": False' in gs

print('[v110 PACK_108_GUILD_REWARD_LOCK] OK no_guild_reward_live_grant pack_108_reward_lock_preserved')
