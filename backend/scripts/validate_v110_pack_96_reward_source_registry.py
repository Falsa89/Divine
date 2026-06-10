#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_reward_source_registry_v1.json')))
assert d.get('file') == 'backend/utils/reward_source_registry.py'
srcs = d.get('sources') or {}
for sid in ('qa_controlled_soft_currency_claim', 'story_progress_marker_claim'):
    assert sid in srcs, sid
    assert srcs[sid].get('live') is True
    assert srcs[sid].get('server_scoped') is True
    assert srcs[sid].get('idempotency') == 'mandatory'
assert 'gems' in d.get('forbidden_reward_types')
assert d.get('unknown_source_blocker') == 'REWARD_SOURCE_NOT_ALLOWLISTED'
assert d.get('premium_grant_blocker') == 'PREMIUM_GRANT_BLOCKED'
import sys; sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY, FORBIDDEN_REWARD_TYPES, list_allowlisted_sources
assert 'qa_controlled_soft_currency_claim' in REWARD_SOURCE_REGISTRY
assert 'story_progress_marker_claim' in REWARD_SOURCE_REGISTRY
assert 'gems' in FORBIDDEN_REWARD_TYPES
assert set(list_allowlisted_sources()) >= {'qa_controlled_soft_currency_claim', 'story_progress_marker_claim'}
# Pack 96 baseline: assert at least the Pack 96 sources are present; Pack 97+ may add more sources.
assert 'qa_controlled_soft_currency_claim' in list_allowlisted_sources()
assert 'story_progress_marker_claim' in list_allowlisted_sources()
print('[v110 PACK_96_REWARD_SOURCE_REGISTRY] OK 2_live_sources gems_forbidden allowlist_consistent')
