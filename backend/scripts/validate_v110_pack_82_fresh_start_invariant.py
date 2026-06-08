#!/usr/bin/env python3
# Pack 82 - Track 6: fresh-start invariant (no S1->S2 copy).
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_82_psp_dual_read_compat/v110_pack_82_psp_dual_read_compat_summary_v1.json')
d = json.load(open(S))
fs = d.get('fresh_start_invariant', {})
assert fs.get('fresh_player_level') == 1
assert fs.get('fresh_player_exp') == 0
assert fs.get('fresh_roster_count') == 0
assert fs.get('fresh_team_count') == 0
assert fs.get('no_s1_to_s2_copy_in_code') is True
assert fs.get('no_account_wide_fallback_as_final_server_level') is True
assert fs.get('no_account_wide_fallback_as_final_server_roster') is True
assert fs.get('no_account_wide_fallback_as_final_server_team') is True
# Static: il route NON deve avere alcuna logica di copia user_heroes da altro server
src = open(os.path.join(R, 'backend/server.py')).read()
# Verifica che il path "no PSP" ritorni esplicitamente livello 1 e exp 0 (fresh-start)
start = src.index('async def get_user_heroes(')
rest = src[start:]
end_candidates = []
for marker in ('\n@app.', '\n@router.', '\nasync def ', '\ndef '):
    idx = rest.find(marker, 100)
    if idx > 0: end_candidates.append(idx)
fn = rest[:min(end_candidates) if end_candidates else len(rest)]
assert '"fresh_start_pending_psp_creation"' in fn, 'fresh start progression state missing in no-PSP branch'
assert '"X-Player-Level"] = "1"' in fn, 'fresh level=1 missing in no-PSP branch'
assert '"X-Player-Exp"] = "0"' in fn, 'fresh exp=0 missing in no-PSP branch'
# NO copy from one server to another
assert '_s1_to_s2_' not in fn.lower()
assert 'copy_from_server' not in fn.lower()
assert 'fallback_server_roster' not in fn.lower()
print('[v110 PACK_82_FRESH_START_INVARIANT] OK no_s1_to_s2_copy fresh_level=1 fresh_exp=0 fresh_roster=0 fresh_team=0 no_account_wide_fallback_as_final_server_state')
