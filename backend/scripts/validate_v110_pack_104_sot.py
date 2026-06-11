#!/usr/bin/env python3
"""Pack 104 — SOT (Source Of Truth) doc + canonical references present."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# SOT doc esiste
sot = os.path.join(R, 'docs/divine/110_SHOP_SOUL_EQUIPMENT_FORGE_STRICT_WRITES_SOT.md')
assert os.path.exists(sot), 'SOT doc missing'
src = open(sot).read()
for kw in ('shop_buy_strict_claim','soul_forge_retire_strict_claim','equipment_equip_strict_claim','equipment_unequip_strict_claim','FORGE_UPGRADE_STRICT_DEFERRED','EQUIPMENT_FUSION_STRICT_DEFERRED','user_id + server_id','reward_live_general=false','release_readiness_claimed=false','users.gold','IAP','gacha'):
    assert kw in src, f'SOT missing: {kw}'
print('[v110 PACK_104_SOT] OK doc_present_all_canonical_keywords_present')
