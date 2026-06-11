#!/usr/bin/env python3
"""Pack 104 — Runtime smoke E2E result presence + integrity."""
import os, json, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(R, 'data/design/v110_pack_104_shop_soul_equipment_forge_strict_writes/v110_pack_104_runtime_smoke_e2e_result_v1.json')
assert os.path.exists(path), 'pack 104 smoke result missing — run smoke_v110_pack_104_shop_soul_equipment_forge_strict_writes_e2e.py first'
d = json.load(open(path))
assert d['real_smoke_executed'] is True, f'smoke not green: {d.get("required_missing")}'
assert d['shop_buy_strict_ready'] is True
assert d['soul_forge_retire_strict_ready'] is True
assert d['equipment_strict_writes_ready'] is True
assert d['forge_strict_ready'] is False, 'forge must remain deferred'
assert d['s1_s2_isolation_verified'] is True
assert d['no_users_gold_gems_experience_mutation'] is True
assert d['no_premium_grant'] is True
assert d['no_iap_gacha_payment'] is True
assert d['no_reward_live_general'] is True
assert d['release_readiness_claimed'] is False
assert d['client_payload_price_grant_ignored'] is True
for required in ('shop_buy_S1_success','shop_buy_replay_idempotent','shop_buy_S2_unaffected','soul_forge_retire_S1_success','soul_forge_replay_idempotent','soul_forge_no_cross_server','equipment_equip_S1_success','equipment_equip_replay_idempotent','equipment_no_cross_server','equipment_unequip_S1_success','forge_deferred_honest','client_payload_ignored','users_invariant','pack_91_103_preserved'):
    assert d['proofs'].get(required) is True, f'missing proof: {required}'
print('[v110 PACK_104_RUNTIME_SMOKE_E2E] OK shop_buy_ready soul_forge_ready equipment_strict_ready forge_deferred S1_S2_isolated no_users_mutation no_premium client_payload_ignored')
