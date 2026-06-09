#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_first_controlled_claim_sources_v1.json')))
live = d.get('first_controlled_sources_live') or []
assert 'qa_controlled_soft_currency_claim' in live
assert 'story_progress_marker_claim' in live
assert d.get('first_controlled_sources_count') == 2
assert d.get('all_sources_server_scoped') is True
assert d.get('all_sources_idempotency_mandatory') is True
assert d.get('no_real_player_facing_grant_source_in_pack_96') is True
print('[v110 PACK_96_FIRST_CONTROLLED_CLAIM_SOURCES] OK 2_sources_live_only no_real_player_facing_in_pack')
