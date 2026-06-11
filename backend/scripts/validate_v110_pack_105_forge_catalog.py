#!/usr/bin/env python3
"""Pack 105 — Forge catalog server-side: no premium, materials whitelisted, capped."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from data.forge_strict_catalog_v1 import (
    UPGRADE_COST_CATALOG_V1, FORGE_RECIPE_CATALOG_V1, FUSION_REQUIREMENT_CATALOG_V1,
    ALLOWED_MATERIALS, MAX_EQUIPMENT_LEVEL_STRICT, MAX_EQUIPMENT_RARITY_STRICT,
    get_upgrade_cost, get_recipe, get_fusion_requirement, CATALOG_VERSION,
)

assert CATALOG_VERSION.startswith('forge_strict_catalog_v1')
assert MAX_EQUIPMENT_LEVEL_STRICT == 30
assert MAX_EQUIPMENT_RARITY_STRICT == 6
assert ALLOWED_MATERIALS == {'steel_ore','magic_dust','ancient_relic','phoenix_feather','crystal_shard'}

FORBIDDEN_SOFT = {'gems','premium_pull','standard_pull','stamina','experience'}

for lvl, c in UPGRADE_COST_CATALOG_V1.items():
    for k in c['soft_currencies']: assert k not in FORBIDDEN_SOFT, f'upgrade forbidden soft: {lvl}.{k}'
    for k in c['materials']: assert k in ALLOWED_MATERIALS, f'upgrade forbidden material: {lvl}.{k}'

for rid, r in FORGE_RECIPE_CATALOG_V1.items():
    for k in r['cost']['soft_currencies']: assert k not in FORBIDDEN_SOFT, f'recipe forbidden soft: {rid}.{k}'
    for k in r['cost']['materials']: assert k in ALLOWED_MATERIALS, f'recipe forbidden material: {rid}.{k}'
    tpl = r['grant_equipment_template']
    assert tpl['rarity'] <= MAX_EQUIPMENT_RARITY_STRICT

for rar, req in FUSION_REQUIREMENT_CATALOG_V1.items():
    for k in req['cost_soft']: assert k not in FORBIDDEN_SOFT, f'fusion forbidden soft: {rar}.{k}'
    for k in req['cost_materials']: assert k in ALLOWED_MATERIALS, f'fusion forbidden material: {rar}.{k}'

# Lookup tests.
assert get_upgrade_cost(2) is not None
assert get_upgrade_cost(30) is not None
assert get_upgrade_cost(31) is None
assert get_upgrade_cost(1) is None
assert get_recipe('iron_sword_recipe') is not None
assert get_recipe('nope') is None
assert get_fusion_requirement(2) is not None
assert get_fusion_requirement(7) is None

print('[v110 PACK_105_FORGE_CATALOG] OK deterministic no_premium materials_whitelisted cap_30_6 lookups_work')
