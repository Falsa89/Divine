#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_live_readiness_update_v1.json')))
for k in ('reward_ledger_live_ready','controlled_claim_paths_ready','wallet_spend_ledger_live_pack_93_preserved','equipment_strict_pack_94_preserved','story_strict_pack_95_preserved','legacy_quarantine_pack_94_95_preserved'):
    assert d.get(k) is True, k
for k in ('reward_ledger_live_enabled_default','reward_live_general','premium_grants','mail_claim_live','achievements_claim_live','daily_claim_live','battlepass_claim_live','afk_claim_live','event_claim_live','release_readiness_claimed'):
    assert d.get(k) is False, k
live_sources = d.get('controlled_claim_paths_live_sources') or []
assert 'qa_controlled_soft_currency_claim' in live_sources
assert 'story_progress_marker_claim' in live_sources
print('[v110 PACK_96_LIVE_READINESS_UPDATE] OK reward_ledger_live_ready_kill_switch_default_off 2_controlled_sources_ready no_general_live no_release_claim')
