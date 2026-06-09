#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_live_readiness_update_v1.json')))
for k in ('reward_ledger_foundation_ready','story_progress_write_guard_ready','story_progress_write_strict_test_only_safe','legacy_guards_ready','earn_mission_quarantine_active','earn_dimension_quarantine_active','earn_pvp_quarantine_active_pack_94_preserved','earn_guild_quarantine_active_pack_94_preserved','shops_buy_quarantine_active','soul_forge_retire_quarantine_active','wallet_spend_ledger_live_pack_93_preserved','equipment_loader_strict_real_pack_94_preserved','equipment_write_strict_real_pack_94_preserved'):
    assert d.get(k) is True, k
for k in ('reward_ledger_live','story_progress_write_grants_live_currency','reward_live','progress_live','release_readiness_claimed'):
    assert d.get(k) is False, k
print('[v110 PACK_95_LIVE_READINESS_UPDATE] OK ledger_foundation_ready story_write_test_only legacy_guards_ready no_reward_live no_release_claim')
