#!/usr/bin/env python3
"""Pack 102 — Hero ID source audit: solo LAUNCH_BASE_HERO_IDS, no premium/legacy/hidden."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from data.character_bible import LAUNCH_BASE_HERO_IDS, EXTRA_PREMIUM_HERO_IDS, CHARACTER_BIBLE_BY_ID
from data.tower_floor_catalog_v1 import TOWER_FLOOR_CATALOG_V1
base_set = set(LAUNCH_BASE_HERO_IDS)
premium_set = set(EXTRA_PREMIUM_HERO_IDS)
assert len(base_set) == 100, f'LAUNCH_BASE count {len(base_set)} != 100'
for f in TOWER_FLOOR_CATALOG_V1:
    for slot in f['enemy_team']:
        hid = slot['hero_id']
        assert hid in base_set, f'floor {f["floor"]} invalid hero_id {hid}'
        assert hid not in premium_set, f'floor {f["floor"]} premium/extra hero {hid}'
        entry = CHARACTER_BIBLE_BY_ID.get(hid)
        assert entry is not None, f'hero_id {hid} not in CHARACTER_BIBLE_BY_ID'
        assert entry.get('release_group') == 'launch_base', f'{hid} release_group not launch_base'
print('[v110 PACK_102_HERO_ID_SOURCE_AUDIT] OK only_launch_base 100_official_heroes no_premium_no_legacy_no_hidden')
