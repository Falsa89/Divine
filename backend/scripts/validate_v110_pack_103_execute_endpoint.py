#!/usr/bin/env python3
"""Pack 103 - Tower execute endpoint static guard."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend/scripts'))
from _pack_101_validator_helpers import extract_async_fn_body
src=open(os.path.join(R,'backend/routes/tower_strict.py')).read()
body=extract_async_fn_body(src, 'tower_strict_battle_execute')
assert body
import re as _re
code = _re.sub(r'"""[\s\S]*?"""', '', body)
code = _re.sub(r"'''[\s\S]*?'''", '', code)
code = _re.sub(r'(?m)#.*$', '', code)
for n in ['REWARD_CLAIM_LEDGER_DISABLED','TOWER_STRICT_EXECUTE_DISABLED','TOWER_FLOOR_CLAIM_DISABLED','SERVER_ID_REQUIRED','IDEMPOTENCY_TOKEN_REQUIRED','FLOOR_REQUIRED','FLOOR_OUT_OF_CATALOG_RANGE','FLOOR_NOT_ALLOWED_FOR_PSP','EXECUTE_ENDPOINT_TEST_ONLY','PLAYER_SERVER_PROFILE_REQUIRED','TOWER_FLOOR_CLAIM_SOURCE','reward_claim_ledger','_slc_pack_103_tower_floor_completion_claim','_record_dq_event','tower_floor_clear_success','tower_strict_battle_execute']:
    assert n in body, n
for forb in ['db.users.update_one(','db.users.insert_one(','users.gold','users.gems','users.experience','db.tower_progress.insert_one(','db.tower_progress.update_one(']:
    assert forb not in code, f'execute leak in active code: {forb}'
print('[v110 PACK_103_EXECUTE_ENDPOINT] OK triple_kill_switch test_only_marker server_scoped no_users_mutation no_legacy_write')
