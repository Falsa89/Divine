#!/usr/bin/env python3
# Pack 80 — Track B: route usage map (verifica file lobby, route reale, sorgenti).
import os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
lobby = open(os.path.join(R, 'frontend/app/pre-battle-lobby.tsx')).read()
route = open(os.path.join(R, 'backend/routes/v96_team_formation.py')).read()
assert '/api/team/get-formation' in lobby, 'lobby must call /api/team/get-formation'
assert 'server_id=' in lobby, 'lobby must pass server_id query param'
assert 'AsyncStorage' in lobby and 'selected_server_id' in lobby, 'selected_server_source AsyncStorage:selected_server_id missing'
assert 'SecureStore' in lobby and 'v96_auth_token' in lobby, 'auth token source SecureStore:v96_auth_token missing'
assert 'EXPO_BACKEND_URL' in lobby, 'backend url env helper missing'
assert '/api/team/get-formation' in route and 'server_id' in route, 'real route does not implement server_id'
assert '/api/encounter-source/get' in lobby, 'authored encounter source route still referenced (no probe-only confusion)'
# Le route promosse devono essere quelle REALMENTE chiamate, NON probe-only.
assert '/api/battle/simulate' not in lobby, 'lobby must NOT call /api/battle/simulate'
print('[v110 LOBBY_TEAM_FETCH_ROUTE_USAGE_MAP] OK lobby->/api/team/get-formation real route mapped server_id=present auth_bearer=present')
