#!/usr/bin/env python3
"""Pack 105 — Live readiness flags update."""
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
smoke_path = os.path.join(R, 'data/design/v110_pack_105_forge_upgrade_fusion_strict_psp_material_ledger_spend/v110_pack_105_runtime_smoke_e2e_result_v1.json')
d = json.load(open(smoke_path))
expected = {
    'equipment_upgrade_strict_ready': True,
    'forge_craft_strict_ready': True,
    'equipment_fusion_strict_ready': True,
    'no_reward_live_general': True,
    'release_readiness_claimed': False,
    'psp_material_storage_active': True,
}
for k, v in expected.items():
    assert d.get(k) == v, f'live readiness mismatch {k}: {d.get(k)} != {v}'
print('[v110 PACK_105_LIVE_READINESS_UPDATE] OK upgrade_ready forge_ready fusion_ready psp_materials reward_live_general_false release_readiness_false')
