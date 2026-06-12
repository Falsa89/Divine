#!/usr/bin/env python3
"""Pack 108 — Arena/PvP/Event Pack 107 preservation.

Verifica che competitive_guards.py NON sia stato modificato in modo
che regredisca le surface Arena/PvP/Event (Pack 107).
Verifica che i blocker canonici Pack 107 siano ancora presenti.
Verifica che guild_preflight Pack 107 resti audit-only (status
AUDIT_LEGACY_NOT_SERVER_SCOPED) accanto a Pack 108 retrofit
(che vive in routes/guild_strict.py).
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
c = open(os.path.join(R, 'backend/routes/competitive_guards.py')).read()

for token in (
    'ARENA_SERVER_SCOPE_REQUIRED', 'ARENA_REWARD_LIVE_DISABLED',
    'PVP_RANKING_SERVER_SCOPE_DEFERRED',
    'GUILD_SERVER_SCOPE_REQUIRED', 'GUILD_REWARD_LIVE_DISABLED',
    'EVENT_SERVER_SCOPE_REQUIRED', 'EVENT_REWARD_LIVE_DISABLED',
    'LEADERBOARD_SERVER_SCOPE_REQUIRED',
    'AUDIT_LEGACY_NOT_SERVER_SCOPED',
    'READY_GATED_REWARDS_DEFERRED',
    'pack_107_test_artifact',
    '_slc_pack_107_arena_preflight',
    '_slc_pack_107_pvp_preflight',
    '_slc_pack_107_event_preflight',
    '_slc_pack_107_guild_preflight',
    'AUTORIZZO_V110_GUILD_SERVER_SCOPE_RETROFIT_PACK_NEXT',
):
    assert token in c, f'pack 107 token missing: {token}'

# No reward live mutation introduced.
for forbidden in ('db.users.update_one', 'db.users.insert_one', 'db.users.delete_one',
                  'db.guild', 'reward_claim_ledger.insert_one', '$inc'):
    assert forbidden not in c, f'competitive_guards regression: {forbidden}'

print('[v110 PACK_108_ARENA_PVP_EVENT_PRESERVATION] OK pack_107_competitive_guards_intact')
