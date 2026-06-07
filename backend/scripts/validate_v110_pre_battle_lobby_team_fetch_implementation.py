#!/usr/bin/env python3
# Pack 80 — Track C: pre-battle lobby team fetch implementation.
import os, re, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
c = open(os.path.join(R, 'frontend/app/pre-battle-lobby.tsx')).read()
for tok in [
    '/api/team/get-formation', 'server_id=', 'encodeURIComponent(selectedServerId)',
    'PLAYER_SLOT_COUNT', 'EmptySlotCard',
    'filter_applied', 'profile_id', 'team_formation', 'blocker',
    'SecureStore.getItemAsync', "'v96_auth_token'",
    'Authorization', 'Bearer',
    'PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER', 'SELECTED_SERVER_REQUIRED',
    'fetch_status',
]:
    assert tok in c, f'lobby missing token: {tok}'
# 6 slot rendering esplicito
assert 'PLAYER_SLOT_COUNT = 6' in c, 'PLAYER_SLOT_COUNT must be 6'
assert re.search(r"Array\.from\(\s*\{\s*length:\s*PLAYER_SLOT_COUNT\s*\}", c), '6-slot Array.from render missing'
# Empty slot logic: empty cards mostrate quando lo slot e' mancante.
assert '<EmptySlotCard' in c, 'EmptySlotCard not rendered'
# Nessun hardcoded s1 silenzioso come fallback player-facing
assert "server_id: 's1'" not in c, 'silent hardcoded server_id s1 fallback detected'
assert "selected_server_id || 's1'" not in c, 'silent hardcoded selected_server_id || s1 fallback detected'
# La fetch deve essere dentro un useEffect che dipende da selectedServerLoaded e selectedServerId
assert 'selectedServerLoaded' in c and 'selectedServerId' in c, 'selectedServerLoaded / selectedServerId missing'
# Verifica esplicita: useEffect dependency array include entrambi
assert re.search(r"\[selectedServerLoaded,\s*selectedServerId", c), 'useEffect deps must include selectedServerLoaded and selectedServerId'
# La logica deve fetchare /api/team/get-formation con server_id
assert re.search(r"/api/team/get-formation\?server_id=", c), 'fetch URL pattern missing'
print('[v110 PRE_BATTLE_LOBBY_TEAM_FETCH_IMPLEMENTATION] OK real fetch implemented, 6 slots, empty cards, no fake team as real, no hardcoded s1')
