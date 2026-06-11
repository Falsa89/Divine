#!/usr/bin/env python3
"""Pack 105 — Reward source registry: 3 new sources registered correctly."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY, get_grant_fn, FORBIDDEN_REWARD_TYPES

for src_id in ('equipment_upgrade_strict_claim','forge_craft_strict_claim','equipment_fusion_strict_claim'):
    src = REWARD_SOURCE_REGISTRY.get(src_id)
    assert src is not None, f'source missing: {src_id}'
    assert src['server_scoped'] is True
    assert src['live'] is True
    assert src['idempotency'] == 'mandatory'
    assert src['pack_origin'] == 'pack_105'
    assert src.get('per_source_kill_switch_default') is False, f'{src_id} default OFF required'
    assert src.get('client_payload_ignored') is True
    assert src.get('server_side_catalog_required') is True
    # reward_types vuoto (no grant currency).
    assert src.get('reward_types', []) == [], f'{src_id} no reward grant'
    assert get_grant_fn(src_id) is not None

# Kill switch env names canonical.
KS_EXPECTED = {
    'equipment_upgrade_strict_claim': 'EQUIPMENT_UPGRADE_STRICT_ENABLED',
    'forge_craft_strict_claim': 'FORGE_CRAFT_STRICT_ENABLED',
    'equipment_fusion_strict_claim': 'EQUIPMENT_FUSION_STRICT_ENABLED',
}
for src_id, ks in KS_EXPECTED.items():
    assert REWARD_SOURCE_REGISTRY[src_id]['per_source_kill_switch_env'] == ks

print('[v110 PACK_105_REWARD_SOURCE] OK 3_sources_registered server_scoped idempotency_mandatory no_reward_grant kill_switch_default_off client_payload_ignored server_side_catalog_required')
