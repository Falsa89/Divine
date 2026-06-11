#!/usr/bin/env python3
"""Pack 103 - SOT presence."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'docs/divine/123_TOWER_EXECUTE_FLOOR_CLAIM_LEDGER_DAILY_QUEST_2_HOOK_SOT.md')
assert os.path.exists(p)
src=open(p).read()
for n in ['tower_floor_completion_claim','POST /api/tower/strict/battle/execute','TOWER_FLOOR_CLAIM_ENABLED','TOWER_STRICT_EXECUTE_ENABLED','tower_floor_clear_success','daily_quest_2','pack_103_test_artifact','floor 100','reward live general']:
    assert n in src, n
print('[v110 PACK_103_SOT] OK')
