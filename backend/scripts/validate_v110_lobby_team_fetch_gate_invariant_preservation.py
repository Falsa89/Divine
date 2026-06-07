#!/usr/bin/env python3
# Pack 80 — Track K: gate/runtime invariant preservation.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_80_lobby_fetch/v110_pack_80_lobby_fetch_summary_v1.json')
d = json.load(open(S))
g = d.get('gate_invariant_preservation', {})
for k in ('postqa_d_gates_changed','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live'):
    assert g.get(k) is False, f'{k} must be false'
for k in ('v107d_binding_preserved','v108_postqa_a_blockers_preserved','v93_resolvePlayerFormation_token_preserved','v91_required_tokens_preserved'):
    assert g.get(k) is True, f'{k} must be true'
# Verifiche di sorgente effettive: i token chiave restano nel lobby
c = open(os.path.join(R, 'frontend/app/pre-battle-lobby.tsx')).read()
for tok in ('launchFromLobby','EXPO_PUBLIC_V107D_PREVIEW_LAUNCH_ENABLED','REAL_PLAYER_TEAM_SOURCE_PENDING','AUTHORED_ENCOUNTER_SOURCE_PENDING','SELECTED_SERVER_REQUIRED','launchAllowedNormal','EXPO_PUBLIC_ALLOW_QA_FALLBACK_BATTLE_LAUNCH','blockerReasons','realPlayerTeamAvailable','authoredEncounterAvailable','selectedServerAvailable','resolvePlayerFormation','safe_fallback_formation','fallback_used','random_opponents_allowed=false','is_random: false','runtime_generated: false','fallback_random_allowed: false','SourceBadge','Modifica Team','Avvia Battaglia'):
    assert tok in c, f'lobby invariant token missing: {tok}'
print('[v110 LOBBY_TEAM_FETCH_GATE_INVARIANT_PRESERVATION] OK postqa_d_unchanged battle_engine_unchanged no_simulate v107d/v108_postqa_a/v93/v91 tokens preserved')
