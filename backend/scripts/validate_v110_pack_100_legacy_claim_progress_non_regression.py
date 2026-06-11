#!/usr/bin/env python3
"""Pack 100 — Legacy claim/progress non-regression: solo daily_login + daily_quest live."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
reg=open(os.path.join(R,'backend/utils/reward_source_registry.py')).read()
for forbidden in ['mail_claim_live','achievements_claim_live','battlepass_claim_live','event_claim_live','afk_claim_live','tower_claim_live']:
    assert forbidden not in reg, f'forbidden source: {forbidden}'
for allowed in ['daily_login_claim','daily_quest_completion_claim']:
    assert allowed in reg, allowed
print('[v110 PACK_100_LEGACY_CLAIM_PROGRESS_NON_REGRESSION] OK only_daily_login_and_daily_quest_live tower_mail_achievements_bp_events_afk_blocked')
