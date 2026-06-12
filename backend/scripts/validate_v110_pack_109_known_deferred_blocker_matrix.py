#!/usr/bin/env python3
"""Pack 109 — Known Deferred Blocker Matrix.

Verifica che il report finale enumeri esplicitamente i blocker canonici.
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
report = open(os.path.join(R, 'docs/divine/110_CLOSED_ALPHA_RC_SWEEP_RELEASE_GATE_FINAL_REPORT.md')).read()
rep_lower = report.lower()
DEFERRED = (
    'GUILD_CHAT_SERVER_SCOPE_DEFERRED', 'GUILD_WAR_SERVER_SCOPE_DEFERRED',
    'GUILD_REWARD_LIVE_DISABLED', 'ARENA_REWARD_LIVE_DISABLED',
    'PVP_RANKING_SERVER_SCOPE_DEFERRED', 'EVENT_REWARD_LIVE_DISABLED',
    'LEADERBOARD_SERVER_SCOPE_REQUIRED', 'BATTLEPASS_DEFERRED',
    'AFK_REWARDS_DEFERRED', 'IAP_GACHA_PAYMENT_DEFERRED',
)
for b in DEFERRED:
    assert b.lower() in rep_lower, f'deferred blocker missing in report: {b}'
print('[v110 PACK_109_KNOWN_DEFERRED_BLOCKER_MATRIX] OK ten_canonical_deferred_blockers_present_in_report')
