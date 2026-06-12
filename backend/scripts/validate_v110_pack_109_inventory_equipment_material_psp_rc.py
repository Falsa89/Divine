#!/usr/bin/env python3
"""Pack 109 — Inventory/Equipment/Material PSP scope RC audit (static)."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for rel, tokens in (
    ('backend/routes/economy_strict.py', ['player_server_profiles', 'equipment', 'materials']),
):
    c = open(os.path.join(R, rel)).read()
    for tok in tokens:
        assert tok in c, f'{rel}: missing {tok}'
# PSP material storage validator already exists (Pack 105). Verifica esistenza.
assert os.path.exists(os.path.join(R, 'backend/scripts/validate_v110_pack_105_data_invariants.py'))
assert os.path.exists(os.path.join(R, 'backend/scripts/validate_mega_release_acceleration_105_forge_upgrade_fusion_strict_psp_material_ledger_spend_rollup.py'))
print('[v110 PACK_109_INVENTORY_EQUIPMENT_MATERIAL_PSP_RC] OK psp_collection_used equipment_materials_present')
