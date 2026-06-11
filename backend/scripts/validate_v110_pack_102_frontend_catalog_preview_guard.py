#!/usr/bin/env python3
"""Pack 102 — Frontend catalog preview guard (NO new component, ma il TowerStrictConsumer NON deve chiamare endpoint legacy o usare hero IDs invalidi)."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f=os.path.join(R,'frontend/src/components/TowerStrictConsumer.tsx')
assert os.path.exists(f), 'TowerStrictConsumer missing'
src=open(f).read()
# Default OFF guard preservato
assert 'EXPO_PUBLIC_TOWER_STRICT_UI_ENABLED' in src
assert "const UI_ENABLED = UI_FLAG === 'true';" in src
assert 'if (!UI_ENABLED && !forceVisible) return null;' in src
# Nessuna chiamata legacy
for forb in ["'/api/tower/status'", '"/api/tower/status"', "'/api/tower/battle'", '"/api/tower/battle"']:
    assert forb not in src, f'legacy call leak: {forb}'
print('[v110 PACK_102_FRONTEND_CATALOG_PREVIEW_GUARD] OK default_off no_legacy_call existing_consumer_safe')
