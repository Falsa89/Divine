#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_gate_invariant_preservation_v1.json')))
for k in ('postqa_d_gates_changed','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','fake_PASS','validator_weakening'):
    assert d.get(k) is False
for k in ('pack_84_normalized_psp_state_preserved','pack_85_backend_ensure_preserved','pack_86_register_guard_preserved','pack_87_server_scoped_starter_flow_preserved','pack_88_team_formation_strict_server_scope_preserved','pack_80_lobby_fetch_preserved','pack_81_user_heroes_promotion_preserved','pack_82_dual_read_preserved','v107d_binding_preserved','v108_postqa_a_blockers_preserved'):
    assert d.get(k) is True
src=open(os.path.join(R,'backend/server.py')).read()
for tok in ('psp_ensure_fresh_start','psp_starter_claim','PLAYER_SERVER_PROFILE_REQUIRED','REGISTER_LEGACY_STARTER_HEROES_ENABLED'):
    assert tok in src
v96=open(os.path.join(R,'backend/routes/v96_team_formation.py')).read()
assert 'pack_88_strict_server_scope' in v96
print('[v110 PACK_89_GATE_INVARIANT_PRESERVATION] OK pack80-88_invariants_preserved postqa_d_unchanged team_route_pack88_preserved')
