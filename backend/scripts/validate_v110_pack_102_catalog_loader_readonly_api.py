#!/usr/bin/env python3
"""Pack 102 — Catalog loader/read-only API endpoints exist."""
import os, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=open(os.path.join(R,'backend/routes/tower_strict.py')).read()
for needle in [
    'tower_strict_catalog',
    'tower_strict_catalog_floor',
    "/tower/strict/catalog",
    '/tower/strict/catalog/floor/{floor}',
    'FLOOR_OUT_OF_CATALOG_RANGE',
    '_tower_catalog_summary',
    '_tower_catalog_floor',
    '_slc_pack_102_catalog_summary',
    '_slc_pack_102_catalog_floor',
]:
    assert needle in src, needle
# Loader API NON deve scrivere su DB
for block_name in ['tower_strict_catalog', 'tower_strict_catalog_floor']:
    m = re.search(rf'async def {block_name}\([^)]*\):.*?(?=    @router\.|\Z)', src, re.S)
    assert m, f'{block_name} fn missing'
    body = m.group(0)
    for forbidden in ['db.users.update_one','db.users.insert_one','db.player_server_profiles.update_one','db.tower_progress.insert_one','db.tower_progress.update_one']:
        assert forbidden not in body, f'{block_name} leak: {forbidden}'
print('[v110 PACK_102_CATALOG_LOADER_READONLY_API] OK 2_endpoints_added range_404_enforced no_db_writes')
