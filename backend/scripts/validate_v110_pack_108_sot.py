#!/usr/bin/env python3
"""Pack 108 — Source of Truth (SOT).

Valida che i file canonici Pack 108 esistano, che siano registrati in
`game_systems.py`, e che PROMPT_MAIN+specs/guardrails siano leggibili.
"""
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in (
    'backend/routes/guild_strict.py',
    'backend/routes/playable_loop_map.py',
    'backend/routes/guild.py',
    'backend/routes/competitive_guards.py',
    'backend/scripts/smoke_v110_pack_108_guild_frontend_playable_loop_e2e.py',
    'frontend/src/utils/playableLoopFlags.ts',
    'frontend/src/utils/serverSwitchRefreshGuard.ts',
    'frontend/src/components/PlayableLoopConsumer.tsx',
    'data/pack_108/extracted/PROMPT_MAIN.md',
    'data/pack_108/extracted/specs/pack108_guardrails.json',
):
    assert os.path.exists(os.path.join(R, p)), p

gs = open(os.path.join(R, 'backend/game_systems.py')).read()
assert 'register_guild_strict_routes' in gs
assert 'register_playable_loop_map_routes' in gs
assert 'Pack 108' in gs

guardrails = json.load(open(os.path.join(R, 'data/pack_108/extracted/specs/pack108_guardrails.json')))
assert guardrails['approval_string_required'] == 'AUTORIZZO_V110_GUILD_SERVER_SCOPE_RETROFIT_FRONTEND_PLAYABLE_LOOP_POLISH_PACK_108'

print('[v110 PACK_108_SOT] OK pack_108_sot_files_present registered_in_game_systems guardrails_canonical')
