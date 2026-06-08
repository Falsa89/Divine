#!/usr/bin/env python3
# Pack 81 - Track 14: gate/runtime invariant preservation.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_81_user_heroes_server_scope/v110_pack_81_user_heroes_server_scope_summary_v1.json')
d = json.load(open(S))
g = d.get('gate_invariant_preservation', {})
for k in ('postqa_d_gates_changed','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live'):
    assert g.get(k) is False, f'{k} must be false'
for k in ('v107d_binding_preserved','v108_postqa_a_blockers_preserved','pack_80_lobby_fetch_preserved','v93_resolvePlayerFormation_token_preserved','v91_required_tokens_preserved'):
    assert g.get(k) is True, f'{k} must be true'
# Lobby invariant tokens preserved
c = open(os.path.join(R, 'frontend/app/pre-battle-lobby.tsx')).read()
for tok in ('PLAYER_SLOT_COUNT', 'EmptySlotCard', 'launchFromLobby', 'REAL_PLAYER_TEAM_SOURCE_PENDING', 'AUTHORED_ENCOUNTER_SOURCE_PENDING', 'SELECTED_SERVER_REQUIRED', 'launchAllowedNormal', 'blockerReasons', 'resolvePlayerFormation', 'safe_fallback_formation', 'fallback_used', 'random_opponents_allowed=false', 'is_random: false', 'runtime_generated: false', 'SourceBadge', 'Modifica Team', 'Avvia Battaglia'):
    assert tok in c, f'lobby invariant token missing: {tok}'
print('[v110 PACK_81_GATE_INVARIANT_PRESERVATION] OK postqa_d_unchanged battle_engine_unchanged pack80_preserved lobby_tokens_preserved')
