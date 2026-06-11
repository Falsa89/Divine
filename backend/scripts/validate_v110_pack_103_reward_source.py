#!/usr/bin/env python3
"""Pack 103 - Reward source tower_floor_completion_claim presence + safety."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
reg=open(os.path.join(R,'backend/utils/reward_source_registry.py')).read()
for n in ['"tower_floor_completion_claim"','"grant_fn_name": "grant_tower_floor_to_psp"','"per_source_kill_switch_env": "TOWER_FLOOR_CLAIM_ENABLED"','_grant_tower_floor_to_psp','floor_band_rewards','"READY_GATED_EXECUTION_REQUIRED"','"grant_tower_floor_to_psp": _grant_tower_floor_to_psp']:
    assert n in reg, n
# Reward bands MUST not include premium
import re
m=re.search(r'"tower_floor_completion_claim"\s*:\s*\{(.*?)\}\s*,\s*\}\s*$', reg, re.S)
# Simpler: assert no gems/premium/pull mentioned in tower_floor source block
block = reg[reg.find('"tower_floor_completion_claim"'):reg.find('"tower_floor_completion_claim"')+2000]
for forbidden in ['gems','pulls','tickets','premium','hero_grant','equipment_grant']:
    assert forbidden not in block, f'tower source leak: {forbidden}'
print('[v110 PACK_103_REWARD_SOURCE] OK tower_floor_source_live ledger_backed psp_soft_only no_premium')
