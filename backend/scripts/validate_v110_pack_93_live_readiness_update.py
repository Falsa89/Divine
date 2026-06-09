#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_93_economy_progress_write_paths/v110_pack_93_live_readiness_update_v1.json')))
assert d.get('currency_write_guard_ready') is True
assert d.get('currency_write_test_only_safe') is True
assert d.get('story_write_guard_ready') is True
assert d.get('story_write_execute_ready') is False
assert d.get('equipment_backfill_preflight_ready') is True
assert d.get('equipment_backfill_execute_ready') is False
assert d.get('equipment_write_guard_ready') is True
assert d.get('equipment_write_execute_ready') is False
assert d.get('reward_claim_ledger_design_ready') is True
assert d.get('reward_claim_ledger_live') is False
for k in ('reward_live','progress_live','release_readiness_claimed'):
    assert d.get(k) is False, k
print('[v110 PACK_93_LIVE_READINESS_UPDATE] OK currency_test_only_live story/equip/ledger_deferred no_release_claim')
