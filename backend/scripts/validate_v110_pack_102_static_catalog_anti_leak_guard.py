#!/usr/bin/env python3
"""Pack 102 — Static catalog anti-leak guard: no DB writes da catalog/loader, no random."""
import os, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=open(os.path.join(R,'backend/data/tower_floor_catalog_v1.py')).read()
# Catalog module DEVE essere import-safe
for forbidden in [
    'AsyncIOMotorClient','motor.motor_asyncio',
    'db.users','db.player_server_profiles','db.tower_progress',
    'update_one(','insert_one(','delete_one(','delete_many(',
    'import random','from random ',
]:
    assert forbidden not in src, f'catalog leak: {forbidden}'
# Strict path catalog endpoints NON devono scrivere
strict=open(os.path.join(R,'backend/routes/tower_strict.py')).read()
for block_name in ['tower_strict_catalog', 'tower_strict_catalog_floor']:
    m = re.search(rf'async def {block_name}\([^)]*\):.*?(?=    @router\.|\Z)', strict, re.S)
    if not m:
        continue
    body = m.group(0)
    for forbidden in ['db.users.update_one','db.users.insert_one','db.player_server_profiles.update_one','db.tower_progress.insert_one','db.tower_progress.update_one','grant_fn(','reward_claim_ledger']:
        assert forbidden not in body, f'{block_name} leak: {forbidden}'
print('[v110 PACK_102_STATIC_CATALOG_ANTI_LEAK_GUARD] OK import_safe no_random no_db_write_from_catalog_endpoints')
