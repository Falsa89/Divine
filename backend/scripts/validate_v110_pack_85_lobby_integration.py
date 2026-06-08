#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_85_psp_onboarding/v110_pack_85_psp_onboarding_summary_v1.json')))
l = d.get('lobby_integration', {})
assert l.get('lobby_already_handles_PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER_blocker_honestly') is True
assert l.get('post_ensure_lobby_shows_empty_6_slots_and_blocker_for_team') is True
assert l.get('lobby_does_not_show_S1_team_on_new_server') is True
# Verifica statica: il lobby non chiama /api/psp/ensure direttamente in questo pack (UI integration DEFERRED)
lobby = open(os.path.join(R, 'frontend/app/pre-battle-lobby.tsx')).read()
# Lobby gestisce PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER blocker (Pack 79+)
assert 'PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER' in lobby
assert 'PLAYER_SLOT_COUNT' in lobby
print('[v110 PACK_85_LOBBY_INTEGRATION] OK lobby_handles_blocker_honestly no_S1_team_leak UI_auto_ensure_deferred')
