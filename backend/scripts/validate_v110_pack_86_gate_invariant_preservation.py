#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_86_lobby_psp_ensure/v110_pack_86_gate_invariant_preservation_v1.json')))
for k in ('postqa_d_gates_changed','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','fake_PASS','validator_weakening'):
    assert d.get(k) is False, f'{k} must be false'
for k in ('pack_84_normalized_psp_state_preserved','pack_85_backend_ensure_preserved','pack_80_lobby_fetch_preserved','pack_81_user_heroes_promotion_preserved','pack_82_dual_read_preserved','v107d_binding_preserved','v108_postqa_a_blockers_preserved'):
    assert d.get(k) is True, f'{k} must be true'
src = open(os.path.join(R, 'backend/server.py')).read()
# Tokens da Pack 80/81/82/85 devono essere ancora presenti
for tok in ('user_heroes_are_server_scoped','objectid_compat_fallback','direct_uuid','X-PSP-Lookup-Mode','X-Player-Level','PLAYER_SERVER_PROFILE_REQUIRED','SELECTED_SERVER_REQUIRED_FOR_PLAYER_FACING','psp_ensure_fresh_start','_slc_psp_no_cross_server_copy','already_exists_no_write','fresh_start_created'):
    assert tok in src, f'preserved token missing in server.py: {tok}'
print('[v110 PACK_86_GATE_INVARIANT_PRESERVATION] OK pack80/81/82/84/85_invariants_preserved postqa_d_unchanged battle_engine_unchanged')
