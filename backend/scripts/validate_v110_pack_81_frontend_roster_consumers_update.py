#!/usr/bin/env python3
# Pack 81 - Track 5: frontend roster consumers update.
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
lobby = open(os.path.join(R, 'frontend/app/pre-battle-lobby.tsx')).read()
# pre-battle-lobby DEVE passare server_id al /api/user/heroes enrichment
assert '/api/user/heroes?server_id=' in lobby, 'lobby enrichment must pass server_id'
assert 'encodeURIComponent(selectedServerId)' in lobby, 'lobby must encode selectedServerId'
# NON deve esserci una chiamata account-wide a /api/user/heroes nel lobby (dev'essere SEMPRE con server_id)
# Tollerato: vecchi commenti potrebbero menzionare la versione account-wide, ma fetch attivo deve passare server_id
fetch_lines = [ln for ln in lobby.splitlines() if 'fetch(' in ln and '/api/user/heroes' in ln]
for ln in fetch_lines:
    assert 'server_id=' in ln, f'lobby fetch /api/user/heroes without server_id: {ln.strip()}'
print('[v110 PACK_81_FRONTEND_ROSTER_CONSUMERS_UPDATE] OK lobby_enrichment_passes_server_id no_account_wide_fetch_in_player_facing_battle_path')
