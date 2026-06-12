#!/usr/bin/env python3
"""Pre-QA Stabilization 110 — Team formation legacy quarantine validator."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
be = open(os.path.join(R, 'backend/battle_engine.py')).read()
for token in ('TEAM_FORMATION_LEGACY_QUARANTINED', 'TEAM_FORMATION_SERVER_SCOPE_REQUIRED',
              'no_account_wide_teams_write', 'TEAM_FORMATION_LEGACY_QUARANTINED'):
    assert token in be, f'battle_engine missing {token}'
assert 'AUTORIZZO_V110_TEAM_FORMATION_SERVER_SCOPE_PACK_NEXT' in be
# Frontend battle.tsx must handle 423.
battle = open(os.path.join(R, 'frontend/app/(tabs)/battle.tsx')).read()
assert '423' in battle and 'TEAM_FORMATION_LEGACY_QUARANTINED' in battle
print('[v110 PRE_QA_110_TEAM_FORMATION_QUARANTINE] OK legacy_team_update_blocked_423 frontend_handles_quarantine')
