#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_91_inventory_frontend_consumer_and_smoke/v110_pack_91_live_readiness_update_v1.json')))
assert d.get('inventory_frontend_consumers_ready') is True
assert d.get('real_mutating_smoke_ready') is True
for k in ('currencies_psp_loader_ready','story_psp_loader_ready','equipment_psp_loader_ready','reward_live','progress_live','release_readiness_claimed'):
    assert d.get(k) is False, k
print('[v110 PACK_91_LIVE_READINESS_UPDATE] OK consumers_ready smoke_ready reward_progress_off no_release_readiness_claimed')
