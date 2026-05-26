#!/usr/bin/env python3
# PROJECT_SOUL_FORGE_EMERGENCY_RESTORE Track E — legacy economy import audit mapping.
import json, sys
from pathlib import Path
J = Path('/app/data/design/soul_forge/economy_legacy_mapping_v1.json')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_E_FULL_ECONOMY_LEGACY_CONTENT_IMPORT_AUDIT_READY'
    # Required explicit classifications from the PROMPT pack
    items = d['items_explicitly_classified']
    for k in ('polvere_dust','anime_souls','essence','sigilli_seals',
              'shop_currencies','materials_from_hero_retirement','old_shop_categories'):
        assert k in items and items[k], f'classification missing: {k}'
    # Mapping must include the 4 key materials
    legacy_names = {row['legacy_name'] for row in d['mapping_table']}
    for needed in ('Prana', 'Soul Seals (Sigilli)', 'Star Dust (Polvere Stellare)', 'Soul Essence'):
        assert needed in legacy_names, f'missing mapping for {needed}'
    # Live vs locked summary present
    lvs = d['live_vs_locked_summary']
    assert any('/api/soul/forge' in x for x in lvs['live'])
    assert any('/api/shops/buy' in x for x in lvs['locked_no_call'])
    assert any('/api/soul-forge/retire' in x for x in lvs['locked_no_call'])
    assert d['reward_formula_change'] is False
    assert d['backend_changes'] == 0 and d['db_writes'] == 0
    print('[PASS] EMERGENCY_RESTORE Track E legacy economy mapping ready')
    return 0
if __name__ == '__main__': sys.exit(main())
