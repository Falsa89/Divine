#!/usr/bin/env python3
# Pack 80 — Track G: story/lobby/combat payload update.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_80_lobby_fetch/v110_pack_80_lobby_fetch_summary_v1.json')
d = json.load(open(S))
p = d.get('story_lobby_combat_payload_update', {})
assert p.get('selected_server_id_propagated') is True
assert p.get('player_team_snapshot_source', '').startswith('real_fetch_team_formation_route')
assert p.get('slot_count') == 6
assert p.get('enemy_source') and 'authored' in p.get('enemy_source')
assert p.get('no_fake_launch_when_blocker_active') is True
lobby = open(os.path.join(R, 'frontend/app/pre-battle-lobby.tsx')).read()
# launchContext include server_id, mode, encounter_id, source_id, source_type
for k in ("server_id:", "mode,", "encounter_id:", "source_id:", "source_type:"):
    assert k in lobby, f'launchContext missing key {k}'
print('[v110 STORY_LOBBY_COMBAT_PAYLOAD_UPDATE] OK selected_server_id propagated slot_count=6 enemy_authored no_fake_launch')
