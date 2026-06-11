#!/usr/bin/env python3
"""Pack 102 — 100 floor catalog generation: exact 100 floors, no missing/duplicate."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from data.tower_floor_catalog_v1 import (
    TOWER_FLOOR_CATALOG_V1, TOWER_FLOOR_CATALOG_BY_FLOOR,
    TOTAL_LAUNCH_FLOORS, CATALOG_VERSION, TEAM_SIZE,
    get_catalog_summary,
)
assert TOTAL_LAUNCH_FLOORS == 100
assert CATALOG_VERSION == 'tower_v1_100_launch'
assert TEAM_SIZE == 6
assert len(TOWER_FLOOR_CATALOG_V1) == 100
# Floors esattamente 1..100
floors = sorted(f['floor'] for f in TOWER_FLOOR_CATALOG_V1)
assert floors == list(range(1, 101)), f'floors not 1..100: {floors[:5]}..{floors[-5:]}'
assert len(set(floors)) == 100, 'duplicate floors'
for f in TOWER_FLOOR_CATALOG_V1:
    assert len(f['enemy_team']) == 6
    ids = [s['hero_id'] for s in f['enemy_team']]
    assert len(set(ids)) == 6, f'floor {f["floor"]} has duplicate hero_id: {ids}'
summary = get_catalog_summary()
assert summary['total_floors'] == 100
assert summary['deterministic'] is True
assert summary['uses_only_launch_base_heroes'] is True
assert summary['borea_or_extra_premium_used'] is False
assert summary['content_identical_across_servers'] is True
print('[v110 PACK_102_100_FLOOR_CATALOG_GENERATION] OK exact_100_floors no_duplicates no_missing summary_clean')
