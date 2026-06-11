#!/usr/bin/env python3
"""Pack 104 — Reward source registry: 4 new sources registered correctly."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY, get_grant_fn, FORBIDDEN_REWARD_TYPES

for src_id in ('shop_buy_strict_claim','soul_forge_retire_strict_claim','equipment_equip_strict_claim','equipment_unequip_strict_claim'):
    src = REWARD_SOURCE_REGISTRY.get(src_id)
    assert src is not None, f'source missing: {src_id}'
    assert src['server_scoped'] is True, f'{src_id} must be server_scoped'
    assert src['live'] is True, f'{src_id} must be live'
    assert src['idempotency'] == 'mandatory', f'{src_id} must require idempotency'
    assert src['pack_origin'] == 'pack_104'
    assert src.get('per_source_kill_switch_default') is False, f'{src_id} must default OFF'
    assert src.get('client_payload_ignored') is True, f'{src_id} must ignore client payload'
    # reward_types: forbidden mai presenti.
    for k in src.get('reward_types', []):
        assert k not in FORBIDDEN_REWARD_TYPES, f'{src_id} cannot reward forbidden {k}'
    assert get_grant_fn(src_id) is not None, f'{src_id} grant_fn missing'

# shop buy: solo soft currencies allowed
shop = REWARD_SOURCE_REGISTRY['shop_buy_strict_claim']
assert 'gems' not in shop['reward_types']
assert 'experience' not in shop['reward_types']
assert shop.get('server_side_catalog_required') is True

# soul forge retire: only mission_coins + honor
sf = REWARD_SOURCE_REGISTRY['soul_forge_retire_strict_claim']
assert set(sf['reward_types']) == {'mission_coins', 'honor'}

# equipment equip/unequip: NO reward grant (reward_types vuoto)
for src_id in ('equipment_equip_strict_claim','equipment_unequip_strict_claim'):
    assert REWARD_SOURCE_REGISTRY[src_id]['reward_types'] == [], f'{src_id} must have no reward types'

print('[v110 PACK_104_REWARD_SOURCE] OK 4_sources_registered server_scoped idempotency_mandatory no_premium kill_switch_default_off client_payload_ignored')
