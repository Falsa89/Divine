#!/usr/bin/env python3
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=open(os.path.join(R,'backend/utils/reward_source_registry.py')).read()
# Reward payload preservation Pack 98/99
assert '"daily_quest_completion_claim"' in src
assert '"mission_coins": 15' in src
assert '"honor": 8' in src
assert '"per_source_kill_switch_env": "DAILY_QUEST_CLAIM_ENABLED"' in src
assert 'grant_daily_quest_to_psp' in src
# Nessun premium currency nel registry per la source quest
import re
block=re.search(r'"daily_quest_completion_claim"\s*:\s*\{[^}]+\}', src, re.S)
assert block, 'daily_quest_completion_claim block missing'
for forbidden in ['gems', 'gold', 'pulls', 'tickets', 'premium']:
    assert forbidden not in block.group(0), f'premium leak in registry block: {forbidden}'
print('[v110 PACK_99_REWARD_PAYLOAD_PRESERVATION] OK fixed_reward_15_8 psp_soft_only no_premium_in_quest_block')
