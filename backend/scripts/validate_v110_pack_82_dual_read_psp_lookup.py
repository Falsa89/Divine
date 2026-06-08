#!/usr/bin/env python3
# Pack 82 - Track 2: dual-read PSP lookup implementation (static).
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = open(os.path.join(R, 'backend/server.py')).read()
# Primo tentativo direct_uuid
assert 'db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})' in src, 'first attempt direct_uuid lookup missing'
# Fallback compat via str(_id)
assert 'str(current_user.get("_id")' in src, 'fallback ObjectId compat lookup missing'
assert 'find_one({"user_id": legacy_uid, "server_id": sid})' in src, 'fallback compat query missing'
# Modes emessi nei header
for mode in ('direct_uuid', 'objectid_compat_fallback', 'not_found', 'skipped_no_server_id'):
    assert f'"{mode}"' in src or f"'{mode}'" in src, f'lookup mode label missing: {mode}'
assert '"X-PSP-Lookup-Mode"' in src, 'X-PSP-Lookup-Mode header missing'
# NESSUNA scrittura DB nella funzione
start = src.index('async def get_user_heroes(')
rest = src[start:]
end_candidates = []
for marker in ('\n@app.', '\n@router.', '\nasync def ', '\ndef '):
    idx = rest.find(marker, 100)
    if idx > 0: end_candidates.append(idx)
fn = rest[:min(end_candidates) if end_candidates else len(rest)]
for forbidden in ('insert_one', 'update_one', 'delete_one', 'replace_one', 'insert_many', 'update_many', 'delete_many'):
    assert forbidden not in fn, f'forbidden DB write in route fn: {forbidden}'
print('[v110 PACK_82_DUAL_READ_PSP_LOOKUP] OK direct_uuid_first objectid_fallback no_db_writes mode_headers_emitted')
