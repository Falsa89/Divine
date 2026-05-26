#!/usr/bin/env python3
# PROJECT_SOUL_FORGE_EMERGENCY_RESTORE Track C — hero grid + filters restored.
import json, sys
from pathlib import Path
J = Path('/app/data/design/soul_forge/emergency_restore_track_c_hero_grid_filters_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_C_SOUL_FORGE_HERO_GRID_AND_FILTERS_RESTORED'
    t = F.read_text()
    # Filter implementation tokens
    assert 'RARITY_FILTERS' in t, 'filter list missing'
    assert 'rarityFilter' in t, 'filter state missing'
    assert 'filterChip' in t, 'filter chip style missing'
    assert 'setRarityFilter' in t, 'filter setter missing'
    # Card fields
    for tok in ('heroName','heroStars','heroLvl','heroEssence','selBadge','protectBadgeV2'):
        assert tok in t, f'hero card style {tok} missing'
    # Filter options present
    keys = {o['key'] for o in d['filter_controls_added']['options']}
    assert {'all','safe','high','1','2','3','4','5'}.issubset(keys)
    assert d['override_4plus_flow_preserved'] is True
    print('[PASS] EMERGENCY_RESTORE Track C hero grid + filters restored')
    return 0
if __name__ == '__main__': sys.exit(main())
