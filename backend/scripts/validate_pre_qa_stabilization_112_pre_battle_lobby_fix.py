#!/usr/bin/env python3
"""Pre-QA Stabilization 112 — Pre-Battle Lobby fix validator."""
import os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
pbl = open(os.path.join(R, 'frontend/app/pre-battle-lobby.tsx')).read()
assert "'v101_selected_server_id'" in pbl, 'pre-battle-lobby missing v101_selected_server_id key'
assert "AsyncStorage.getItem('selected_server_id')" not in pbl, 'old wrong key still present'
assert 'getAuthTokenCompat' in pbl, 'authTokenCompat not adopted'
assert "SecureStore.getItemAsync('v96_auth_token')" not in pbl, 'raw SecureStore call still present'
lines = [ln for ln in pbl.split('\n') if not ln.lstrip().startswith('//')]
clean = '\n'.join(lines)
assert re.search(r"\|\|\s*['\"]s1['\"]", clean) is None, 'silent s1 fallback in pre-battle-lobby'
print('[v112 PRE_QA_112_PRE_BATTLE_LOBBY_FIX] OK v101_key_used authTokenCompat_adopted no_raw_securestore no_silent_s1')
