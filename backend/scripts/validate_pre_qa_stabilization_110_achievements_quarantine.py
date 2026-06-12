#!/usr/bin/env python3
"""Pre-QA Stabilization 110 — Achievements legacy claim quarantine validator."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ach = open(os.path.join(R, 'backend/routes/achievements.py')).read()
for t in ('ACHIEVEMENT_LEGACY_CLAIM_QUARANTINED', 'ACHIEVEMENT_LEGACY_CLAIM_ENABLED',
          'ACHIEVEMENT_CONTROLLED_CLAIM_REQUIRED', 'no_gold_gems_stamina_mutation',
          'pack_106_controlled_rewards', 'AUTORIZZO_V110_ACHIEVEMENTS_LIVE_PACK_NEXT'):
    assert t in ach, f'achievements.py missing {t}'
# Pack 106 controlled rewards preserved.
assert os.path.exists(os.path.join(R, 'backend/routes/controlled_rewards.py'))
print('[v110 PRE_QA_110_ACHIEVEMENTS_QUARANTINE] OK legacy_claim_quarantined controlled_rewards_pack_106_preserved')
