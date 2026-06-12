#!/usr/bin/env python3
"""Pack 108 — Gate / runtime invariant preservation.

Verifica che i Pack precedenti (91–2107) non siano regredeiti:
  - tower_strict, economy_strict, controlled_rewards, competitive_guards
    sono ancora registrati;
  - i kill switch ledger live / daily login / daily quest restano
    default-OFF nello stato del repo (.env non li ha attivati);
  - Pack 108 NON ha rimosso nessuna delle registrazioni precedenti.
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
gs = open(os.path.join(R, 'backend/game_systems.py')).read()
for reg in (
    'register_tower_strict_routes',
    'register_economy_strict_routes',
    'register_controlled_rewards_routes',
    'register_competitive_guards_routes',
    'register_guild_strict_routes',
    'register_playable_loop_map_routes',
    'register_reward_claim_routes',
    'register_daily_login_claim_routes',
    'register_daily_quest_claim_routes',
    'register_daily_quest_tracker_routes',
):
    assert reg in gs, f'missing registration: {reg}'

# .env backend: nessun reward live attivato di default.
env_path = os.path.join(R, 'backend/.env')
env = open(env_path).read() if os.path.exists(env_path) else ''
for flag in ('REWARD_LIVE_GENERAL', 'REWARD_CLAIM_LEDGER_LIVE_ENABLED',
             'DAILY_LOGIN_CLAIM_ENABLED', 'DAILY_QUEST_CLAIM_ENABLED',
             'GUILD_REWARD_LIVE_ENABLED', 'ARENA_REWARD_LIVE_ENABLED',
             'PVP_REWARD_LIVE_ENABLED', 'EVENT_REWARD_LIVE_ENABLED',
             'GUILD_STRICT_PREFLIGHT_ENABLED',
             'GUILD_STRICT_MEMBERSHIP_READ_ENABLED',
             'GUILD_STRICT_SEARCH_READ_ENABLED'):
    # Se appare nel .env, deve essere false. Se non appare, default OFF.
    if flag in env:
        line = [l for l in env.split('\n') if l.startswith(flag + '=')]
        if line:
            assert line[0].split('=', 1)[1].strip().lower() in ('false', '0', 'no', 'off', ''), f'flag {flag} not default OFF in backend/.env'

print('[v110 PACK_108_GATE_INVARIANT_PRESERVATION] OK previous_pack_registrations_intact backend_env_no_reward_live_default')
