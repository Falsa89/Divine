#!/usr/bin/env python3
"""Pack 108 — Live readiness update.

Verifica che NESSUN file Pack 108 dichiari release_readiness=true.
Verifica che il report Pack 108 indichi `release_readiness_claimed=false`.
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILES = (
    'backend/routes/guild_strict.py',
    'backend/routes/playable_loop_map.py',
    'backend/routes/competitive_guards.py',
    'frontend/src/utils/playableLoopFlags.ts',
    'frontend/src/utils/serverSwitchRefreshGuard.ts',
    'frontend/src/components/PlayableLoopConsumer.tsx',
)
for rel in FILES:
    c = open(os.path.join(R, rel)).read()
    assert 'release_readiness_claimed": True' not in c
    assert "release_readiness_claimed': True" not in c
    assert 'release_readiness_claimed=true' not in c.lower()

# Report must explicitly say release_readiness_claimed=false (presence check).
report = os.path.join(R, 'docs/divine/110_GUILD_SERVER_SCOPE_RETROFIT_FRONTEND_PLAYABLE_LOOP_POLISH_FINAL_REPORT.md')
if os.path.exists(report):
    r = open(report).read()
    assert 'release_readiness_claimed=false' in r.lower() or 'release_readiness_claimed: false' in r.lower()
print('[v110 PACK_108_LIVE_READINESS_UPDATE] OK no_release_readiness_claim_anywhere')
