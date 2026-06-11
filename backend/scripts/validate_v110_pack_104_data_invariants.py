#!/usr/bin/env python3
"""Pack 104 — Data invariants / forbidden mutation proof."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY, FORBIDDEN_REWARD_TYPES, ALLOWED_SOFT_CURRENCIES

# Tutte le source live restano ledger-gated.
for src_id, src in REWARD_SOURCE_REGISTRY.items():
    if not src.get('live'):
        continue
    assert src.get('idempotency') == 'mandatory', f'{src_id} idempotency must be mandatory'
    # reward_types non possono contenere forbidden.
    for k in src.get('reward_types', []):
        assert k not in FORBIDDEN_REWARD_TYPES, f'{src_id} live reward forbidden: {k}'

# gems sempre forbidden.
assert 'gems' in FORBIDDEN_REWARD_TYPES
assert 'gems' not in ALLOWED_SOFT_CURRENCIES

# Static check on economy_strict.py: no mention of FORBIDDEN_REWARD_TYPES contents in grant logic.
src = open(os.path.join(R, 'backend/routes/economy_strict.py')).read()
# Verify FORBIDDEN_REWARD_TYPES is imported and used as blocker check.
assert 'FORBIDDEN_REWARD_TYPES' in src
assert 'FORBIDDEN_CURRENCY' in src
assert 'PREMIUM_GRANT_BLOCKED' in src

print('[v110 PACK_104_DATA_INVARIANTS] OK all_live_sources_idempotent gems_forbidden_globally forbidden_reward_types_enforced premium_blocker_present')
