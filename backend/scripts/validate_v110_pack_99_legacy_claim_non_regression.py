#!/usr/bin/env python3
"""Pack 99 legacy claim source non-regression: solo daily_login + daily_quest sources reali."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
reg=open(os.path.join(R,'backend/utils/reward_source_registry.py')).read()
# Only allowed live player-facing sources
allowed_live=['daily_login_claim','daily_quest_completion_claim']
# Other sources must remain non-live or non-player-facing
for forbidden in ['mail_claim_live','achievements_claim_live','battle_pass_claim_live','event_claim_live','afk_claim_live']:
    assert forbidden not in reg, f'forbidden live source present: {forbidden}'
for src in allowed_live:
    assert src in reg, src
print('[v110 PACK_99_LEGACY_CLAIM_NON_REGRESSION] OK only_daily_login_and_daily_quest mail_achievements_bp_events_afk_blocked')
