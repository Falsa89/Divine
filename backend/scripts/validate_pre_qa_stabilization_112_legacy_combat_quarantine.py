#!/usr/bin/env python3
"""Pre-QA Stabilization 112 — Legacy combat routes quarantine validator."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
c = open(os.path.join(R, 'backend/routes/combat.py')).read()
for t in ('PVP_BATTLE_LEGACY_QUARANTINED', 'EVENTS_BATTLE_LEGACY_QUARANTINED',
          'STORY_BATTLE_LEGACY_NO_SERVER_ID_QUARANTINED',
          'STORY_BATTLE_STRICT_SERVER_SCOPED_REQUIRED',
          'PVP_BATTLE_LEGACY_ENABLED', 'EVENTS_BATTLE_LEGACY_ENABLED',
          'STORY_BATTLE_LEGACY_ENABLED',
          'no_users_gold_gems_experience_mutation',
          'AUTORIZZO_V110_PVP_BATTLE_LIVE_PACK_NEXT',
          'AUTORIZZO_V110_EVENTS_BATTLE_LIVE_PACK_NEXT',
          'AUTORIZZO_V110_STORY_BATTLE_LIVE_PACK_NEXT'):
    assert t in c, f'combat.py missing: {t}'
print('[v112 PRE_QA_112_LEGACY_COMBAT_QUARANTINE] OK pvp_events_story_quarantine_guards_present')
