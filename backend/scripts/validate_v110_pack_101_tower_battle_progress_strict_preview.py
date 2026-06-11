#!/usr/bin/env python3
"""Pack 101 — Tower strict battle preview: deterministico, NO reward grant, NO mutation."""
import os, sys, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend/scripts'))
from _pack_101_validator_helpers import extract_async_fn_body
src=open(os.path.join(R,'backend/routes/tower_strict.py')).read()
body = extract_async_fn_body(src, 'tower_strict_battle_preview')
assert body, 'preview fn missing'
for needle in [
    'SERVER_ID_REQUIRED', 'PLAYER_SERVER_PROFILE_REQUIRED',
    'no_reward_grant_on_preview',
    'REWARD_QUARANTINED_PENDING_LEDGER',
    '_preview_compute',
    '_slc_pack_101_battle_preview',
]:
    assert needle in body, needle
# Preview MUST not write to db
for forbidden in ['db.users.update_one(', 'db.player_server_profiles.update_one(', 'db.tower_progress.insert_one(', 'db.user_equipment.insert_one(']:
    assert forbidden not in body, f'preview leak (write): {forbidden}'
for forbidden in ['grant_fn(', 'reward_claim_ledger.insert']:
    assert forbidden not in body, f'preview reward leak: {forbidden}'
# _preview_compute deve essere deterministica (no random in the function body)
comp_idx = src.find('def _preview_compute(')
assert comp_idx >= 0, '_preview_compute fn missing'
# Estrai dal def fino alla prossima funzione top-level o EOF
rest = src[comp_idx:]
import re as _re
m_next = _re.search(r'(?m)^def |^async def |^class ', rest[1:])
if m_next:
    comp_body = rest[:m_next.start() + 1]
else:
    comp_body = rest
# Strip docstring/comments per controllare solo il codice attivo
comp_code = _re.sub(r'"""[\s\S]*?"""', '', comp_body)
comp_code = _re.sub(r"'''[\s\S]*?'''", '', comp_code)
comp_code = _re.sub(r'(?m)#.*$', '', comp_code)
assert 'random' not in comp_code, 'preview compute must be deterministic (no random in active code)'
print('[v110 PACK_101_TOWER_BATTLE_PROGRESS_STRICT_PREVIEW] OK deterministic no_reward no_mutation no_random')
