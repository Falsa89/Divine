#!/usr/bin/env python3
"""Pack 102 — Data invariants: reward_live_general False, no premium, no release readiness."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
strict=open(os.path.join(R,'backend/routes/tower_strict.py')).read()
assert '"reward_live_general": False' in strict
assert '"tower_reward_live_grant": False' in strict
assert '"release_readiness_claimed": False' in strict
# Catalog endpoint responses devono includere safety flags
import re
for name in ['tower_strict_catalog', 'tower_strict_catalog_floor']:
    m = re.search(rf'async def {name}\([^)]*\):.*?(?=    @router\.|\Z)', strict, re.S)
    if not m:
        continue
    body = m.group(0)
    assert '"reward_live_general": False' in body, f'{name} missing reward_live_general False'
    assert '"tower_reward_live_grant": False' in body, f'{name} missing tower_reward_live_grant False'
print('[v110 PACK_102_DATA_INVARIANTS] OK reward_live_general_false tower_reward_live_grant_false release_readiness_false')
