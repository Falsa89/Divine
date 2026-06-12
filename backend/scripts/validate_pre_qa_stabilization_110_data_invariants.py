#!/usr/bin/env python3
"""Pre-QA Stabilization 110 — Data invariants forbidden mutation proof."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Verify no NEW mutation guards are missing.
for fp, must_contain in (
    ('backend/server.py', ['GACHA_LIVE_DISABLED_PRE_QA']),
    ('backend/battle_engine.py', ['TEAM_FORMATION_LEGACY_QUARANTINED']),
    ('backend/routes/achievements.py', ['ACHIEVEMENT_LEGACY_CLAIM_QUARANTINED']),
):
    c = open(os.path.join(R, fp)).read()
    for t in must_contain:
        assert t in c, f'{fp}: must contain {t}'
print('[v110 PRE_QA_110_DATA_INVARIANTS] OK three_critical_quarantine_guards_present')
