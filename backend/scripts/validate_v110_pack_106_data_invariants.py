#!/usr/bin/env python3
"""Pack 106 — Data invariants + Pack 105 preservation."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY, FORBIDDEN_REWARD_TYPES, ALLOWED_SOFT_CURRENCIES

for s in ('equipment_upgrade_strict_claim','forge_craft_strict_claim','equipment_fusion_strict_claim'):
    assert REWARD_SOURCE_REGISTRY[s]['live'] is True
for s in ('mail_claim_controlled','achievement_claim_controlled','daily_weekly_reward_claim'):
    assert REWARD_SOURCE_REGISTRY[s]['idempotency'] == 'mandatory'

assert 'gems' in FORBIDDEN_REWARD_TYPES
assert 'gems' not in ALLOWED_SOFT_CURRENCIES

src = open(os.path.join(R, 'backend/routes/controlled_rewards.py')).read()
assert 'FORBIDDEN_REWARD_TYPES' in src
assert 'PREMIUM_GRANT_BLOCKED' in src or '_PremiumGrantBlocked' in src
assert 'ACHIEVEMENT_COMPLETION_REQUIRED' in src
assert 'MAIL_NOT_FOUND' in src
assert 'ACHIEVEMENT_NOT_FOUND' in src
assert 'TASK_NOT_FOUND' in src

print('[v110 PACK_106_DATA_INVARIANTS] OK pack_105_sources_preserved pack_106_idempotency_mandatory gems_forbidden completion_required_blocker_present catalog_404_blockers_present')
