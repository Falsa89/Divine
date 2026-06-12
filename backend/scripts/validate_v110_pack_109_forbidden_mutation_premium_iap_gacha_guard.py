#!/usr/bin/env python3
"""Pack 109 — Forbidden mutation / premium / IAP / gacha static guard.

Niente route Pack 109 deve aver attivato/registrato IAP/gacha/payment.
"""
import os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
gs = open(os.path.join(R, 'backend/game_systems.py')).read()
for forbidden in ('register_iap_routes', 'register_gacha_routes', 'register_store_payment_routes',
                  'register_battlepass_live_routes', 'register_afk_reward_live_routes'):
    assert forbidden not in gs, f'forbidden registration: {forbidden}'

# Pack 109 deve NON aver introdotto reward live general True.
rsr = os.path.join(R, 'backend/utils/reward_source_registry.py')
if os.path.exists(rsr):
    c = open(rsr).read().lower()
    for forbidden_token in ('guild_reward_live"', 'arena_reward_live"', 'pvp_reward_live"',
                            'event_reward_live"', 'battlepass_reward_live"', 'afk_reward_live"'):
        assert forbidden_token not in c, f'reward_source_registry: forbidden live source {forbidden_token}'

# .env backend non attiva reward live di default.
env_path = os.path.join(R, 'backend/.env')
if os.path.exists(env_path):
    env = open(env_path).read()
    for flag in ('REWARD_LIVE_GENERAL', 'GUILD_REWARD_LIVE_ENABLED',
                 'ARENA_REWARD_LIVE_ENABLED', 'PVP_REWARD_LIVE_ENABLED',
                 'EVENT_REWARD_LIVE_ENABLED', 'BATTLEPASS_REWARD_LIVE_ENABLED',
                 'AFK_REWARD_LIVE_ENABLED'):
        m = re.search(rf'^{flag}=(\S+)', env, re.MULTILINE)
        if m:
            assert m.group(1).strip().lower() in ('false', '0', 'no', 'off', ''), f'{flag} attivo in .env'
print('[v110 PACK_109_FORBIDDEN_MUTATION_PREMIUM_IAP_GACHA_GUARD] OK no_iap_gacha_payment_registered no_reward_live_sources no_reward_live_env_flag_true')
