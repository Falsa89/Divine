#!/usr/bin/env python3
"""Pack 105 — SOT (Source Of Truth) doc presence + canonical references."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sot = os.path.join(R, 'docs/divine/110_FORGE_UPGRADE_FUSION_STRICT_PSP_MATERIAL_LEDGER_SPEND_SOT.md')
assert os.path.exists(sot), 'SOT doc missing'
src = open(sot).read()
for kw in ('equipment_upgrade_strict_claim','forge_craft_strict_claim','equipment_fusion_strict_claim',
           'PSP Material Storage','player_server_profiles.materials','EQUIPMENT_UPGRADE_STRICT_ENABLED',
           'FORGE_CRAFT_STRICT_ENABLED','EQUIPMENT_FUSION_STRICT_ENABLED','user_id + server_id',
           'reward_live_general=false','release_readiness_claimed=false','users.gold','IAP','gacha',
           'UPGRADE_COST_CATALOG_V1','FORGE_RECIPE_CATALOG_V1','FUSION_REQUIREMENT_CATALOG_V1',
           'MAX_EQUIPMENT_LEVEL_STRICT = 30','MAX_EQUIPMENT_RARITY_STRICT = 6'):
    assert kw in src, f'SOT missing: {kw}'
print('[v110 PACK_105_SOT] OK doc_present_all_canonical_keywords_present')
