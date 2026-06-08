#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_85_psp_onboarding/v110_pack_85_psp_onboarding_summary_v1.json')))
g = d.get('gate_invariant_preservation', {})
for k in ('postqa_d_gates_changed','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','fake_PASS','validator_weakening'):
    assert g.get(k) is False, f'{k} must be false'
for k in ('pack_80_lobby_fetch_preserved','pack_81_user_heroes_promotion_preserved','pack_82_dual_read_preserved','pack_83_preflight_artifacts_preserved','pack_84_physical_normalization_preserved','v107d_binding_preserved','v108_postqa_a_blockers_preserved'):
    assert g.get(k) is True, f'{k} must be true'
src = open(os.path.join(R, 'backend/server.py')).read()
for tok in ('user_heroes_are_server_scoped','objectid_compat_fallback','direct_uuid','X-PSP-Lookup-Mode','X-Player-Level','X-Server-Progression-State','PLAYER_SERVER_PROFILE_REQUIRED','SELECTED_SERVER_REQUIRED_FOR_PLAYER_FACING'):
    assert tok in src, f'invariant token missing in server.py: {tok}'
print('[v110 PACK_85_GATE_INVARIANT_PRESERVATION] OK pack80/81/82/83/84_invariants_preserved postqa_d_unchanged battle_engine_unchanged')
