#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_88_team_formation_strict_server_scope/v110_pack_88_gate_invariant_preservation_v1.json')))
for k in ('postqa_d_gates_changed','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','fake_PASS','validator_weakening'):
    assert d.get(k) is False
for k in ('pack_84_normalized_psp_state_preserved','pack_85_backend_ensure_preserved','pack_86_register_guard_preserved','pack_87_server_scoped_starter_flow_preserved','pack_80_lobby_fetch_preserved','pack_81_user_heroes_promotion_preserved','pack_82_dual_read_preserved','v107d_binding_preserved','v108_postqa_a_blockers_preserved'):
    assert d.get(k) is True
src = open(os.path.join(R, 'backend/server.py')).read()
for tok in ('psp_ensure_fresh_start','psp_starter_claim','server_scoped_starter_flow_pack_87','already_claimed_no_write','PLAYER_SERVER_PROFILE_REQUIRED','REGISTER_LEGACY_STARTER_HEROES_ENABLED'):
    assert tok in src, f'preserved token missing in server.py: {tok}'
print('[v110 PACK_88_GATE_INVARIANT_PRESERVATION] OK pack80-87_invariants_preserved postqa_d_unchanged battle_engine_unchanged')
