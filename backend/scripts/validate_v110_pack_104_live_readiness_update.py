#!/usr/bin/env python3
"""Pack 104 — Live readiness flags update."""
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Live readiness summary atteso post-Pack-104.
allowed = {
    'shop_buy_strict_ready': True,
    'soul_forge_retire_strict_ready': True,
    'equipment_strict_writes_ready': True,
    'forge_strict_ready': False,
    'tower_floor_claim_ready': True,  # Pack 103 preserved
    'tower_execute_ready': True,        # Pack 103 preserved
    'reward_live_general': False,
    'premium_grants': False,
    'release_readiness_claimed': False,
}
# Verifico smoke result.
smoke_path = os.path.join(R, 'data/design/v110_pack_104_shop_soul_equipment_forge_strict_writes/v110_pack_104_runtime_smoke_e2e_result_v1.json')
d = json.load(open(smoke_path))
for k, v in allowed.items():
    if k in d:
        assert d[k] == v, f'live readiness mismatch {k}: {d[k]} != {v}'
print('[v110 PACK_104_LIVE_READINESS_UPDATE] OK shop_ready soul_forge_ready equipment_strict_ready forge_deferred reward_live_general_false release_readiness_false')
