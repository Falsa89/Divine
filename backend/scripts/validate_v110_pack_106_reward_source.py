#!/usr/bin/env python3
"""Pack 106 — Reward source registry: 3 new sources registered correctly."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY, get_grant_fn, FORBIDDEN_REWARD_TYPES

for src_id in ('mail_claim_controlled','achievement_claim_controlled','daily_weekly_reward_claim'):
    src = REWARD_SOURCE_REGISTRY.get(src_id)
    assert src is not None, f'source missing: {src_id}'
    assert src['server_scoped'] is True
    assert src['live'] is True
    assert src['idempotency'] == 'mandatory'
    assert src['pack_origin'] == 'pack_106'
    assert src.get('per_source_kill_switch_default') is False
    assert src.get('client_payload_ignored') is True
    assert src.get('server_side_catalog_required') is True
    for k in src.get('reward_types', []):
        assert k not in FORBIDDEN_REWARD_TYPES, f'{src_id} live reward forbidden: {k}'
    assert get_grant_fn(src_id) is not None

# Achievement requires completion proof.
assert REWARD_SOURCE_REGISTRY['achievement_claim_controlled'].get('completion_proof_required') is True
# Daily/weekly has period_keying.
assert REWARD_SOURCE_REGISTRY['daily_weekly_reward_claim'].get('period_keying') == 'UTC_day_or_iso_week'

KS_EXPECTED = {
    'mail_claim_controlled': 'MAIL_CLAIM_CONTROLLED_ENABLED',
    'achievement_claim_controlled': 'ACHIEVEMENT_CLAIM_CONTROLLED_ENABLED',
    'daily_weekly_reward_claim': 'DAILY_WEEKLY_REWARD_CLAIM_ENABLED',
}
for src_id, ks in KS_EXPECTED.items():
    assert REWARD_SOURCE_REGISTRY[src_id]['per_source_kill_switch_env'] == ks

print('[v110 PACK_106_REWARD_SOURCE] OK 3_sources_registered server_scoped idempotency_mandatory completion_proof_present period_keying_set kill_switch_default_off client_payload_ignored')
