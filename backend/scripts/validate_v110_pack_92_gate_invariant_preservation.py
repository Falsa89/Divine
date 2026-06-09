#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_gate_invariant_preservation_v1.json')))
g = d.get('gates', {})
for k in ('postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','release_readiness_claimed','fake_PASS','validator_weakening'):
    assert g.get(k) is False, k
for k in ('pack_84_psp_normalization_preserved','pack_85_psp_ensure_preserved','pack_86_register_guard_preserved','pack_87_starter_claim_preserved','pack_88_team_formation_strict_preserved','pack_89_get_inventory_strict_preserved','pack_90_inventory_write_paths_strict_preserved','pack_91_inventory_frontend_migration_preserved'):
    assert g.get(k) is True, k
print('[v110 PACK_92_GATE_INVARIANT_PRESERVATION] OK postqa_d_locked pack_84_91_preserved no_release_claim')
