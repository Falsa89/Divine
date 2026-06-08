#!/usr/bin/env python3
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = open(os.path.join(R, 'backend/server.py')).read()
assert "@app.post(\"/api/psp/ensure\")" in src, 'POST /api/psp/ensure decorator missing'
assert 'async def psp_ensure_fresh_start' in src
for must in ('player_server_profiles', 'insert_one', 'find_one', 'PLAYER_SERVER_PROFILE', 'server_id', '_slc_psp_created_by_pack', '_slc_psp_fresh_start', '_slc_psp_no_cross_server_copy', '"player_level": 1', '"player_exp": 0', '"team_formation": []', '"onboarding_state": "pending"'):
    assert must in src, f'ensure route missing token: {must}'
# NESSUNA lettura di altri server
start = src.index('async def psp_ensure_fresh_start')
rest = src[start:]
end_candidates = []
for marker in ('\n@app.', '\n@router.', '\nasync def ', '\ndef '):
    idx = rest.find(marker, 100)
    if idx > 0: end_candidates.append(idx)
fn = rest[:min(end_candidates) if end_candidates else len(rest)]
# Forbidden: nessuna find query con server_id != sid (cross-server read)
for forbidden in ('find_one({"user_id": uid}).limit', 'find({"user_id": uid, "server_id":', 'user_heroes.insert_one', 'user_heroes.update_one'):
    assert forbidden not in fn, f'forbidden cross-server/heroes write detected: {forbidden}'
# Solo 1 insert_one
assert fn.count('insert_one') == 1, f'expected exactly 1 insert_one in ensure fn; got {fn.count("insert_one")}'
print('[v110 PACK_85_ROUTE_MAP_AND_ENSURE_IMPLEMENTATION] OK POST_/api/psp/ensure_implemented fresh_start_fields_only no_cross_server_copy_or_heroes_write')
