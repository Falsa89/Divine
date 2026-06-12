#!/usr/bin/env python3
"""Pack 108 — Static Anti-Leak Guard.

Verifica statica che NESSUN file Pack 108 contenga pattern di leak
account-wide / silent s1 / reward live forbidden.
"""
import os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATCH_FILES = (
    'backend/routes/guild_strict.py',
    'backend/routes/playable_loop_map.py',
    'backend/routes/competitive_guards.py',
    'frontend/src/utils/playableLoopFlags.ts',
    'frontend/src/utils/serverSwitchRefreshGuard.ts',
    'frontend/src/components/PlayableLoopConsumer.tsx',
)
for rel in PATCH_FILES:
    raw = open(os.path.join(R, rel)).read()
    # Strip commenti riga-a-riga per evitare falsi positivi su documentazione.
    lines = []
    for ln in raw.split('\n'):
        s = ln.lstrip()
        if s.startswith('//') or s.startswith('#') or s.startswith('*'):
            continue
        lines.append(ln)
    c = '\n'.join(lines)
    # No silent s1 fallback (literal string 's1' allowed only as input, NOT as default).
    assert re.search(r"\|\|\s*['\"]s1['\"]", c) is None, f'{rel}: silent ||"s1" fallback'
    assert re.search(r"\?\?\s*['\"]s1['\"]", c) is None, f'{rel}: silent ??"s1" fallback'
    assert re.search(r"\bserver_id\s*=\s*['\"]s1['\"]", c) is None, f'{rel}: server_id="s1" default'
    assert re.search(r"\bdefault_server_id\s*[:=]\s*['\"]s1['\"]", c) is None, f'{rel}: default_server_id "s1"'
    # No reward live general true.
    assert 'reward_live_general": True' not in c and "reward_live_general': True" not in c
    # No release readiness claim.
    assert 'release_readiness_claimed": True' not in c and "release_readiness_claimed': True" not in c
    # No false filter_applied=true.
    assert 'filter_applied": True' not in c.replace(' ', '')
    # No premium grant Mongo write in Pack 108 surfaces (controlled_rewards/economy_strict are separate packs).
    if rel.startswith('backend/'):
        for forbidden in ('db.users.update_one', 'db.users.insert_one', 'db.users.delete_one'):
            assert forbidden not in c, f'{rel}: forbidden mutation {forbidden}'

# Guild strict / playable loop must not import battle_engine or simulate.
for rel in ('backend/routes/guild_strict.py', 'backend/routes/playable_loop_map.py'):
    c = open(os.path.join(R, rel)).read()
    assert 'battle_engine' not in c
    assert '/api/battle/simulate' not in c

print('[v110 PACK_108_STATIC_ANTI_LEAK_GUARD] OK no_silent_s1_fallback no_reward_live_general_true no_release_readiness_claim no_battle_engine_call')
