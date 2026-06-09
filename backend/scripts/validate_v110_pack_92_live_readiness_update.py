#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_live_readiness_update_v1.json')))
assert d.get('inventory_read_write_frontend_ready') is True
assert d.get('frontend_server_id_sweep_ready') is True
assert d.get('currency_loader_ready') is True
assert d.get('story_loader_ready') is True
assert d.get('equipment_loader_ready') is False
assert d.get('equipment_loader_preflight_ready') is True
for k in ('currency_spend_write_ready','story_progress_write_ready','equipment_write_ready','reward_claim_ledger_live','reward_live','progress_live','release_readiness_claimed'):
    assert d.get(k) is False, k
print('[v110 PACK_92_LIVE_READINESS_UPDATE] OK loaders_ready_or_preflight equipment_deferred no_writes_live no_release_claim')
