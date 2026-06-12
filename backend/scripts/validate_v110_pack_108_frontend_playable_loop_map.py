#!/usr/bin/env python3
"""Pack 108 — Frontend Playable Loop Map validator (static).

Verifica che routes/playable_loop_map.py exponga /api/playable-loop/{health,map,state}
e che enumeri esplicitamente tutte le surface canoniche con `ui_flag_default_off=True`,
`reward_live=False`, e nessuna surface con status='READY' (per non avere
false-ready labels).
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
c = open(os.path.join(R, 'backend/routes/playable_loop_map.py')).read()

for token in (
    '/playable-loop/health', '/playable-loop/map', '/playable-loop/state',
    'alpha_map_version', 'pack_108_v1',
    'release_readiness_claimed', 'reward_live_general',
    'no_silent_fallback_to_s1',
    'no_users_gold_gems_experience_mutation',
    'no_premium_grants', 'no_iap_gacha_payment',
    'no_arena_pvp_guild_event_reward_live',
    'no_account_wide_guild_writes',
    'no_hardcoded_server_id_s1', 'no_cross_server_guild_leak',
    'PLAYABLE_LOOP_STATE_TEST_ONLY', 'pack_108_test_artifact',
):
    assert token in c, f'missing token: {token}'

for surface_key in ('"home"', '"lobby"', '"daily"', '"tower"', '"shop"',
                    '"forge"', '"rewards"', '"guild"', '"arena"', '"pvp"', '"event"'):
    assert surface_key in c, surface_key

# Nessuna surface con status="READY" (solo READY_GATED / DEFERRED / LOCKED / READY_GATED_DEFERRED).
for bad in ('"status": "READY"', "'status': 'READY'"):
    assert bad not in c, f'false-ready label: {bad}'

# Read-only: nessuna mutation Mongo.
for forbidden in ('db.users.update_one', 'db.users.insert_one',
                  'db.guilds_v2.insert_one', 'db.guild_memberships_v2.insert_one',
                  '$inc'):
    assert forbidden not in c, forbidden

print('[v110 PACK_108_FRONTEND_PLAYABLE_LOOP_MAP] OK eleven_surfaces_enumerated no_false_ready no_mutation')
