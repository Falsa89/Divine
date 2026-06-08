#!/usr/bin/env python3
# Pack 83 - Track M: gate/runtime invariant preservation.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_psp_normalization_preflight/v110_psp_normalization_preflight_summary_v1.json')
d = json.load(open(S))
g = d.get('gate_invariant_preservation', {})
for k in ('postqa_d_gates_changed','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','fake_PASS','validator_weakening'):
    assert g.get(k) is False, f'{k} must be false'
for k in ('pack_80_lobby_fetch_preserved','pack_81_user_heroes_promotion_preserved','pack_82_dual_read_preserved','v107d_binding_preserved','v108_postqa_a_blockers_preserved'):
    assert g.get(k) is True, f'{k} must be true'
# Pack 82 dual-read static check still in server.py
src = open(os.path.join(R, 'backend/server.py')).read()
for tok in ('objectid_compat_fallback', 'X-PSP-Lookup-Mode', 'X-Player-Level', 'X-Server-Progression-State', 'user_heroes_are_server_scoped'):
    assert tok in src, f'Pack 82 invariant token missing in server.py: {tok}'
print('[v110 PACK_83_GATE_INVARIANT_PRESERVATION] OK pack80/81/82 invariants preserved postqa_d_unchanged battle_engine_unchanged')
