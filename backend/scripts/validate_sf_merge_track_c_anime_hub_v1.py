#!/usr/bin/env python3
import json, sys
from pathlib import Path
J = Path('/app/data/design/audit/sf_merge/track_c_anime_hub_panels_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_C_SOUL_FORGE_ABSORB_ECONOMY_MATERIALS_AND_SHOP_PREVIEW_READY'
    assert len(d['panels_added']) >= 4
    assert d['new_live_buy_buttons'] == 0
    assert d['new_api_mutating_calls'] == 0
    t = F.read_text()
    for tok in ['merge_hub','Materiali Anime','Negozio Anime','Regole','Tesoreria','/treasury','ANIME HUB']:
        assert tok in t, f'missing token in soul-forge: {tok}'
    assert 'IN PREPARAZIONE' in t
    print('[PASS] SF-MERGE Track C anime hub panels')
    return 0
if __name__=='__main__': sys.exit(main())
