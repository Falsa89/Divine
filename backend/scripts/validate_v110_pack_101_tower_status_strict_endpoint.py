#!/usr/bin/env python3
"""Pack 101 — Tower strict status endpoint: server_id required, read-only."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend/scripts'))
from _pack_101_validator_helpers import extract_async_fn_body
src=open(os.path.join(R,'backend/routes/tower_strict.py')).read()
body = extract_async_fn_body(src, 'tower_strict_status')
assert body, 'status fn missing'
for needle in ['SERVER_ID_REQUIRED', 'PLAYER_SERVER_PROFILE_REQUIRED', 'get_tower_progress_strict', '_slc_pack_101_tower_strict_status']:
    assert needle in body, needle
# Status MUST not write to db
for forbidden in ['db.users.update_one', 'db.users.insert_one', 'db.player_server_profiles.update_one', 'db.tower_progress.insert_one', 'db.tower_progress.update_one']:
    assert forbidden not in body, f'status leak (write): {forbidden}'
print('[v110 PACK_101_TOWER_STATUS_STRICT_ENDPOINT] OK server_id_required psp_required read_only_no_writes')
